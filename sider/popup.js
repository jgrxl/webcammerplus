// Vue 3 Chat Interface for Sider AI Clone
document.addEventListener('DOMContentLoaded', function() {
  const { createApp } = Vue;
  
  const app = createApp({
    data() {
      return {
        title: 'Sider AI',
        messages: [],
        currentMessage: '',
        isTyping: false,
        messageIdCounter: 1,
        showChat: false,
        showEdit: false,
        editContent: '',
        activeEditTab: 'write',
        replyOriginalText: '',
        replyResponseText: '',
        activeReplyMode: 'comment',
        showTranslate: false,
        translateText: '',
        translateFromLang: 'auto',
        translateToLang: 'en',
        showHome: true,
        showAnalytics: false,
        activeAnalyticsTab: 'dashboard',
        isAuthenticated: false,
        user: null,
        sidebarExpanded: false,
        isAttached: false,
        events: [],
        eventIdCounter: 1,
        autoScroll: true,
        websocket: null
      }
    },
    methods: {
      sendMessage() {
        if (!this.currentMessage.trim() || this.isTyping) return;
        
        // Add user message
        const userMessage = {
          id: this.messageIdCounter++,
          text: this.currentMessage.trim(),
          type: 'user',
          timestamp: new Date()
        };
        
        this.messages.push(userMessage);
        const messageText = this.currentMessage.trim();
        this.currentMessage = '';
        
        // Scroll to bottom
        this.$nextTick(() => {
          this.scrollToBottom();
        });
        
        // Simulate AI response
        this.simulateAIResponse(messageText);
      },
      
      simulateAIResponse(userMessage) {
        this.isTyping = true;
        
        // Simulate typing delay
        setTimeout(() => {
          const aiMessage = {
            id: this.messageIdCounter++,
            text: this.generateAIResponse(userMessage),
            type: 'ai',
            timestamp: new Date()
          };
          
          this.messages.push(aiMessage);
          this.isTyping = false;
          
          // Scroll to bottom
          this.$nextTick(() => {
            this.scrollToBottom();
          });
        }, 1000 + Math.random() * 2000); // Random delay 1-3 seconds
      },
      
      generateAIResponse(userMessage) {
        // Simple response generation for demo
        const responses = [
          `I understand you said: "${userMessage}". How can I help you further?`,
          `That's an interesting question about "${userMessage}". Let me think about that...`,
          `Thank you for asking about "${userMessage}". Here's what I think...`,
          `Great question! Regarding "${userMessage}", I'd suggest...`,
          `I'd be happy to help with "${userMessage}". Here's my perspective...`
        ];
        
        return responses[Math.floor(Math.random() * responses.length)];
      },
      
      handleKeyPress(event) {
        if (event.key === 'Enter' && !event.shiftKey) {
          event.preventDefault();
          this.sendMessage();
        }
      },
      
      scrollToBottom() {
        const messagesArea = this.$refs.messagesArea;
        if (messagesArea) {
          messagesArea.scrollTop = messagesArea.scrollHeight;
        }
      },
      
      toggleChat() {
        this.showChat = true;
        this.showEdit = false;
        this.showTranslate = false;
        this.showHome = false;
        this.showAnalytics = false;
      },
      
      toggleEdit() {
        this.showEdit = true;
        this.showChat = false;
        this.showTranslate = false;
        this.showHome = false;
        this.showAnalytics = false;
      },
      
      switchEditTab(tab) {
        this.activeEditTab = tab;
      },
      
      switchReplyMode(mode) {
        this.activeReplyMode = mode;
      },
      
      async generateContent() {
        if (!this.editContent.trim()) return;
        
        try {
          // You can integrate with your AI service here
          console.log('Generating content for:', this.editContent);
          // For now, just log - you can add real AI integration later
        } catch (error) {
          console.error('Content generation error:', error);
        }
      },
      
      async generateReply() {
        if (!this.replyOriginalText.trim() || !this.replyResponseText.trim()) return;
        
        try {
          console.log('Generating reply for:', this.replyOriginalText, 'with idea:', this.replyResponseText);
          // For now, just log - you can add real AI integration later
        } catch (error) {
          console.error('Reply generation error:', error);
        }
      },
      
      toggleTranslate() {
        this.showTranslate = true;
        this.showChat = false;
        this.showEdit = false;
        this.showHome = false;
        this.showAnalytics = false;
      },
      
      async performTranslation() {
        if (!this.translateText.trim()) return;
        
        try {
          console.log('Translating:', this.translateText, 'from', this.translateFromLang, 'to', this.translateToLang);
          // For now, just log - you can add real translation integration later
        } catch (error) {
          console.error('Translation error:', error);
        }
      },
      
      toggleHome() {
        this.showHome = true;
        this.showChat = false;
        this.showEdit = false;
        this.showTranslate = false;
        this.showAnalytics = false;
      },

      toggleAnalytics() {
        this.showAnalytics = true;
        this.showChat = false;
        this.showEdit = false;
        this.showTranslate = false;
        this.showHome = false;
      },
      
      switchAnalyticsTab(tab) {
        this.activeAnalyticsTab = tab;
      },

      toggleSidebar() {
        this.sidebarExpanded = !this.sidebarExpanded;
      },
      
      async toggleAuth() {
        if (this.isAuthenticated) {
          // Show user menu dropdown instead of logging out
          if (window.userMenu) {
            window.userMenu.toggleDropdown();
          }
        } else {
          await this.login();
        }
      },
      
      async login() {
        try {
          const auth0Service = await window.getAuth0Service();
          await auth0Service.login();
          // Refresh user menu after login
          if (window.userMenu) {
            await window.userMenu.refresh();
          }
        } catch (error) {
          console.error('Login failed:', error);
        }
      },
      
      async logout() {
        try {
          const auth0Service = await window.getAuth0Service();
          await auth0Service.logout();
          this.isAuthenticated = false;
          this.user = null;
        } catch (error) {
          console.error('Logout failed:', error);
        }
      },
      
      async checkAuthStatus() {
        try {
          const auth0Service = await window.getAuth0Service();
          this.isAuthenticated = auth0Service.isAuthenticated;
          this.user = auth0Service.user;
          
          // Get fresh token if authenticated
          if (this.isAuthenticated) {
            await auth0Service.getToken();
            // Add sample credits if not present
            if (this.user && !this.user.credits) {
              this.user.credits = 40;
            }
          }
        } catch (error) {
          console.error('Auth status check failed:', error);
          this.isAuthenticated = false;
          this.user = null;
        }
      },

      showUpgradeModal() {
        alert('Upgrade to Pro for 35% OFF! 🚀\n\nUnlock unlimited credits and premium features.');
      },

      toggleFavorites() {
        alert('Favorites feature coming soon! ❤️');
      },

      showHelpModal() {
        alert('Need help? 🤔\n\nContact our support team or check our documentation.');
      },

      showContactModal() {
        alert('Get in touch! 📧\n\nEmail us at support@webcammerplus.com');
      },

      async toggleAttach() {
        if (this.isAttached) {
          await this.disconnectFromChaturbate();
        } else {
          await this.attachToChaturbate();
        }
      },

      async attachToChaturbate() {
        try {
          // Make sure we're on home tab to see events
          if (!this.showHome) {
            this.toggleHome();
          }

          // Initialize SocketIO connection
          if (!window.io) {
            this.addEvent('error', 'SocketIO library not loaded');
            return;
          }

          // Create SocketIO connection to our backend
          const serverUrl = `${window.location.protocol}//${window.location.hostname}:5000`;
          this.websocket = window.io(`${serverUrl}/chaturbate`);
          
          this.websocket.on('connect', () => {
            this.isAttached = true;
            this.addEvent('system', 'Connected to Chaturbate');
            console.log('Connected to Chaturbate WebSocket');
          });
          
          this.websocket.on('chaturbate_event', (data) => {
            this.handleChaturbateEvent(data);
          });

          this.websocket.on('chaturbate_status', (data) => {
            this.addEvent('system', `Chaturbate status: ${data.status}`);
          });

          this.websocket.on('chaturbate_error', (data) => {
            this.addEvent('error', `Chaturbate error: ${data.error}`);
          });
          
          this.websocket.on('disconnect', () => {
            this.isAttached = false;
            this.addEvent('system', 'Disconnected from Chaturbate');
            console.log('Disconnected from Chaturbate WebSocket');
          });
          
          this.websocket.on('connect_error', (error) => {
            console.error('WebSocket connection error:', error);
            this.addEvent('error', 'Connection error occurred');
          });
          
        } catch (error) {
          console.error('Failed to connect to Chaturbate:', error);
          this.addEvent('error', 'Failed to connect to Chaturbate');
        }
      },

      async disconnectFromChaturbate() {
        if (this.websocket) {
          this.websocket.disconnect();
          this.websocket = null;
        }
        this.isAttached = false;
      },

      handleChaturbateEvent(data) {
        let message = '';
        
        switch (data.type) {
          case 'tip':
            message = `💰 ${data.username} tipped ${data.amount} tokens`;
            if (data.message) message += `: ${data.message}`;
            break;
          case 'chat':
            message = `💬 ${data.username}: ${data.message}`;
            break;
          case 'private':
            message = `📧 Private message from ${data.username}`;
            break;
          case 'user_join':
            message = `👋 ${data.username} joined the room`;
            break;
          case 'user_leave':
            message = `👋 ${data.username} left the room`;
            break;
          case 'media_purchase':
            message = `🎬 ${data.username} purchased ${data.media_name}`;
            break;
          case 'system':
            message = data.message || `System: ${data.type}`;
            break;
          default:
            message = data.message || `📝 ${data.type}: ${JSON.stringify(data)}`;
        }
        
        // Use timestamp from data if available, otherwise current time
        const timestamp = data.timestamp ? new Date(data.timestamp * 1000) : new Date();
        this.addEventWithTimestamp(data.type, message, timestamp);
      },

      addEvent(type, message) {
        this.addEventWithTimestamp(type, message, new Date());
      },

      addEventWithTimestamp(type, message, timestamp) {
        const event = {
          id: this.eventIdCounter++,
          type: type,
          message: message,
          timestamp: timestamp
        };
        
        this.events.push(event);
        
        // Limit events to last 1000 to prevent memory issues
        if (this.events.length > 1000) {
          this.events = this.events.slice(-1000);
        }
        
        // Auto scroll to bottom if enabled
        if (this.autoScroll) {
          this.$nextTick(() => {
            this.scrollEventsToBottom();
          });
        }
      },

      clearEvents() {
        this.events = [];
      },

      toggleAutoScroll() {
        this.autoScroll = !this.autoScroll;
        if (this.autoScroll) {
          this.$nextTick(() => {
            this.scrollEventsToBottom();
          });
        }
      },

      scrollEventsToBottom() {
        const container = this.$refs.eventsContainer;
        if (container) {
          container.scrollTop = container.scrollHeight;
        }
      },

      formatTime(date) {
        // Handle both Date objects and timestamp numbers
        const dateObj = typeof date === 'number' ? new Date(date * 1000) : date;
        return dateObj.toLocaleTimeString('en-US', { 
          hour12: false, 
          hour: '2-digit', 
          minute: '2-digit', 
          second: '2-digit' 
        });
      }
    },
    
    async mounted() {
      // Check auth status after component mounts
      await this.checkAuthStatus();
      
      // Refresh user menu to sync authentication state
      if (window.userMenu) {
        await window.userMenu.refresh();
      }
      
      // Add welcome message after component mounts
      setTimeout(() => {
        const welcomeMessage = {
          id: this.messageIdCounter++,
          text: 'Hello! I\'m your AI assistant. How can I help you today?',
          type: 'ai',
          timestamp: new Date()
        };
        this.messages.push(welcomeMessage);
      }, 500);
    }
  });
  
  const vueApp = app.mount('#app');
  window.vueApp = vueApp;
});