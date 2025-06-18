// Authentication Module
class AuthModule {
  constructor() {
    this.isAuthenticated = false;
    this.user = null;
    this.checkingAuth = false;
    this.authCheckInterval = null;
  }

  async checkAuthStatus() {
    if (this.checkingAuth) return { isAuthenticated: this.isAuthenticated, user: this.user };
    
    this.checkingAuth = true;
    
    try {
      const auth0Service = await window.getAuth0Service();
      this.isAuthenticated = auth0Service.isAuthenticated;
      this.user = auth0Service.user;
      
      if (this.isAuthenticated) {
        await auth0Service.getToken();
        if (this.user && !this.user.credits) {
          this.user.credits = 40;
        }
      }
      
      return { isAuthenticated: this.isAuthenticated, user: this.user };
    } catch (error) {
      console.error('Auth status check failed:', error);
      this.isAuthenticated = false;
      this.user = null;
      return { isAuthenticated: false, user: null };
    } finally {
      this.checkingAuth = false;
    }
  }

  async login() {
    try {
      const auth0Service = await window.getAuth0Service();
      await auth0Service.login();
      return true;
    } catch (error) {
      console.error('Login failed:', error);
      return false;
    }
  }

  async logout() {
    try {
      const auth0Service = await window.getAuth0Service();
      await auth0Service.logout();
      this.isAuthenticated = false;
      this.user = null;
      return true;
    } catch (error) {
      console.error('Logout failed:', error);
      return false;
    }
  }

  async handlePostLogin() {
    const justLoggedIn = sessionStorage.getItem('auth0_just_logged_in') === 'true';
    if (justLoggedIn) {
      console.log('Just logged in, refreshing UI components...');
      sessionStorage.removeItem('auth0_just_logged_in');
      
      if (window.userMenu) {
        await window.userMenu.refresh();
      }
      
      return true;
    }
    return false;
  }

  startPeriodicAuthCheck(callback, interval = 60000) {
    this.stopPeriodicAuthCheck();
    this.authCheckInterval = setInterval(async () => {
      const authState = await this.checkAuthStatus();
      if (callback) callback(authState);
    }, interval);
  }

  stopPeriodicAuthCheck() {
    if (this.authCheckInterval) {
      clearInterval(this.authCheckInterval);
      this.authCheckInterval = null;
    }
  }

  getAuthState() {
    return {
      isAuthenticated: this.isAuthenticated,
      user: this.user
    };
  }
}

// Export as singleton
window.authModule = new AuthModule();