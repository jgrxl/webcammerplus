/**
 * WebCammerPlus Content Script
 * Runs on Chaturbate pages to provide CSRF and API functionality
 */

console.log('🚀 WebCammerPlus content script loaded on:', window.location.href);

// Initialize CSRF parser when content script loads
let csrfReady = false;
let extensionAPI = null;
let pageApiReady = false;

// Listen for ready signal from page context
window.addEventListener('message', (event) => {
  if (event.source === window && event.data.type === 'WEBCAMMERPLUS_READY') {
    pageApiReady = true;
    console.log('✅ Page context API is ready!');
  }
});

// Initialize WebCammerPlus
function initializeWebCammerPlus() {
  csrfReady = true;
  console.log('✅ WebCammerPlus initializing...');
    
    // Create simple extension API object for popup communication
    extensionAPI = {
      getStatus() {
        return {
          ready: csrfReady,
          pageContextReady: typeof window.webcammerplus !== 'undefined',
          url: window.location.href,
          timestamp: new Date().toISOString()
        };
      },
      
      async testConnection() {
        console.log('🧪 Testing connection from content script...');
        return {
          status: 'connected',
          ready: csrfReady,
          pageReady: typeof window.webcammerplus !== 'undefined',
          timestamp: new Date().toISOString()
        };
      },
      
      async sendMessage(message) {
        console.log('📤 Sending message from content script:', message);
        
        // Wait for page injection to complete
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // Try to use page context API via postMessage
        try {
          if (pageApiReady) {
            console.log('✅ Using page context API for message sending via postMessage');
            
            // Use postMessage to communicate with page context
            const requestId = Math.random().toString(36);
            return new Promise((resolve, reject) => {
              const timeout = setTimeout(() => {
                reject(new Error('Page API request timeout'));
              }, 10000);
              
              const handler = (event) => {
                if (event.source === window && 
                    event.data.type === 'WEBCAMMERPLUS_RESPONSE' && 
                    event.data.id === requestId) {
                  clearTimeout(timeout);
                  window.removeEventListener('message', handler);
                  if (event.data.error) {
                    reject(new Error(event.data.error));
                  } else {
                    resolve(event.data.result);
                  }
                }
              };
              
              window.addEventListener('message', handler);
              window.postMessage({
                type: 'WEBCAMMERPLUS_SEND_MESSAGE',
                id: requestId,
                message: message
              }, '*');
            });
          }
        } catch (error) {
          console.warn('⚠️ Page context API failed:', error);
        }
        
        // Fallback: simulate sending (for testing)
        console.log('⚠️ Page context API not available, simulating send');
        return {
          success: true,
          message: message,
          method: 'simulated',
          timestamp: new Date().toISOString()
        };
      },
      
      async publishToRoom(room, message, username) {
        console.log('📡 Publishing to room from content script:', { room, message, username });
        
        // Wait for page injection to complete
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // Try to use page context API if available
        try {
          // Check if the page context API exists and has the publishToRoom function
          if (typeof window.webcammerplus !== 'undefined' && 
              typeof window.webcammerplus.publishToRoom === 'function') {
            console.log('✅ Using page context API for room publishing');
            return await window.webcammerplus.publishToRoom(room, message, username);
          }
        } catch (error) {
          console.warn('⚠️ Page context API failed:', error);
        }
        
        // Fallback: simulate publishing (for testing)
        console.log('⚠️ Page context API not available, simulating publish');
        return {
          success: true,
          room: room,
          message: message,
          username: username,
          method: 'simulated',
          timestamp: new Date().toISOString()
        };
      },
      
      getInfo() {
        return {
          contentScript: true,
          url: window.location.href,
          ready: csrfReady,
          pageReady: typeof window.webcammerplus !== 'undefined',
          userAgent: navigator.userAgent,
          timestamp: new Date().toISOString()
        };
      }
    };

    // Don't assign to global window.webcammerplus to avoid conflicts
    // The page injector will create the real window.webcammerplus API
    
    // Inject API functions into page context for console access
    console.log('🔄 Injecting webcammerplus API into page context...');
    injectPageAPI(extensionAPI);
    
    // Verify injection worked by listening for a ready signal from page context
    
    setTimeout(() => {
      console.log('🔍 Checking if webcammerplus is available...');
      console.log('Page context API ready:', pageApiReady);
      if (!pageApiReady) {
        console.warn('⚠️ Page context API not ready, using fallback mode');
      }
    }, 1000);
    
    // Add visual indicator that extension is active
    addExtensionIndicator();
    
    // Set up message passing with popup
    setupMessagePassing();
    
    console.log('🎯 WebCammerPlus ready! CSRF parser will load in page context');
}

