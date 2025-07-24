# 🚀 AI Airbnb Search - Deployment Guide

## 📋 **DEPLOYMENT OVERVIEW**

This application is ready for deployment on Render.com with a simplified 2-service architecture:
- **Backend**: Flask API with OpenRouter LLM + RapidAPI Airbnb19 integration
- **Frontend**: React TypeScript application with mobile-first design

## 🔧 **RENDER.COM DEPLOYMENT STEPS**

### **Step 1: Sign Up and Connect GitHub**
1. Go to [render.com](https://render.com) and sign up
2. Connect your GitHub account
3. Select the repository: `ai-airbnb-search-app`

### **Step 2: Deploy Backend Service**
1. Click "New +" → "Web Service"
2. Select your GitHub repository
3. Configure:
   - **Name**: `ai-airbnb-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `cd backend && pip install -r requirements.txt`
   - **Start Command**: `cd backend && gunicorn --config gunicorn.conf.py app:app`
   - **Plan**: `Starter` (free tier)
   - **Region**: `Oregon` (or closest to your users)

### **Step 3: Configure Backend Environment Variables**
Add these environment variables in Render dashboard:

```bash
# Required - OpenRouter API Key
OPENROUTER_API_KEY=your-actual-openrouter-api-key-here

# Required - RapidAPI Configuration
RAPIDAPI_KEY=d8dad7a0d0msh79d5e302536f59cp1e388bjsn65fdb4ba9233
RAPIDAPI_HOST=airbnb19.p.rapidapi.com

# Flask Configuration
FLASK_ENV=production
CORS_ORIGINS=*

# OpenRouter Configuration
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
```

### **Step 4: Deploy Frontend Service**
1. Click "New +" → "Static Site"
2. Select your GitHub repository
3. Configure:
   - **Name**: `ai-airbnb-frontend`
   - **Build Command**: `cd frontend && npm ci && npm run build`
   - **Publish Directory**: `./frontend/build`
   - **Plan**: `Starter` (free tier)

### **Step 5: Configure Frontend Environment Variables**
Add these environment variables:

```bash
# Backend API URL (will be auto-populated by Render)
REACT_APP_API_URL=https://ai-airbnb-backend.onrender.com

# Production settings
NODE_ENV=production
```

## 🔑 **REQUIRED API KEYS**

### **OpenRouter API Key** (Required for LLM features)
1. Go to [openrouter.ai](https://openrouter.ai)
2. Sign up and get your API key
3. Add to backend environment variables as `OPENROUTER_API_KEY`

### **RapidAPI Key** (Already Configured)
- The RapidAPI key for Airbnb19 is already included
- Key: `d8dad7a0d0msh79d5e302536f59cp1e388bjsn65fdb4ba9233`
- This provides access to real Airbnb property data

## 🎯 **DEPLOYMENT VALIDATION**

### **Backend Health Check**
```bash
curl https://ai-airbnb-backend.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "services": {
    "flask_backend": true,
    "rapidapi_airbnb": true,
    "openrouter": true
  },
  "version": "3.0.0-direct-rapidapi"
}
```

### **Frontend Validation**
1. Visit: `https://ai-airbnb-frontend.onrender.com`
2. Test search: "Find a place in San Francisco"
3. Verify carousel shows exactly 5 properties
4. Test mobile responsiveness

### **End-to-End Test**
1. Enter search query: "Find a luxury apartment in New York"
2. Verify LLM processes the query
3. Confirm real Airbnb properties are returned
4. Check property carousel functionality
5. Test mobile touch gestures

## 🔧 **TROUBLESHOOTING**

### **Common Issues**

#### **Backend Fails to Start**
- Check environment variables are set correctly
- Verify OpenRouter API key is valid
- Check build logs for Python dependency issues

#### **Frontend Build Fails**
- Ensure Node.js version is 18+
- Check for TypeScript compilation errors
- Verify all dependencies are in package.json

#### **API Communication Fails**
- Verify CORS settings allow frontend domain
- Check REACT_APP_API_URL points to correct backend
- Ensure backend health endpoint is accessible

#### **No Search Results**
- Verify RapidAPI key is working
- Check backend logs for API call failures
- Test with different location queries

### **Debug Commands**

```bash
# Check backend logs
curl https://ai-airbnb-backend.onrender.com/health

# Test search endpoint
curl -X POST https://ai-airbnb-backend.onrender.com/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{"query":"Find a place in San Francisco"}'

# Check frontend build
npm run build
```

## 📊 **PERFORMANCE EXPECTATIONS**

### **Response Times**
- Health check: < 200ms
- Property search: 2-5 seconds (includes LLM processing)
- Frontend load: < 3 seconds

### **Capacity**
- Concurrent users: 100+ (Render Starter plan)
- Daily searches: 1000+ (RapidAPI limits)
- Storage: Minimal (stateless application)

## 🔄 **AUTO-DEPLOYMENT**

The application is configured for automatic deployment:
- **Trigger**: Push to `main` branch
- **Backend**: Automatically rebuilds and redeploys
- **Frontend**: Automatically rebuilds and redeploys
- **Rollback**: Available through Render dashboard

## 🎉 **SUCCESS CRITERIA**

✅ **Deployment Complete When**:
- [ ] Backend health check returns 200 OK
- [ ] Frontend loads without errors
- [ ] Search returns real Airbnb properties
- [ ] Property carousel displays exactly 5 results
- [ ] Mobile interface is responsive
- [ ] Touch gestures work on mobile devices

## 📞 **SUPPORT**

### **Render.com Resources**
- [Render Documentation](https://render.com/docs)
- [Environment Variables Guide](https://render.com/docs/environment-variables)
- [Troubleshooting Guide](https://render.com/docs/troubleshooting)

### **API Documentation**
- [OpenRouter API](https://openrouter.ai/docs)
- [RapidAPI Airbnb19](https://rapidapi.com/DataCrawler/api/airbnb19)

---

**🚀 Ready to deploy! The application is fully configured and tested for production deployment on Render.com.**
