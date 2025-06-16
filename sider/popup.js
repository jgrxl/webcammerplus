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
        sidebarExpanded: false
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