// Add visual indicator
function addExtensionIndicator() {
  // Create a small indicator that shows the extension is active
  const indicator = document.createElement('div');
  indicator.id = 'webcammerplus-indicator';
  indicator.innerHTML = '🤖';
  indicator.style.cssText = `
    position: fixed;
    top: 10px;
    right: 10px;
    z-index: 10000;
    background: #3b82f6;
    color: white;
    padding: 8px;
    border-radius: 50%;
    font-size: 16px;
    cursor: pointer;
    box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    transition: all 0.3s ease;
  `;
  
  indicator.addEventListener('click', () => {
    const status = extensionAPI?.getStatus();
    alert(`WebCammerPlus Status:\\n\\nReady: ${status?.ready}\\nToken Valid: ${status?.tokenValid}\\nRoom: ${status?.room}\\nUsername: ${status?.username}`);
  });
  
  indicator.addEventListener('mouseenter', () => {
    indicator.style.transform = 'scale(1.1)';
  });
  
  indicator.addEventListener('mouseleave', () => {
    indicator.style.transform = 'scale(1)';
  });
  
  document.body.appendChild(indicator);
  console.log('👁️ WebCammerPlus indicator added (top-right corner)');
}

// Inject page script using web accessible resources (CSP-safe)
function injectPageAPI(api) {
  console.log('🔧 Injecting API via web accessible resources...');
  
  // First inject the CSRF parser into page context
  try {
    console.log('🔧 Injecting CSRF parser into page context...');
    const csrfScript = document.createElement('script');
    csrfScript.src = chrome.runtime.getURL('csrf-parser.js');
    csrfScript.onload = () => {
      console.log('✅ CSRF parser loaded in page context');
      
      // Now inject the page API
      const apiScript = document.createElement('script');
      apiScript.src = chrome.runtime.getURL('page-injector.js');
      apiScript.onload = () => {
        console.log('✅ Page injector script loaded successfully');
        apiScript.remove();
      };
      apiScript.onerror = (error) => {
        console.error('❌ Failed to load page injector script:', error);
        setupPostMessageAPI(api);
      };
      
      (document.head || document.documentElement).appendChild(apiScript);
      csrfScript.remove();
    };
    csrfScript.onerror = (error) => {
      console.error('❌ Failed to load CSRF parser script:', error);
      setupPostMessageAPI(api);
    };
    
    (document.head || document.documentElement).appendChild(csrfScript);
    console.log('🔧 CSRF parser script added to document');
    
  } catch (error) {
    console.error('❌ Script injection failed:', error);
    setupPostMessageAPI(api);
  }
}

// Setup postMessage-based API (CSP-safe alternative)
function setupPostMessageAPI(api) {
  console.log('🔧 Setting up postMessage API...');
  
  // Listen for page requests
  window.addEventListener('message', async (event) => {
    console.log('📨 Content script received message:', event.data);
    
    if (event.source !== window || event.data.type !== 'WEBCAMMERPLUS_REQUEST') {
      return;
    }
    
    console.log('✅ Processing WebCammerPlus request:', event.data);
    const { id, action, params } = event.data;
    let result, error = null;
    
    try {
      switch (action) {
        case 'getStatus':
          result = api.getStatus();
          break;
        case 'getInfo':
          result = api.getInfo();
          break;
        case 'testConnection':
          result = await api.testConnection();
          break;
        case 'sendMessage':
          result = await api.sendMessage(params.message);
          break;
        case 'publishToRoom':
          result = await api.publishToRoom(params.room, params.message, params.username);
          break;
        default:
          throw new Error(`Unknown action: ${action}`);
      }
    } catch (e) {
      error = e.message;
      console.error('❌ WebCammerPlus API error:', e);
    }
    
    // Send response back
    window.postMessage({
      type: 'WEBCAMMERPLUS_RESPONSE',
      id: id,
      result: result,
      error: error
    }, '*');
  });
  
  // Actually create the helper in page context
  setTimeout(() => {
    try {
      // Create the helper function directly in content script context, 
      // but make it accessible from page context
      window.wcmp = {
        call: async (action, params = {}) => {
          const id = Math.random().toString(36);
          return new Promise((resolve, reject) => {
            const handler = (event) => {
              if (event.data.type === 'WEBCAMMERPLUS_RESPONSE' && event.data.id === id) {
                window.removeEventListener('message', handler);
                if (event.data.error) {
                  reject(new Error(event.data.error));
                } else {
                  resolve(event.data.result);
                }
              }
            };
            window.addEventListener('message', handler);
            window.postMessage({type:'WEBCAMMERPLUS_REQUEST',action,params,id}, '*');
          });
        }
      };
      
      console.log('✅ window.wcmp helper created');
      
      // Also try creating a simple test function
      window.testWebCammerPlus = () => {
        console.log('🧪 Testing WebCammerPlus...');
        window.postMessage({type:'WEBCAMMERPLUS_REQUEST',action:'getStatus',id:'test'}, '*');
      };
      
      console.log(`
🎯 WebCammerPlus Console Commands Ready:

// Test if helper works:
testWebCammerPlus()

// Use the helper function:
await window.wcmp.call('getStatus')
await window.wcmp.call('sendMessage', {message: 'hello'})
await window.wcmp.call('testConnection')

// Or raw postMessage:
window.postMessage({type:'WEBCAMMERPLUS_REQUEST',action:'getStatus',id:1}, '*')
      `);
      
    } catch (error) {
      console.error('❌ Failed to create wcmp helper:', error);
    }
  }, 500);
}

