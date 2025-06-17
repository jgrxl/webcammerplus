// Ultra Slim App Component - Minimal orchestration layer
const AppUltraSlim = {
  name: 'AppUltraSlim',
  
  data() {
    return {
      // UI State only
      sidebarExpanded: false,
      activeView: 'home',
      activeTab: 'messages',
      showFilterMenu: false,
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
              :auto-scroll="true"
              :message-filters="messageFilters"
              :show-filter-menu="showFilterMenu"
              :message-sort-order="sortOrder"
              :show-tippers-only="showTippersOnly"
              :show-moderators-only="showModeratorsOnly"
              :enable-tip-amount-filter="enableTipAmountFilter"
              :min-tip-amount="minTipAmount"
              @clear-events="clearEvents"
              @toggle-auto-scroll="toggleAutoScroll"
              @toggle-message-filter="toggleMessageFilter"
              @toggle-filter-menu="toggleFilterMenu"
              @update-filters="updateFilters"
            />
          </template>
          
          <!-- Other tabs -->
          <template #inbox>
            <div class="inbox-tab">Inbox ({{ inboxState.conversations.length }} conversations)</div>
          </template>
          
          <template #tippers>
            <analytics-view @view-user="handleUserClick" />
          </template>
        </home-view>
        
        <!-- Chat View -->
        <chat-view
          v-if="activeView === 'chat'"
          :messages="chatMessages"
          :is-typing="isChatTyping"
          @send-message="sendChatMessage"
        />
        
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
    // Auth computed
    isAuthenticated() {
      return window.authModule.isAuthenticated;
    },
    user() {
      return window.authModule.user;
    },
    
    // WebSocket computed
    isAttached() {
      return window.webSocketService.isConnected;
    },
    
    // State computed
    events() {
      return window.stateManager.getEvents();
    },
    onlineUsersCount() {
      return window.stateManager.getOnlineUsersCount();
    },
    topTippers() {
      return window.stateManager.getTopTippers();
    },
    
    // Filter computed
    filters() {
      return window.filterModule.getFilters();
    },
    messageFilters() {
      return this.filters.messageTypes;
    },
    sortOrder() {
      return this.filters.sortOrder;
    },
    showTippersOnly() {
      return this.filters.showTippersOnly;
    },
    showModeratorsOnly() {
      return this.filters.showModeratorsOnly;
    },
    enableTipAmountFilter() {
      return this.filters.enableTipAmountFilter;
    },
    minTipAmount() {
      return this.filters.minTipAmount;
    },
    filteredEvents() {
      return window.filterModule.filterEvents(this.events);
    },
    
    // Inbox computed
    inboxState() {
      return window.inboxModule.getInboxState();
    },
    inboxUnreadCount() {
      return this.inboxState.unreadCount;
    },
    
    // Chat computed
    chatState() {
      return window.chatModule.getChatState();
    },
    chatMessages() {
      return this.chatState.messages;
    },
    isChatTyping() {
      return this.chatState.isTyping;
    }
  },
  
  methods: {
    // UI Methods
    toggleSidebar() {
      this.sidebarExpanded = !this.sidebarExpanded;
    },
    navigateToView(view) {
      this.activeView = view;
    },
    switchTab(tab) {
      this.activeTab = tab;
      this.onTabSwitch(tab);
    },
    toggleFilterMenu() {
      this.showFilterMenu = !this.showFilterMenu;
    },
    
    // Auth delegation
    async toggleAuth() {
      if (this.isAuthenticated) {
        window.userMenu?.toggleDropdown();
      } else {
        await window.authModule.login();
      }
    },
    
    // WebSocket delegation
    async toggleAttach() {
      if (this.isAttached) {
        window.webSocketService.disconnect();
      } else {
        await this.connectToChaturbate();
      }
    },
    
    async connectToChaturbate() {
      const healthy = await window.apiService.checkHealth();
      if (!healthy) {
        window.stateManager.addEvent('error', 'Backend server not available');
        return;
      }
      
      await window.webSocketService.connect();
      this.setupEventHandlers();
      this.loadInitialData();
    },
    
    setupEventHandlers() {
      window.webSocketService.on('chaturbate_event', this.handleChaturbateEvent);
      window.webSocketService.on('private_message', this.handlePrivateMessage);
    },
    
    handleChaturbateEvent(data) {
      const parsed = window.EventParser.parseEvent(data);
      const message = window.EventParser.formatEventMessage(parsed);
      
      window.stateManager.addEvent(
        parsed.type,
        message,
        new Date(parsed.timestamp * 1000),
        parsed.username,
        { amount: parsed.amount }
      );
      
      if (parsed.type === 'user_join' && parsed.username) {
        window.stateManager.addOnlineUser(parsed.username);
      } else if (parsed.type === 'user_leave' && parsed.username) {
        window.stateManager.removeOnlineUser(parsed.username);
      }
    },
    
    handlePrivateMessage(data) {
      window.inboxModule.handleNewPrivateMessage(data);
    },
    
    // Filter delegation
    clearEvents() {
      window.stateManager.clearEvents();
    },
    toggleAutoScroll() {
      // Implement if needed
    },
    toggleMessageFilter(type) {
      window.filterModule.toggleMessageType(type);
    },
    updateFilters(filters) {
      window.filterModule.updateFilters(filters);
    },
    
    // Chat delegation
    sendChatMessage(text) {
      window.chatModule.sendUserMessage(text);
    },
    
    // Data loading
    async loadInitialData() {
      await Promise.all([
        window.apiService.getTippers().then(result => {
          if (result.success) {
            window.stateManager.updateTopTippers(result.tippers.map(t => ({
              username: t.username,
              totalTokens: t.total_tokens
            })));
          }
        }),
        window.apiService.getTotalTips()
      ]);
    },
    
    async onTabSwitch(tab) {
      if (tab === 'inbox') {
        await window.inboxModule.loadInboxData();
      } else if (tab === 'tippers' && window.stateManager.shouldRefreshTippers()) {
        this.loadInitialData();
      }
    },
    
    // User modal
    async handleUserClick(username) {
      this.showUserInfoModal = true;
      this.loadingUserInfo = true;
      this.selectedUserInfo = { username, status: 'Loading...', stats: null };
      
      const stats = await window.apiService.getUserStats(username);
      if (stats) {
        this.selectedUserInfo = {
          username,
          status: stats.user_status || 'Regular',
          stats
        };
      }
      this.loadingUserInfo = false;
    },
    
    closeUserInfoModal() {
      this.showUserInfoModal = false;
      this.selectedUserInfo = null;
    },
    
    async startPrivateMessage(username) {
      this.closeUserInfoModal();
      this.activeView = 'home';
      this.activeTab = 'inbox';
      await window.inboxModule.selectConversation(username);
    }
  },
  
  async mounted() {
    // Initialize auth
    await window.authModule.checkAuthStatus();
    await window.authModule.handlePostLogin();
    
    // Start periodic auth check
    window.authModule.startPeriodicAuthCheck((authState) => {
      this.$forceUpdate();
    });
    
    // Add welcome message
    setTimeout(() => {
      window.chatModule.addWelcomeMessage();
    }, 500);
  },
  
  beforeUnmount() {
    window.authModule.stopPeriodicAuthCheck();
    window.stateManager.clearAllDebounceTimers();
    window.webSocketService.disconnect();
  }
};

// Global handler for clickable usernames
window.vueApp = window.vueApp || {};
window.vueApp.handleUserClick = function(username) {
  const app = document.getElementById('app').__vue_app__.config.globalProperties.$root;
  app.handleUserClick(username);
};

window.AppUltraSlim = AppUltraSlim;