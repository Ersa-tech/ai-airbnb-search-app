import os
import logging
import time
import subprocess
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

# Configuration
MCP_SERVER_URL = os.getenv('MCP_SERVER_URL', 'http://localhost:8080')

def call_airbnb_search(location, checkin=None, checkout=None, adults=1, children=0, infants=0, pets=0, min_price=None, max_price=None):
    """Call real Airbnb MCP server search tool"""
    try:
        # Prepare search parameters
        search_params = {
            "location": location,
            "adults": adults,
            "ignoreRobotsText": True  # For testing purposes
        }
        
        if checkin:
            search_params["checkin"] = checkin
        if checkout:
            search_params["checkout"] = checkout
        if children > 0:
            search_params["children"] = children
        if infants > 0:
            search_params["infants"] = infants
        if pets > 0:
            search_params["pets"] = pets
        if min_price:
            search_params["minPrice"] = min_price
        if max_price:
            search_params["maxPrice"] = max_price
            
        logger.info(f"Calling Airbnb MCP with params: {search_params}")
        
        # Prepare MCP tool call
        mcp_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "airbnb_search",
                "arguments": search_params
            }
        }
        
        # Execute MCP call
        result = subprocess.run([
            'npx', '-y', '@openbnb/mcp-server-airbnb', '--ignore-robots-txt'
        ], input=json.dumps(mcp_request), text=True, capture_output=True, timeout=30)
        
        if result.returncode == 0:
            try:
                response = json.loads(result.stdout)
                listings = response.get('result', {}).get('listings', [])
                logger.info(f"MCP returned {len(listings)} listings")
                return listings
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse MCP response: {e}")
                logger.error(f"Raw output: {result.stdout}")
                return []
        else:
            logger.error(f"MCP call failed with code {result.returncode}")
            logger.error(f"Error output: {result.stderr}")
            return []
            
    except subprocess.TimeoutExpired:
        logger.error("MCP call timed out")
        return []
    except Exception as e:
        logger.error(f"Airbnb search error: {str(e)}")
        return []

def extract_location_from_query(query):
    """Extract location from natural language query"""
    query_lower = query.lower()
    
    # Common location patterns
    if 'san francisco' in query_lower or 'sf' in query_lower:
        return 'San Francisco, CA'
    elif 'new york' in query_lower or 'nyc' in query_lower:
        return 'New York, NY'
    elif 'los angeles' in query_lower or 'la' in query_lower:
        return 'Los Angeles, CA'
    elif 'chicago' in query_lower:
        return 'Chicago, IL'
    elif 'miami' in query_lower:
        return 'Miami, FL'
    elif 'seattle' in query_lower:
        return 'Seattle, WA'
    elif 'boston' in query_lower:
        return 'Boston, MA'
    elif 'austin' in query_lower:
        return 'Austin, TX'
    elif 'denver' in query_lower:
        return 'Denver, CO'
    elif 'portland' in query_lower:
        return 'Portland, OR'
    else:
        # Extract location after common phrases
        patterns = [
            r'in\s+([^,]+(?:,\s*[^,]+)?)',
            r'near\s+([^,]+(?:,\s*[^,]+)?)',
            r'around\s+([^,]+(?:,\s*[^,]+)?)',
            r'at\s+([^,]+(?:,\s*[^,]+)?)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query_lower)
            if match:
                location = match.group(1).strip()
                # Capitalize properly
                return ' '.join(word.capitalize() for word in location.split())
        
        return 'San Francisco, CA'  # Default fallback

def transform_airbnb_properties(airbnb_properties):
    """Transform Airbnb MCP response to our expected format"""
    transformed = []
    
    for prop in airbnb_properties:
        try:
            # Extract pricing information
            pricing = prop.get('pricing', {})
            rate = pricing.get('rate', {})
            price = rate.get('amount', 0)
            currency = rate.get('currency', 'USD')
            
            # Extract images
            images = prop.get('images', [])
            image_url = images[0].get('url', '') if images else ''
            
            # Extract location info
            contextual_pictures = prop.get('contextualPictures', [])
            location_caption = contextual_pictures[0].get('caption', '') if contextual_pictures else ''
            
            # Build property object
            transformed_prop = {
                'id': prop.get('id', ''),
                'title': prop.get('name', ''),
                'price': price,
                'currency': currency,
                'rating': prop.get('avgRating', 0),
                'reviewCount': prop.get('reviewsCount', 0),
                'imageUrl': image_url,
                'location': location_caption or prop.get('location', ''),
                'url': prop.get('url', ''),
                'type': prop.get('roomType', ''),
                'guests': prop.get('previewAmenities', []),
                'source': 'real_airbnb_mcp',
                'bedrooms': prop.get('bedrooms', 0),
                'bathrooms': prop.get('bathrooms', 0),
                'amenities': prop.get('amenities', [])
            }
            
            # Ensure we have a valid URL
            if not transformed_prop['url'].startswith('http'):
                transformed_prop['url'] = f"https://www.airbnb.com/rooms/{transformed_prop['id']}"
            
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
                'real_mcp_server': True,
                'openrouter': openrouter_service.is_available()
            },
            'version': '2.0.0-real-airbnb'
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
        
        # Step 2: Search properties using real Airbnb MCP server
        airbnb_properties = call_airbnb_search(location)
        
        if not airbnb_properties:
            logger.warning("No properties returned from Airbnb MCP")
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
                'source': 'real_airbnb_mcp'
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
    logger.info(f"Using REAL Airbnb MCP Server (OpenBnB)")
    logger.info(f"Debug mode: {debug}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
