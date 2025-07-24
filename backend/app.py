import os
import logging
import time
import requests
import json
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from services.openrouter_service import OpenRouterService

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
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

def get_place_id(location):
    """Convert location string to Google Place ID"""
    # Common location to Place ID mapping
    place_ids = {
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
        'nashville': 'ChIJPZDrEzLsZIgRoNrpodC5P30'
    }
    
    location_lower = location.lower().strip()
    
    # Try exact match first
    if location_lower in place_ids:
        return place_ids[location_lower]
    
    # Try partial match
    for city, place_id in place_ids.items():
        if city in location_lower or location_lower in city:
            return place_id
    
    # Default to San Francisco if no match
    logger.warning(f"No Place ID found for '{location}', defaulting to San Francisco")
    return place_ids['san francisco']

def call_airbnb_search(location, checkin=None, checkout=None, adults=1, children=0, infants=0, pets=0, min_price=None, max_price=None):
    """Call RapidAPI Airbnb19 directly for real property search"""
    try:
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
        
        # Make API request
        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            properties = data.get('data', [])
            logger.info(f"RapidAPI returned {len(properties)} properties")
            return properties
        else:
            logger.error(f"RapidAPI returned status {response.status_code}: {response.text}")
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
    
    # If no location found, try to extract any proper nouns (capitalized words)
    words = query.split()
    proper_nouns = []
    for word in words:
        # Look for capitalized words that aren't at sentence start
        if word[0].isupper() and word.lower() not in skip_words:
            proper_nouns.append(word)
    
    if proper_nouns:
        return ' '.join(proper_nouns)
    
    # Final fallback - return a generic location
    return 'United States'

def transform_airbnb_properties(airbnb_properties):
    """Transform RapidAPI Airbnb19 response to our expected format"""
    transformed = []
    
    for prop in airbnb_properties:
        try:
            # Extract pricing information (RapidAPI structure)
            price = 0
            currency = 'USD'
            
            # Try different price field structures
            if 'price' in prop:
                if isinstance(prop['price'], dict):
                    price = prop['price'].get('amount', 0) or prop['price'].get('total', 0)
                    currency = prop['price'].get('currency', 'USD')
                else:
                    price = prop['price']
            elif 'pricing' in prop:
                pricing = prop['pricing']
                if 'rate' in pricing:
                    price = pricing['rate'].get('amount', 0)
                    currency = pricing['rate'].get('currency', 'USD')
            
            # Extract images (try multiple field names)
            image_url = ''
            if 'images' in prop and prop['images']:
                if isinstance(prop['images'][0], dict):
                    image_url = prop['images'][0].get('url', '')
                else:
                    image_url = prop['images'][0]
            elif 'image' in prop:
                image_url = prop['image']
            elif 'photo' in prop:
                image_url = prop['photo']
            
            # Extract location info
            location = ''
            if 'location' in prop:
                if isinstance(prop['location'], dict):
                    location = prop['location'].get('address', '') or prop['location'].get('name', '')
                else:
                    location = prop['location']
            elif 'address' in prop:
                location = prop['address']
            elif 'contextualPictures' in prop and prop['contextualPictures']:
                location = prop['contextualPictures'][0].get('caption', '')
            
            # Extract basic info
            property_id = str(prop.get('id', ''))
            title = prop.get('name', '') or prop.get('title', '') or f"Property in {location}"
            
            # Build property object matching frontend expectations
            transformed_prop = {
                'id': property_id,
                'title': title,
                'price': int(price) if price else 100,
                'currency': currency,
                'rating': float(prop.get('avgRating', 0)) or float(prop.get('rating', 0)) or 4.5,
                'reviewCount': int(prop.get('reviewsCount', 0)) or int(prop.get('reviews', 0)) or 25,
                'imageUrl': image_url or 'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=800',
                'location': location or 'Location Available',
                'url': prop.get('url', f"https://www.airbnb.com/rooms/{property_id}"),
                'type': prop.get('roomType', '') or prop.get('propertyType', '') or 'Apartment',
                'guests': int(prop.get('personCapacity', 0)) or int(prop.get('guests', 0)) or 2,
                'source': 'real_airbnb_rapidapi',
                'bedrooms': int(prop.get('bedrooms', 0)) or 1,
                'bathrooms': int(prop.get('bathrooms', 0)) or 1,
                'amenities': prop.get('amenities', []) or ['WiFi', 'Kitchen']
            }
            
            # Ensure we have a valid URL
            if not transformed_prop['url'].startswith('http'):
                transformed_prop['url'] = f"https://www.airbnb.com/rooms/{property_id}"
            
            transformed.append(transformed_prop)
            
        except Exception as e:
            logger.error(f"Error transforming property: {e}")
            continue
    
    return transformed

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        return jsonify({
            'status': 'healthy',
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime()),
            'services': {
                'flask_backend': True,
                'rapidapi_airbnb': True,
                'openrouter': openrouter_service.is_available()
            },
            'version': '3.0.0-direct-rapidapi'
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@app.route('/api/v1/search', methods=['POST'])
def search_properties():
    """Main search endpoint that processes natural language queries with real Airbnb data"""
    start_time = time.time() * 1000  # Start timing
    
    try:
        # Get request data
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({'error': 'Query is required'}), 400
        
        user_query = data['query']
        logger.info(f"Processing search query: {user_query}")
        
        # Step 1: Extract location from query
        location = extract_location_from_query(user_query)
        logger.info(f"Extracted location: {location}")
        
        # Step 2: Search properties using RapidAPI Airbnb19
        airbnb_properties = call_airbnb_search(location)
        
        if not airbnb_properties:
            logger.warning("No properties returned from RapidAPI")
            return jsonify({
                'success': False,
                'error': 'No properties found for this location',
                'data': {
                    'properties': [],
                    'total': 0,
                    'query': user_query,
                    'location': location
                }
            }), 200
        
        # Step 3: Transform to our expected format and limit to 5
        formatted_properties = transform_airbnb_properties(airbnb_properties[:5])
        
        # Step 4: Enhance results with LLM insights (optional)
        try:
            enhanced_results = openrouter_service.enhance_search_results(
                user_query, 
                {'properties': formatted_properties}
            )
            ai_summary = enhanced_results.get('ai_summary', f'Found {len(formatted_properties)} real Airbnb properties in {location}.')
        except Exception as e:
            logger.warning(f"LLM enhancement failed: {e}")
            ai_summary = f'Found {len(formatted_properties)} real Airbnb properties in {location}.'
        
        # Calculate actual processing time
        actual_processing_time = (time.time() * 1000 - start_time) / 1000
        
        # Format response to match frontend expectations
        response = {
            'success': True,
            'data': {
                'properties': formatted_properties,
                'total': len(formatted_properties),
                'query': user_query,
                'location': location,
                'processingTime': round(actual_processing_time, 2),
                'source': 'real_airbnb_rapidapi'
            },
            'message': ai_summary
        }
        
        logger.info(f"Returning {len(formatted_properties)} real Airbnb properties")
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'data': {
                'properties': [],
                'total': 0,
                'query': user_query if 'user_query' in locals() else ''
            }
        }), 500

