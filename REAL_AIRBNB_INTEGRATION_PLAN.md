# 🎯 REAL AIRBNB INTEGRATION PLAN
## Replacing Mock Data with OpenBnB MCP Server

**Date**: July 23, 2025  
**Status**: 🟡 READY TO IMPLEMENT  
**Priority**: P0 - Critical fix for mock data issue

---

## 🔍 **SOLUTION OVERVIEW**

We've identified the **OpenBnB MCP Airbnb Server** as the perfect solution to replace our mock data implementation. This is a real, production-ready MCP server that provides actual Airbnb data without requiring API keys.

### **Key Benefits**
- ✅ **Real Airbnb Data**: Actual property listings, not mock data
- ✅ **No API Keys Required**: Works without external API authentication
- ✅ **Production Ready**: 233 stars, actively maintained
- ✅ **MCP Protocol**: True Model Context Protocol implementation
- ✅ **Comprehensive Features**: Search, filtering, detailed property info

---

## 📋 **IMPLEMENTATION STRATEGY**

### **Phase 1: Replace Mock MCP Server** (1 hour)

#### **1.1 Remove Current Mock Implementation**
```bash
# Remove our fake MCP server
rm -rf ai-airbnb-search/mcp-server/http-wrapper.js
rm -rf ai-airbnb-search/mcp-server/package.json
rm -rf ai-airbnb-search/mcp-server/Dockerfile
```

#### **1.2 Install Real OpenBnB MCP Server**
```bash
cd ai-airbnb-search/mcp-server
npm init -y
npm install @openbnb/mcp-server-airbnb
```

#### **1.3 Create MCP Server Wrapper**
Create a new `mcp-server.js` that uses the real OpenBnB server:
```javascript
#!/usr/bin/env node
const { spawn } = require('child_process');

// Start the real OpenBnB MCP server
const mcpServer = spawn('npx', ['-y', '@openbnb/mcp-server-airbnb', '--ignore-robots-txt'], {
  stdio: 'inherit'
});

mcpServer.on('error', (error) => {
  console.error('MCP Server error:', error);
  process.exit(1);
});

mcpServer.on('close', (code) => {
  console.log(`MCP Server exited with code ${code}`);
  process.exit(code);
});
```

### **Phase 2: Update Backend Integration** (30 minutes)

#### **2.1 Modify Backend to Use Real MCP Tools**
Update `backend/app.py` to use the real MCP server tools:
```python
# Replace mock data calls with real MCP tool calls
@app.route('/api/v1/search', methods=['POST'])
def search_properties():
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        # Use real MCP server tools
        search_params = parse_search_query(query)
        
        # Call real airbnb_search tool
        properties = call_mcp_tool('airbnb_search', search_params)
        
        return jsonify({
            'success': True,
            'properties': properties[:5],  # Return exactly 5 properties
            'source': 'real_airbnb_mcp'
        })
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
```

#### **2.2 Add MCP Tool Integration**
```python
import subprocess
import json

def call_mcp_tool(tool_name, params):
    """Call real MCP server tool"""
    try:
        # Prepare MCP tool call
        mcp_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": params
            }
        }
        
        # Call MCP server
        result = subprocess.run([
            'npx', '-y', '@openbnb/mcp-server-airbnb'
        ], input=json.dumps(mcp_request), text=True, capture_output=True)
        
        if result.returncode == 0:
            response = json.loads(result.stdout)
            return response.get('result', [])
        else:
            raise Exception(f"MCP call failed: {result.stderr}")
            
    except Exception as e:
        logger.error(f"MCP tool call error: {str(e)}")
        raise
```

### **Phase 3: Update Deployment Configuration** (15 minutes)

#### **3.1 Update render.yaml**
```yaml
services:
  - type: web
    name: mcp-server
    env: node
    buildCommand: npm install @openbnb/mcp-server-airbnb
    startCommand: npx -y @openbnb/mcp-server-airbnb --ignore-robots-txt
    envVars:
      - key: NODE_ENV
        value: production
      - key: PORT
        value: 8080
```

#### **3.2 Update Backend Dependencies**
```txt
# Add to requirements.txt
requests>=2.31.0
```

### **Phase 4: Testing & Validation** (30 minutes)

