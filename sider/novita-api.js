// Simple Novita AI API service - following engineering principles
// Start with simplest solution that works

class NovitaAPI {
  constructor() {
    this.apiKey = 'sk_Z2EJOtHGNf5Nv2tgSoouT6PZzbXoY3UoLjpn5C5cYkE';
    this.baseURL = 'https://api.novita.ai';
    this.isConfigured = true;
  }
  

  // Initialize with API key (optional - key already set)
  init(apiKey) {
    if (apiKey && typeof apiKey === 'string') {
      this.apiKey = apiKey;
      this.isConfigured = true;
    }
  }

  // Simple chat completion - single responsibility
  async chat(message) {
    if (!this.isConfigured) {
      throw new Error('Novita API not configured. Call init() first.');
    }

    if (!message || typeof message !== 'string') {
      throw new Error('Message must be a non-empty string');
    }

    console.log(`${this.baseURL}/v3/openai/chat/completions`);

    const url = `${this.baseURL}/v3/openai/chat/completions`;
    const requestBody = {
      model: 'qwen/qwen3-4b-fp8', // Start with basic model
      messages: [
        {
          role: 'user',
          content: message
        }
      ],
      max_tokens: 150, // Keep responses concise
      temperature: 0.7
    };

    // Log the full request details
    console.log('🔍 Novita API Request Details:');
    console.log('URL:', url);
    console.log('Method: POST');
    console.log('Headers:', {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${this.apiKey.substring(0, 10)}...`
    });
    console.log('Request Body:', requestBody);

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.apiKey}`
        },
        body: JSON.stringify(requestBody)
      });

      console.log('📥 API Response Status:', response.status, response.statusText);
      console.log('📥 API Response Headers:', Object.fromEntries(response.headers));

      if (!response.ok) {
        // Read response body once and handle both JSON and text
        let errorDetails = '';
        try {
          const responseText = await response.text();
          console.log('❌ API Error Response Text:', responseText);
          
          // Try to parse as JSON first
          try {
            const errorData = JSON.parse(responseText);
            console.log('❌ API Error Response JSON:', errorData);
            errorDetails = errorData.error?.message || JSON.stringify(errorData);
          } catch (jsonError) {
            // If not JSON, use the text directly
            errorDetails = responseText;
          }
        } catch (e) {
          errorDetails = 'Unable to read error response';
        }
        throw new Error(`API request failed: ${response.status} ${response.statusText} - ${errorDetails}`);
      }

      const data = await response.json();
      console.log('✅ API Success Response:', data);
      
      // Extract response text - fail gracefully
      if (data.choices && data.choices[0] && data.choices[0].message) {
        return data.choices[0].message.content.trim();
      } else {
        console.log('❌ Unexpected response format:', data);
        throw new Error('Unexpected API response format');
      }

    } catch (error) {
      // Human-friendly error messages
      if (error.name === 'TypeError' && error.message.includes('fetch')) {
        throw new Error('Network error - please check your connection');
      }
      throw error; // Re-throw with original message for debugging
    }
  }

  // Test if API is working - practical value
  async test() {
    try {
      const response = await this.chat('Hello, please respond with "API working"');
      return response.toLowerCase().includes('api working') || response.length > 0;
    } catch (error) {
      return false;
    }
  }
}

// Export for use in popup
window.NovitaAPI = NovitaAPI;