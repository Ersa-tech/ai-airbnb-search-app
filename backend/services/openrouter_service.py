import os
import json
import requests
import logging
import time
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class OpenRouterService:
    """Service for interacting with OpenRouter API for LLM processing"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        self.base_url = "https://openrouter.ai/api/v1"
        self.model = os.getenv('OPENROUTER_MODEL', 'anthropic/claude-3-haiku')
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": os.getenv('APP_URL', 'http://localhost:3000'),
            "X-Title": "AI Airbnb Search"
        }
    
    def is_available(self) -> bool:
        """Check if OpenRouter service is available"""
        return bool(self.api_key)
    
    def _make_request(self, messages: List[Dict], max_tokens: int = 1000) -> Optional[str]:
        """Make a request to OpenRouter API"""
        if not self.api_key:
            logger.warning("OpenRouter API key not configured")
            return None
        
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": 0.7
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data['choices'][0]['message']['content']
            else:
                logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"OpenRouter request failed: {str(e)}")
            return None
    
    def process_search_query(self, user_query: str) -> Optional[Dict]:
        """Process natural language query and extract search parameters"""
        
        system_prompt = """You are an AI assistant that extracts Airbnb search parameters from natural language queries.

Extract the following information and return ONLY a valid JSON object:
- location: string (city, state, neighborhood, or area - be specific)
- adults: number (default: 2, but calculate based on bedrooms if mentioned)
- children: number (default: 0)
- infants: number (default: 0)
- pets: number (default: 0)
- checkin: string (YYYY-MM-DD format, if mentioned)
- checkout: string (YYYY-MM-DD format, if mentioned)
- price_min: number (if mentioned)
- price_max: number (if mentioned)
- property_type: string (house, apartment, villa, mansion, estate, cabin, etc.)
- bedrooms: number (exact number if specified, even if 10+)
- bathrooms: number (if mentioned)
- guests: number (total capacity needed)
- amenities: array of strings (pool, hot tub, wifi, kitchen, etc.)
- special_requirements: array (large group, wedding, reunion, etc.)

IMPORTANT: For large properties (5+ bedrooms), estimate guest capacity as bedrooms × 2.
Handle specific numbers even beyond typical Airbnb limits (11 bedrooms = 22+ guests).

Examples:
Query: "Find a place in San Francisco for 4 people"
Response: {"location": "San Francisco", "adults": 4, "guests": 4}

Query: "11 bedroom house in Texas"
Response: {"location": "Texas", "property_type": "house", "bedrooms": 11, "guests": 22, "adults": 22}

Query: "luxury 8 bedroom villa in Napa Valley for 20 people with pool"
Response: {"location": "Napa Valley", "property_type": "villa", "bedrooms": 8, "guests": 20, "adults": 20, "amenities": ["pool"], "special_requirements": ["luxury"]}

