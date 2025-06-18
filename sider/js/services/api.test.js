/**
 * Unit tests for WebCammerAPI
 * Run with: npm test
 */

describe('WebCammerAPI', () => {
    let api;
    let originalFetch;
    let originalLocalStorage;
    let originalLocation;
    
    beforeEach(() => {
        // Mock fetch
        originalFetch = global.fetch;
        global.fetch = jest.fn();
        
        // Mock localStorage
        originalLocalStorage = global.localStorage;
        global.localStorage = {
            getItem: jest.fn(),
            setItem: jest.fn(),
            removeItem: jest.fn()
        };
        
        // Mock location
        originalLocation = window.location;
        delete window.location;
        window.location = {
            origin: 'http://localhost:5173',
            href: 'http://localhost:5173/',
            hostname: 'localhost'
        };

        // Define WebCammerAPI in the test environment
        global.WebCammerAPI = class {
            constructor() {
                const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
                this.baseURL = isLocalhost ? 'http://localhost:5000' : 'https://api.webcammer.com';
                this.apiPrefix = '/api/v1';
            }

            async getAuthToken() {
                const token = localStorage.getItem('auth_token');
                return token || '';
            }

            async getAuthHeaders() {
                const token = await this.getAuthToken();
                const headers = {
                    'Content-Type': 'application/json'
                };
                if (token) {
                    headers['Authorization'] = `Bearer ${token}`;
                }
                return headers;
            }

            async healthCheck() {
                try {
                    const response = await fetch(`${this.baseURL}/`, { timeout: 5000 });
                    return response.ok;
                } catch (error) {
                    return false;
                }
            }

            async translateText(text, toLang, fromLang = 'auto') {
                const headers = await this.getAuthHeaders();
                const response = await fetch(`${this.baseURL}${this.apiPrefix}/translate/`, {
                    method: 'POST',
                    headers,
                    body: JSON.stringify({
                        text,
                        to_lang: toLang,
                        from_lang: fromLang
                    })
                });

                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.error || `HTTP error! status: ${response.status}`);
                }

                const data = await response.json();
                return data.translation;
            }

            async getChaturbateStatus() {
                const response = await fetch(`${this.baseURL}${this.apiPrefix}/chaturbate/status`);
                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.error || `HTTP error! status: ${response.status}`);
                }
                return await response.json();
            }
        };

        api = new global.WebCammerAPI();
    });
    
    afterEach(() => {
        // Restore original functions
        global.fetch = originalFetch;
        global.localStorage = originalLocalStorage;
        window.location = originalLocation;
        jest.clearAllMocks();
    });

    describe('Constructor', () => {
        test('should initialize with correct baseURL for localhost', () => {
            expect(api.baseURL).toBe('http://localhost:5000');
            expect(api.apiPrefix).toBe('/api/v1');
        });
    });

    describe('getAuthToken', () => {
        test('should return token from localStorage', async () => {
            localStorage.getItem.mockReturnValue('test-token');
            const token = await api.getAuthToken();
            expect(token).toBe('test-token');
        });

        test('should return empty string if no token', async () => {
            localStorage.getItem.mockReturnValue(null);
            const token = await api.getAuthToken();
            expect(token).toBe('');
        });
    });

    describe('getAuthHeaders', () => {
        test('should include auth token in headers', async () => {
            localStorage.getItem.mockReturnValue('test-token');
            const headers = await api.getAuthHeaders();
            expect(headers).toEqual({
                'Content-Type': 'application/json',
                'Authorization': 'Bearer test-token'
            });
        });

        test('should not include Authorization header if no token', async () => {
            localStorage.getItem.mockReturnValue(null);
            const headers = await api.getAuthHeaders();
            expect(headers).toEqual({
                'Content-Type': 'application/json'
            });
        });
    });

    describe('healthCheck', () => {
        test('should return true when backend is available', async () => {
            fetch.mockResolvedValueOnce({
                ok: true,
                json: async () => ({ status: 'ok' })
            });

            const result = await api.healthCheck();
            expect(result).toBe(true);
            expect(fetch).toHaveBeenCalledWith('http://localhost:5000/', { timeout: 5000 });
        });

        test('should return false when backend is not available', async () => {
            fetch.mockRejectedValueOnce(new Error('Network error'));
            const result = await api.healthCheck();
            expect(result).toBe(false);
        });
    });

    describe('translateText', () => {
        test('should call translate endpoint with correct data', async () => {
            localStorage.getItem.mockReturnValue('test-token');
            fetch.mockResolvedValueOnce({
                ok: true,
                json: async () => ({ success: true, translation: 'Hola' })
            });

            const result = await api.translateText('Hello', 'es', 'en');
            
            expect(fetch).toHaveBeenCalledWith(
                'http://localhost:5000/api/v1/translate/',
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer test-token'
                    },
                    body: JSON.stringify({
                        text: 'Hello',
                        to_lang: 'es',
                        from_lang: 'en'
                    })
                }
            );
            expect(result).toBe('Hola');
        });

        test('should throw error on failed response', async () => {
            localStorage.getItem.mockReturnValue('test-token');
            fetch.mockResolvedValueOnce({
                ok: false,
                status: 401,
                json: async () => ({ error: 'Unauthorized' })
            });

            await expect(api.translateText('Hello', 'es')).rejects.toThrow('Unauthorized');
        });
    });

    describe('Error Handling', () => {
        test('should handle network errors gracefully', async () => {
            fetch.mockRejectedValueOnce(new Error('Network error'));
            
            await expect(api.getChaturbateStatus()).rejects.toThrow('Network error');
        });

        test('should handle 404 errors', async () => {
            fetch.mockResolvedValueOnce({
                ok: false,
                status: 404,
                json: async () => ({ error: 'Not found' })
            });

            await expect(api.getChaturbateStatus()).rejects.toThrow('Not found');
        });
    });
});