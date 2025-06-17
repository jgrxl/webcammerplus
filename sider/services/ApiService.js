// API Service for handling all backend API calls
class ApiService {
  constructor() {
    this.baseURL = window.location.origin.includes('localhost') ? 'http://localhost:5000' : window.location.origin;
    this.apiPrefix = '/api/v1';
    this.defaultTimeout = 5000;
  }

  // Get auth token
  async getAuthToken() {
    try {
      if (window.getAuth0Service) {
        const auth0Service = await window.getAuth0Service();
        const token = await auth0Service.getToken();
        if (token) return token;
      }
      return localStorage.getItem('auth_token') || '';
    } catch (error) {
      console.error('Failed to get auth token:', error);
      return localStorage.getItem('auth_token') || '';
    }
  }

  // Get auth headers
  async getAuthHeaders() {
    const headers = {
      'Content-Type': 'application/json'
    };
    
    const authToken = await this.getAuthToken();
    if (authToken) {
      headers['Authorization'] = `Bearer ${authToken}`;
    }
    
    return headers;
  }

  // Generic fetch with timeout and error handling
  async fetchWithTimeout(url, options = {}, timeout = this.defaultTimeout) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      // Check if response is JSON
      const contentType = response.headers.get('content-type');
      const isJson = contentType && contentType.includes('application/json');

      if (!response.ok) {
        if (response.status === 401) {
          console.log('Unauthorized - authentication required');
        } else if (response.status === 500) {
          console.warn('Server error - check authentication');
        }
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      if (isJson) {
        return await response.json();
      } else {
        throw new Error('Server returned non-JSON response');
      }
    } catch (error) {
      clearTimeout(timeoutId);
      
      if (error.name === 'AbortError') {
        throw new Error('Request timeout');
      }
      throw error;
    }
  }

  // Health check
  async checkHealth() {
    try {
      const response = await this.fetchWithTimeout(`${this.baseURL}/`, {}, 3000);
      return response.status === 'ok';
    } catch (error) {
      console.warn('Health check failed:', error.message);
      return false;
    }
  }

  // Inbox API calls
  async getInboxStats() {
    try {
      const headers = await this.getAuthHeaders();
      return await this.fetchWithTimeout(
        `${this.baseURL}${this.apiPrefix}/inbox/stats`,
        { headers }
      );
    } catch (error) {
      console.warn('Failed to fetch inbox stats:', error.message);
      return { total_messages: 0, unread_messages: 0, read_messages: 0 };
    }
  }

  async getConversations() {
    try {
      const headers = await this.getAuthHeaders();
      return await this.fetchWithTimeout(
        `${this.baseURL}${this.apiPrefix}/inbox/conversations`,
        { headers }
      );
    } catch (error) {
      console.warn('Failed to fetch conversations:', error.message);
      return [];
    }
  }

  async getMessages(username) {
    try {
      const headers = await this.getAuthHeaders();
      return await this.fetchWithTimeout(
        `${this.baseURL}${this.apiPrefix}/inbox/conversations/${username}`,
        { headers }
      );
    } catch (error) {
      console.warn('Failed to fetch messages:', error.message);
      return [];
    }
  }

  async markMessageAsRead(messageId) {
    try {
      const headers = await this.getAuthHeaders();
      return await this.fetchWithTimeout(
        `${this.baseURL}${this.apiPrefix}/inbox/messages/${messageId}/read`,
        { method: 'POST', headers }
      );
    } catch (error) {
      console.warn('Failed to mark message as read:', error.message);
      return false;
    }
  }

  // User stats
  async getUserStats(username, days = 30) {
    try {
      const headers = await this.getAuthHeaders();
      return await this.fetchWithTimeout(
        `${this.baseURL}${this.apiPrefix}/user_stats/${username}?days=${days}`,
        { headers }
      );
    } catch (error) {
      console.warn('Failed to fetch user stats:', error.message);
      return null;
    }
  }

  // Analytics/InfluxDB API calls
  async getTippers(days = 1, limit = 10) {
    try {
      const headers = await this.getAuthHeaders();
      return await this.fetchWithTimeout(
        `${this.baseURL}${this.apiPrefix}/influx/tippers`,
        {
          method: 'POST',
          headers,
          body: JSON.stringify({ days, limit })
        }
      );
    } catch (error) {
      console.warn('Failed to fetch tippers:', error.message);
      return { success: false, tippers: [] };
    }
  }

  async getTotalTips(days = 1) {
    try {
      const headers = await this.getAuthHeaders();
      return await this.fetchWithTimeout(
        `${this.baseURL}${this.apiPrefix}/influx/tips`,
        {
          method: 'POST',
          headers,
          body: JSON.stringify({ days })
        }
      );
    } catch (error) {
      console.warn('Failed to fetch total tips:', error.message);
      return { success: false, total_tokens: 0 };
    }
  }

  // Auth/Usage API calls
  async getUsage() {
    try {
      const headers = await this.getAuthHeaders();
      return await this.fetchWithTimeout(
        `${this.baseURL}${this.apiPrefix}/auth/usage`,
        { headers }
      );
    } catch (error) {
      console.warn('Failed to fetch usage:', error.message);
      return null;
    }
  }

  async getSubscriptionStatus() {
    try {
      const headers = await this.getAuthHeaders();
      return await this.fetchWithTimeout(
        `${this.baseURL}${this.apiPrefix}/subscription/status`,
        { headers }
      );
    } catch (error) {
      console.warn('Failed to fetch subscription status:', error.message);
      return null;
    }
  }

  async createBillingPortalSession(returnUrl) {
    try {
      const headers = await this.getAuthHeaders();
      return await this.fetchWithTimeout(
        `${this.baseURL}${this.apiPrefix}/subscription/billing-portal`,
        {
          method: 'POST',
          headers,
          body: JSON.stringify({ return_url: returnUrl })
        }
      );
    } catch (error) {
      console.warn('Failed to create billing portal session:', error.message);
      throw error;
    }
  }
}

// Export as singleton
window.apiService = new ApiService();