Return ONLY the JSON object, no other text."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ]
        
        response = self._make_request(messages, max_tokens=500)
        
        if response:
            try:
                # Clean the response to extract JSON
                response = response.strip()
                if response.startswith('```json'):
                    response = response[7:-3]
                elif response.startswith('```'):
                    response = response[3:-3]
                
                search_params = json.loads(response)
                
                # Validate and set defaults
                search_params.setdefault('adults', 2)
                search_params.setdefault('children', 0)
                search_params.setdefault('infants', 0)
                search_params.setdefault('pets', 0)
                
                return search_params
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse OpenRouter response as JSON: {e}")
                logger.error(f"Response was: {response}")
                
                # Fallback: extract location manually
                return self._fallback_query_processing(user_query)
        
        return self._fallback_query_processing(user_query)
    
    def _fallback_query_processing(self, user_query: str) -> Dict:
        """Enhanced fallback method for query processing when LLM fails"""
        import re
        
        query_lower = user_query.lower()
        
        # Enhanced location detection with aliases and abbreviations
        location_map = {
            'sf': 'San Francisco',
            'nyc': 'New York',
            'la': 'Los Angeles',
            'vegas': 'Las Vegas',
            'francisco': 'San Francisco',
            'miami': 'Miami',
            'york': 'New York',
            'angeles': 'Los Angeles',
            'chicago': 'Chicago',
            'boston': 'Boston',
            'seattle': 'Seattle',
            'austin': 'Austin',
            'dallas': 'Dallas',
            'houston': 'Houston',
            'denver': 'Denver',
            'atlanta': 'Atlanta',
            'texas': 'Texas',
            'california': 'California',
            'florida': 'Florida',
            'colorado': 'Colorado',
            'napa': 'Napa Valley',
            'hamptons': 'The Hamptons',
            'aspen': 'Aspen',
            'tahoe': 'Lake Tahoe'
        }
        
        location = "San Francisco"  # Default
        for key, value in location_map.items():
            if key in query_lower:
                location = value
                break
        
        # Enhanced number extraction (including written numbers)
        number_words = {
            'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
            'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
            'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14, 'fifteen': 15,
            'sixteen': 16, 'seventeen': 17, 'eighteen': 18, 'nineteen': 19, 'twenty': 20
        }
        
        # Extract numbers (digits first, then words)
        numbers = re.findall(r'\d+', user_query)
        bedrooms = None
        guests = 2
        
        # Look for bedroom mentions
        bedroom_match = re.search(r'(\d+)\s*bedroom', query_lower)
        if bedroom_match:
            bedrooms = int(bedroom_match.group(1))
            guests = bedrooms * 2  # Estimate 2 guests per bedroom
        
        # Look for guest/people mentions
        people_match = re.search(r'(\d+)\s*(people|person|guest)', query_lower)
        if people_match:
            guests = int(people_match.group(1))
        
        # Check for written numbers
        for word, num in number_words.items():
            if f"{word} bedroom" in query_lower:
                bedrooms = num
                guests = max(guests, num * 2)
            elif f"{word} people" in query_lower or f"{word} person" in query_lower:
                guests = num
        
        # If we found any numbers but no specific context, use the first one
        if numbers and not bedrooms and not people_match:
            first_num = int(numbers[0])
            if first_num > 20:  # Likely a price, not guests
                pass
            else:
                guests = first_num
        
        # Property type detection
        property_types = {
            'house': 'house',
            'villa': 'villa',
            'mansion': 'mansion',
            'estate': 'estate',
            'cabin': 'cabin',
            'cottage': 'cottage',
            'apartment': 'apartment',
            'condo': 'apartment',
            'loft': 'loft'
        }
        
        property_type = None
        for key, value in property_types.items():
            if key in query_lower:
                property_type = value
                break
        
        # Amenity detection
        amenities = []
        amenity_keywords = {
            'pool': 'pool',
            'hot tub': 'hot tub',
            'jacuzzi': 'hot tub',
            'wifi': 'wifi',
            'kitchen': 'kitchen',
            'parking': 'parking',
            'beach': 'beachfront',
            'ocean': 'ocean view',
            'mountain': 'mountain view'
        }
        
        for keyword, amenity in amenity_keywords.items():
            if keyword in query_lower:
                amenities.append(amenity)
        
        # Build result
        result = {
            "location": location,
            "adults": guests,
            "children": 0,
            "infants": 0,
            "pets": 0,
            "guests": guests
        }
        
        if bedrooms:
            result["bedrooms"] = bedrooms
        if property_type:
            result["property_type"] = property_type
        if amenities:
            result["amenities"] = amenities
        
        # Special requirements detection
        special_requirements = []
        if any(word in query_lower for word in ['luxury', 'luxurious', 'upscale']):
            special_requirements.append('luxury')
        if any(word in query_lower for word in ['wedding', 'reunion', 'group', 'party']):
            special_requirements.append('large group')
        if special_requirements:
            result["special_requirements"] = special_requirements
        
        return result
    
    def enhance_search_results(self, user_query: str, properties_data: Dict) -> Dict:
        """Enhance search results with LLM insights"""
        
        if not self.api_key:
            # Return original data if no API key
            return properties_data
        
        system_prompt = """You are an AI assistant that enhances Airbnb search results with helpful insights.

Given a user's search query and property results, add a brief, helpful summary and highlight why these properties match the user's needs.

Return the original JSON structure with these additions:
- Add "ai_summary" field with 1-2 sentences about the search results
- Add "match_reasons" array with 2-3 reasons why these properties fit the query
- Keep all original property data intact

Be concise and focus on value to the user."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Query: {user_query}\n\nResults: {json.dumps(properties_data, indent=2)}"}
        ]
        
        response = self._make_request(messages, max_tokens=800)
        
        if response:
            try:
                # Try to parse enhanced results
                enhanced = json.loads(response)
                return enhanced
            except json.JSONDecodeError:
                # If parsing fails, add simple enhancements
                pass
        
        # Fallback enhancement
        properties_data['ai_summary'] = f"Found {len(properties_data.get('properties', []))} properties matching your search criteria."
        properties_data['match_reasons'] = [
            "Properties match your location preference",
            "Accommodates your group size",
            "Variety of price points available"
        ]
        
        return properties_data
    
    def enhance_property_details(self, property_data: Dict) -> Dict:
        """Enhance individual property details with LLM insights"""
        
        if not self.api_key:
            return property_data
        
        system_prompt = """You are an AI assistant that enhances Airbnb property details with helpful insights.

Add these fields to the property data:
- "ai_highlights": array of 3-4 key selling points
- "best_for": string describing who this property is ideal for
- "local_tips": array of 2-3 local area insights

Keep all original data intact and be concise."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Property: {json.dumps(property_data, indent=2)}"}
        ]
        
        response = self._make_request(messages, max_tokens=600)
        
        if response:
            try:
                enhanced = json.loads(response)
                return enhanced
            except json.JSONDecodeError:
                pass
        
        # Fallback enhancement
        property_data['ai_highlights'] = [
            "Great location",
            "Well-equipped amenities",
            "Excellent value"
        ]
        property_data['best_for'] = "Travelers seeking comfort and convenience"
        property_data['local_tips'] = [
            "Explore nearby attractions",
            "Try local restaurants"
        ]
        
        return property_data
    
    def generate_search_suggestions(self, partial_query: str) -> List[str]:
        """Generate search suggestions based on partial input"""
        
        if not self.api_key or len(partial_query) < 2:
            return [
                "Find a place in San Francisco",
                "Beach house in Miami",
                "Apartment in New York",
                "Villa with pool",
                "Pet-friendly accommodation"
            ]
        
        system_prompt = """Generate 5 helpful Airbnb search suggestions based on the partial query.

Return ONLY a JSON array of strings. Each suggestion should be a complete, natural search query.

Examples:
Input: "beach"
Output: ["Beach house in Miami", "Beachfront apartment in California", "Beach villa with ocean view", "Beach cottage for families", "Luxury beach resort"]

Input: "san"
Output: ["San Francisco downtown apartment", "San Diego beach house", "San Antonio family home", "Santa Monica beachfront", "San Jose business travel"]"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": partial_query}
        ]
        
        response = self._make_request(messages, max_tokens=300)
        
        if response:
            try:
                suggestions = json.loads(response)
                if isinstance(suggestions, list):
                    return suggestions[:5]
            except json.JSONDecodeError:
                pass
        
        # Fallback suggestions
        return [
            f"{partial_query} in San Francisco",
            f"{partial_query} in Miami",
            f"{partial_query} in New York",
            f"{partial_query} with pool",
            f"{partial_query} for families"
        ]
