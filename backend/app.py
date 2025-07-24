import os
import logging
import time
import requests
import json
import re
from typing import Dict, List, Optional, Any, Union
from functools import wraps
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from enum import Enum
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from services.openrouter_service import OpenRouterService

# Load environment variables
load_dotenv()

# Enhanced logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('airbnb_search.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configure CORS for internal use (simplified security)
CORS(app, origins="*")

# Initialize services
openrouter_service = OpenRouterService()

# RapidAPI Configuration
RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY', 'd8dad7a0d0msh79d5e302536f59cp1e388bjsn65fdb4ba9233')
RAPIDAPI_HOST = os.getenv('RAPIDAPI_HOST', 'airbnb19.p.rapidapi.com')

class ErrorType(Enum):
    """Error types for better error handling"""
    API_TIMEOUT = "api_timeout"
    API_ERROR = "api_error"
    PARSING_ERROR = "parsing_error"
    VALIDATION_ERROR = "validation_error"
    NETWORK_ERROR = "network_error"
    RATE_LIMIT = "rate_limit"

@dataclass
class SearchResult:
    """Structured search result"""
    success: bool
    properties: List[Dict]
    error: Optional[str] = None
    error_type: Optional[ErrorType] = None
    processing_time: float = 0.0
    source: str = "unknown"

