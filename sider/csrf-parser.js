/**
 * CSRF Token Parser for WebCammerPlus
 * Handles extraction, monitoring, and usage of Chaturbate CSRF tokens
 */

class CSRFParser {
  constructor() {
    this.currentToken = null;
    this.tokenChangeCallbacks = [];
    this.refreshInterval = null;
    this.refreshIntervalMs = 30000; // Check every 30 seconds
    this.lastTokenCheck = 0;
    this.tokenCheckDebounce = 5000; // Minimum 5 seconds between checks
    this._sendingMessage = false; // Flag to prevent recursion in message sending
    
    // Initialize token extraction
    this.extractToken();
    this.startPeriodicRefresh();
    
    console.log('🔐 CSRF Parser initialized');
  }

  /**
   * Extract CSRF token from various sources
   * Priority: Cookie > Form Fields > Meta Tags
   */
  extractToken() {
    let token = null;
    const extractionMethods = [
      () => this.getTokenFromCookie(),
      () => this.getTokenFromForm(),
      () => this.getTokenFromMeta()
    ];

    for (const method of extractionMethods) {
      try {
        token = method();
        if (token) {
          console.log('✅ CSRF token extracted via:', method.name);
          break;
        }
      } catch (error) {
        console.warn(`⚠️ Failed to extract token via ${method.name}:`, error);
      }
    }

    if (token && token !== this.currentToken) {
      const oldToken = this.currentToken;
      this.currentToken = token;
      console.log('🔄 CSRF token updated:', {
        old: oldToken ? `${oldToken.substring(0, 8)}...` : null,
        new: `${token.substring(0, 8)}...`
      });
      this.notifyTokenChange(token, oldToken);
    }

    return token;
  }

  /**
   * Extract token from cookies (most reliable for Chaturbate)
   */
  getTokenFromCookie() {
    const cookies = document.cookie.split('; ');
    for (const cookie of cookies) {
      if (cookie.startsWith('csrftoken=')) {
        const token = cookie.split('=')[1];
        if (token && token.length > 10) { // Basic validation
          return token;
        }
      }
    }
    return null;
  }

  /**
   * Extract token from form fields (backup method)
   */
  getTokenFromForm() {
    const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
    if (csrfInput && csrfInput.value) {
      return csrfInput.value;
    }
    return null;
  }

  /**
   * Extract token from meta tags (rare but possible)
   */
  getTokenFromMeta() {
    const metaTag = document.querySelector('meta[name="csrf-token"]');
    if (metaTag && metaTag.content) {
      return metaTag.content;
    }
    return null;
  }

  /**
   * Get current token (with automatic refresh if stale)
   */
  getCurrentToken(forceRefresh = false) {
    const now = Date.now();
    const timeSinceLastCheck = now - this.lastTokenCheck;
    
    // Refresh if forced, no current token, or been too long since last check
    if (forceRefresh || !this.currentToken || timeSinceLastCheck > this.tokenCheckDebounce) {
      this.lastTokenCheck = now;
      this.extractToken();
    }
    
    return this.currentToken;
  }

  /**
   * Register callback for token changes
   */
  onTokenChange(callback) {
    if (typeof callback === 'function') {
      this.tokenChangeCallbacks.push(callback);
    }
  }

  /**
   * Notify all callbacks of token change
   */
  notifyTokenChange(newToken, oldToken) {
    this.tokenChangeCallbacks.forEach(callback => {
      try {
        callback(newToken, oldToken);
      } catch (error) {
        console.error('❌ Error in token change callback:', error);
      }
    });
  }

  /**
   * Start periodic token refresh
   */
  startPeriodicRefresh() {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
    }

    this.refreshInterval = setInterval(() => {
      const oldToken = this.currentToken;
      this.extractToken();
      
      // Log periodic check (only if token changed)
      if (this.currentToken !== oldToken) {
        console.log('🔄 Periodic CSRF token refresh completed');
      }
    }, this.refreshIntervalMs);

