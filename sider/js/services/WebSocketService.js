// WebSocket Service for Chaturbate Connection
class WebSocketService {
  constructor() {
    this.socket = null;
    this.isConnected = false;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 3;
    this.reconnectDelay = 1000;
    this.eventHandlers = new Map();
    this.serverUrl = `${window.location.protocol}//${window.location.hostname}:5000`;
  }

  // Register event handlers
  on(event, handler) {
    if (!this.eventHandlers.has(event)) {
      this.eventHandlers.set(event, []);
    }
    this.eventHandlers.get(event).push(handler);
  }

  // Remove event handler
  off(event, handler) {
    if (this.eventHandlers.has(event)) {
      const handlers = this.eventHandlers.get(event);
      const index = handlers.indexOf(handler);
      if (index > -1) {
        handlers.splice(index, 1);
      }
    }
  }

  // Emit event to all registered handlers
  emit(event, data) {
    if (this.eventHandlers.has(event)) {
      this.eventHandlers.get(event).forEach(handler => {
        try {
          handler(data);
        } catch (error) {
          console.error(`Error in event handler for ${event}:`, error);
        }
      });
    }
  }

  // Connect to WebSocket
  async connect() {
    return new Promise((resolve, reject) => {
      try {
        if (!window.io) {
          reject(new Error('SocketIO library not loaded'));
          return;
        }

        // Create socket with options
        this.socket = window.io(`${this.serverUrl}/chaturbate`, {
          timeout: 5000,
          reconnection: true,
          reconnectionAttempts: this.maxReconnectAttempts,
          reconnectionDelay: this.reconnectDelay,
          reconnectionDelayMax: 5000
        });

        // Set up connection timeout
        const connectionTimeout = setTimeout(() => {
          if (!this.isConnected) {
            this.disconnect();
            reject(new Error('Connection timeout'));
          }
        }, 10000);

        // Handle connection events
        this.socket.on('connect', () => {
          clearTimeout(connectionTimeout);
          this.isConnected = true;
          this.reconnectAttempts = 0;
          console.log('✅ WebSocket connected');
          this.emit('connected');
          resolve();
        });

        this.socket.on('disconnect', () => {
          clearTimeout(connectionTimeout);
          this.isConnected = false;
          console.log('❌ WebSocket disconnected');
          this.emit('disconnected');
        });

        this.socket.on('connect_error', (error) => {
          console.error('WebSocket connection error:', error);
          this.emit('error', error);
        });

        // Handle Chaturbate events
        this.socket.on('chaturbate_event', (data) => {
          this.emit('chaturbate_event', data);
        });

        this.socket.on('chaturbate_status', (data) => {
          this.emit('chaturbate_status', data);
        });

        this.socket.on('chaturbate_error', (data) => {
          this.emit('chaturbate_error', data);
        });

        this.socket.on('private_message', (data) => {
          this.emit('private_message', data);
        });

      } catch (error) {
        reject(error);
      }
    });
  }

  // Disconnect from WebSocket
  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
    this.isConnected = false;
  }

  // Send event to server
  send(event, data) {
    if (this.socket && this.isConnected) {
      this.socket.emit(event, data);
    } else {
      console.warn('Cannot send event - not connected');
    }
  }
}

// Export as singleton
window.webSocketService = new WebSocketService();