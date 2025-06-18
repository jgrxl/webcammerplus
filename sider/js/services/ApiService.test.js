// ApiService.test.js
import { ApiService } from './ApiService.js';

// Mock fetch
global.fetch = jest.fn();

describe('ApiService', () => {
  let apiService;

  beforeEach(() => {
    apiService = new ApiService();
    fetch.mockClear();
    localStorage.clear();
  });

  describe('getAuthToken', () => {
    it('should get token from Auth0 service if available', async () => {
      const mockToken = 'auth0-token-123';
      window.getAuth0Service = jest.fn().mockResolvedValue({
        getToken: jest.fn().mockResolvedValue(mockToken)
      });

      const token = await apiService.getAuthToken();
      
      expect(token).toBe(mockToken);
    });

    it('should fallback to localStorage if Auth0 not available', async () => {
      const mockToken = 'local-token-456';
      window.getAuth0Service = undefined;
      localStorage.setItem('auth_token', mockToken);

      const token = await apiService.getAuthToken();
      
      expect(token).toBe(mockToken);
    });
  });

  describe('fetchWithTimeout', () => {
    it('should fetch successfully with JSON response', async () => {
      const mockData = { success: true, data: 'test' };
      fetch.mockResolvedValueOnce({
        ok: true,
        headers: new Map([['content-type', 'application/json']]),
        json: async () => mockData
      });

      const result = await apiService.fetchWithTimeout('http://test.com/api');
      
      expect(result).toEqual(mockData);
      expect(fetch).toHaveBeenCalledWith('http://test.com/api', expect.any(Object));
    });

    it('should throw error on non-OK response', async () => {
      fetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        headers: new Map()
      });

      await expect(apiService.fetchWithTimeout('http://test.com/api'))
        .rejects.toThrow('HTTP 404: Not Found');
    });

    it('should handle timeout', async () => {
      fetch.mockImplementationOnce(() => 
        new Promise((resolve) => setTimeout(resolve, 10000))
      );

      await expect(apiService.fetchWithTimeout('http://test.com/api', {}, 100))
        .rejects.toThrow('Request timeout');
    });
  });

  describe('getTippers', () => {
    it('should fetch tippers with correct parameters', async () => {
      const mockTippers = { success: true, tippers: [{ username: 'user1', total_tokens: 100 }] };
      const mockToken = 'test-token';
      
      apiService.getAuthToken = jest.fn().mockResolvedValue(mockToken);
      fetch.mockResolvedValueOnce({
        ok: true,
        headers: new Map([['content-type', 'application/json']]),
        json: async () => mockTippers
      });

      const result = await apiService.getTippers(7, 10);
      
      expect(result).toEqual(mockTippers);
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/influx/tippers'),
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Authorization': `Bearer ${mockToken}`,
            'Content-Type': 'application/json'
          }),
          body: JSON.stringify({ days: 7, limit: 10 })
        })
      );
    });

    it('should return empty tippers on error', async () => {
      apiService.getAuthToken = jest.fn().mockResolvedValue('token');
      fetch.mockRejectedValueOnce(new Error('Network error'));

      const result = await apiService.getTippers(7, 10);
      
      expect(result).toEqual({ success: false, tippers: [] });
    });
  });
});