#### **4.1 Local Testing**
```bash
# Test MCP server directly
npx -y @openbnb/mcp-server-airbnb --ignore-robots-txt

# Test backend integration
cd backend
python app.py

# Test search endpoint
curl -X POST http://localhost:5000/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{"query":"Find a place in San Francisco"}'
```

#### **4.2 Validation Checklist**
- [ ] Real Airbnb properties returned (not mock data)
- [ ] Properties have real URLs (airbnb.com links)
- [ ] Images are actual property photos
- [ ] Prices reflect real Airbnb pricing
- [ ] Exactly 5 properties displayed in carousel
- [ ] All property details are authentic

---

## 🔧 **DETAILED IMPLEMENTATION STEPS**

### **Step 1: Replace MCP Server Implementation**

```bash
cd ai-airbnb-search/mcp-server

# Remove mock files
rm http-wrapper.js package.json Dockerfile

# Create new package.json
cat > package.json << 'EOF'
{
  "name": "real-airbnb-mcp-server",
  "version": "1.0.0",
  "description": "Real Airbnb MCP Server Integration",
  "main": "mcp-server.js",
  "scripts": {
    "start": "node mcp-server.js",
    "dev": "npx -y @openbnb/mcp-server-airbnb --ignore-robots-txt"
  },
  "dependencies": {
    "@openbnb/mcp-server-airbnb": "^0.1.3"
  }
}
EOF

# Create MCP server wrapper
cat > mcp-server.js << 'EOF'
#!/usr/bin/env node
const { spawn } = require('child_process');
const path = require('path');

console.log('Starting Real Airbnb MCP Server...');

// Start the real OpenBnB MCP server
const mcpServer = spawn('npx', ['-y', '@openbnb/mcp-server-airbnb', '--ignore-robots-txt'], {
  stdio: 'inherit',
  env: { ...process.env, NODE_ENV: 'production' }
});

mcpServer.on('error', (error) => {
  console.error('MCP Server error:', error);
  process.exit(1);
});

mcpServer.on('close', (code) => {
  console.log(`MCP Server exited with code ${code}`);
  process.exit(code);
});

// Handle graceful shutdown
process.on('SIGTERM', () => {
  console.log('Received SIGTERM, shutting down gracefully');
  mcpServer.kill('SIGTERM');
});

process.on('SIGINT', () => {
  console.log('Received SIGINT, shutting down gracefully');
  mcpServer.kill('SIGINT');
});
EOF

chmod +x mcp-server.js

# Install dependencies
npm install
```

### **Step 2: Update Backend Integration**

