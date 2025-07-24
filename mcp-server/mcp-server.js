#!/usr/bin/env node

const { spawn } = require('child_process');
const path = require('path');
const http = require('http');

console.log('🚀 Starting Real Airbnb MCP Server...');
console.log('📍 Using OpenBnB MCP Server for authentic Airbnb data');

// Health check endpoint for Render.com
const server = http.createServer((req, res) => {
  if (req.url === '/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ 
      status: 'healthy', 
      service: 'real-airbnb-mcp-server',
      timestamp: new Date().toISOString(),
      version: '1.0.0'
    }));
  } else if (req.url === '/') {
    res.writeHead(200, { 'Content-Type': 'text/html' });
    res.end(`
      <html>
        <head><title>Real Airbnb MCP Server</title></head>
        <body>
          <h1>🏠 Real Airbnb MCP Server</h1>
          <p>✅ Status: Running</p>
          <p>🔗 Using: OpenBnB MCP Server v0.1.3</p>
          <p>📊 Data Source: Real Airbnb listings</p>
          <p>🕒 Started: ${new Date().toISOString()}</p>
        </body>
      </html>
    `);
  } else {
    res.writeHead(404, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'Not found' }));
  }
});

const PORT = process.env.PORT || 8080;
server.listen(PORT, () => {
  console.log(`🌐 Health check server running on port ${PORT}`);
  console.log(`📍 Health endpoint: http://localhost:${PORT}/health`);
});

// Start the real OpenBnB MCP server
console.log('🔄 Initializing OpenBnB MCP Server...');
const mcpServer = spawn('npx', ['-y', '@openbnb/mcp-server-airbnb', '--ignore-robots-txt'], {
  stdio: ['inherit', 'pipe', 'pipe'],
  env: { 
    ...process.env, 
    NODE_ENV: 'production',
    IGNORE_ROBOTS_TXT: 'true'
  }
});

// Log MCP server output
mcpServer.stdout.on('data', (data) => {
  console.log(`[MCP] ${data.toString().trim()}`);
});

mcpServer.stderr.on('data', (data) => {
  console.error(`[MCP ERROR] ${data.toString().trim()}`);
});

mcpServer.on('error', (error) => {
  console.error('❌ MCP Server error:', error);
  process.exit(1);
});

mcpServer.on('close', (code) => {
  console.log(`🔴 MCP Server exited with code ${code}`);
  if (code !== 0) {
    console.error('❌ MCP Server crashed, exiting...');
    process.exit(code);
  }
});

// Handle graceful shutdown
const gracefulShutdown = (signal) => {
  console.log(`\n🛑 Received ${signal}, shutting down gracefully...`);
  
  // Close health check server
  server.close(() => {
    console.log('✅ Health check server closed');
  });
  
  // Kill MCP server
  if (mcpServer && !mcpServer.killed) {
    console.log('🔄 Stopping MCP server...');
    mcpServer.kill('SIGTERM');
    
    // Force kill after 5 seconds
    setTimeout(() => {
      if (!mcpServer.killed) {
        console.log('⚠️ Force killing MCP server...');
        mcpServer.kill('SIGKILL');
      }
    }, 5000);
  }
  
  setTimeout(() => {
    console.log('👋 Goodbye!');
    process.exit(0);
  }, 1000);
};

process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
process.on('SIGINT', () => gracefulShutdown('SIGINT'));

// Log startup completion
setTimeout(() => {
  console.log('✅ Real Airbnb MCP Server is ready!');
  console.log('🎯 Now serving authentic Airbnb property data');
}, 2000);
