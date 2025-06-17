// Home View Component
const HomeView = {
  name: 'HomeView',
  props: {
    isAttached: {
      type: Boolean,
      default: false
    },
    activeTab: {
      type: String,
      default: 'messages'
    },
    onlineUsers: {
      type: Number,
      default: 0
    },
    inboxUnreadCount: {
      type: Number,
      default: 0
    }
  },
  
  template: `
    <div class="home-content">
      <div class="content-header">
        <h1>WebCammer+</h1>
        <div class="connection-status" v-if="isAttached">
          <div class="status-dot connected"></div>
          <span>Connected to Chaturbate</span>
        </div>
      </div>
      
      <!-- Not attached state -->
      <div v-if="!isAttached" class="blank-content">
        <div class="blank-placeholder">
          <div class="blank-icon">🤖</div>
          <h2>Welcome to WebCammer+</h2>
          <p>Your AI-powered assistant is ready to help. Click the "Attach" button below to connect to Chaturbate and start receiving events.</p>
        </div>
      </div>
      
      <!-- Attached state with tabs -->
      <div v-if="isAttached" class="chaturbate-interface">
        <!-- Tab Navigation -->
        <div class="tab-navigation">
          <div 
            :class="['tab-item', { 'active': activeTab === 'messages' }]" 
            @click="$emit('switch-tab', 'messages')"
          >
            CHAT
          </div>
          <div 
            :class="['tab-item', { 'active': activeTab === 'inbox' }]" 
            @click="$emit('switch-tab', 'inbox')"
          >
            INBOX <span v-if="inboxUnreadCount > 0" class="unread-badge">{{ inboxUnreadCount }}</span>
          </div>
          <div 
            :class="['tab-item', { 'active': activeTab === 'tippers' }]" 
            @click="$emit('switch-tab', 'tippers')"
          >
            TIPPERS
          </div>
          <div 
            :class="['tab-item', { 'active': activeTab === 'ranking' }]" 
            @click="$emit('switch-tab', 'ranking')"
          >
            RANKING
          </div>
          <div 
            :class="['tab-item', { 'active': activeTab === 'users' }]" 
            @click="$emit('switch-tab', 'users')"
          >
            USERS ({{ onlineUsers }})
          </div>
          <div class="tab-controls">
            <button class="settings-btn" title="Settings">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="3"/>
                <path d="M12 1v6m0 6v6m11-7h-6m-6 0H1"/>
              </svg>
            </button>
          </div>
        </div>
        
        <!-- Tab Content (slot for different tab components) -->
        <div class="tab-content">
          <slot :name="activeTab"></slot>
        </div>
      </div>
      
      <!-- Attach/Detach Button -->
      <attach-button 
        :is-attached="isAttached"
        @toggle-attach="$emit('toggle-attach')"
      />
    </div>
  `
};

// Register the component
window.componentLoader.register('home-view', HomeView);