class CircuitBreaker:
    """Circuit breaker pattern for external API calls"""
    
    def __init__(self, failure_threshold=5, recovery_timeout=60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
        self._lock = threading.Lock()
    
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        with self._lock:
            if self.state == 'OPEN':
                if time.time() - self.last_failure_time > self.recovery_timeout:
                    self.state = 'HALF_OPEN'
                else:
                    raise Exception("Circuit breaker is OPEN")
            
            try:
                result = func(*args, **kwargs)
                if self.state == 'HALF_OPEN':
                    self.state = 'CLOSED'
                    self.failure_count = 0
                return result
            except Exception as e:
                self.failure_count += 1
                self.last_failure_time = time.time()
                
                if self.failure_count >= self.failure_threshold:
                    self.state = 'OPEN'
                
                raise e

class RetryHandler:
    """Retry handler with exponential backoff"""
    
    @staticmethod
    def retry_with_backoff(max_retries=3, base_delay=1, max_delay=60):
        """Decorator for retry with exponential backoff"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                for attempt in range(max_retries + 1):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        if attempt == max_retries:
                            logger.error(f"Function {func.__name__} failed after {max_retries} retries: {e}")
                            raise e
                        
                        delay = min(base_delay * (2 ** attempt), max_delay)
                        logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}, retrying in {delay}s: {e}")
                        time.sleep(delay)
                
                return None
            return wrapper
        return decorator

class InputValidator:
    """Input validation and sanitization"""
    
    @staticmethod
    def sanitize_query(query: str) -> str:
        """Sanitize user query input"""
        if not isinstance(query, str):
            return ""
        
        # Remove potential XSS and injection attempts
        query = re.sub(r'<[^>]*>', '', query)  # Remove HTML tags
        query = re.sub(r'[^\w\s\-\.,\'\"]', '', query)  # Keep only safe characters
        query = query.strip()
        
        # Limit length
        if len(query) > 1000:
            query = query[:1000]
            logger.warning("Query truncated due to length")
        
        return query
    
    @staticmethod
    def validate_location(location: str) -> bool:
        """Validate location input"""
        if not isinstance(location, str):
            return False
        
        location = location.strip()
        
        # Check for minimum length
        if len(location) < 1:
            return False
        
        # Check for maximum length
        if len(location) > 100:
            return False
        
        # Check for at least one letter
        if not re.search(r'[a-zA-Z]', location):
            return False
        
        return True
    
    @staticmethod
    def validate_filters(filters: Dict) -> Dict:
        """Validate and sanitize filter inputs"""
        if not isinstance(filters, dict):
            return {}
        
        validated_filters = {}
        
        # Validate amenities
        if 'amenities' in filters and isinstance(filters['amenities'], list):
            validated_filters['amenities'] = [
                str(amenity)[:50] for amenity in filters['amenities'][:20]  # Limit count and length
            ]
        
        # Validate property types
        if 'propertyTypes' in filters and isinstance(filters['propertyTypes'], list):
            valid_types = ['entire_house', 'private_room', 'shared_room', 'apartment', 'villa']
            validated_filters['propertyTypes'] = [
                ptype for ptype in filters['propertyTypes'] if ptype in valid_types
            ]
        
        # Validate price range
        if 'priceMin' in filters:
            try:
                price_min = float(filters['priceMin'])
                if 0 <= price_min <= 10000:
                    validated_filters['priceMin'] = price_min
            except (ValueError, TypeError):
                pass
        
        if 'priceMax' in filters:
            try:
                price_max = float(filters['priceMax'])
                if 0 <= price_max <= 50000:
                    validated_filters['priceMax'] = price_max
            except (ValueError, TypeError):
                pass
        
        return validated_filters

class EnhancedDataTransformer:
    """Enhanced data transformation with better error handling"""
    
    @staticmethod
    def safe_extract_price(price_data: Any) -> int:
        """Safely extract price from various formats"""
        try:
            if isinstance(price_data, (int, float)):
                return max(int(price_data), 0)
            
            if isinstance(price_data, str):
                # Remove currency symbols and extract numbers
                price_str = re.sub(r'[^\d.]', '', price_data)
                if price_str:
                    return max(int(float(price_str)), 0)
            
            if isinstance(price_data, dict):
                # Try common price field names
                for field in ['price', 'amount', 'value', 'cost']:
                    if field in price_data:
                        return EnhancedDataTransformer.safe_extract_price(price_data[field])
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.warning(f"Price extraction failed: {e}")
        
        return 100  # Default fallback price
    
    @staticmethod
    def safe_extract_rating(rating_data: Any) -> tuple[float, int]:
        """Safely extract rating and review count"""
        rating = 4.5
        review_count = 0
        
        try:
            if isinstance(rating_data, str):
                # Handle formats like "4.81 (53)" or "New"
                if rating_data.lower() == 'new':
                    return 0.0, 0
                
                # Extract rating and review count
                match = re.search(r'(\d+\.?\d*)\s*\((\d+)\)', rating_data)
                if match:
                    rating = float(match.group(1))
                    review_count = int(match.group(2))
                else:
                    # Try to extract just the rating
                    rating_match = re.search(r'(\d+\.?\d*)', rating_data)
                    if rating_match:
                        rating = float(rating_match.group(1))
            
            elif isinstance(rating_data, (int, float)):
                rating = float(rating_data)
            
            # Validate rating range
            rating = max(0.0, min(5.0, rating))
            review_count = max(0, review_count)
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.warning(f"Rating extraction failed: {e}")
        
        return rating, review_count
    
    @staticmethod
    def safe_extract_image_url(image_data: Any) -> str:
        """Safely extract image URL"""
        default_image = 'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=800'
        
        try:
            if isinstance(image_data, str) and image_data.startswith('http'):
                return image_data
            
            if isinstance(image_data, list) and image_data:
                for item in image_data:
                    if isinstance(item, dict):
                        for field in ['picture', 'url', 'src', 'image']:
                            if field in item and isinstance(item[field], str):
                                if item[field].startswith('http'):
                                    return item[field]
                    elif isinstance(item, str) and item.startswith('http'):
                        return item
            
            if isinstance(image_data, dict):
                for field in ['picture', 'url', 'src', 'image']:
                    if field in image_data and isinstance(image_data[field], str):
                        if image_data[field].startswith('http'):
                            return image_data[field]
        
        except (TypeError, AttributeError) as e:
            logger.warning(f"Image URL extraction failed: {e}")
        
        return default_image

# Initialize enhanced services
circuit_breaker = CircuitBreaker()
input_validator = InputValidator()
data_transformer = EnhancedDataTransformer()

def get_place_id(location):
    """Convert location string to Google Place ID with international support"""
    # Enhanced location to Place ID mapping with international cities
    place_ids = {
        # US Cities
        'san francisco': 'ChIJIQBpAG2ahYAR_6128GcTUEo',
        'new york': 'ChIJOwg_06VPwokRYv534QaPC8g',
        'los angeles': 'ChIJE9on3F3HwoAR9AhGJW_fL-I',
        'chicago': 'ChIJ7cv00DwsDogRAMDACa2m4K8',
        'miami': 'ChIJEcHIDqKw2YgRZU-t3XHylv8',
        'seattle': 'ChIJVTPokywQkFQRmtVEaUZlJRA',
        'boston': 'ChIJGzE-4ua3t4kRoRqiaseu_Qg',
        'washington': 'ChIJW-T2Wt7Gt4kRKl2I1CJFUsI',
        'las vegas': 'ChIJ0X31pIK3voARo3mz1ebVzDo',
        'denver': 'ChIJzxcfI6qAa4cR1jaKJ_j0jhE',
        'austin': 'ChIJLwPMoJm1RIYRetVp1EtGm10',
        'portland': 'ChIJJ3SpfQsLlVQRkYXR9ua5Nhw',
        'atlanta': 'ChIJ5dSg2UeX9YgRBS2sMgYvZpQ',
        'phoenix': 'ChIJa147K9HKwoARHuGSk8b3cHo',
        'philadelphia': 'ChIJ60u11Ni3xokRwVg-jNgU9Yk',
        'san diego': 'ChIJ0X31pIK3voARo3mz1ebVzDo',
        'dallas': 'ChIJS5dFe_cZTIYRj2dH9qSb7Lk',
        'houston': 'ChIJAYWNSLS4QIYROwVl894CDco',
        'orlando': 'ChIJvQz5TjQl54gRRNSLC4_U7Lk',
        'nashville': 'ChIJPZDrEzLsZIgRoNrpodC5P30',
        
        # International Cities
        'london': 'ChIJdd4hrwug2EcRmSrV3Vo6llI',
        'paris': 'ChIJD7fiBh9u5kcRYJSMaMOCCwQ',
        'tokyo': 'ChIJ51cu8IcbXWARiRtXIothAS4',
        'sydney': 'ChIJP3Sa8ziYEmsRUKgyFmh9AQM',
        'barcelona': 'ChIJ5TCOcRaYpBIRCmZHTz37sEQ',
        'rome': 'ChIJu46S-ZZhLxMROG5lkwZ3D7k',
        'amsterdam': 'ChIJVXealLU_xkcRja_At0z9AGY',
        'berlin': 'ChIJAVkDPzdOqEcRcDteJg9eNg8',
        'madrid': 'ChIJgTwKgJcpQg0RaSKMYcHeNsQ',
        'vienna': 'ChIJN1t_tDeuEmsRUsoyG83frY4',
        'prague': 'ChIJi3lwCZyTC0cRkEAWZg-vAAQ',
        'budapest': 'ChIJyc_U0TTxQUcRYBEeDCnEAAQ',
        'lisbon': 'ChIJ--acWvpzGQ0R4dWB0Y9T5fI',
        'dublin': 'ChIJL6wn6oAOZ0gRoHExl6nHAAo',
        'copenhagen': 'ChIJIz2AXDxTUkYRmFgW2OI5__s',
        'stockholm': 'ChIJ-1-U7rZyyEYRzZLgw9BDqQQ',
        'oslo': 'ChIJOfBn8mFuQUYRmh4j019gkn4',
        'helsinki': 'ChIJ3fnh-L5LkkYRRI7RpIXXxQQ',
        'zurich': 'ChIJGbIKnZPJkEcRp8Wa7JkXQQQ',
        'geneva': 'ChIJL3JqrwJjjEcRaEwY6ySh_Q4',
        'brussels': 'ChIJl5fz7WR9w0cRzaXdXo_hmpE',
        'milan': 'ChIJ53USP0nBhkcRjQ50xhPN_zw',
        'florence': 'ChIJrdbSgKNWKhMRk6t7AkG_7jQ',
        'venice': 'ChIJf-7Fa3XJfkcRBONgdBYEYjQ',
        'naples': 'ChIJd01Kz2SRORMRDjvOSqe_QQQ',
        'athens': 'ChIJ8UNwBh-9oRQR3Y1mdkU1Nic',
        'istanbul': 'ChIJawhoAASnyhQR0LABvJj-zOE',
        'moscow': 'ChIJybDUc_xKtUYRTM9XV8zWRD0',
        'mumbai': 'ChIJwe1EZjDG5zsRaYxkjY_tpF0',
        'delhi': 'ChIJL_P_CXMEDTkRw0ZdG-0GVvw',
        'singapore': 'ChIJyY4rtGcX2jERIKTaKVXwOgQ',
        'hong kong': 'ChIJD5gyo-3iAzQRfMnq27qzivA',
        'seoul': 'ChIJzWXFYYuifDUR64Pq5LTtioU',
        'bangkok': 'ChIJ2a1DUOOe4jARSKy4mLMiDgQ',
        'mexico city': 'ChIJB3UBaGEZ0oURaLlXbBiAiOo',
        'sao paulo': 'ChIJ0WGkg4FEzpQRrlsz_whLqZs',
        'rio de janeiro': 'ChIJW6AIkVXemwARTtIvZ2xC3FA',
        'buenos aires': 'ChIJvQz5TjQl54gRRNSLC4_U7Lk',
    }
    
    location_lower = location.lower().strip()
    
    # Try exact match first
    if location_lower in place_ids:
        return place_ids[location_lower]
    
    # Try partial match
    for city, place_id in place_ids.items():
        if city in location_lower or location_lower in city:
            return place_id
    
    # Enhanced fallback logic
    abbreviations = {
        'sf': 'san francisco',
        'nyc': 'new york',
        'la': 'los angeles',
        'vegas': 'las vegas',
    }
    
    for abbr, full_name in abbreviations.items():
        if abbr == location_lower and full_name in place_ids:
            return place_ids[full_name]
    
    # Default to San Francisco if no match
    logger.warning(f"No Place ID found for '{location}', defaulting to San Francisco")
    return place_ids['san francisco']

def extract_multiple_locations_from_query(query):
    """Extract multiple locations from queries like 'cheapest large homes globally' or 'best properties in Europe'"""
    query_lower = query.lower().strip()
    
    # Global/multi-country patterns
    global_patterns = [
        r'globally|worldwide|international|anywhere',
        r'best.*in.*world|cheapest.*globally|most.*expensive.*worldwide',
        r'across.*countries|multiple.*countries|different.*countries'
    ]
    
    # Regional patterns
    regional_patterns = {
        'europe': ['london', 'paris', 'barcelona', 'rome', 'amsterdam', 'berlin', 'madrid', 'vienna', 'prague'],
        'asia': ['tokyo', 'singapore', 'hong kong', 'seoul', 'bangkok', 'mumbai', 'delhi'],
        'americas': ['new york', 'los angeles', 'mexico city', 'sao paulo', 'buenos aires'],
        'north america': ['new york', 'los angeles', 'chicago', 'mexico city'],
        'south america': ['sao paulo', 'rio de janeiro', 'buenos aires'],
    }
    
    # Check for global patterns
    for pattern in global_patterns:
        if re.search(pattern, query_lower):
            # Return top international cities for global search
            return ['new york', 'london', 'paris', 'tokyo', 'sydney']
    
    # Check for regional patterns
    for region, cities in regional_patterns.items():
        if region in query_lower:
            return cities[:5]  # Return top 5 cities from region
    
    # Default to single location extraction
    return [extract_location_from_query(query)]

def extract_search_criteria_from_query(query):
    """Extract search criteria like 'cheapest', 'largest', 'most expensive' from query"""
    query_lower = query.lower().strip()
    
    criteria = {
        'sort_by': None,
        'property_size': None,
        'price_preference': None
    }
    
    # Price-related patterns
    if re.search(r'cheapest|budget|affordable|lowest.?price', query_lower):
        criteria['sort_by'] = 'price_asc'
        criteria['price_preference'] = 'budget'
    elif re.search(r'most.?expensive|luxury|highest.?price|premium', query_lower):
        criteria['sort_by'] = 'price_desc'
        criteria['price_preference'] = 'luxury'
    
    # Size-related patterns
    if re.search(r'large|big|huge|massive|spacious', query_lower):
        criteria['property_size'] = 'large'
    elif re.search(r'small|tiny|compact|cozy', query_lower):
        criteria['property_size'] = 'small'
    
    return criteria

@RetryHandler.retry_with_backoff(max_retries=2, base_delay=1)
def call_airbnb_search(location, checkin=None, checkout=None, adults=1, children=0, infants=0, pets=0, min_price=None, max_price=None):
    """Enhanced call to RapidAPI Airbnb19 with circuit breaker and retry logic"""
    try:
        # Validate location first
        if not input_validator.validate_location(location):
            logger.error(f"Invalid location: {location}")
            return []
        
        # Get Place ID for the location
        place_id = get_place_id(location)
        logger.info(f"Using Place ID {place_id} for location: {location}")
        
        # Prepare RapidAPI request
        url = "https://airbnb19.p.rapidapi.com/api/v2/searchPropertyByPlaceId"
        
        params = {
            "placeId": place_id,
            "adults": adults,
            "currency": "USD",
            "guestFavorite": False,
            "ib": False
        }
        
        # Add optional parameters if provided
        if children > 0:
            params["children"] = children
        if infants > 0:
            params["infants"] = infants
        if pets > 0:
            params["pets"] = pets
        if checkin:
            params["checkin"] = checkin
        if checkout:
            params["checkout"] = checkout
        if min_price:
            params["minPrice"] = min_price
        if max_price:
            params["maxPrice"] = max_price
        
        headers = {
            "x-rapidapi-host": RAPIDAPI_HOST,
            "x-rapidapi-key": RAPIDAPI_KEY
        }
        
        logger.info(f"Calling RapidAPI with params: {params}")
        
        # Make API request with circuit breaker
        def api_call():
            response = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=15
            )
            
            if response.status_code == 429:  # Rate limit
                raise Exception("Rate limit exceeded")
            elif response.status_code != 200:
                raise Exception(f"API returned status {response.status_code}: {response.text}")
            
            return response.json()
        
        data = circuit_breaker.call(api_call)
        
        if 'data' in data and 'list' in data['data']:
            properties = data['data']['list']
            logger.info(f"RapidAPI returned {len(properties)} properties for {location}")
            return properties
        else:
            logger.warning(f"Unexpected API response structure: {list(data.keys())}")
            return []
            
    except requests.exceptions.Timeout:
        logger.error("RapidAPI request timed out")
        return []
    except requests.exceptions.ConnectionError:
        logger.error("Failed to connect to RapidAPI")
        return []
    except Exception as e:
        logger.error(f"RapidAPI error: {str(e)}")
        return []

def search_multiple_locations(locations, criteria, filters=None):
    """Enhanced search multiple locations with concurrent processing"""
    if not locations:
        return []
    
    # Limit number of concurrent locations
    locations = locations[:10]  # Max 10 locations
    
    all_properties = []
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        # Submit all location searches
        future_to_location = {
            executor.submit(call_airbnb_search, location): location
            for location in locations
        }
        
        # Collect results
        for future in as_completed(future_to_location):
            location = future_to_location[future]
            try:
                properties = future.result()
                # Add location info to each property
                for prop in properties:
                    prop['search_location'] = location
                all_properties.extend(properties)
            except Exception as e:
                logger.error(f"Error searching {location}: {e}")
                continue
    
    logger.info(f"Found {len(all_properties)} total properties across {len(locations)} locations")
    return all_properties

def extract_location_from_query(query):
    """Universal location extraction from natural language query"""
    query_lower = query.lower().strip()
    
    # Enhanced location extraction patterns
    location_patterns = [
        # Direct location patterns
        r'in\s+([^,\.\?!]+(?:,\s*[^,\.\?!]+)*)',
        r'near\s+([^,\.\?!]+(?:,\s*[^,\.\?!]+)*)',
        r'around\s+([^,\.\?!]+(?:,\s*[^,\.\?!]+)*)',
        r'at\s+([^,\.\?!]+(?:,\s*[^,\.\?!]+)*)',
        r'to\s+([^,\.\?!]+(?:,\s*[^,\.\?!]+)*)',
        r'from\s+([^,\.\?!]+(?:,\s*[^,\.\?!]+)*)',
        r'visit\s+([^,\.\?!]+(?:,\s*[^,\.\?!]+)*)',
        r'explore\s+([^,\.\?!]+(?:,\s*[^,\.\?!]+)*)',
        r'stay\s+in\s+([^,\.\?!]+(?:,\s*[^,\.\?!]+)*)',
        r'places?\s+in\s+([^,\.\?!]+(?:,\s*[^,\.\?!]+)*)',
        r'accommodation\s+in\s+([^,\.\?!]+(?:,\s*[^,\.\?!]+)*)',
        r'hotel\s+in\s+([^,\.\?!]+(?:,\s*[^,\.\?!]+)*)',
        r'apartment\s+in\s+([^,\.\?!]+(?:,\s*[^,\.\?!]+)*)',
        r'room\s+in\s+([^,\.\?!]+(?:,\s*[^,\.\?!]+)*)',
        r'house\s+in\s+([^,\.\?!]+(?:,\s*[^,\.\?!]+)*)',
        # Location at end of query
        r'([^,\.\?!]+(?:,\s*[^,\.\?!]+)*)$'
    ]
    
    # Try each pattern
    for pattern in location_patterns:
        matches = re.findall(pattern, query_lower)
        for match in matches:
            location = match.strip()
            
            # Skip common non-location words
            skip_words = {
                'a', 'an', 'the', 'big', 'small', 'nice', 'good', 'great', 'beautiful', 
                'cheap', 'expensive', 'luxury', 'budget', 'find', 'looking', 'search',
                'apartment', 'house', 'room', 'place', 'hotel', 'accommodation',
                'stay', 'night', 'week', 'month', 'vacation', 'holiday', 'trip',
                'family', 'couple', 'group', 'people', 'person', 'guest', 'guests',
                'bedroom', 'bathroom', 'kitchen', 'pool', 'wifi', 'parking'
            }
            
            # Clean and validate location
            location_words = [word.strip() for word in location.split() if word.strip()]
            location_words = [word for word in location_words if word not in skip_words]
            
            if location_words and len(' '.join(location_words)) >= 2:
                # Capitalize properly and return
                cleaned_location = ' '.join(word.capitalize() for word in location_words)
                
                # Additional validation - must contain at least one letter
                if re.search(r'[a-zA-Z]', cleaned_location):
                    return cleaned_location
    
    # Final fallback - return a generic location
    return 'United States'

def transform_airbnb_properties(airbnb_properties):
    """Enhanced transform RapidAPI Airbnb19 response with better error handling"""
    transformed = []
    
    for prop in airbnb_properties:
        try:
            # Use enhanced data transformer
            transformed_prop = transform_property_with_validation(prop)
            if transformed_prop:
                transformed.append(transformed_prop)
                
        except Exception as e:
            logger.error(f"Error transforming property: {e}")
            continue
    
    return transformed

def transform_property_with_validation(property_data: Dict) -> Optional[Dict]:
    """Transform property data with comprehensive validation"""
    try:
        if not isinstance(property_data, dict):
            return None
        
        listing = property_data.get('listing', {})
        if not isinstance(listing, dict):
            listing = {}
        
        # Extract required fields with fallbacks
        property_id = str(listing.get('id', '') or property_data.get('id', '') or 'unknown')
        if property_id == 'unknown':
            return None  # Skip properties without valid ID
        
        title = (listing.get('legacyName', '') or 
                property_data.get('title', '') or 
                f"Property {property_id}")
        
        # Extract price
        structured_price = property_data.get('structuredDisplayPrice', {})
        primary_line = structured_price.get('primaryLine', {})
        price = data_transformer.safe_extract_price(primary_line.get('price', 100))
        
        # Extract rating and reviews
        rating_str = property_data.get('avgRatingLocalized', '4.5 (25)')
        rating, review_count = data_transformer.safe_extract_rating(rating_str)
        
        # Extract image
        contextual_pictures = property_data.get('contextualPictures', [])
        image_url = data_transformer.safe_extract_image_url(contextual_pictures)
        
        # Extract location
        demand_stay = property_data.get('demandStayListing', {})
        location_info = demand_stay.get('location', {})
        city = location_info.get('city', '') or listing.get('legacyCity', '')
        search_location = property_data.get('search_location', '')
        location = city or search_location or 'Location Available'
        
        # Build validated property object
        transformed_property = {
            'id': property_id,
            'title': title[:200],  # Limit title length
            'price': price,
            'currency': 'USD',
            'rating': rating,
            'reviewCount': review_count,
            'imageUrl': image_url,
            'location': location[:100],  # Limit location length
            'url': f"https://www.airbnb.com/rooms/{property_id}",
            'type': listing.get('title', 'Apartment')[:50],
            'guests': 2,  # Default
            'source': 'real_airbnb_rapidapi',
            'bedrooms': 1,  # Default
            'bathrooms': 1,  # Default
            'amenities': ['WiFi', 'Kitchen']  # Default
        }
        
        return transformed_property
        
    except Exception as e:
        logger.error(f"Property transformation failed: {e}")
        return None

# Flask Routes
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'version': '2.0.0'
    })

@app.route('/api/v1/search', methods=['POST'])
def search_properties():
    """Enhanced search endpoint with comprehensive error handling"""
    start_time = time.time()
    
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided',
                'data': {'properties': [], 'total': 0}
            }), 400
        
        # Extract and validate query
        query = data.get('query', '')
        clean_query = input_validator.sanitize_query(query)
        
        if not clean_query:
            return jsonify({
                'success': False,
                'error': 'Invalid or empty query',
                'data': {'properties': [], 'total': 0}
            }), 400
        
        # Extract and validate filters
        filters = data.get('filters', {})
        clean_filters = input_validator.validate_filters(filters)
        
        logger.info(f"Processing search request: '{clean_query}' with filters: {clean_filters}")
        
        # Extract locations and criteria from query
        locations = extract_multiple_locations_from_query(clean_query)
        criteria = extract_search_criteria_from_query(clean_query)
        
        logger.info(f"Extracted locations: {locations}")
        logger.info(f"Extracted criteria: {criteria}")
        
        # Perform search
        if len(locations) > 1:
            # Multi-location search
            airbnb_properties = search_multiple_locations(locations, criteria, clean_filters)
        else:
            # Single location search
            airbnb_properties = call_airbnb_search(locations[0])
            # Add location info to each property
            for prop in airbnb_properties:
                prop['search_location'] = locations[0]
        
        # Transform properties
        transformed_properties = transform_airbnb_properties(airbnb_properties)
        
        # Apply sorting based on criteria
        if criteria.get('sort_by') == 'price_asc':
            transformed_properties.sort(key=lambda x: x.get('price', 0))
        elif criteria.get('sort_by') == 'price_desc':
            transformed_properties.sort(key=lambda x: x.get('price', 0), reverse=True)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Prepare response
        response = {
            'success': True,
            'data': {
                'properties': transformed_properties,
                'total': len(transformed_properties),
                'query': clean_query,
                'locations': locations,
                'criteria': criteria,
                'processingTime': round(processing_time, 2),
                'source': 'enhanced_rapidapi_search'
            }
        }
        
        logger.info(f"Search completed successfully: {len(transformed_properties)} properties in {processing_time:.2f}s")
        return jsonify(response)
        
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"Search request failed: {e}")
        
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'data': {
                'properties': [],
                'total': 0,
                'query': query if 'query' in locals() else '',
                'processingTime': round(processing_time, 2)
            }
        }), 500

@app.route('/ai-search', methods=['POST'])
def ai_search():
    """AI-powered search endpoint using OpenRouter"""
    start_time = time.time()
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        query = data.get('query', '')
        clean_query = input_validator.sanitize_query(query)
        
        if not clean_query:
            return jsonify({
                'success': False,
                'error': 'Invalid or empty query'
            }), 400
        
        logger.info(f"Processing AI search request: '{clean_query}'")
        
        # Use OpenRouter service for AI processing
        ai_response = openrouter_service.process_search_query(clean_query)
        
        processing_time = time.time() - start_time
        
        response = {
            'success': True,
            'data': ai_response,
            'processingTime': round(processing_time, 2)
        }
        
        return jsonify(response)
        
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"AI search failed: {e}")
        
        return jsonify({
            'success': False,
            'error': 'AI search service unavailable',
            'processingTime': round(processing_time, 2)
        }), 500

@app.route('/locations', methods=['GET'])
def get_supported_locations():
    """Get list of supported locations"""
    locations = [
        # US Cities
        'San Francisco', 'New York', 'Los Angeles', 'Chicago', 'Miami', 'Seattle',
        'Boston', 'Washington', 'Las Vegas', 'Denver', 'Austin', 'Portland',
        'Atlanta', 'Phoenix', 'Philadelphia', 'San Diego', 'Dallas', 'Houston',
        'Orlando', 'Nashville',
        
        # International Cities
        'London', 'Paris', 'Tokyo', 'Sydney', 'Barcelona', 'Rome', 'Amsterdam',
        'Berlin', 'Madrid', 'Vienna', 'Prague', 'Budapest', 'Lisbon', 'Dublin',
        'Copenhagen', 'Stockholm', 'Oslo', 'Helsinki', 'Zurich', 'Geneva',
        'Brussels', 'Milan', 'Florence', 'Venice', 'Naples', 'Athens', 'Istanbul',
        'Moscow', 'Mumbai', 'Delhi', 'Singapore', 'Hong Kong', 'Seoul', 'Bangkok',
        'Mexico City', 'Sao Paulo', 'Rio de Janeiro', 'Buenos Aires'
    ]
    
    return jsonify({
        'success': True,
        'data': {
            'locations': sorted(locations),
            'total': len(locations)
        }
    })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Starting Enhanced AI Airbnb Search Server on port {port}")
    logger.info(f"Debug mode: {debug}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