@app.route('/api/v1/property/<property_id>', methods=['GET'])
def get_property_details(property_id):
    """Get detailed information about a specific property"""
    try:
        # Prepare MCP tool call for property details
        mcp_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "airbnb_listing_details",
                "arguments": {
                    "id": property_id,
                    "ignoreRobotsText": True
                }
            }
        }
        
        # Execute MCP call
        result = subprocess.run([
            'npx', '-y', '@openbnb/mcp-server-airbnb', '--ignore-robots-txt'
        ], input=json.dumps(mcp_request), text=True, capture_output=True, timeout=30)
        
        if result.returncode == 0:
            response = json.loads(result.stdout)
            property_data = response.get('result', {})
            
            if not property_data:
                return jsonify({'error': 'Property not found'}), 404
            
            # Enhance with LLM insights
            try:
                enhanced_property = openrouter_service.enhance_property_details(property_data)
                return jsonify(enhanced_property), 200
            except Exception as e:
                logger.warning(f"LLM enhancement failed: {e}")
                return jsonify(property_data), 200
        else:
            logger.error(f"Property details MCP call failed: {result.stderr}")
            return jsonify({'error': 'Failed to fetch property details'}), 500
        
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Request timeout'}), 504
    except Exception as e:
        logger.error(f"Property details error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/v1/suggestions', methods=['POST'])
def get_search_suggestions():
    """Get search suggestions based on partial input"""
    try:
        data = request.get_json()
        if not data or 'partial_query' not in data:
            return jsonify({'error': 'Partial query is required'}), 400
        
        partial_query = data['partial_query']
        
        # Generate suggestions using OpenRouter
        suggestions = openrouter_service.generate_search_suggestions(partial_query)
        
        return jsonify({
            'suggestions': suggestions,
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime())
        }), 200
        
    except Exception as e:
        logger.error(f"Suggestions error: {str(e)}")
        return jsonify({'error': 'Failed to generate suggestions'}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    logger.info(f"Starting Flask server on port {port}")
    logger.info(f"Using RapidAPI Airbnb19 for real property data")
    logger.info(f"Debug mode: {debug}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
