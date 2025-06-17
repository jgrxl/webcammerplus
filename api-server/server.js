/**
 * WebCammerPlus API Server
 * REST API for controlling Chrome extension and Chaturbate functions
 */

const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const WebSocket = require('ws');
const { v4: uuidv4 } = require('uuid');

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json());

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // Limit each IP to 100 requests per windowMs
  message: { error: 'Too many requests, please try again later' }
});
app.use('/api/', limiter);

// Storage for active extension connections
const activeExtensions = new Map();
const pendingRequests = new Map();

// WebSocket server for extension communication
const wss = new WebSocket.Server({ port: 3002 });

wss.on('connection', (ws) => {
  const extensionId = uuidv4();
  console.log(`🔗 Extension connected: ${extensionId}`);
  
  activeExtensions.set(extensionId, {
    ws,
    connected: true,
    lastSeen: Date.now(),
    capabilities: []
  });

  ws.on('message', (data) => {
    try {
      const message = JSON.parse(data);
      handleExtensionMessage(extensionId, message);
    } catch (error) {
      console.error('❌ Invalid message from extension:', error);
    }
  });

  ws.on('close', () => {
    console.log(`🔌 Extension disconnected: ${extensionId}`);
    activeExtensions.delete(extensionId);
  });

  // Send connection confirmation
  ws.send(JSON.stringify({
    type: 'connection',
    extensionId,
    message: 'Connected to WebCammerPlus API server'
  }));
});

// Handle messages from extensions
function handleExtensionMessage(extensionId, message) {
  console.log(`📨 Message from ${extensionId}:`, message);

  switch (message.type) {
    case 'response':
      // Handle API response from extension
      if (message.requestId && pendingRequests.has(message.requestId)) {
        const { resolve } = pendingRequests.get(message.requestId);
        pendingRequests.delete(message.requestId);
        resolve(message.data);
      }
      break;

    case 'error':
      // Handle error response from extension
      if (message.requestId && pendingRequests.has(message.requestId)) {
        const { reject } = pendingRequests.get(message.requestId);
        pendingRequests.delete(message.requestId);
        reject(new Error(message.error));
      }
      break;

    case 'capabilities':
      // Extension reporting its capabilities
      const extension = activeExtensions.get(extensionId);
      if (extension) {
        extension.capabilities = message.capabilities;
        extension.lastSeen = Date.now();
      }
      break;

    case 'event':
      // Real-time event from extension (tips, messages, etc.)
      console.log(`🎯 Real-time event from ${extensionId}:`, message.event);
      // Could broadcast to connected clients here
      break;
  }
}

// Send request to extension and wait for response
async function sendToExtension(action, params = {}, timeout = 10000) {
  if (activeExtensions.size === 0) {
    throw new Error('No active extensions connected');
  }

  // Use first available extension (could implement load balancing)
  const [extensionId, extension] = Array.from(activeExtensions.entries())[0];
  
  if (!extension.connected) {
    throw new Error('Extension not connected');
  }

  const requestId = uuidv4();
  const request = {
    type: 'request',
    requestId,
    action,
    params
  };

  return new Promise((resolve, reject) => {
    // Store pending request
    pendingRequests.set(requestId, { resolve, reject });

    // Set timeout
    setTimeout(() => {
      if (pendingRequests.has(requestId)) {
        pendingRequests.delete(requestId);
        reject(new Error('Request timeout'));
      }
    }, timeout);

    // Send to extension
    extension.ws.send(JSON.stringify(request));
  });
}

// API Routes

/**
 * GET /api/status
 * Get API server and extension status
 */
app.get('/api/status', (req, res) => {
  const extensions = Array.from(activeExtensions.entries()).map(([id, ext]) => ({
    id,
    connected: ext.connected,
    lastSeen: ext.lastSeen,
    capabilities: ext.capabilities
  }));

  res.json({
    status: 'running',
    timestamp: new Date().toISOString(),
    extensions: {
      total: extensions.length,
      active: extensions.filter(e => e.connected).length,
      list: extensions
    },
    pendingRequests: pendingRequests.size,
    uptime: process.uptime()
  });
});

/**
 * POST /api/chaturbate/status
 * Get Chaturbate connection status from extension
 */
app.post('/api/chaturbate/status', async (req, res) => {
  try {
    const result = await sendToExtension('getStatus');
    res.json({
      success: true,
      data: result
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * POST /api/chaturbate/send-message
 * Send a chat message via extension
 * Body: { "message": "Hello world!" }
 */
app.post('/api/chaturbate/send-message', async (req, res) => {
  try {
    const { message } = req.body;
    
    if (!message || typeof message !== 'string') {
      return res.status(400).json({
        success: false,
        error: 'Message is required and must be a string'
      });
    }

    const result = await sendToExtension('sendMessage', { message });
    res.json({
      success: true,
      data: result,
      message: `Message sent: ${message}`
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * POST /api/chaturbate/publish-to-room
 * Publish message to specific room
 * Body: { "room": "roomname", "message": "Hello!", "username": "user" }
 */
app.post('/api/chaturbate/publish-to-room', async (req, res) => {
  try {
    const { room, message, username } = req.body;
    
    if (!room || !message || !username) {
      return res.status(400).json({
        success: false,
        error: 'room, message, and username are required'
      });
    }

    const result = await sendToExtension('publishToRoom', { room, message, username });
    res.json({
      success: true,
      data: result,
      message: `Message published to room ${room}`
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * POST /api/chaturbate/test-connection
 * Test Chaturbate API connection
 */
app.post('/api/chaturbate/test-connection', async (req, res) => {
  try {
    const result = await sendToExtension('testConnection');
    res.json({
      success: true,
      data: result,
      message: 'Connection test successful'
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * GET /api/chaturbate/token-info
 * Get CSRF token information
 */
app.get('/api/chaturbate/token-info', async (req, res) => {
  try {
    const result = await sendToExtension('getInfo');
    res.json({
      success: true,
      data: result
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error('❌ API Error:', err);
  res.status(500).json({
    success: false,
    error: 'Internal server error'
  });
});

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({
    success: false,
    error: 'Endpoint not found',
    availableEndpoints: [
      'GET /api/status',
      'POST /api/chaturbate/status',
      'POST /api/chaturbate/send-message',
      'POST /api/chaturbate/publish-to-room',
      'POST /api/chaturbate/test-connection',
      'GET /api/chaturbate/token-info'
    ]
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`
🚀 WebCammerPlus API Server Running!

📡 HTTP API: http://localhost:${PORT}
🔌 WebSocket: ws://localhost:3002
📋 Status: http://localhost:${PORT}/api/status

🎯 Available Endpoints:
├── GET  /api/status
├── POST /api/chaturbate/status
├── POST /api/chaturbate/send-message
├── POST /api/chaturbate/publish-to-room
├── POST /api/chaturbate/test-connection
└── GET  /api/chaturbate/token-info

💡 Test with: curl http://localhost:${PORT}/api/status
  `);
});

console.log('🔧 WebSocket server listening on port 3002 for extension connections');