    console.log(`⏰ Periodic CSRF refresh started (${this.refreshIntervalMs}ms interval)`);
  }

  /**
   * Stop periodic refresh
   */
  stopPeriodicRefresh() {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
      this.refreshInterval = null;
      console.log('⏸️ Periodic CSRF refresh stopped');
    }
  }

  /**
   * Make authenticated request to Chaturbate API
   */
  async makeAuthenticatedRequest(url, options = {}) {
    const token = this.getCurrentToken();
    
    if (!token) {
      throw new Error('No CSRF token available');
    }

    // Prepare headers
    const headers = {
      'X-CSRFToken': token,
      'Content-Type': 'application/x-www-form-urlencoded',
      ...options.headers
    };

    // Handle different body types
    let body = options.body;
    if (options.method === 'POST') {
      if (body instanceof FormData) {
        // Add CSRF token to FormData
        body.append('csrfmiddlewaretoken', token);
        // Remove Content-Type to let browser set it with boundary
        delete headers['Content-Type'];
      } else if (typeof body === 'string') {
        // Add CSRF token to URL-encoded string
        body += (body ? '&' : '') + `csrfmiddlewaretoken=${encodeURIComponent(token)}`;
      } else if (body && typeof body === 'object') {
        // Convert object to URL-encoded string with CSRF token
        const params = new URLSearchParams(body);
        params.append('csrfmiddlewaretoken', token);
        body = params.toString();
      } else if (!body) {
        // No body, just send CSRF token
        body = `csrfmiddlewaretoken=${encodeURIComponent(token)}`;
      }
    }

    console.log('🌐 Making authenticated request:', {
      url,
      method: options.method || 'GET',
      hasToken: !!token,
      tokenPreview: token ? `${token.substring(0, 8)}...` : null
    });

    try {
      const response = await fetch(url, {
        ...options,
        headers,
        body
      });

      // Check for CSRF-related errors
      if (response.status === 403) {
        const responseText = await response.text();
        if (responseText.includes('CSRF') || responseText.includes('Forbidden')) {
          console.warn('🚫 CSRF token may be invalid, forcing refresh');
          this.extractToken(); // Force refresh token
          throw new Error('CSRF token validation failed');
        }
      }

      return response;
    } catch (error) {
      console.error('❌ Authenticated request failed:', error);
      throw error;
    }
  }

  /**
   * Convenience method for common Chaturbate API endpoints
   */
  async callChaturbateAPI(endpoint, data = {}, method = 'POST') {
    const baseUrl = window.location.origin;
    const fullUrl = `${baseUrl}${endpoint}`;
    
    return await this.makeAuthenticatedRequest(fullUrl, {
      method,
      body: data
    });
  }

  /**
   * Get broadcast status (example API call)
   */
  async getBroadcastStatus() {
    try {
      const response = await this.callChaturbateAPI('/api/get_my_broadcast_status/');
      if (response.ok) {
        return await response.json();
      } else {
        throw new Error(`API call failed: ${response.status} ${response.statusText}`);
      }
    } catch (error) {
      console.error('❌ Failed to get broadcast status:', error);
      throw error;
    }
  }

  /**
   * Get room list (example API call)
   */
  async getRoomList(params = {}) {
    try {
      const response = await this.callChaturbateAPI('/api/get_room_list/', params);
      if (response.ok) {
        return await response.json();
      } else {
        throw new Error(`API call failed: ${response.status} ${response.statusText}`);
      }
    } catch (error) {
      console.error('❌ Failed to get room list:', error);
      throw error;
    }
  }

  /**
   * Send private message (example API call)
   */
  async sendPrivateMessage(username, message) {
    try {
      const response = await this.callChaturbateAPI('/api/send_private_message/', {
        username,
        message
      });
      if (response.ok) {
        return await response.json();
      } else {
        throw new Error(`API call failed: ${response.status} ${response.statusText}`);
      }
    } catch (error) {
      console.error('❌ Failed to send private message:', error);
      throw error;
    }
  }

  /**
   * Publish chat message to live room (based on your example)
   */
  async publishChatMessage(room, message, username) {
    try {
      const formData = new FormData();
      formData.append('room', room);
      formData.append('message', JSON.stringify({"m": message}));
      formData.append('username', username);
      
      // CSRF token will be added automatically by makeAuthenticatedRequest
      const response = await this.makeAuthenticatedRequest('/push_service/publish_chat_message_live/', {
        method: 'POST',
        body: formData,
        headers: {
          // Don't set Content-Type - let browser set it with boundary for FormData
          'X-Requested-With': 'XMLHttpRequest'
        }
      });

      if (response.ok) {
        const data = await response.json();
        console.log('✅ Chat message published:', data);
        return data;
      } else {
        throw new Error(`API call failed: ${response.status} ${response.statusText}`);
      }
    } catch (error) {
      console.error('❌ Failed to publish chat message:', error);
      throw error;
    }
  }

  /**
   * Send message with auto-detected room and username
   */
  async sendChatMessage(message) {
    // Prevent multiple simultaneous messages
    if (this._sendingMessage) {
      console.warn('⚠️ Already sending a message, ignoring duplicate request');
      throw new Error('Already sending a message');
    }
    
    this._sendingMessage = true;
    try {
      console.log('🚀 Sending chat message:', message);
      
      // Try to detect current room and username from page
      const room = this.extractRoomFromURL();
      const username = this.extractUsernameFromPage();
      
      if (!room || !username) {
        throw new Error('Could not detect room or username from current page');
      }

      const result = await this.publishChatMessage(room, message, username);
      console.log('✅ Chat message sent successfully:', result);
      return result;
    } catch (error) {
      console.error('❌ Failed to send chat message:', error);
      throw error;
    } finally {
      // Reset flag after a delay
      setTimeout(() => {
        this._sendingMessage = false;
      }, 1000);
    }
  }

  /**
   * Extract room name from current URL
   */
  extractRoomFromURL() {
    const path = window.location.pathname;
    // Match patterns like /room_name/ or /b/room_name/
    const roomMatch = path.match(/\/(?:b\/)?([^\/]+)\/?$/);
    return roomMatch ? roomMatch[1] : null;
  }

  /**
   * Extract username from page elements
   */
  extractUsernameFromPage() {
    // Try multiple selectors that might contain the username
    const selectors = [
      '.username',
      '[data-username]',
      '.user-name',
      '#username'
    ];

    for (const selector of selectors) {
      const element = document.querySelector(selector);
      if (element) {
        return element.textContent?.trim() || element.getAttribute('data-username');
      }
    }

    // Fallback: try to extract from URL or other page indicators
    return this.extractRoomFromURL(); // Often room name = username for broadcasters
  }

  /**
   * Get token validation status
   */
  isTokenValid() {
    const token = this.getCurrentToken();
    return token && token.length > 10; // Basic validation
  }

  /**
   * Get token info for debugging
   */
  getTokenInfo() {
    const token = this.getCurrentToken();
    return {
      hasToken: !!token,
      tokenLength: token ? token.length : 0,
      tokenPreview: token ? `${token.substring(0, 8)}...${token.substring(-4)}` : null,
      lastRefresh: new Date(this.lastTokenCheck).toISOString(),
      refreshInterval: this.refreshIntervalMs,
      isRefreshActive: !!this.refreshInterval
    };
  }

  /**
   * Cleanup - stop all timers and clear callbacks
   */
  destroy() {
    this.stopPeriodicRefresh();
    this.tokenChangeCallbacks = [];
    this.currentToken = null;
    console.log('🧹 CSRF Parser destroyed');
  }
}

// Create global instance
window.csrfParser = new CSRFParser();

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
  module.exports = CSRFParser;
}

console.log('🔐 CSRF Parser loaded and ready');