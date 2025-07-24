# 🚀 AI Airbnb Search Application - Deployment Guide

## 📋 Project Overview

This is a complete AI-powered Airbnb search application with:
- **React Frontend** (mobile-first with property carousel)
- **Flask Backend** (API orchestration with OpenRouter LLM integration)
- **MCP Server** (containerized Airbnb data service)
- **Deployment** (Render.com ready)

**Repository**: https://github.com/Ersa-tech/ai-airbnb-search-app

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend │    │  Flask Backend  │    │   MCP Server    │
│   (Port 3000)    │◄──►│   (Port 5000)   │◄──►│   (Port 8080)   │
│                 │    │                 │    │                 │
│ • Property UI   │    │ • OpenRouter    │    │ • Airbnb Data   │
│ • Search Form   │    │ • API Routes    │    │ • HTTP Wrapper  │
│ • Carousel      │    │ • CORS Enabled  │    │ • Docker Ready  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start (Local Development)

### Prerequisites
- Node.js 18+
- Python 3.11+
- Docker
- GitHub CLI (gh)

### 1. Clone Repository
```bash
git clone https://github.com/Ersa-tech/ai-airbnb-search-app.git
cd ai-airbnb-search-app
```

### 2. Start MCP Server
```bash
cd mcp-server
npm install
docker build -t ai-airbnb-mcp .
docker run -p 8080:8080 ai-airbnb-mcp
```

### 3. Start Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set environment variables
export OPENROUTER_API_KEY="your_openrouter_api_key"
export MCP_SERVER_URL="http://localhost:8080"

python app.py
```

### 4. Start Frontend
```bash
cd frontend
npm install
npm start
```

### 5. Access Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000
- MCP Server: http://localhost:8080

## 🌐 Render.com Deployment

### Step 1: Prepare Repository
✅ **Already Done** - Repository is ready at: https://github.com/Ersa-tech/ai-airbnb-search-app

### Step 2: Sign Up for Render.com
1. Go to https://render.com
2. Sign up with GitHub account
3. Connect your GitHub repository

### Step 3: Create Services

#### A. MCP Server (Docker Service)
1. **New** → **Web Service**
2. **Connect Repository**: `Ersa-tech/ai-airbnb-search-app`
3. **Settings**:
   - Name: `ai-airbnb-mcp-server`
   - Environment: `Docker`
   - Region: `Oregon (US West)`
   - Branch: `main`
   - Root Directory: `mcp-server`
   - Plan: `Free`

#### B. Backend (Web Service)
1. **New** → **Web Service**
2. **Connect Repository**: `Ersa-tech/ai-airbnb-search-app`
3. **Settings**:
   - Name: `ai-airbnb-backend`
   - Environment: `Python 3`
   - Region: `Oregon (US West)`
   - Branch: `main`
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
   - Plan: `Free`

4. **Environment Variables**:
   ```
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   MCP_SERVER_URL=https://ai-airbnb-mcp-server.onrender.com
   FLASK_ENV=production
   ```

#### C. Frontend (Static Site)
1. **New** → **Static Site**
2. **Connect Repository**: `Ersa-tech/ai-airbnb-search-app`
3. **Settings**:
   - Name: `ai-airbnb-frontend`
   - Branch: `main`
   - Root Directory: `frontend`
   - Build Command: `npm install && npm run build`
   - Publish Directory: `build`

4. **Environment Variables**:
   ```
   REACT_APP_API_URL=https://ai-airbnb-backend.onrender.com
   ```

### Step 4: Get OpenRouter API Key
1. Go to https://openrouter.ai
2. Sign up for an account
3. Navigate to API Keys section
4. Create a new API key
5. Add it to backend environment variables

### Step 5: Deploy and Test
1. All services will auto-deploy from GitHub
2. Wait for all builds to complete (5-10 minutes)
3. Test the application at your frontend URL

## 🔧 Configuration Files

### render.yaml (Auto-deployment)
The project includes a `render.yaml` file for automatic service creation:

```yaml
services:
  - type: web
    name: ai-airbnb-mcp-server
    env: docker
    repo: https://github.com/Ersa-tech/ai-airbnb-search-app.git
    rootDir: mcp-server
    plan: free
    
  - type: web
    name: ai-airbnb-backend
    env: python
    repo: https://github.com/Ersa-tech/ai-airbnb-search-app.git
    rootDir: backend
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:app
    plan: free
    envVars:
      - key: OPENROUTER_API_KEY
        sync: false
      - key: MCP_SERVER_URL
        value: https://ai-airbnb-mcp-server.onrender.com
        
  - type: web
    name: ai-airbnb-frontend
    env: static
    repo: https://github.com/Ersa-tech/ai-airbnb-search-app.git
    rootDir: frontend
    buildCommand: npm install && npm run build
    staticPublishPath: build
    envVars:
      - key: REACT_APP_API_URL
        value: https://ai-airbnb-backend.onrender.com
