// Test setup file
// Mock browser APIs that might not be available in jsdom

// Mock WebSocket
global.WebSocket = class WebSocket {
  constructor(url) {
    this.url = url;
    this.readyState = 0;
    setTimeout(() => {
      this.readyState = 1;
      if (this.onopen) this.onopen();
    }, 100);
  }
  
  send(data) {
    // Mock send
  }
  
  close() {
    this.readyState = 3;
    if (this.onclose) this.onclose();
  }
};

// Mock Auth0 service
global.window.getAuth0Service = jest.fn().mockResolvedValue({
  getToken: jest.fn().mockResolvedValue('mock-auth0-token')
});