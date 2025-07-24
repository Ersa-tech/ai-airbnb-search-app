import os
import json
import logging
import requests
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
- location: string (city, neighborhood, or area)
- adults: number (default: 2)
- children: number (default: 0)
- infants: number (default: 0)
- pets: number (default: 0)
- checkin: string (YYYY-MM-DD format, if mentioned)
- checkout: string (YYYY-MM-DD format, if mentioned)
- price_min: number (if mentioned)
- price_max: number (if mentioned)
- property_type: string (if mentioned: "apartment", "house", "villa", etc.)

Examples:
Query: "Find a place in San Francisco for 4 people"
Response: {"location": "San Francisco", "adults": 4, "children": 0, "infants": 0, "pets": 0}

Query: "Looking for a beach house in Miami under $300"
Response: {"location": "Miami", "adults": 2, "children": 0, "infants": 0, "pets": 0, "price_max": 300, "property_type": "house"}

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
        """Fallback method for query processing when LLM fails"""
        # Simple keyword extraction
        query_lower = user_query.lower()
        
        # Try to extract location (common patterns)
        location = "San Francisco"  # Default
        for word in user_query.split():
            if word.lower() in ['francisco', 'miami', 'york', 'angeles', 'chicago', 'boston', 'seattle']:
                if 'francisco' in word.lower():
                    location = "San Francisco"
                elif 'miami' in word.lower():
                    location = "Miami"
                elif 'york' in word.lower():
                    location = "New York"
                elif 'angeles' in word.lower():
                    location = "Los Angeles"
                else:
                    location = word.title()
                break
        
        # Extract number of people
        adults = 2
        import re
        numbers = re.findall(r'\d+', user_query)
        if numbers:
            adults = min(int(numbers[0]), 16)  # Cap at 16 people
        
        return {
            "location": location,
            "adults": adults,
            "children": 0,
            "infants": 0,
            "pets": 0
        }
    
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