```python
# Update backend/app.py
import subprocess
import json
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins="*")

logger = logging.getLogger(__name__)

def call_airbnb_search(location, checkin=None, checkout=None, adults=1):
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
            
        # Call MCP server tool
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
            response = json.loads(result.stdout)
            return response.get('result', {}).get('listings', [])
        else:
            logger.error(f"MCP call failed: {result.stderr}")
            return []
            
    except Exception as e:
        logger.error(f"Airbnb search error: {str(e)}")
        return []

@app.route('/api/v1/search', methods=['POST'])
def search_properties():
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        # Parse location from query (simple implementation)
        location = extract_location_from_query(query)
        
        # Call real Airbnb search
        properties = call_airbnb_search(location)
        
        # Transform to our expected format and limit to 5
        formatted_properties = transform_airbnb_properties(properties[:5])
        
        return jsonify({
            'success': True,
            'properties': formatted_properties,
            'source': 'real_airbnb_mcp',
            'total': len(formatted_properties)
        })
        
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

def extract_location_from_query(query):
    """Extract location from natural language query"""
    # Simple implementation - can be enhanced with NLP
    query_lower = query.lower()
    
    # Common location patterns
    if 'san francisco' in query_lower or 'sf' in query_lower:
        return 'San Francisco, CA'
    elif 'new york' in query_lower or 'nyc' in query_lower:
        return 'New York, NY'
    elif 'los angeles' in query_lower or 'la' in query_lower:
        return 'Los Angeles, CA'
    else:
        # Extract location after common phrases
        import re
        patterns = [
            r'in\s+([^,]+(?:,\s*[^,]+)?)',
            r'near\s+([^,]+(?:,\s*[^,]+)?)',
            r'around\s+([^,]+(?:,\s*[^,]+)?)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query_lower)
            if match:
                return match.group(1).title()
        
        return 'San Francisco, CA'  # Default fallback

def transform_airbnb_properties(airbnb_properties):
    """Transform Airbnb MCP response to our expected format"""
    transformed = []
    
    for prop in airbnb_properties:
        transformed_prop = {
            'id': prop.get('id', ''),
            'title': prop.get('name', ''),
            'price': prop.get('pricing', {}).get('rate', {}).get('amount', 0),
            'currency': prop.get('pricing', {}).get('rate', {}).get('currency', 'USD'),
            'rating': prop.get('avgRating', 0),
            'reviewCount': prop.get('reviewsCount', 0),
            'imageUrl': prop.get('images', [{}])[0].get('url', ''),
            'location': prop.get('contextualPictures', [{}])[0].get('caption', ''),
            'url': prop.get('url', ''),
            'type': prop.get('roomType', ''),
            'guests': prop.get('previewAmenities', []),
            'source': 'real_airbnb'
        }
        transformed.append(transformed_prop)
    
    return transformed

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

### **Step 3: Update Deployment**

```yaml
# Update render.yaml
services:
  # MCP Server - Real Airbnb Integration
  - type: web
    name: ai-airbnb-mcp-server
    env: node
    region: oregon
    plan: starter
    buildCommand: npm install
    startCommand: npm start
    envVars:
      - key: NODE_ENV
        value: production
      - key: PORT
        value: 8080
    healthCheckPath: /health

  # Backend - Updated for real MCP integration
  - type: web
    name: ai-airbnb-backend
    env: python
    region: oregon
    plan: starter
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn -c gunicorn.conf.py app:app
    envVars:
      - key: FLASK_ENV
        value: production
      - key: MCP_SERVER_URL
        value: https://ai-airbnb-mcp-server.onrender.com
      - key: OPENROUTER_API_KEY
        fromService:
          type: web
          name: ai-airbnb-backend
          envVarKey: OPENROUTER_API_KEY
    healthCheckPath: /health

  # Frontend - No changes needed
  - type: static
    name: ai-airbnb-frontend
    buildCommand: npm run build
    staticPublishPath: ./build
    envVars:
      - key: REACT_APP_API_URL
        value: https://ai-airbnb-backend.onrender.com
```

---

## 🎯 **SUCCESS CRITERIA**

### **Must Have**
- [ ] Real Airbnb properties displayed (verified by checking URLs)
- [ ] Properties link to actual Airbnb listings
- [ ] Images are real property photos (not stock images)
- [ ] Prices reflect actual Airbnb pricing
- [ ] Exactly 5 properties in carousel
- [ ] Search functionality works with natural language

### **Should Have**
- [ ] Property details are comprehensive and accurate
- [ ] Search results are relevant to query
- [ ] Error handling for failed searches
- [ ] Loading states during search

### **Could Have**
- [ ] Advanced filtering options
- [ ] Pagination for more results
- [ ] Detailed property information modal

---

## 🚀 **DEPLOYMENT TIMELINE**

### **Immediate (Next 2 hours)**
1. **Replace MCP Server** (1 hour)
   - Remove mock implementation
   - Install OpenBnB MCP server
   - Test locally

2. **Update Backend** (30 minutes)
   - Integrate real MCP tools
   - Update API endpoints
   - Test integration

3. **Deploy & Test** (30 minutes)
   - Deploy to Render.com
   - Verify real data flow
   - Test end-to-end functionality

### **Expected Results**
- ✅ Real Airbnb properties displayed
- ✅ Authentic booking links
- ✅ Actual property photos and pricing
- ✅ Fully functional search with real data

---

## 📊 **VERIFICATION METHODS**

### **How to Verify Real Data**
1. **Check URLs**: Should be `https://www.airbnb.com/rooms/[real-id]`
2. **Test Booking Links**: Should lead to actual Airbnb booking pages
3. **Verify Images**: Should be unique property photos, not stock images
4. **Cross-Reference Prices**: Should match current Airbnb pricing
5. **Test Multiple Locations**: Should return different properties for different cities

### **Red Flags for Mock Data**
- ❌ URLs like `https://airbnb.com/rooms/enhanced_123`
- ❌ Generic property names
- ❌ Stock photos from Unsplash
- ❌ Round number pricing ($100, $200, $300)
- ❌ Identical properties across different searches

---

This plan will completely eliminate the mock data issue and provide a real, production-ready Airbnb search experience using the OpenBnB MCP server.