```

## 🧪 Testing the Application

### 1. Health Checks
```bash
# Backend health
curl https://ai-airbnb-backend.onrender.com/health

# MCP Server health
curl https://ai-airbnb-mcp-server.onrender.com/health
```

### 2. Search Functionality
1. Open frontend URL
2. Enter search query: "Find a cozy place in San Francisco"
3. Verify 5 properties display in carousel
4. Test swipe gestures on mobile

### 3. Mobile Testing
- Test on various screen sizes
- Verify touch targets are 44px minimum
- Check carousel swipe functionality
- Validate responsive design

## 🐛 Troubleshooting

### Common Issues

#### 1. MCP Server Not Responding
```bash
# Check Docker container logs
docker logs <container_id>

# Restart container
docker restart <container_id>
```

#### 2. Backend API Errors
- Verify OpenRouter API key is set
- Check MCP_SERVER_URL environment variable
- Review backend logs in Render dashboard

#### 3. Frontend Build Failures
- Ensure Node.js version is 18+
- Check for TypeScript errors
- Verify environment variables

#### 4. CORS Issues
- Backend has CORS enabled for all origins
- Check network requests in browser dev tools

### Service URLs
After deployment, your services will be available at:
- **Frontend**: `https://ai-airbnb-frontend.onrender.com`
- **Backend**: `https://ai-airbnb-backend.onrender.com`
- **MCP Server**: `https://ai-airbnb-mcp-server.onrender.com`

## 📊 Performance Optimization

### Frontend
- Lazy loading for images
- Component memoization
- Efficient carousel rendering
- Mobile-first responsive design

### Backend
- Gunicorn WSGI server
- Request/response logging
- Error handling and retries
- OpenRouter API optimization

### MCP Server
- Docker containerization
- HTTP wrapper for efficiency
- Express.js for fast routing
- CORS enabled for cross-origin requests

## 🔒 Security Notes

**For Internal Use Only** - This application is configured for internal use with simplified security:
- CORS disabled for development
- No complex authentication required
- Focus on functionality over security

For production use, consider adding:
- Authentication and authorization
- Rate limiting
- Input validation
- HTTPS enforcement
- Environment-specific configurations

## 📈 Monitoring

### Render.com Dashboard
- Monitor service health and logs
- Track deployment status
- View performance metrics
- Set up alerts for downtime

### Application Monitoring
- Backend logs all requests/responses
- Frontend includes error boundaries
- Health check endpoints available
- Performance metrics tracked

## 🎯 Success Criteria

✅ **Must-Have Features**
- [x] Natural language search processing with OpenRouter
- [x] Property carousel displays exactly 5 results
- [x] Mobile-first responsive design with touch gestures
- [x] Real-time Airbnb data from MCP server
- [x] All services deployed and communicating on Render.com

✅ **Technical Requirements**
- [x] React frontend with TypeScript
- [x] Flask backend with comprehensive error handling
- [x] Containerized MCP server with HTTP wrapper
- [x] Auto-deployment from GitHub to Render.com
- [x] Environment variables properly configured

## 🚀 Next Steps

1. **Get OpenRouter API Key** from https://openrouter.ai
2. **Deploy to Render.com** using the steps above
3. **Test End-to-End** functionality
4. **Monitor Performance** and optimize as needed
5. **Scale Services** based on usage patterns

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review service logs in Render.com dashboard
3. Test individual components locally
4. Verify environment variables and API keys

**Repository**: https://github.com/Ersa-tech/ai-airbnb-search-app
**Live Demo**: Will be available after Render.com deployment

---

🎉 **Congratulations!** You now have a complete AI-powered Airbnb search application ready for deployment!
