// Main App Component
const App = {
  name: 'App',
  
  data() {
    return {
      // UI State
      sidebarExpanded: false,
      activeView: 'home',
      
      // Auth State
      isAuthenticated: false,
      user: null,
      _checkingAuth: false,
      
      // Server State
      serverAvailable: true,
      
      // Chaturbate State
      isAttached: false,
      websocket: null,
      events: [],
      eventIdCounter: 1,
      autoScroll: true,
      refreshDebounceTimer: null,
      
      // Home Tab State
      activeTab: 'messages',
      onlineUsers: 0,
      currentRank: null,
      totalTokensToday: 0,
      viewersCount: 0,
      
      // Chat State
      messages: [],
      currentMessage: '',
      isTyping: false,
      messageIdCounter: 1,
      
      // Message Filters
      messageFilters: ['tip', 'chat', 'system'],
      showFilterMenu: false,
      messageSortOrder: 'newest',
      showTippersOnly: false,
      showModeratorsOnly: false,
      enableTipAmountFilter: false,
      minTipAmount: 1,
      
      // Inbox State
      conversations: [],
      currentConversation: null,
      currentMessages: [],
      inboxStats: { total_messages: 0, unread_messages: 0, read_messages: 0 },
      inboxUnreadCount: 0,
      lastConversationsLoadTime: 0,
      conversationsLoadInterval: 120000,
      _navigatingToConversation: false,
      loadingMessages: false,
      
      // Users State
      onlineUsersList: [
        { username: 'BigTipper', status: 'Premium' },
        { username: 'ChatUser1', status: 'Regular' },
        { username: 'Viewer2', status: 'Regular' },
        { username: 'ModeratorX', status: 'Moderator' }
      ],
      userFilter: 'all',
      userSort: 'last_message',
      userSearchQuery: '',
      userStatsCache: {},
      userStatsLoading: new Set(),
      
      // Tippers State
      topTippers: [],
      tippersTimeFilter: 'today',
      tippersRefreshTimer: null,
      hasLoadedTippers: false,
      
      // Modal State
      showUserInfoModal: false,
      selectedUserInfo: null,
      loadingUserInfo: false
    };
  },
  
  template: `
    <div id="app">
      <!-- Sidebar -->
      <sidebar-component
        :expanded="sidebarExpanded"
        :is-authenticated="isAuthenticated"
        :user="user"
        :active-view="activeView"
        @toggle-sidebar="toggleSidebar"
        @navigate="navigateToView"
        @toggle-auth="toggleAuth"
      />
      
      <!-- Main Content Area -->
      <div class="main-content">
        <!-- Home View -->
        <home-view
          v-if="activeView === 'home'"
          :is-attached="isAttached"
          :active-tab="activeTab"
          :online-users="onlineUsers"
          :inbox-unread-count="inboxUnreadCount"
          @switch-tab="switchTab"
          @toggle-attach="toggleAttach"
        >
          <!-- Messages Tab -->
          <template #messages>
            <messages-tab
              :events="events"
              :auto-scroll="autoScroll"
              :message-filters="messageFilters"
              :show-filter-menu="showFilterMenu"
              :message-sort-order="messageSortOrder"
              :show-tippers-only="showTippersOnly"
              :show-moderators-only="showModeratorsOnly"
              :enable-tip-amount-filter="enableTipAmountFilter"
              :min-tip-amount="minTipAmount"
              @clear-events="clearEvents"
              @toggle-auto-scroll="toggleAutoScroll"
              @toggle-message-filter="toggleMessageFilter"
              @toggle-filter-menu="toggleFilterMenu"
              @update-filters="updateMessageFilters"
            />
          </template>
          
          <!-- Other tabs will be added here -->
          <template #inbox>
            <div class="inbox-tab">Inbox content (to be implemented)</div>
          </template>
          
          <template #tippers>
            <div class="tippers-tab">Tippers content (to be implemented)</div>
          </template>
          
          <template #ranking>
            <div class="ranking-tab">Ranking content (to be implemented)</div>
          </template>
          
          <template #users>
            <div class="users-tab">Users content (to be implemented)</div>
          </template>
        </home-view>
        
        <!-- Chat View -->
        <chat-view
          v-if="activeView === 'chat'"
          :messages="messages"
          :is-typing="isTyping"
          @send-message="sendMessage"
        />
        
        <!-- Other views (Edit, Translate, Analytics) will be added here -->
        <div v-if="activeView === 'edit'" class="edit-content">
          <h1>Edit & Write (to be implemented)</h1>
        </div>
        
        <div v-if="activeView === 'translate'" class="translate-content">
          <h1>Translate (to be implemented)</h1>
        </div>
        
        <div v-if="activeView === 'analytics'" class="analytics-content">
          <h1>Analytics (to be implemented)</h1>
        </div>
      </div>
      
      <!-- Modals -->
      <user-info-modal
        v-if="showUserInfoModal"
        :user-info="selectedUserInfo"
        :loading="loadingUserInfo"
        @close="closeUserInfoModal"
        @start-message="startPrivateMessage"
      />
    </div>
  `,
  
  computed: {
    filteredEvents() {
      if (this.messageFilters.length === 0) {
        return [];
      }
      
      let filtered = this.events.filter(event => {
        const eventCategory = this.getEventCategory(event.type);
        if (!this.messageFilters.includes(eventCategory)) {
          return false;
        }

        if (this.showTippersOnly && eventCategory !== 'tip') {
          return false;
        }

        if (this.showModeratorsOnly) {
          const isModerator = event.message && (
            event.message.includes('Moderator') || 
            event.username === 'ModeratorX'
          );
          if (!isModerator) {
            return false;
          }
        }

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

      if (this.messageSortOrder === 'oldest') {
        filtered = filtered.slice().reverse();
      }

      return filtered;
    }
  },
  
  methods: {
    // UI Navigation
    toggleSidebar() {
      this.sidebarExpanded = !this.sidebarExpanded;
    },
    
    navigateToView(view) {
      this.activeView = view;
      if (view === 'home') {
        this.showHome = true;
        this.showChat = false;
        this.showEdit = false;
        this.showTranslate = false;
        this.showAnalytics = false;
      }
    },
    
    switchTab(tab) {
      this.activeTab = tab;
      if (tab === 'tippers' && !this.hasLoadedTippers && this.topTippers.length === 0) {
        this.showDemoTippers();
        this.fetchTippersFromInflux();
      }
      if (tab === 'inbox') {
        if (!this._navigatingToConversation) {
          this.currentConversation = null;
          this.currentMessages = [];
        }
        this.loadInboxData();
      }
      if (tab === 'users') {
        this.loadUserStatsForVisibleUsers();
      }
    },
    
    // Auth Methods
    async toggleAuth() {
      if (this.isAuthenticated) {
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
        if (window.userMenu) {
          await window.userMenu.refresh();
        }
      } catch (error) {
        console.error('Login failed:', error);
      }
    },
    
    async checkAuthStatus() {
      if (this._checkingAuth) {
        return;
      }
      
      this._checkingAuth = true;
      
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
      } catch (error) {
        console.error('Auth status check failed:', error);
        this.isAuthenticated = false;
        this.user = null;
      } finally {
        this._checkingAuth = false;
      }
    },
    
    // Server Health Check
    async checkServerHealth() {
      try {
        const serverUrl = `${window.location.protocol}//${window.location.hostname}:5000`;
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 3000);
        
        const response = await fetch(`${serverUrl}/`, {
          signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        this.serverAvailable = response.ok;
        return response.ok;
      } catch (error) {
        this.serverAvailable = false;
        console.warn('Server health check failed:', error.message);
        return false;
      }
    },
    
    // Chaturbate Connection
    async toggleAttach() {
      if (this.isAttached) {
        await this.disconnectFromChaturbate();
      } else {
        const serverAvailable = await this.checkServerHealth();
        if (!serverAvailable) {
          this.addEvent('error', 'Cannot connect: Backend server is not available. Please ensure the server is running on port 5000.');
          return;
        }
        await this.attachToChaturbate();
      }
    },
    
    async attachToChaturbate() {
      // Implementation from popup.js
      console.log('Attaching to Chaturbate...');
      // Add WebSocket connection logic here
    },
    
    async disconnectFromChaturbate() {
      if (this.websocket) {
        this.websocket.disconnect();
        this.websocket = null;
      }
      this.isAttached = false;
    },
    
    // Event Management
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
      
      if (this.events.length > 1000) {
        this.events = this.events.slice(-1000);
      }
      
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
    },
    
    toggleMessageFilter(filterType) {
      const index = this.messageFilters.indexOf(filterType);
      if (index > -1) {
        this.messageFilters.splice(index, 1);
      } else {
        this.messageFilters.push(filterType);
      }
    },
    
    toggleFilterMenu() {
      this.showFilterMenu = !this.showFilterMenu;
    },
    
    updateMessageFilters(filters) {
      this.messageSortOrder = filters.sortOrder;
      this.showTippersOnly = filters.showTippersOnly;
      this.showModeratorsOnly = filters.showModeratorsOnly;
      this.enableTipAmountFilter = filters.enableTipAmountFilter;
      this.minTipAmount = filters.minTipAmount;
    },
    
    getEventCategory(eventType) {
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
      let message = event.message || '';
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
      
      if (username) {
        username = username.replace(/[^\w\s]/g, '').trim();
        if (username && username !== 'System') {
          const escapedUsername = username.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
          const usernameRegex = new RegExp(`\\b${escapedUsername}\\b`, 'g');
          const clickableHtml = `<span class="clickable-username" onclick="window.vueApp.handleUserClick('${username}')">${username}</span>`;
          message = message.replace(usernameRegex, clickableHtml);
        }
      }
      
      return message;
    },
    
    // Chat Methods
    sendMessage(messageText) {
      if (!messageText.trim() || this.isTyping) return;
      
      const userMessage = {
        id: this.messageIdCounter++,
        text: messageText,
        type: 'user',
        timestamp: new Date()
      };
      
      this.messages.push(userMessage);
      this.simulateAIResponse(messageText);
    },
    
    simulateAIResponse(userMessage) {
      this.isTyping = true;
      
      setTimeout(() => {
        const aiMessage = {
          id: this.messageIdCounter++,
          text: this.generateAIResponse(userMessage),
          type: 'ai',
          timestamp: new Date()
        };
        
        this.messages.push(aiMessage);
        this.isTyping = false;
      }, 1000 + Math.random() * 2000);
    },
    
    generateAIResponse(userMessage) {
      const responses = [
        `I understand you said: "${userMessage}". How can I help you further?`,
        `That's an interesting question about "${userMessage}". Let me think about that...`,
        `Thank you for asking about "${userMessage}". Here's what I think...`,
        `Great question! Regarding "${userMessage}", I'd suggest...`,
        `I'd be happy to help with "${userMessage}". Here's my perspective...`
      ];
      
      return responses[Math.floor(Math.random() * responses.length)];
    },
    
    // User Info Modal
    async handleUserClick(username) {
      console.log('User clicked:', username);
      this.loadingUserInfo = true;
      this.showUserInfoModal = true;
      this.selectedUserInfo = {
        username: username,
        status: this.getUserStatusFromCache(username),
        stats: null
      };
      
      try {
        const stats = await this.getUserStats(username, true);
        this.selectedUserInfo.stats = stats;
      } catch (error) {
        console.error('Failed to load user info:', error);
      } finally {
        this.loadingUserInfo = false;
      }
    },
    
    closeUserInfoModal() {
      this.showUserInfoModal = false;
      this.selectedUserInfo = null;
      this.loadingUserInfo = false;
    },
    
    async startPrivateMessage(username) {
      this.closeUserInfoModal();
      this._navigatingToConversation = true;
      this.currentConversation = username;
      this.currentMessages = [];
      this.activeView = 'home';
      this.activeTab = 'inbox';
      await this.$nextTick();
      
      if (this.conversations.length === 0 && this.isAuthenticated) {
        await this.loadConversations(true);
      }
      
      const existingConversation = this.conversations.find(conv => conv.from_user === username);
      if (existingConversation) {
        this.loadMessages(username).catch(error => {
          console.error('Failed to load messages:', error);
        });
      }
      
      this._navigatingToConversation = false;
    },
    
    getUserStatusFromCache(username) {
      const userStats = this.userStatsCache[username];
      return userStats?.user_status || 'Regular';
    },
    
    // Placeholder methods for features to be implemented
    async loadInboxData() {
      console.log('Loading inbox data...');
    },
    
    async fetchTippersFromInflux() {
      console.log('Fetching tippers...');
    },
    
    showDemoTippers() {
      this.topTippers = [
        { username: 'Loading...', totalTokens: 0 }
      ];
    },
    
    async loadUserStatsForVisibleUsers() {
      console.log('Loading user stats...');
    },
    
    scrollEventsToBottom() {
      // This will be handled by the MessagesTab component
    }
  },
  
  watch: {
    isAuthenticated(newVal, oldVal) {
      if (newVal !== oldVal) {
        console.log('Authentication state changed:', oldVal, '->', newVal);
        if (window.userMenu) {
          window.userMenu.refresh();
        }
        this.$forceUpdate();
      }
    }
  },
  
  async mounted() {
    await this.checkAuthStatus();
    
    const justLoggedIn = sessionStorage.getItem('auth0_just_logged_in') === 'true';
    if (justLoggedIn) {
      console.log('Just logged in, refreshing UI components...');
      sessionStorage.removeItem('auth0_just_logged_in');
      
      if (window.userMenu) {
        await window.userMenu.refresh();
      }
      
      this.$forceUpdate();
    } else if (window.userMenu && this.isAuthenticated) {
      await window.userMenu.refresh();
    }
    
    this.onlineUsers = this.onlineUsersList.length;
    
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
};

// Export for use
window.App = App;