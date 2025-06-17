// Refactored App Component using modular services
const AppRefactored = {
  name: 'AppRefactored',
  
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
      
      // Home Tab State
      activeTab: 'messages',
      
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
      inboxUnreadCount: 0,
      loadingMessages: false,
      
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
          :online-users="onlineUsersCount"
          :inbox-unread-count="inboxUnreadCount"
          @switch-tab="switchTab"
          @toggle-attach="toggleAttach"
        >
          <!-- Messages Tab -->
          <template #messages>
            <messages-tab
              :events="filteredEvents"
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
          
          <!-- Other tabs slots here -->
        </home-view>
        
        <!-- Other views here -->
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
    events() {
      return window.stateManager.getEvents();
    },
    
    onlineUsersCount() {
      return window.stateManager.getOnlineUsersCount();
    },
    
    autoScroll() {
      return true; // Can be made reactive if needed
    },
    
    filteredEvents() {
      if (this.messageFilters.length === 0) return [];
      
      let filtered = this.events.filter(event => {
        const eventCategory = this.getEventCategory(event.type);
        if (!this.messageFilters.includes(eventCategory)) return false;

        // Apply filters
        if (this.showTippersOnly && eventCategory !== 'tip') return false;
        if (this.enableTipAmountFilter && eventCategory === 'tip') {
          const amount = event.amount || 0;
          if (amount < this.minTipAmount) return false;
        }

        return true;
      });

      // Apply sorting
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
    },
    
    switchTab(tab) {
      this.activeTab = tab;
      
      if (tab === 'tippers') {
        this.loadTippers();
      } else if (tab === 'inbox') {
        this.loadInboxData();
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
      } catch (error) {
        console.error('Login failed:', error);
      }
    },
    
    async checkAuthStatus() {
      if (this._checkingAuth) return;
      
      this._checkingAuth = true;
      
      try {
        const auth0Service = await window.getAuth0Service();
        this.isAuthenticated = auth0Service.isAuthenticated;
        this.user = auth0Service.user;
        
        if (this.isAuthenticated) {
          await auth0Service.getToken();
        }
      } catch (error) {
        console.error('Auth status check failed:', error);
        this.isAuthenticated = false;
        this.user = null;
      } finally {
        this._checkingAuth = false;
      }
    },
    
    // WebSocket Connection
    async toggleAttach() {
      if (this.isAttached) {
        await this.disconnect();
      } else {
        await this.connect();
      }
    },
    
    async connect() {
      try {
        // Check server health first
        const healthy = await window.apiService.checkHealth();
        if (!healthy) {
          this.addSystemEvent('Cannot connect: Backend server is not available');
          return;
        }
        
        // Connect WebSocket
        await window.webSocketService.connect();
        this.isAttached = true;
        
        // Set up event handlers
        this.setupWebSocketHandlers();
        
        // Load initial data
        this.loadInitialData();
      } catch (error) {
        console.error('Connection failed:', error);
        this.addSystemEvent('Failed to connect: ' + error.message);
      }
    },
    
    async disconnect() {
      window.webSocketService.disconnect();
      this.isAttached = false;
    },
    
    setupWebSocketHandlers() {
      // Handle Chaturbate events
      window.webSocketService.on('chaturbate_event', (data) => {
        this.handleChaturbateEvent(data);
      });
      
      window.webSocketService.on('chaturbate_status', (data) => {
        this.addSystemEvent(`Chaturbate status: ${data.status}`);
      });
      
      window.webSocketService.on('chaturbate_error', (data) => {
        this.addSystemEvent(`Chaturbate error: ${data.error}`, 'error');
      });
      
      window.webSocketService.on('private_message', (data) => {
        this.handlePrivateMessage(data);
      });
    },
    
    handleChaturbateEvent(rawData) {
      // Parse event using EventParser
      const parsed = window.EventParser.parseEvent(rawData);
      
      // Format message
      const message = window.EventParser.formatEventMessage(parsed);
      
      // Add to state
      window.stateManager.addEvent(
        parsed.type,
        message,
        new Date(parsed.timestamp * 1000),
        parsed.username,
        { amount: parsed.amount }
      );
      
      // Update UI based on event type
      if (parsed.type === 'user_join' && parsed.username) {
        window.stateManager.addOnlineUser(parsed.username);
      } else if (parsed.type === 'user_leave' && parsed.username) {
        window.stateManager.removeOnlineUser(parsed.username);
      } else if (parsed.type === 'tip' && this.isAttached) {
        // Debounce data refresh
        window.stateManager.debounce('refresh-data', () => {
          this.loadTippers();
          this.loadTotalTips();
        }, 2000);
      }
    },
    
    handlePrivateMessage(data) {
      this.inboxUnreadCount++;
      this.addSystemEvent(`Private message from ${data.from_username}`, 'private_message');
      
      if (this.activeTab === 'inbox') {
        this.loadInboxData();
      }
    },
    
    addSystemEvent(message, type = 'system') {
      window.stateManager.addEvent(type, message);
    },
    
    // Event Management
    clearEvents() {
      window.stateManager.clearEvents();
    },
    
    toggleAutoScroll() {
      // Implement auto-scroll toggle
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
      Object.assign(this, filters);
    },
    
    getEventCategory(eventType) {
      const categoryMap = {
        'tip': 'tip',
        'chat': 'chat',
        'system': 'system',
        'user_join': 'system',
        'user_leave': 'system',
        'media_purchase': 'system',
        'private': 'system',
        'error': 'system'
      };
      return categoryMap[eventType] || 'system';
    },
    
    formatMessageWithClickableUsers(event) {
      if (!event.username) return event.message;
      return window.EventParser.makeUsernameClickable(event.message, event.username);
    },
    
    // Data Loading
    async loadInitialData() {
      await Promise.all([
        this.loadTippers(),
        this.loadTotalTips()
      ]);
    },
    
    async loadTippers() {
      if (!window.stateManager.shouldRefreshTippers()) return;
      
      const result = await window.apiService.getTippers();
      if (result.success && result.tippers) {
        const formatted = result.tippers.map(t => ({
          username: t.username,
          totalTokens: t.total_tokens
        }));
        window.stateManager.updateTopTippers(formatted);
      }
    },
    
    async loadTotalTips() {
      const result = await window.apiService.getTotalTips();
      if (result.success) {
        this.totalTokensToday = result.total_tokens;
      }
    },
    
    async loadInboxData() {
      if (!this.isAuthenticated) return;
      
      const [stats, conversations] = await Promise.all([
        window.apiService.getInboxStats(),
        this.loadConversations()
      ]);
      
      this.inboxUnreadCount = stats.unread_messages || 0;
    },
    
    async loadConversations() {
      // Check cache first
      const cached = window.stateManager.getConversationsCache();
      if (cached) {
        this.conversations = cached;
        return cached;
      }
      
      // Load from API
      const conversations = await window.apiService.getConversations();
      window.stateManager.setConversationsCache(conversations);
      this.conversations = conversations;
      return conversations;
    },
    
    // User interactions
    async handleUserClick(username) {
      this.loadingUserInfo = true;
      this.showUserInfoModal = true;
      this.selectedUserInfo = {
        username: username,
        status: 'Regular',
        stats: null
      };
      
      try {
        // Check cache first
        let stats = window.stateManager.getUserStats(username);
        
        if (!stats && !window.stateManager.isLoadingUserStats(username)) {
          window.stateManager.setLoadingUserStats(username, true);
          stats = await window.apiService.getUserStats(username);
          window.stateManager.setUserStats(username, stats);
          window.stateManager.setLoadingUserStats(username, false);
        }
        
        if (stats) {
          this.selectedUserInfo.stats = stats;
          this.selectedUserInfo.status = stats.user_status || 'Regular';
        }
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
      this.currentConversation = username;
      this.activeView = 'home';
      this.activeTab = 'inbox';
      await this.loadInboxData();
    }
  },
  
  async mounted() {
    // Initialize auth
    await this.checkAuthStatus();
    
    // Handle post-login
    const justLoggedIn = sessionStorage.getItem('auth0_just_logged_in') === 'true';
    if (justLoggedIn) {
      sessionStorage.removeItem('auth0_just_logged_in');
      if (window.userMenu) {
        await window.userMenu.refresh();
      }
    }
    
    // Add welcome message
    setTimeout(() => {
      this.messages.push({
        id: this.messageIdCounter++,
        text: 'Hello! I\'m your AI assistant. How can I help you today?',
        type: 'ai',
        timestamp: new Date()
      });
    }, 500);
  },
  
  beforeUnmount() {
    // Clean up
    window.stateManager.clearAllDebounceTimers();
    window.webSocketService.disconnect();
  }
};

// Make handleUserClick globally accessible
window.vueApp = window.vueApp || {};
window.vueApp.handleUserClick = function(username) {
  const app = document.getElementById('app').__vue_app__.config.globalProperties.$root;
  app.handleUserClick(username);
};

// Export
window.AppRefactored = AppRefactored;