import os
import logging
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import requests
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

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Check MCP server health
        mcp_response = requests.get(f"{MCP_SERVER_URL}/health", timeout=5)
        mcp_healthy = mcp_response.status_code == 200
        
        return jsonify({
            'status': 'healthy',
            'timestamp': '2025-07-24T01:16:00.000Z',
            'services': {
                'flask_backend': True,
                'mcp_server': mcp_healthy,
                'openrouter': openrouter_service.is_available()
            }
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@app.route('/api/v1/search', methods=['POST'])
def search_properties():
    """Main search endpoint that processes natural language queries"""
    start_time = time.time() * 1000  # Start timing
    
    try:
        # Get request data
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({'error': 'Query is required'}), 400
        
        user_query = data['query']
        logger.info(f"Processing search query: {user_query}")
        
        # Step 1: Process query with OpenRouter LLM
        search_params = openrouter_service.process_search_query(user_query)
        if not search_params:
            return jsonify({'error': 'Failed to process search query'}), 500
        
        logger.info(f"Extracted search parameters: {search_params}")
        
        # Step 2: Search properties using MCP server
        mcp_response = requests.post(
            f"{MCP_SERVER_URL}/search",
            json=search_params,
            timeout=10
        )
        
        if mcp_response.status_code != 200:
            logger.error(f"MCP server error: {mcp_response.status_code}")
            return jsonify({'error': 'Property search failed'}), 500
        
        properties_data = mcp_response.json()
        
        # Step 3: Enhance results with LLM insights
        enhanced_results = openrouter_service.enhance_search_results(
            user_query, 
            properties_data
        )
        
        # Ensure exactly 5 properties for carousel
        properties = enhanced_results.get('properties', properties_data.get('properties', []))[:5]
        
        # Calculate actual processing time
        actual_processing_time = (time.time() * 1000 - start_time) / 1000
        
        # Format response to match frontend expectations
        response = {
            'success': True,
            'data': {
                'properties': properties,
                'total': len(properties),
                'query': user_query,
                'processingTime': round(actual_processing_time, 2)
            },
            'message': enhanced_results.get('ai_summary', f'Found {len(properties)} properties matching your search.')
        }
        
        logger.info(f"Returning {len(properties)} properties")
        
        return jsonify(response), 200
        
    except requests.exceptions.Timeout:
        logger.error("Request timeout")
        return jsonify({'error': 'Request timeout'}), 504
    except requests.exceptions.ConnectionError:
        logger.error("Connection error to MCP server")
        return jsonify({'error': 'Service unavailable'}), 503
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/v1/property/<property_id>', methods=['GET'])
def get_property_details(property_id):
    """Get detailed information about a specific property"""
    try:
        # Get property details from MCP server
        mcp_response = requests.get(
            f"{MCP_SERVER_URL}/details/{property_id}",
            timeout=10
        )
        
        if mcp_response.status_code == 404:
            return jsonify({'error': 'Property not found'}), 404
        elif mcp_response.status_code != 200:
            return jsonify({'error': 'Failed to fetch property details'}), 500
        
        property_data = mcp_response.json()
        
        # Enhance with LLM insights
        enhanced_property = openrouter_service.enhance_property_details(property_data)
        
        return jsonify(enhanced_property), 200
        
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Request timeout'}), 504
    except requests.exceptions.ConnectionError:
        return jsonify({'error': 'Service unavailable'}), 503
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
            'timestamp': '2025-07-24T01:16:00.000Z'
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
    logger.info(f"MCP Server URL: {MCP_SERVER_URL}")
    logger.info(f"Debug mode: {debug}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
