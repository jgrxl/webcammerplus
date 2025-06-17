// Attach Button Component
const AttachButton = {
  name: 'AttachButton',
  props: {
    isAttached: {
      type: Boolean,
      default: false
    }
  },
  
  template: `
    <div class="attach-controls">
      <button 
        @click="$emit('toggle-attach')" 
        :class="['attach-button', isAttached ? 'attached' : 'detached']"
      >
        <svg v-if="!isAttached" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/>
          <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>
        </svg>
        <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M18.36 18.36a9 9 0 1 1-12.72 0"/>
          <line x1="12" y1="2" x2="12" y2="12"/>
        </svg>
        <span>{{ isAttached ? 'Detach' : 'Attach' }}</span>
      </button>
    </div>
  `
};

// Register the component
window.componentLoader.register('attach-button', AttachButton);