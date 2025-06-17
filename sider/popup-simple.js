// Simple WebCammerPlus Extension without Vue template compilation
document.addEventListener('DOMContentLoaded', function() {
  console.log('🚀 WebCammerPlus Simple Interface loaded');
  
  // Simple API interface without complex Vue templates
  window.api = {
    async call(endpoint, params = {}) {
      const startTime = Date.now();
      console.log(`🌐 API Call: ${endpoint}`, params);
      
      try {
        let result;
        
        switch (endpoint) {
          case '/status':
            result = await sendMessageToContentScript({ action: 'getStatus' });
            break;
            
          case '/send-message':
            if (!params.message) throw new Error('message parameter required');
            result = await sendMessageToContentScript({ 
              action: 'sendMessage', 
              message: params.message 
            });
            break;
            
          case '/test-connection':
            result = await sendMessageToContentScript({ action: 'testConnection' });
            break;
            
          default:
            throw new Error(`Unknown endpoint: ${endpoint}`);
        }
        
        const duration = Date.now() - startTime;
        console.log(`✅ API Success: ${endpoint} (${duration}ms)`, result);
        
        return {
          success: true,
          data: result,
          endpoint,
          duration,
          timestamp: new Date().toISOString()
        };
        
      } catch (error) {
        const duration = Date.now() - startTime;
        console.error(`❌ API Error: ${endpoint} (${duration}ms)`, error);
        
        return {
          success: false,
          error: error.message,
          endpoint,
          duration,
          timestamp: new Date().toISOString()
        };
      }
    }
  };
  
  // Helper function to communicate with content script
  async function sendMessageToContentScript(message) {
    return new Promise(async (resolve) => {
      chrome.tabs.query({ active: true, currentWindow: true }, async (tabs) => {
        console.log('🔍 Active tabs:', tabs);
        
        if (!tabs || tabs.length === 0) {
          resolve({ success: false, error: 'No active tab found' });
          return;
        }
        
        const activeTab = tabs[0];
        console.log('🔍 Active tab URL:', activeTab.url);
        
        if (!activeTab.url.includes('chaturbate.com')) {
          resolve({ 
            success: false, 
            error: `Not on Chaturbate page. Current URL: ${activeTab.url}` 
          });
          return;
        }
        
        console.log('📤 Sending message to content script:', message);
        chrome.tabs.sendMessage(activeTab.id, message, (response) => {
          if (chrome.runtime.lastError) {
            console.error('❌ Content script communication error:', chrome.runtime.lastError);
            
            // Try to inject content script manually as fallback
            console.log('🔄 Attempting to inject content script manually...');
            chrome.scripting.executeScript({
              target: { tabId: activeTab.id },
              files: ['content-script.js']
            }).then(() => {
              console.log('✅ Content script injected manually, retrying message...');
              // Retry the message after a short delay
              setTimeout(() => {
                chrome.tabs.sendMessage(activeTab.id, message, (retryResponse) => {
                  if (chrome.runtime.lastError) {
                    console.error('❌ Retry failed:', chrome.runtime.lastError);
                    resolve({ 
                      success: false, 
                      error: `Content script not responding after injection: ${chrome.runtime.lastError.message}` 
                    });
                  } else {
                    console.log('✅ Retry successful:', retryResponse);
                    resolve(retryResponse);
                  }
                });
              }, 1000);
            }).catch((error) => {
              console.error('❌ Manual injection failed:', error);
              resolve({ 
                success: false, 
                error: `Content script injection failed: ${error.message}` 
              });
            });
          } else {
            console.log('✅ Content script response:', response);
            resolve(response);
          }
        });
      });
    });
  }
  
  // Update status display
  function updateStatus(message, type = 'info') {
    const statusEl = document.getElementById('status');
    if (statusEl) {
      statusEl.textContent = message;
      statusEl.className = `status ${type}`;
    }
  }
  
  // Add result to results section
  function addResult(result) {
    const resultsEl = document.getElementById('results');
    if (resultsEl) {
      const resultEl = document.createElement('div');
      resultEl.className = `result ${result.success ? 'success' : 'error'}`;
      resultEl.innerHTML = `
        <div class="result-header">
          <strong>${result.endpoint}</strong>
          <span class="duration">${result.duration}ms</span>
        </div>
        <div class="result-body">
          ${result.success ? 
            `<pre>${JSON.stringify(result.data, null, 2)}</pre>` :
            `<span class="error">${result.error}</span>`
          }
        </div>
      `;
      resultsEl.insertBefore(resultEl, resultsEl.firstChild);
      
      // Limit to 10 results
      while (resultsEl.children.length > 10) {
        resultsEl.removeChild(resultsEl.lastChild);
      }
    }
  }
  
  // Debug function to check current tab
  async function debugTab() {
    updateStatus('Checking tab...', 'loading');
    
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      const result = {
        success: true,
        data: {
          tabCount: tabs.length,
          activeTab: tabs[0] ? {
            url: tabs[0].url,
            title: tabs[0].title,
            id: tabs[0].id
          } : null,
          isChaturbate: tabs[0] ? tabs[0].url.includes('chaturbate.com') : false
        },
        endpoint: '/debug-tab',
        duration: 0,
        timestamp: new Date().toISOString()
      };
      
      addResult(result);
      updateStatus(result.data.isChaturbate ? 'On Chaturbate' : 'Not on Chaturbate', 
                  result.data.isChaturbate ? 'success' : 'error');
    });
  }

  // Button event handlers
  async function testStatus() {
    updateStatus('Testing status...', 'loading');
    const result = await window.api.call('/status');
    addResult(result);
    updateStatus(result.success ? 'Status OK' : 'Status failed', result.success ? 'success' : 'error');
  }
  
  async function testConnection() {
    updateStatus('Testing connection...', 'loading');
    const result = await window.api.call('/test-connection');
    addResult(result);
    updateStatus(result.success ? 'Connection OK' : 'Connection failed', result.success ? 'success' : 'error');
  }
  
  let isProcessing = false;
  
  async function sendTestMessage() {
    if (isProcessing) {
      console.warn('⚠️ Already processing a message, ignoring duplicate request');
      return;
    }
    
    isProcessing = true;
    updateStatus('Sending test message...', 'loading');
    
    try {
      const result = await window.api.call('/send-message', { message: 'Hello from WebCammerPlus!' });
      addResult(result);
      updateStatus(result.success ? 'Message sent' : 'Message failed', result.success ? 'success' : 'error');
    } finally {
      // Add delay before allowing next message
      setTimeout(() => {
        isProcessing = false;
      }, 1000);
    }
  }
  
  async function sendCustomMessage() {
    if (isProcessing) {
      console.warn('⚠️ Already processing a message, ignoring duplicate request');
      return;
    }
    
    const input = document.getElementById('messageInput');
    const message = input.value.trim();
    
    if (!message) {
      updateStatus('Please enter a message', 'error');
      return;
    }
    
    isProcessing = true;
    updateStatus(`Sending: ${message}`, 'loading');
    
    try {
      const result = await window.api.call('/send-message', { message });
      addResult(result);
      updateStatus(result.success ? 'Message sent' : 'Message failed', result.success ? 'success' : 'error');
      
      if (result.success) {
        input.value = '';
      }
    } finally {
      // Add delay before allowing next message
      setTimeout(() => {
        isProcessing = false;
      }, 1000);
    }
  }
  
  // Set up event listeners (prevent multiple attachments)
  const debugTabBtn = document.getElementById('debugTabBtn');
  const testStatusBtn = document.getElementById('testStatusBtn');
  const testConnectionBtn = document.getElementById('testConnectionBtn');
  const sendTestMessageBtn = document.getElementById('sendTestMessageBtn');
  const sendCustomMessageBtn = document.getElementById('sendCustomMessageBtn');
  
  // Remove any existing listeners first
  debugTabBtn.removeEventListener('click', debugTab);
  testStatusBtn.removeEventListener('click', testStatus);
  testConnectionBtn.removeEventListener('click', testConnection);
  sendTestMessageBtn.removeEventListener('click', sendTestMessage);
  sendCustomMessageBtn.removeEventListener('click', sendCustomMessage);
  
  // Add fresh listeners
  debugTabBtn.addEventListener('click', debugTab);
  testStatusBtn.addEventListener('click', testStatus);
  testConnectionBtn.addEventListener('click', testConnection);
  sendTestMessageBtn.addEventListener('click', sendTestMessage);
  sendCustomMessageBtn.addEventListener('click', sendCustomMessage);
  
  // Handle Enter key in message input
  document.getElementById('messageInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
      sendCustomMessage();
    }
  });
  
  console.log('✅ WebCammerPlus API ready');
  updateStatus('Ready');
});