// Vue 3 Chat Interface for Sider AI Clone
document.addEventListener('DOMContentLoaded', function() {
  console.log('🚀 DOM loaded, starting Vue app...');
  
  if (typeof Vue === 'undefined') {
    console.error('❌ Vue is not loaded!');
    return;
  }
  
  const { createApp } = Vue;
  console.log('✅ Vue is loaded, creating app...');
  
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
        messageFilters: ['tip', 'chat', 'system'],
        showFilterMenu: false,
        messageSortOrder: 'newest',
        showTippersOnly: false,
        showModeratorsOnly: false,
        enableTipAmountFilter: false,
        minTipAmount: 1,
        showUserInfoModal: false,
        selectedUserInfo: null,
        loadingUserInfo: false,
        websocket: null,
        refreshDebounceTimer: null,
        activeTab: 'messages',
        onlineUsers: 0,
        currentRank: null,
        totalTokensToday: 0,
        viewersCount: 0,
        userFilter: 'all',
        userSort: 'last_message',
        userSearchQuery: '',
        topTippers: [],
        tippersTimeFilter: 'today',
        tippersRefreshTimer: null,
        hasLoadedTippers: false,
        onlineUsersList: [
          { username: 'BigTipper', status: 'Premium' },
          { username: 'ChatUser1', status: 'Regular' },
          { username: 'Viewer2', status: 'Regular' },
          { username: 'ModeratorX', status: 'Moderator' }
        ],
        userStatsCache: {},  // Cache for user statistics
        userStatsLoading: new Set(),  // Track which users are being loaded
        // Inbox related data
        conversations: [],
        currentConversation: null,
        currentMessages: [],
        inboxStats: { total_messages: 0, unread_messages: 0, read_messages: 0 },
        inboxUnreadCount: 0,
        lastConversationsLoadTime: 0,
        conversationsLoadInterval: 120000,  // 2 minutes in milliseconds
        _navigatingToConversation: false,  // Private flag for navigation
        loadingMessages: false  // Loading state for messages
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
            // Load initial data from InfluxDB
            this.refreshInfluxData();
          });
          
          this.websocket.on('chaturbate_event', (data) => {
            this.handleChaturbateEvent(data);
            // Refresh InfluxDB data periodically when receiving tip events (but not chat to avoid spam)
            if (this.isAttached && data.type === 'tip') {
              // Debounce the refresh to avoid too many calls
              clearTimeout(this.refreshDebounceTimer);
              this.refreshDebounceTimer = setTimeout(() => {
                this.refreshInfluxData();
              }, 2000);
            }
          });

          this.websocket.on('chaturbate_status', (data) => {
            this.addEvent('system', `Chaturbate status: ${data.status}`);
          });

          this.websocket.on('chaturbate_error', (data) => {
            this.addEvent('error', `Chaturbate error: ${data.error}`);
          });

          this.websocket.on('private_message', (data) => {
            this.handlePrivateMessage(data);
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
            // Update tipper stats
            this.updateTipperStats(data.username, data.amount);
            // Ensure user is in the list
            this.updateUsersList(data.username, 'join');
            break;
          case 'chat':
            message = `💬 ${data.username}: ${data.message}`;
            // Ensure user is in the list
            this.updateUsersList(data.username, 'join');
            break;
          case 'private':
            message = `📧 Private message from ${data.username}`;
            break;
          case 'user_join':
            message = `👋 ${data.username} joined the room`;
            this.updateUsersList(data.username, 'join');
            break;
          case 'user_leave':
            message = `👋 ${data.username} left the room`;
            this.updateUsersList(data.username, 'leave');
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
            setTimeout(() => {
              this.scrollEventsToBottom();
            }, 10);
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

      toggleMessageFilter(filterType) {
        const index = this.messageFilters.indexOf(filterType);
        if (index > -1) {
          // Remove filter
          this.messageFilters.splice(index, 1);
        } else {
          // Add filter
          this.messageFilters.push(filterType);
        }
      },

      scrollEventsToBottom() {
        const container = this.$refs.eventsContainer;
        if (container) {
          container.scrollTop = container.scrollHeight;
          // Double-check scroll position in case of timing issues
          setTimeout(() => {
            if (container && this.autoScroll) {
              container.scrollTop = container.scrollHeight;
            }
          }, 50);
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
      },

      async switchTab(tab) {
        this.activeTab = tab;
        // Fetch tippers data when switching to tippers tab
        if (tab === 'tippers') {
          // Show demo data on first load if no data exists
          if (!this.hasLoadedTippers && this.topTippers.length === 0) {
            this.showDemoTippers();
          }
          this.fetchTippersFromInflux();
        }
        // Load inbox data when switching to inbox tab
        if (tab === 'inbox') {
          // Don't clear current conversation if we're being directed to a specific one
          // Only clear if manually switching to inbox
          if (!this._navigatingToConversation) {
            this.currentConversation = null;
            this.currentMessages = [];
          }
          await this.loadInboxData();
        }
        // Load user stats when switching to users tab
        if (tab === 'users') {
          this.loadUserStatsForVisibleUsers();
        }
      },
      
      showDemoTippers() {
        // Show some demo data while waiting for real data
        this.topTippers = [
          { username: 'Loading...', totalTokens: 0 }
        ];
      },

      setUserFilter(filter) {
        this.userFilter = filter;
      },

      setUserSort(sortBy) {
        this.userSort = sortBy;
      },

      onUserSearch() {
        // This method can be used for debouncing or additional search logic if needed
        // For now, the reactive userSearchQuery will trigger filteredUsers to update
      },

      clearUserSearch() {
        this.userSearchQuery = '';
      },

      toggleFilterMenu() {
        this.showFilterMenu = !this.showFilterMenu;
      },

      closeFilterMenu() {
        this.showFilterMenu = false;
      },

      applyMessageSort() {
        // Trigger filteredEvents recomputation
        this.$forceUpdate();
      },

      applyUserFilter() {
        // Trigger filteredEvents recomputation
        this.$forceUpdate();
      },

      applyTipFilter() {
        // Trigger filteredEvents recomputation
        this.$forceUpdate();
      },

      resetMessageFilters() {
        this.messageFilters = ['tip', 'chat', 'system'];
        this.messageSortOrder = 'newest';
        this.showTippersOnly = false;
        this.showModeratorsOnly = false;
        this.enableTipAmountFilter = false;
        this.minTipAmount = 1;
      },



      getTipperBadge(index) {
        const badges = ['👑', '💎', '⭐', '🥇', '🥈', '🥉'];
        return badges[index] || '🎖️';
      },

      updateTipperStats(username, amount) {
        // Since we're now using InfluxDB, we don't need to update local state
        // The data will be refreshed via refreshInfluxData() calls
        // Just update today's total for immediate feedback
        this.totalTokensToday += amount;
        
        // If we're on the tippers tab, refresh the tippers list
        if (this.activeTab === 'tippers') {
          // Debounce the refresh to avoid too many API calls
          clearTimeout(this.tippersRefreshTimer);
          this.tippersRefreshTimer = setTimeout(() => {
            this.fetchTippersFromInflux();
          }, 2000); // Wait 2 seconds before refreshing
        }
      },

      updateUsersList(username, action) {
        if (action === 'join') {
          if (!this.onlineUsersList.find(u => u.username === username)) {
            this.onlineUsersList.push({
              username: username,
              status: 'Regular'
            });
          }
        } else if (action === 'leave') {
          this.onlineUsersList = this.onlineUsersList.filter(u => u.username !== username);
        }
        this.onlineUsers = this.onlineUsersList.length;
      },

      async fetchTippersFromInflux() {
        try {
          // Map time filter to days
          const daysMap = {
            'today': 1,
            'week': 7,
            'month': 30
          };
          const days = daysMap[this.tippersTimeFilter] || 1;
          
          const serverUrl = `${window.location.protocol}//${window.location.hostname}:5000`;
          const response = await fetch(`${serverUrl}/api/v1/influx/tippers`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              days: days,
              limit: 10  // Get top 10 tippers
            })
          });
          
          if (response.ok) {
            const result = await response.json();
            if (result.success && result.tippers) {
              // Map the response to match the frontend's expected format
              this.topTippers = result.tippers.map(tipper => ({
                username: tipper.username,
                totalTokens: tipper.total_tokens
              }));
              this.hasLoadedTippers = true;
            }
          }
        } catch (error) {
          console.error('Failed to fetch tippers from InfluxDB:', error);
        }
      },
      
      onTippersTimeFilterChange() {
        // Refresh tippers data when time filter changes
        this.fetchTippersFromInflux();
      },

      async fetchTotalTipsFromInflux() {
        try {
          const serverUrl = `${window.location.protocol}//${window.location.hostname}:5000`;
          const response = await fetch(`${serverUrl}/api/v1/influx/tips`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              days: 1
            })
          });
          
          if (response.ok) {
            const data = await response.json();
            if (data.success) {
              this.totalTokensToday = data.total_tokens;
            }
          }
        } catch (error) {
          console.error('Failed to fetch total tips from InfluxDB:', error);
        }
      },

      async refreshInfluxData() {
        await Promise.all([
          this.fetchTippersFromInflux(),
          this.fetchTotalTipsFromInflux()
        ]);
      },

      // Inbox methods
      async loadInboxData() {
        try {
          // Only load inbox data if user is authenticated
          if (!this.isAuthenticated) {
            console.warn('User not authenticated, skipping inbox data load');
            return;
          }

          // Load stats and conversations in parallel
          // But only load conversations if we don't have any cached or it's been a while
          const promises = [this.loadInboxStats()];
          
          const now = Date.now();
          const timeSinceLastLoad = now - this.lastConversationsLoadTime;
          const shouldReloadConversations = this.conversations.length === 0 || timeSinceLastLoad > 30000; // 30 seconds
          
          if (shouldReloadConversations) {
            promises.push(this.loadConversations());
          }

          await Promise.all(promises);
        } catch (error) {
          console.error('Failed to load inbox data:', error);
        }
      },

      async getAuthToken() {
        try {
          const auth0Service = await window.getAuth0Service();
          if (auth0Service.isAuthenticated) {
            const token = await auth0Service.getToken();
            // Debug: log user info to help with inbox setup
            if (auth0Service.user) {
              console.log('🔍 Current user for inbox:', {
                auth0_id: auth0Service.user.sub,
                email: auth0Service.user.email,
                nickname: auth0Service.user.nickname,
                name: auth0Service.user.name
              });
            }
            return token;
          }
          return null;
        } catch (error) {
          console.error('Failed to get auth token:', error);
          return null;
        }
      },

      async loadInboxStats() {
        try {
          const token = await this.getAuthToken();
          if (!token) {
            console.warn('No auth token available for inbox stats');
            return;
          }

          const response = await fetch('http://localhost:5000/api/v1/inbox/stats', {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });

          if (response.ok) {
            this.inboxStats = await response.json();
            this.inboxUnreadCount = this.inboxStats.unread_messages || 0;
          } else {
            console.error('Failed to fetch inbox stats:', response.status, response.statusText);
          }
        } catch (error) {
          console.error('Failed to load inbox stats:', error);
        }
      },

      async loadConversations(forceLoad = false) {
        try {
          // Check if we should skip loading based on time interval
          const now = Date.now();
          const timeSinceLastLoad = now - this.lastConversationsLoadTime;
          
          if (!forceLoad && timeSinceLastLoad < this.conversationsLoadInterval) {
            console.log(`📋 Skipping conversations load - only ${Math.round(timeSinceLastLoad/1000)}s since last load (need ${this.conversationsLoadInterval/1000}s)`);
            return;
          }

          const token = await this.getAuthToken();
          if (!token) {
            console.warn('No auth token available for conversations');
            return;
          }

          console.log('📋 Loading conversations from API...');
          const response = await fetch('http://localhost:5000/api/v1/inbox/conversations', {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });

          if (response.ok) {
            this.conversations = await response.json();
            this.lastConversationsLoadTime = now;  // Update last load time
            console.log('📋 Loaded conversations:', this.conversations.length, 'conversations');
            console.log('📋 Conversations data:', this.conversations);
            // Log each conversation for debugging
            this.conversations.forEach((conv, index) => {
              console.log(`📋 Conversation ${index + 1}:`, {
                from: conv.from_user,
                message: conv.last_message,
                unread: conv.unread_count
              });
            });
          } else {
            console.error('Failed to fetch conversations:', response.status, response.statusText);
            this.conversations = [];
          }
        } catch (error) {
          console.error('Failed to load conversations:', error);
          this.conversations = [];
        }
      },

      async selectConversation(username) {
        console.log('👆 Selecting conversation with:', username);
        this.currentConversation = username;
        await this.loadMessages(username);
      },

      async loadMessages(username) {
        try {
          console.log('📨 Loading messages for:', username);
          this.loadingMessages = true;
          
          const token = await this.getAuthToken();
          if (!token) {
            console.warn('No auth token available for messages');
            this.loadingMessages = false;
            return;
          }

          const response = await fetch(`http://localhost:5000/api/v1/inbox/conversations/${username}`, {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });

          console.log('📨 Response status:', response.status);
          if (response.ok) {
            this.currentMessages = await response.json();
            console.log('📨 Loaded messages:', this.currentMessages.length, 'messages');
            console.log('📨 Messages data:', this.currentMessages);
          } else {
            console.error('Failed to fetch messages:', response.status, response.statusText);
            const errorText = await response.text();
            console.error('Error response:', errorText);
            this.currentMessages = [];
          }

          // Auto-mark as read when viewing
          this.markConversationAsRead();
        } catch (error) {
          console.error('Failed to load messages:', error);
          this.currentMessages = [];
        } finally {
          this.loadingMessages = false;
        }
      },

      async markConversationAsRead() {
        if (!this.currentConversation) return;

        try {
          const token = await this.getAuthToken();
          if (!token) {
            console.warn('No auth token available for marking messages as read');
            return;
          }

          const unreadMessages = this.currentMessages.filter(msg => !msg.is_read && !msg.is_sent);

          for (const msg of unreadMessages) {
            const response = await fetch(`http://localhost:5000/api/v1/inbox/messages/${msg.id}/read`, {
              method: 'POST',
              headers: {
                'Authorization': `Bearer ${token}`
              }
            });
            
            if (!response.ok) {
              console.error('Failed to mark message as read:', response.status, response.statusText);
            }
          }

          // Update local state
          this.currentMessages.forEach(msg => {
            if (!msg.is_sent) msg.is_read = true;
          });

          // Refresh stats and conversations
          await this.loadInboxStats();
          await this.loadConversations();
        } catch (error) {
          console.error('Failed to mark messages as read:', error);
        }
      },

      async refreshMessages() {
        if (this.currentConversation) {
          await this.loadMessages(this.currentConversation);
        }
      },

      async refreshInbox() {
        // Force refresh both conversations and current messages
        await this.loadConversations(true);
        if (this.currentConversation) {
          await this.loadMessages(this.currentConversation);
        }
        await this.loadInboxStats();
      },

      formatInboxTimestamp(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;

        if (diff < 60000) { // Less than 1 minute
          return 'Just now';
        } else if (diff < 3600000) { // Less than 1 hour
          return `${Math.floor(diff / 60000)}m ago`;
        } else if (diff < 86400000) { // Less than 1 day
          return `${Math.floor(diff / 3600000)}h ago`;
        } else if (diff < 604800000) { // Less than 1 week
          return `${Math.floor(diff / 86400000)}d ago`;
        } else {
          return date.toLocaleDateString();
        }
      },

      handlePrivateMessage(data) {
        console.log('New private message received:', data);
        
        // Update unread count
        this.inboxUnreadCount++;
        
        // If on inbox tab, refresh the data
        if (this.activeTab === 'inbox') {
          // Force refresh conversations to show new message immediately
          this.loadConversations(true);
          
          // If viewing the conversation from this sender, refresh messages
          if (this.currentConversation === data.from_username) {
            this.loadMessages(data.from_username);
          }
        }
        
        // Add to events feed as well
        this.addEvent('private_message', `Private message from ${data.from_username}: ${data.message}`);
      },

      async getUserStats(username, forceRefresh = false) {
        // Check if we already have this user's stats (unless forcing refresh)
        if (!forceRefresh && this.userStatsCache[username]) {
          return this.userStatsCache[username];
        }

        // Check if we're already loading this user's stats
        if (this.userStatsLoading.has(username)) {
          return null;
        }

        try {
          this.userStatsLoading.add(username);
          const token = await this.getAuthToken();
          if (!token) {
            return null;
          }

          const response = await fetch(`http://localhost:5000/api/v1/user_stats/${username}?days=30`, {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });

          if (response.ok) {
            const stats = await response.json();
            // Cache the stats for 5 minutes
            this.userStatsCache[username] = {
              ...stats,
              cachedAt: Date.now()
            };
            return stats;
          } else {
            console.error('Failed to fetch user stats:', response.status, response.statusText);
            return null;
          }
        } catch (error) {
          console.error('Error fetching user stats:', error);
          return null;
        } finally {
          this.userStatsLoading.delete(username);
        }
      },

      async loadUserStatsForVisibleUsers() {
        // Load stats for currently visible users in the users tab
        if (this.activeTab !== 'users') return;

        const visibleUsers = this.filteredUsers.slice(0, 10); // Limit to first 10 users
        for (const user of visibleUsers) {
          // Only load if we don't have cached stats (or they're old)
          const cached = this.userStatsCache[user.username];
          const isStale = !cached || (Date.now() - cached.cachedAt > 300000); // 5 minutes
          
          if (isStale) {
            await this.getUserStats(user.username);
          }
        }
      },

      formatTimeAgo(timestamp) {
        if (!timestamp) return 'Never';
        
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;

        if (diff < 60000) { // Less than 1 minute
          return 'Just now';
        } else if (diff < 3600000) { // Less than 1 hour
          return `${Math.floor(diff / 60000)}m ago`;
        } else if (diff < 86400000) { // Less than 1 day
          return `${Math.floor(diff / 3600000)}h ago`;
        } else if (diff < 604800000) { // Less than 1 week
          return `${Math.floor(diff / 86400000)}d ago`;
        } else {
          return date.toLocaleDateString();
        }
      },

      clearUserStatsCache() {
        // Clear all cached user stats to force fresh data
        this.userStatsCache = {};
        this.userStatsLoading.clear();
        console.log('📊 User stats cache cleared');
      },

      getUserStatusClass(username) {
        const userStats = this.userStatsCache[username];
        const userStatus = userStats?.user_status || 'Regular';
        
        switch (userStatus) {
          case 'VIP':
            return 'user-vip';
          case 'Premium':
            return 'user-premium';
          case 'Supporter':
            return 'user-supporter';
          case 'Tipper':
            return 'user-tipper';
          case 'Moderator':
            return 'user-moderator';
          default:
            return 'user-regular';
        }
      },

      openUserProfile(username) {
        const profileUrl = `https://chaturbate.com/${username}`;
        window.open(profileUrl, '_blank');
      },

      startAutoRefresh() {
        // Auto-refresh user stats every minute
        setInterval(() => {
          if (this.activeTab === 'users' && this.filteredUsers.length > 0) {
            console.log('🔄 Auto-refreshing user stats...');
            this.loadUserStatsForVisibleUsers();
          }
        }, 60000); // 60 seconds
      },

      getEventCategory(eventType) {
        // Map event types to filter categories
        switch (eventType) {
          case 'tip':
            return 'tip';
          case 'chat':
            return 'chat';
          case 'system':
          case 'user_join':
          case 'user_leave':
          case 'media_purchase':
          case 'private':
          case 'error':
            return 'system';
          default:
            return 'system';
        }
      },

      formatMessageWithClickableUsers(event) {
        // Format the event message with clickable usernames
        let message = event.message || '';
        console.log('🔍 Formatting message:', { event, message });
        
        // Extract username from the message for tip and chat events
        let username = null;
        if (event.username) {
          username = event.username;
        } else if (event.type === 'tip' && message.includes(' tipped ')) {
          const tipMatch = message.match(/^(.+?) tipped/);
          if (tipMatch) {
            username = tipMatch[1];
          }
        } else if (event.type === 'chat' && message.includes(': ')) {
          const chatMatch = message.match(/^(.+?):/);
          if (chatMatch) {
            username = chatMatch[1];
          }
        }

        // Clean username by removing emojis and extra spaces
        if (username) {
          username = username.replace(/[^\w\s]/g, '').trim(); // Remove emojis and special chars
          if (!username) {
            username = null; // If nothing left after cleaning, set to null
          }
        }

        console.log('🔍 Extracted username:', username);

        // If we found a username, make it clickable
        if (username && username !== 'System') {
          const escapedUsername = username.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
          const usernameRegex = new RegExp(`\\b${escapedUsername}\\b`, 'g');
          const clickableHtml = `<span class="clickable-username" onclick="window.vueApp.handleUserClick('${username}')">${username}</span>`;
          message = message.replace(usernameRegex, clickableHtml);
          console.log('✅ Made username clickable:', { username, clickableHtml, finalMessage: message });
        }

        return message;
      },

      async handleUserClick(username) {
        console.log('👆 User clicked:', username);
        
        // Set loading state
        this.loadingUserInfo = true;
        this.showUserInfoModal = true;
        this.selectedUserInfo = {
          username: username,
          status: this.getUserStatusFromCache(username),
          stats: null
        };

        try {
          // Fetch user statistics
          const stats = await this.getUserStats(username, true); // Force refresh
          this.selectedUserInfo.stats = stats;
        } catch (error) {
          console.error('Failed to load user info:', error);
        } finally {
          this.loadingUserInfo = false;
        }
      },

      getUserStatusFromCache(username) {
        const userStats = this.userStatsCache[username];
        return userStats?.user_status || 'Regular';
      },

      closeUserInfoModal() {
        this.showUserInfoModal = false;
        this.selectedUserInfo = null;
        this.loadingUserInfo = false;
      },

      async startPrivateMessage(username) {
        // This integrates with the inbox system
        console.log('Starting private message with:', username);
        
        // Close the modal immediately
        this.closeUserInfoModal();
        
        // Set flag to indicate we're navigating to a specific conversation
        this._navigatingToConversation = true;
        
        // Set the current conversation immediately for instant UI feedback
        this.currentConversation = username;
        this.currentMessages = [];
        
        // Switch to inbox tab (don't await - let it happen async)
        this.switchTab('inbox');
        
        // Start loading conversations if needed (in parallel)
        const conversationsPromise = this.conversations.length === 0 && this.isAuthenticated
          ? this.loadConversations(true)
          : Promise.resolve();
        
        // Wait for next tick only
        await this.$nextTick();
        
        // Now wait for conversations to load if they were loading
        if (conversationsPromise) {
          await conversationsPromise;
        }
        
        // Check if we have an existing conversation with this user
        const existingConversation = this.conversations.find(conv => conv.from_user === username);
        
        if (existingConversation) {
          // Load messages for existing conversation
          console.log('📬 Loading messages for:', username);
          // Don't await - let messages load in background
          this.loadMessages(username).catch(error => {
            console.error('Failed to load messages:', error);
          });
        } else {
          // No existing conversation - we already set up empty state above
          console.log('📝 No existing conversation with:', username, '- showing empty thread');
        }
        
        // Clear the navigation flag
        this._navigatingToConversation = false;
      }
    },

    computed: {
      filteredEvents() {
        if (this.messageFilters.length === 0) {
          return [];
        }
        
        let filtered = this.events.filter(event => {
          // Basic type filtering
          const eventCategory = this.getEventCategory(event.type);
          if (!this.messageFilters.includes(eventCategory)) {
            return false;
          }

          // User type filtering
          if (this.showTippersOnly && eventCategory !== 'tip') {
            // Only show tips if tippers only is enabled
            return false;
          }

          if (this.showModeratorsOnly) {
            // Check if user is a moderator (simplified check)
            const isModerator = event.message && (
              event.message.includes('Moderator') || 
              event.username === 'ModeratorX' // Add other moderator checks as needed
            );
            if (!isModerator) {
              return false;
            }
          }

          // Tip amount filtering
          if (this.enableTipAmountFilter && eventCategory === 'tip') {
            const tipMatch = event.message.match(/tipped (\d+) tokens/);
            if (tipMatch) {
              const tipAmount = parseInt(tipMatch[1]);
              if (tipAmount < this.minTipAmount) {
                return false;
              }
            }
          }

          return true;
        });

        // Apply sorting
        if (this.messageSortOrder === 'oldest') {
          filtered = filtered.slice().reverse();
        }
        // 'newest' is already the default order

        return filtered;
      },

      filteredUsers() {
        let users = [];
        
        // First apply filters
        if (this.userFilter === 'all') {
          users = [...this.onlineUsersList];
        } else if (this.userFilter === 'tippers') {
          const tipperUsernames = this.topTippers.map(t => t.username);
          users = this.onlineUsersList.filter(u => tipperUsernames.includes(u.username));
        } else if (this.userFilter === 'moderators') {
          users = this.onlineUsersList.filter(u => u.status === 'Moderator');
        }
        
        // Apply search filter if there's a search query
        if (this.userSearchQuery.trim()) {
          const searchQuery = this.userSearchQuery.toLowerCase().trim();
          users = users.filter(user => {
            // Search in username
            const usernameMatch = user.username.toLowerCase().includes(searchQuery);
            
            // Search in user status from cache
            const userStats = this.userStatsCache[user.username];
            const statusMatch = userStats?.user_status?.toLowerCase().includes(searchQuery) || 
                              user.status?.toLowerCase().includes(searchQuery);
            
            return usernameMatch || statusMatch;
          });
        }
        
        // Then apply sorting
        return users.sort((a, b) => {
          const aStats = this.userStatsCache[a.username];
          const bStats = this.userStatsCache[b.username];
          
          // If no stats available, put them at the end
          if (!aStats && !bStats) return 0;
          if (!aStats) return 1;
          if (!bStats) return -1;
          
          switch (this.userSort) {
            case 'last_message':
              const aMessage = new Date(aStats.last_message_time || 0);
              const bMessage = new Date(bStats.last_message_time || 0);
              return bMessage - aMessage; // Most recent first
              
            case 'last_tip':
              const aTip = new Date(aStats.last_tip_time || 0);
              const bTip = new Date(bStats.last_tip_time || 0);
              return bTip - aTip; // Most recent first
              
            case 'total_tips':
              return (bStats.total_tip_amount || 0) - (aStats.total_tip_amount || 0); // Highest first
              
            case 'session_tips':
              // For session tips, we'll use today's tips as a proxy
              // This would need to be enhanced to track actual session data
              return (bStats.total_tips || 0) - (aStats.total_tips || 0); // Most tips first
              
            default:
              return 0;
          }
        });
      }
    },

    watch: {
      filteredEvents() {
        // Auto scroll when filtered events change and auto-scroll is enabled
        if (this.autoScroll) {
          this.$nextTick(() => {
            setTimeout(() => {
              this.scrollEventsToBottom();
            }, 10);
          });
        }
      }
    },
    
    async mounted() {
      // Check auth status after component mounts
      await this.checkAuthStatus();
      
      // Refresh user menu to sync authentication state
      if (window.userMenu) {
        await window.userMenu.refresh();
      }
      
      // Initialize online users count
      this.onlineUsers = this.onlineUsersList.length;
      
      // Start auto-refresh for user stats
      this.startAutoRefresh();
      
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
  
  console.log('🔧 Mounting Vue app to #app...');
  const vueApp = app.mount('#app');
  window.vueApp = vueApp;
  console.log('✅ Vue app mounted successfully!');
  console.log('🔍 Initial modal state:', {
    showUserInfoModal: vueApp.showUserInfoModal,
    selectedUserInfo: vueApp.selectedUserInfo
  });
});