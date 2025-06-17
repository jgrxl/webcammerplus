// User Info Modal Component
const UserInfoModal = {
  name: 'UserInfoModal',
  props: {
    userInfo: {
      type: Object,
      default: null
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  
  template: `
    <div class="modal-overlay" @click="$emit('close')">
      <div class="modal-content user-info-modal" @click.stop>
        <div class="modal-header">
          <h3>User Information</h3>
          <button class="modal-close" @click="$emit('close')">&times;</button>
        </div>
        
        <div class="modal-body">
          <div v-if="loading" class="loading">
            Loading user information...
          </div>
          
          <div v-else-if="userInfo" class="user-info-content">
            <div class="user-header">
              <div class="user-avatar-large">
                <span>{{ userInfo.username.charAt(0).toUpperCase() }}</span>
              </div>
              <div class="user-details">
                <h2>{{ userInfo.username }}</h2>
                <span :class="['user-status', 'status-' + userInfo.status.toLowerCase()]">
                  {{ userInfo.status }}
                </span>
              </div>
            </div>
            
            <div v-if="userInfo.stats" class="user-stats">
              <div class="stat-row">
                <span class="stat-label">Total Tips:</span>
                <span class="stat-value">{{ userInfo.stats.total_tips || 0 }} tips</span>
              </div>
              <div class="stat-row">
                <span class="stat-label">Total Amount:</span>
                <span class="stat-value">{{ userInfo.stats.total_tip_amount || 0 }} tokens</span>
              </div>
              <div class="stat-row">
                <span class="stat-label">Last Tip:</span>
                <span class="stat-value">{{ formatTimeAgo(userInfo.stats.last_tip_time) }}</span>
              </div>
              <div class="stat-row">
                <span class="stat-label">Last Message:</span>
                <span class="stat-value">{{ formatTimeAgo(userInfo.stats.last_message_time) }}</span>
              </div>
            </div>
            
            <div class="modal-actions">
              <button class="btn btn-primary" @click="$emit('start-message', userInfo.username)">
                Send Private Message
              </button>
              <button class="btn btn-secondary" @click="openProfile">
                View Profile
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  
  methods: {
    formatTimeAgo(timestamp) {
      if (!timestamp) return 'Never';
      
      const date = new Date(timestamp);
      const now = new Date();
      const diff = now - date;

      if (diff < 60000) {
        return 'Just now';
      } else if (diff < 3600000) {
        return `${Math.floor(diff / 60000)}m ago`;
      } else if (diff < 86400000) {
        return `${Math.floor(diff / 3600000)}h ago`;
      } else if (diff < 604800000) {
        return `${Math.floor(diff / 86400000)}d ago`;
      } else {
        return date.toLocaleDateString();
      }
    },
    
    openProfile() {
      if (this.userInfo && this.userInfo.username) {
        const profileUrl = `https://chaturbate.com/${this.userInfo.username}`;
        window.open(profileUrl, '_blank');
      }
    }
  }
};

// Register the component
window.componentLoader.register('user-info-modal', UserInfoModal);