/**
 * WebCammerPlus API Bridge
 * Connects Chrome extension to external API server via WebSocket
 */

class WebCammerPlusAPIBridge {
  constructor() {
    this.ws = null;
    this.connected = false;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000;
    this.serverUrl = 'ws://localhost:3002';
    
    this.connect();
    
    console.log('🌉 WebCammerPlus API Bridge initialized');
  }

  connect() {
    try {
      console.log('🔗 Connecting to API server...');
      this.ws = new WebSocket(this.serverUrl);
      
      this.ws.onopen = () => {
        console.log('✅ Connected to WebCammerPlus API server');
        this.connected = true;
        this.reconnectAttempts = 0;
        
        // Send capabilities to server
        this.sendCapabilities();
      };
      
      this.ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          this.handleServerMessage(message);
        } catch (error) {
          console.error('❌ Invalid message from server:', error);
        }
      };
      
      this.ws.onclose = () => {
        console.log('🔌 Disconnected from API server');
        this.connected = false;
        this.reconnect();
      };
      
      this.ws.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
      };
      
    } catch (error) {
      console.error('❌ Failed to connect to API server:', error);
      this.reconnect();
    }
  }

  reconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('❌ Max reconnection attempts reached');
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * this.reconnectAttempts;
    
    console.log(`🔄 Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
    
    setTimeout(() => {
      this.connect();
    }, delay);
  }

  sendCapabilities() {
    if (!this.connected) return;
    
    const capabilities = [
      'getStatus',
      'sendMessage',
      'publishToRoom',
      'testConnection',
      'getInfo'
    ];
    
    this.send({
      type: 'capabilities',
      capabilities,
      timestamp: Date.now(),
      userAgent: navigator.userAgent,
      url: window.location.href
    });
  }

  send(message) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.warn('⚠️ Cannot send message - not connected to server');
    }
  }

  async handleServerMessage(message) {
    console.log('📨 Message from API server:', message);

    switch (message.type) {
      case 'connection':
        console.log('🎯 Server connection confirmed:', message.message);
        break;

      case 'request':
        await this.handleAPIRequest(message);
        break;

      default:
        console.log('ℹ️ Unknown message type:', message.type);
    }
  }

  async handleAPIRequest(message) {
    const { requestId, action, params } = message;
    
    try {
      console.log(`🎯 Handling API request: ${action}`, params);
      
      let result;
      
      // Check if webcammerplus is available
      if (typeof window.webcammerplus === 'undefined') {
        throw new Error('WebCammerPlus not available in page context');
      }

      // Execute the requested action
      switch (action) {
        case 'getStatus':
          result = window.webcammerplus.getStatus();
          break;

        case 'getInfo':
          result = window.webcammerplus.getInfo();
          break;

        case 'testConnection':
          result = await window.webcammerplus.testConnection();
          break;

        case 'sendMessage':
          if (!params.message) {
            throw new Error('Message parameter required');
          }
          result = await window.webcammerplus.sendMessage(params.message);
          break;

        case 'publishToRoom':
          const { room, message: msg, username } = params;
          if (!room || !msg || !username) {
            throw new Error('room, message, and username parameters required');
          }
          result = await window.webcammerplus.publishToRoom(room, msg, username);
          break;

        default:
          throw new Error(`Unknown action: ${action}`);
      }

      // Send success response
      this.send({
        type: 'response',
        requestId,
        data: result,
        timestamp: Date.now()
      });

      console.log(`✅ API request completed: ${action}`);

    } catch (error) {
      console.error(`❌ API request failed: ${action}`, error);
      
      // Send error response
      this.send({
        type: 'error',
        requestId,
        error: error.message,
        timestamp: Date.now()
      });
    }
  }

  // Send real-time events to server
  sendEvent(eventType, eventData) {
    if (!this.connected) return;
    
    this.send({
      type: 'event',
      event: {
        type: eventType,
        data: eventData,
        timestamp: Date.now(),
        url: window.location.href
      }
    });
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.connected = false;
    console.log('🔌 API Bridge disconnected');
  }
}

// Initialize API bridge
let apibridge = null;

// Wait for page to be ready
function initializeAPIBridge() {
  if (typeof window.webcammerplus !== 'undefined') {
    apibridge = new WebCammerPlusAPIBridge();
    console.log('🌉 API Bridge ready');
  } else {
    console.log('⏳ Waiting for webcammerplus...');
    setTimeout(initializeAPIBridge, 1000);
  }
}

// Start initialization
setTimeout(initializeAPIBridge, 2000);

// Make bridge available globally for debugging
window.apibridge = apibridge;