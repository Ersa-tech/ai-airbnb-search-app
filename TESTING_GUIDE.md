# 🧪 AI Airbnb Search - Testing Guide

## 🎯 **CURRENT STATUS**

**Date**: July 23, 2025
**MCP Server**: ✅ LIVE & HEALTHY
**Backend**: ✅ LIVE & HEALTHY  
**Frontend**: ⏳ REDEPLOYING (TailwindCSS fix applied)

## 🔑 **REQUIRED: OpenRouter API Key**

To test the full application functionality, you need an OpenRouter API key:

### **Get OpenRouter API Key**
1. Go to https://openrouter.ai/
2. Sign up for a free account
3. Navigate to "Keys" section
4. Create a new API key
5. Copy the key (starts with `sk-or-v1-...`)

### **Configure Backend Environment Variables**
In Render.com dashboard:
1. Go to `ai-airbnb-backend` service
2. Click "Environment" tab
3. Add these variables:
```
OPENROUTER_API_KEY=sk-or-v1-your-actual-key-here
MCP_SERVER_URL=https://ai-airbnb-mcp-server.onrender.com
FLASK_ENV=production
```
4. Click "Save Changes" (will trigger redeploy)

## 🧪 **TESTING SEQUENCE**

### **Phase 1: Service Health Checks**

```bash
# Test MCP Server
curl https://ai-airbnb-mcp-server.onrender.com/health

# Expected Response:
{"status":"healthy","timestamp":"2025-07-24T02:27:16.976Z","service":"ai-airbnb-mcp-server"}

# Test Backend
curl https://ai-airbnb-backend.onrender.com/health

# Expected Response:
{
  "services": {
    "flask_backend": true,
    "mcp_server": true,
    "openrouter": true
  },
  "status": "healthy",
  "timestamp": "2025-07-24T01:16:00.000Z"
}

# Test Frontend (once deployed)
curl -I https://ai-airbnb-frontend.onrender.com

# Expected: HTTP 200 OK
```

### **Phase 2: API Endpoint Testing**

```bash
# Test search endpoint (requires OpenRouter API key)
curl -X POST https://ai-airbnb-backend.onrender.com/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{"query":"Find a cozy apartment in San Francisco for 2 guests"}'

# Expected Response:
{
  "success": true,
  "properties": [
    {
      "id": "...",
      "title": "...",
      "price": "...",
      "location": "...",
      "image_url": "...",
      "rating": "...",
      "amenities": [...]
    }
    // ... 4 more properties (total of 5)
  ],
  "query": "Find a cozy apartment in San Francisco for 2 guests",
  "processed_query": "...",
  "total_results": 5
}
```

### **Phase 3: Frontend UI Testing**

1. **Open Frontend**: https://ai-airbnb-frontend.onrender.com
2. **Check Mobile Responsiveness**:
   - Test on mobile viewport (320px width)
   - Verify touch targets are 44px minimum
   - Test swipe gestures on carousel
3. **Test Search Functionality**:
   - Enter: "Find a beachfront villa in Miami for 4 people"
   - Verify loading state appears
   - Check that exactly 5 properties display in carousel
   - Test carousel navigation (swipe/arrows)
4. **Test Error Handling**:
   - Try invalid search queries
   - Test with network disconnected
   - Verify error messages display correctly

### **Phase 4: End-to-End Integration Testing**

```javascript
// Test complete workflow
const testWorkflow = async () => {
  // 1. Frontend sends search request
  const response = await fetch('https://ai-airbnb-backend.onrender.com/api/v1/search', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: 'Luxury penthouse in NYC' })
  });
  
  // 2. Backend processes with OpenRouter
  // 3. Backend fetches data from MCP server
  // 4. Frontend displays 5 properties in carousel
  
  const data = await response.json();
  console.log('Properties returned:', data.properties.length); // Should be 5
};
```

## 🎯 **SUCCESS CRITERIA CHECKLIST**

### **Technical Requirements**
- [ ] All services return healthy status
- [ ] OpenRouter API key configured and working
- [ ] MCP server returns Airbnb data
- [ ] Backend processes natural language queries
- [ ] Frontend displays exactly 5 properties
- [ ] Mobile-first design works on all screen sizes

### **User Experience Requirements**
- [ ] Search form is intuitive and responsive
- [ ] Loading states provide clear feedback
- [ ] Property cards display all required information
- [ ] Carousel navigation works smoothly
- [ ] Error messages are helpful and clear
- [ ] Touch gestures work on mobile devices

### **Performance Requirements**
- [ ] Initial page load < 3 seconds
- [ ] Search results load < 5 seconds
- [ ] Images load progressively (lazy loading)
- [ ] Smooth animations and transitions
- [ ] No console errors in browser

## 🚨 **COMMON ISSUES & SOLUTIONS**

### **Frontend Build Fails**
- **Issue**: TailwindCSS PostCSS configuration
- **Solution**: ✅ FIXED - Moved tailwindcss to devDependencies

### **Backend API Errors**
- **Issue**: OpenRouter API key not configured
- **Solution**: Add OPENROUTER_API_KEY environment variable

### **MCP Server Not Responding**
- **Issue**: Docker container not running
- **Solution**: Check Render logs, restart service if needed

### **CORS Errors**
- **Issue**: Frontend can't connect to backend
- **Solution**: Backend already configured with CORS(app, origins="*")

### **Mobile UI Issues**
- **Issue**: Touch targets too small
- **Solution**: All interactive elements are 44px minimum

## 📊 **MONITORING & DEBUGGING**

### **Service Logs**
- **Render Dashboard**: Check logs for each service
- **Browser Console**: Check for JavaScript errors
- **Network Tab**: Monitor API requests/responses

### **Performance Monitoring**
- **Lighthouse**: Test performance, accessibility, SEO
- **Mobile Testing**: Use Chrome DevTools device emulation
- **Load Testing**: Test with multiple concurrent users

## 🎉 **DEPLOYMENT SUCCESS VALIDATION**

When all tests pass, you'll have:
1. ✅ **Working AI-powered search** with natural language processing
2. ✅ **Real-time Airbnb data** from MCP server integration
3. ✅ **Mobile-optimized UI** with property carousel showing exactly 5 results
4. ✅ **Production deployment** on Render.com with auto-deployment from GitHub
5. ✅ **Comprehensive error handling** and user feedback

**Next Step**: Get your OpenRouter API key and configure the backend environment variables!
