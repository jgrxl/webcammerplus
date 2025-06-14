// Auth0 Service for Sider AI Clone
class Auth0Service {
  constructor() {
    this.auth0Client = null;
    this.isAuthenticated = false;
    this.user = null;
    
    // Auth0 configuration
    this.config = {
      domain: 'dev-4xh5xi1xfh7w7y2n.us.auth0.com',
      clientId: '57sIYSODLSDddlyQVokooAFjTEHDNRYo',
      redirectUri: window.location.origin
    };
    
    this.init();
  }
  
  async init() {
    try {
      // Initialize Auth0 client
      this.auth0Client = await auth0.createAuth0Client({
        domain: this.config.domain,
        clientId: this.config.clientId,
        authorizationParams: {
          redirect_uri: this.config.redirectUri
        }
      });
      
      // Check if user is authenticated
      this.isAuthenticated = await this.auth0Client.isAuthenticated();
      
      if (this.isAuthenticated) {
        this.user = await this.auth0Client.getUser();
      }
      
      // Handle redirect callback
      if (window.location.search.includes("code=")) {
        await this.handleRedirectCallback();
      }
      
    } catch (error) {
      console.error('Auth0 initialization error:', error);
    }
  }
  
  async login() {
    try {
      await this.auth0Client.loginWithRedirect();
    } catch (error) {
      console.error('Login error:', error);
    }
  }
  
  async logout() {
    try {
      await this.auth0Client.logout({
        logoutParams: {
          returnTo: window.location.origin
        }
      });
    } catch (error) {
      console.error('Logout error:', error);
    }
  }
  
  async handleRedirectCallback() {
    try {
      await this.auth0Client.handleRedirectCallback();
      this.isAuthenticated = await this.auth0Client.isAuthenticated();
      
      if (this.isAuthenticated) {
        this.user = await this.auth0Client.getUser();
      }
      
      // Remove code from URL
      window.history.replaceState({}, document.title, window.location.pathname);
      
    } catch (error) {
      console.error('Redirect callback error:', error);
    }
  }
  
  async getUser() {
    if (this.isAuthenticated && this.auth0Client) {
      return await this.auth0Client.getUser();
    }
    return null;
  }
  
  async getToken() {
    if (this.isAuthenticated && this.auth0Client) {
      try {
        return await this.auth0Client.getTokenSilently();
      } catch (error) {
        console.error('Token error:', error);
        return null;
      }
    }
    return null;
  }
}

// Export for use in other files
window.Auth0Service = Auth0Service;