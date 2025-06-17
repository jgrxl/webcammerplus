// Auth0 Service for WebCammer+
class Auth0Service {
  constructor() {
    this.auth0Client = null;
    this.isAuthenticated = false;
    this.user = null;
    this.initialized = false;
    this.initPromise = null;
    
    // Auth0 configuration - these should be environment variables in production
    this.config = {
      domain: 'dev-4xh5xi1xfh7w7y2n.us.auth0.com',
      clientId: '57sIYSODLSDddlyQVokooAFjTEHDNRYo',
      redirectUri: window.location.origin,
      audience: 'https://dev-4xh5xi1xfh7w7y2n.us.auth0.com/api/v2/' // Your Auth0 API identifier
    };
  }
  
  async init() {
    if (this.initPromise) {
      return this.initPromise;
    }
    
    this.initPromise = this._doInit();
    return this.initPromise;
  }
  
  async _doInit() {
    try {
      // Prevent multiple initializations
      if (this.initialized) {
        console.log('Auth0 already initialized, skipping...');
        return;
      }
      
      // Check if Auth0 SDK is loaded
      if (typeof auth0 === 'undefined' || !auth0.createAuth0Client) {
        throw new Error('Auth0 SDK not loaded. Make sure to include the Auth0 SPA SDK script.');
      }
      
      console.log('Initializing Auth0 client...');
      
      // Initialize Auth0 client
      this.auth0Client = await auth0.createAuth0Client({
        domain: this.config.domain,
        clientId: this.config.clientId,
        authorizationParams: {
          redirect_uri: this.config.redirectUri,
          audience: this.config.audience,
          scope: 'openid profile email offline_access'
        },
        cacheLocation: 'localstorage',
        useRefreshTokens: true
      });
      
      console.log('Auth0 client initialized successfully');
      
      // Handle redirect callback first - but only if we haven't already processed it
      const isCallbackUrl = window.location.search.includes("code=") && window.location.search.includes("state=");
      const hasProcessedCallback = sessionStorage.getItem('auth0_callback_processed') === 'true';
      
      if (isCallbackUrl && !hasProcessedCallback) {
        console.log('Handling redirect callback...');
        sessionStorage.setItem('auth0_callback_processed', 'true');
        await this.handleRedirectCallback();
      } else if (!isCallbackUrl && hasProcessedCallback) {
        // Clear the flag when we're no longer on a callback URL
        sessionStorage.removeItem('auth0_callback_processed');
      }
      
      // Check if user is authenticated
      this.isAuthenticated = await this.auth0Client.isAuthenticated();
      console.log('Authentication status:', this.isAuthenticated);
      
      if (this.isAuthenticated) {
        this.user = await this.auth0Client.getUser();
        console.log('Authenticated user:', this.user);
      }
      
      this.initialized = true;
      
    } catch (error) {
      console.error('Auth0 initialization error:', error);
      this.initialized = false;
      throw error;
    }
  }
  
  async ensureInitialized() {
    if (!this.initialized) {
      await this.init();
    }
    
    if (!this.auth0Client) {
      throw new Error('Auth0 client not initialized');
    }
  }
  
  async login() {
    try {
      await this.ensureInitialized();
      
      console.log('Starting login flow...');
      await this.auth0Client.loginWithRedirect({
        authorizationParams: {
          redirect_uri: this.config.redirectUri,
          audience: this.config.audience,
          scope: 'openid profile email offline_access'
        }
      });
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  }
  
  async logout() {
    try {
      await this.ensureInitialized();
      
      console.log('Starting logout flow...');
      await this.auth0Client.logout({
        logoutParams: {
          returnTo: window.location.origin
        }
      });
    } catch (error) {
      console.error('Logout error:', error);
      throw error;
    }
  }
  
  async handleRedirectCallback() {
    try {
      if (!this.auth0Client) {
        throw new Error('Auth0 client not initialized');
      }
      
      console.log('Processing redirect callback...');
      const result = await this.auth0Client.handleRedirectCallback();
      
      this.isAuthenticated = await this.auth0Client.isAuthenticated();
      
      if (this.isAuthenticated) {
        this.user = await this.auth0Client.getUser();
        console.log('Login successful, user:', this.user);
      }
      
      // Remove code and state from URL
      const url = new URL(window.location);
      url.searchParams.delete('code');
      url.searchParams.delete('state');
      window.history.replaceState({}, document.title, url.toString());
      
      return result;
      
    } catch (error) {
      console.error('Redirect callback error:', error);
      
      // Remove code and state from URL even on error
      const url = new URL(window.location);
      url.searchParams.delete('code');
      url.searchParams.delete('state');
      window.history.replaceState({}, document.title, url.toString());
      
      throw error;
    }
  }
  
  async getUser() {
    try {
      await this.ensureInitialized();
      
      if (this.isAuthenticated && this.auth0Client) {
        return await this.auth0Client.getUser();
      }
      return null;
    } catch (error) {
      console.error('Get user error:', error);
      return null;
    }
  }
  
  async getToken() {
    try {
      await this.ensureInitialized();
      
      if (this.isAuthenticated && this.auth0Client) {
        const token = await this.auth0Client.getTokenSilently({
          authorizationParams: {
            audience: this.config.audience,
            scope: 'openid profile email offline_access'
          }
        });
        
        // Store token for API calls
        localStorage.setItem('auth_token', token);
        return token;
      }
      return null;
    } catch (error) {
      console.warn('Token refresh failed, but user is still authenticated:', error.message || error);
      
      // Only redirect to login for specific errors, not missing refresh tokens
      if (error.error === 'login_required' || error.error === 'consent_required') {
        console.log('Token refresh failed, redirecting to login...');
        await this.login();
      }
      
      // Return cached token if available
      return localStorage.getItem('auth_token') || null;
    }
  }
  
  async checkSession() {
    try {
      await this.ensureInitialized();
      
      // Try to get token silently to check if session is valid
      await this.getToken();
      
      this.isAuthenticated = await this.auth0Client.isAuthenticated();
      
      if (this.isAuthenticated) {
        this.user = await this.auth0Client.getUser();
      }
      
      return this.isAuthenticated;
    } catch (error) {
      console.error('Session check error:', error);
      this.isAuthenticated = false;
      this.user = null;
      return false;
    }
  }
  
  // Helper method to check if Auth0 SDK is loaded
  static isAuth0SDKLoaded() {
    return typeof auth0 !== 'undefined' && auth0.createAuth0Client;
  }
  
  // Static method to load Auth0 SDK if not already loaded
  static async loadAuth0SDK() {
    if (Auth0Service.isAuth0SDKLoaded()) {
      return Promise.resolve();
    }
    
    return new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = 'https://cdn.auth0.com/js/auth0-spa-js/2.1/auth0-spa-js.production.js';
      script.onload = () => {
        console.log('Auth0 SDK loaded successfully');
        resolve();
      };
      script.onerror = () => {
        console.error('Failed to load Auth0 SDK');
        reject(new Error('Failed to load Auth0 SDK'));
      };
      document.head.appendChild(script);
    });
  }
}

// Global instance
let auth0Service = null;

// Function to get Auth0 service instance
async function getAuth0Service() {
  if (!auth0Service) {
    // Load Auth0 SDK if needed
    await Auth0Service.loadAuth0SDK();
    
    // Create and initialize service
    auth0Service = new Auth0Service();
    await auth0Service.init();
  }
  
  return auth0Service;
}

// Export for use in other files
window.Auth0Service = Auth0Service;
window.getAuth0Service = getAuth0Service;