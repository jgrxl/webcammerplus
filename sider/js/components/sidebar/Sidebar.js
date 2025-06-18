// Sidebar Component
const Sidebar = {
  name: 'Sidebar',
  props: {
    expanded: {
      type: Boolean,
      default: false
    },
    isAuthenticated: {
      type: Boolean,
      default: false
    },
    user: {
      type: Object,
      default: null
    },
    activeView: {
      type: String,
      default: 'home'
    }
  },
  
  template: `
    <div class="sidebar-container">
      <!-- Hamburger menu when collapsed -->
      <div v-if="!expanded" class="hamburger-menu-collapsed" @click="$emit('toggle-sidebar')">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="3" y1="6" x2="21" y2="6"/>
          <line x1="3" y1="12" x2="21" y2="12"/>
          <line x1="3" y1="18" x2="21" y2="18"/>
        </svg>
      </div>
      
      <!-- Expanded sidebar -->
      <div v-if="expanded" class="sidebar sidebar-expanded">
        <!-- Close button -->
        <div class="sidebar-close" @click="$emit('toggle-sidebar')">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"/>
            <line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </div>
        
        <!-- Navigation icons -->
        <div 
          :class="['sidebar-icon', 'home-icon', { active: activeView === 'home' }]" 
          @click="$emit('navigate', 'home')"
          title="Home"
        >
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
            <polyline points="9 22 9 12 15 12 15 22"/>
          </svg>
        </div>
        
        <div 
          :class="['sidebar-icon', 'chat-icon', { active: activeView === 'chat' }]" 
          @click="$emit('navigate', 'chat')"
          title="Chat"
        >
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
          </svg>
        </div>
        
        <div 
          :class="['sidebar-icon', 'edit-icon', { active: activeView === 'edit' }]" 
          @click="$emit('navigate', 'edit')"
          title="Edit & Write"
        >
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
          </svg>
        </div>
        
        <div 
          :class="['sidebar-icon', 'translate-icon', { active: activeView === 'translate' }]" 
          @click="$emit('navigate', 'translate')"
          title="Translate"
        >
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12.913 17H21m-8.087 0l-2.75-7.25M12.913 17l2.75-7.25M10.163 9.75l2.75 7.25m0-7.25h5.5m-5.5 0L11 6.5M3 5.5h7m0 0l1.163 3.25M3 5.5V10m0-4.5v-2m7 2l1.163 3.25M3 10v2.5m0-2.5h4.163m0 0L10.163 9.75"/>
          </svg>
        </div>
        
        
        <!-- Profile/Auth Icon -->
        <div 
          :class="['sidebar-icon', 'profile-icon', isAuthenticated ? 'authenticated' : 'unauthenticated']" 
          @click="$emit('toggle-auth')" 
          :title="isAuthenticated ? \`Logout \${user?.name || 'User'}\` : 'Login'"
        >
          <svg v-if="!isAuthenticated" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"/>
            <polyline points="10,17 15,12 10,7"/>
            <line x1="15" y1="12" x2="3" y2="12"/>
          </svg>
          <img v-else-if="user?.picture" :src="user.picture" :alt="user.name" style="width: 24px; height: 24px; border-radius: 50%; object-fit: cover;">
          <svg v-else width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
            <circle cx="12" cy="7" r="4"/>
          </svg>
        </div>
      </div>
    </div>
  `,
  
  methods: {
    // Methods are handled via events to parent
  }
};

// Register the component
window.componentLoader.register('sidebar-component', Sidebar);