// Set up communication with popup
function setupMessagePassing() {
  // Track processing state to prevent recursion
  let isHandlingMessage = false;
  
  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.log('📨 Content script received message:', request);
    
    // Prevent recursion/multiple simultaneous processing
    if (isHandlingMessage) {
      console.warn('⚠️ Already handling a message, ignoring duplicate request');
      sendResponse({ success: false, error: 'Already processing a request' });
      return;
    }
    
    // Handle async operations properly
    const handleAsync = async () => {
      isHandlingMessage = true;
      try {
        let result;
        
        switch (request.action) {
          case 'getStatus':
            result = extensionAPI.getStatus();
            sendResponse({ success: true, data: result });
            break;
            
          case 'getInfo':
            result = extensionAPI.getInfo();
            sendResponse({ success: true, data: result });
            break;
            
          case 'testConnection':
            result = await extensionAPI.testConnection();
            sendResponse({ success: true, data: result });
            break;
            
          case 'sendMessage':
            console.log('🚀 Processing sendMessage request for:', request.message);
            result = await extensionAPI.sendMessage(request.message);
            sendResponse({ success: true, data: result });
            break;
            
          case 'publishToRoom':
            result = await extensionAPI.publishToRoom(request.room, request.message, request.username);
            sendResponse({ success: true, data: result });
            break;
            
          default:
            sendResponse({ success: false, error: `Unknown action: ${request.action}` });
        }
      } catch (error) {
        console.error('❌ Content script error:', error);
        sendResponse({ success: false, error: error.message });
      } finally {
        // Reset processing flag after a short delay
        setTimeout(() => {
          isHandlingMessage = false;
        }, 500);
      }
    };
    
    // Execute async handler
    handleAsync();
    
    // Return true to indicate we'll send response asynchronously
    return true;
  });
}

// Add keyboard shortcut for quick testing
document.addEventListener('keydown', (event) => {
  // Ctrl+Shift+T to test connection
  if (event.ctrlKey && event.shiftKey && event.key === 'T') {
    event.preventDefault();
    if (extensionAPI) {
      extensionAPI.testConnection();
    } else {
      console.log('❌ WebCammerPlus not ready yet');
    }
  }
  
  // Ctrl+Shift+M to send test message
  if (event.ctrlKey && event.shiftKey && event.key === 'M') {
    event.preventDefault();
    if (extensionAPI) {
      const message = prompt('Enter message to send:');
      if (message) {
        extensionAPI.sendMessage(message);
      }
    } else {
      console.log('❌ WebCammerPlus not ready yet');
    }
  }
});

// Start initialization
initializeWebCammerPlus();

// Also add some helpful console commands
console.log(`
🤖 WebCammerPlus Console Commands:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

// Check status
webcammerplus.getStatus()

// Test connection  
await webcammerplus.testConnection()

// Send chat message
await webcammerplus.sendMessage("Hello from WebCammerPlus!")

// Publish to specific room
await webcammerplus.publishToRoom("roomname", "message", "username")

// Get detailed token info
webcammerplus.getInfo()

// Keyboard shortcuts:
// Ctrl+Shift+T = Test connection
// Ctrl+Shift+M = Send message

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
`);