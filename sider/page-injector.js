/**
 * Page Context Injector for WebCammerPlus
 * This script runs in the actual page context and can access the console
 */

console.log('🚀 WebCammerPlus page injector loaded');

// Create the API in page context
window.webcammerplus = {
  getStatus() {
    console.log('📋 webcammerplus.getStatus() called');
    if (window.csrfParser) {
      return {
        ready: true,
        token: window.csrfParser.getCurrentToken(),
        tokenValid: window.csrfParser.isTokenValid(),
        room: window.csrfParser.extractRoomFromURL(),
        username: window.csrfParser.extractUsernameFromPage()
      };
    } else {
      return { ready: false, error: 'CSRF Parser not available' };
    }
  },

  getInfo() {
    console.log('📋 webcammerplus.getInfo() called');
    return window.csrfParser ? window.csrfParser.getTokenInfo() : null;
  },

  async sendMessage(message) {
    console.log('💬 webcammerplus.sendMessage() called:', message);
    if (window.csrfParser) {
      return await window.csrfParser.sendChatMessage(message);
    } else {
      throw new Error('CSRF Parser not available');
    }
  },

  async testConnection() {
    console.log('🧪 webcammerplus.testConnection() called');
    if (window.csrfParser) {
      return await window.csrfParser.getBroadcastStatus();
    } else {
      throw new Error('CSRF Parser not available');
    }
  },

  async publishToRoom(room, message, username) {
    console.log('📡 webcammerplus.publishToRoom() called:', { room, message, username });
    if (window.csrfParser) {
      return await window.csrfParser.publishChatMessage(room, message, username);
    } else {
      throw new Error('CSRF Parser not available');
    }
  }
};

// Create helper functions
window.wcmp = {
  async call(action, params = {}) {
    console.log('🔧 wcmp.call() called:', action, params);
    switch (action) {
      case 'getStatus':
        return window.webcammerplus.getStatus();
      case 'getInfo':
        return window.webcammerplus.getInfo();
      case 'testConnection':
        return await window.webcammerplus.testConnection();
      case 'sendMessage':
        return await window.webcammerplus.sendMessage(params.message);
      case 'publishToRoom':
        return await window.webcammerplus.publishToRoom(params.room, params.message, params.username);
      default:
        throw new Error(`Unknown action: ${action}`);
    }
  }
};

// Test function
window.testWebCammerPlus = () => {
  console.log('🧪 Testing WebCammerPlus...');
  const status = window.webcammerplus.getStatus();
  console.log('📊 Status:', status);
  return status;
};

console.log('✅ WebCammerPlus API ready in page context!');
console.log('🎯 Available commands:');
console.log('  - webcammerplus.getStatus()');
console.log('  - await webcammerplus.sendMessage("hello")');
console.log('  - await webcammerplus.testConnection()');
console.log('  - testWebCammerPlus()');
console.log('  - await wcmp.call("getStatus")');

// Listen for messages from content script
window.addEventListener('message', async (event) => {
  if (event.source !== window) return;
  
  if (event.data.type === 'WEBCAMMERPLUS_SEND_MESSAGE') {
    console.log('📨 Page context received sendMessage request:', event.data);
    
    try {
      const result = await window.webcammerplus.sendMessage(event.data.message);
      window.postMessage({
        type: 'WEBCAMMERPLUS_RESPONSE',
        id: event.data.id,
        result: result
      }, '*');
    } catch (error) {
      console.error('❌ Page context sendMessage error:', error);
      window.postMessage({
        type: 'WEBCAMMERPLUS_RESPONSE',
        id: event.data.id,
        error: error.message
      }, '*');
    }
  }
});

// Signal to content script that page API is ready
window.postMessage({ type: 'WEBCAMMERPLUS_READY' }, '*');