// WebCammer+ API service - calls local Flask backend instead of Novita directly
// This provides better security, validation, and consistent responses

class WebCammerAPI {
  constructor() {
    // Use regular environment variable access or default
    this.baseURL = window.location.origin.includes('localhost') ? 'http://localhost:5000' : window.location.origin;
    this.apiPrefix = '/api/v1';
  }

  async getAuthToken() {
    try {
      // Try to get token from Auth0 service first
      if (window.getAuth0Service) {
        const auth0Service = await window.getAuth0Service();
        const token = await auth0Service.getToken();
        if (token) {
          return token;
        }
      }
      
      // Fallback to localStorage
      return localStorage.getItem('auth_token') || '';
    } catch (error) {
      console.error('Failed to get auth token:', error);
      return localStorage.getItem('auth_token') || '';
    }
  }

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

  // Health check to verify backend is running
  async healthCheck() {
    try {
      const response = await fetch(`${this.baseURL}/`);
      const data = await response.json();
      return data.status === 'ok';
    } catch (error) {
      console.error('Health check failed:', error);
      return false;
    }
  }

  // Translate text using backend API
  async translate(text, toLang, fromLang = null) {
    if (!text || typeof text !== 'string') {
      throw new Error('Text must be a non-empty string');
    }
    if (!toLang || typeof toLang !== 'string') {
      throw new Error('Target language must be specified');
    }

    const url = `${this.baseURL}${this.apiPrefix}/translate/`;
    const requestBody = {
      text: text,
      to_lang: toLang,
      ...(fromLang && { from_lang: fromLang })
    };

    console.log('🔍 Translation Request:', requestBody);

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: await this.getAuthHeaders(),
        body: JSON.stringify(requestBody)
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(`Translation failed: ${response.status} - ${errorData.error || response.statusText}`);
      }

      const data = await response.json();
      console.log('✅ Translation Response:', data);
      
      if (data.success && data.translation) {
        return data.translation;
      } else {
        throw new Error(data.error || 'Translation failed');
      }

    } catch (error) {
      if (error.name === 'TypeError' && error.message.includes('fetch')) {
        throw new Error('Network error - please check if the backend is running');
      }
      throw error;
    }
  }

  // Generate reply using backend API
  async generateReply(originalText, responseIdea, style, toLang) {
    if (!originalText || typeof originalText !== 'string') {
      throw new Error('Original text must be a non-empty string');
    }
    if (!responseIdea || typeof responseIdea !== 'string') {
      throw new Error('Response idea must be specified');
    }
    if (!style || typeof style !== 'string') {
      throw new Error('Style must be specified');
    }
    if (!toLang || typeof toLang !== 'string') {
      throw new Error('Target language must be specified');
    }

    const url = `${this.baseURL}${this.apiPrefix}/reply/`;
    const requestBody = {
      original_text: originalText,
      response_idea: responseIdea,
      style: style,
      to_lang: toLang
    };

    console.log('🔍 Reply Request:', requestBody);

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: await this.getAuthHeaders(),
        body: JSON.stringify(requestBody)
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(`Reply generation failed: ${response.status} - ${errorData.error || response.statusText}`);
      }

      const data = await response.json();
      console.log('✅ Reply Response:', data);
      
      if (data.success && data.reply) {
        return data.reply;
      } else {
        throw new Error(data.error || 'Reply generation failed');
      }

    } catch (error) {
      if (error.name === 'TypeError' && error.message.includes('fetch')) {
        throw new Error('Network error - please check if the backend is running');
      }
      throw error;
    }
  }

  // Generate written content using backend API
  async write(style, text, toLang) {
    if (!style || typeof style !== 'string') {
      throw new Error('Style must be specified');
    }
    if (!text || typeof text !== 'string') {
      throw new Error('Text/topic must be a non-empty string');
    }
    if (!toLang || typeof toLang !== 'string') {
      throw new Error('Target language must be specified');
    }

    const url = `${this.baseURL}${this.apiPrefix}/write/`;
    const requestBody = {
      style: style,
      text: text,
      to_lang: toLang
    };

    console.log('🔍 Write Request:', requestBody);

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: await this.getAuthHeaders(),
        body: JSON.stringify(requestBody)
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(`Writing failed: ${response.status} - ${errorData.error || response.statusText}`);
      }

      const data = await response.json();
      console.log('✅ Write Response:', data);
      
      if (data.success && data.written_text) {
        return data.written_text;
      } else {
        throw new Error(data.error || 'Writing failed');
      }

    } catch (error) {
      if (error.name === 'TypeError' && error.message.includes('fetch')) {
        throw new Error('Network error - please check if the backend is running');
      }
      throw error;
    }
  }

  // Legacy chat method - now uses write API for general text generation
  async chat(message, style = 'conversational', language = 'en') {
    if (!message || typeof message !== 'string') {
      throw new Error('Message must be a non-empty string');
    }

    console.log('🔄 Converting chat to write API call');
    return await this.write(style, message, language);
  }

  // Test if API is working
  async test() {
    try {
      const isHealthy = await this.healthCheck();
      if (!isHealthy) {
        return false;
      }

      // Test with a simple translation
      const testResult = await this.translate('Hello', 'es');
      return testResult && testResult.length > 0;
    } catch (error) {
      console.error('API test failed:', error);
      return false;
    }
  }

  // Get InfluxDB analytics data
  async getInfluxData(endpoint, requestData = {}) {
    const url = `${this.baseURL}${this.apiPrefix}/influx/${endpoint}`;
    
    console.log(`🔍 InfluxDB ${endpoint} Request:`, requestData);

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: await this.getAuthHeaders(),
        body: JSON.stringify(requestData)
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(`InfluxDB request failed: ${response.status} - ${errorData.error || response.statusText}`);
      }

      const data = await response.json();
      console.log(`✅ InfluxDB ${endpoint} Response:`, data);
      return data;

    } catch (error) {
      if (error.name === 'TypeError' && error.message.includes('fetch')) {
        throw new Error('Network error - please check if the backend is running');
      }
      throw error;
    }
  }

  // Convenience methods for InfluxDB endpoints
  async getTips(days = 7) {
    return await this.getInfluxData('tips', { days });
  }

  async getTopChatters(days = 7, limit = 10) {
    return await this.getInfluxData('chatters', { days, limit });
  }

  async searchInflux(searchParams) {
    return await this.getInfluxData('search', searchParams);
  }
}

// Export for use in popup (maintain backward compatibility)
window.NovitaAPI = WebCammerAPI;
window.WebCammerAPI = WebCammerAPI;