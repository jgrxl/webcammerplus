// Messages Tab Component
const MessagesTab = {
  name: 'MessagesTab',
  props: {
    events: {
      type: Array,
      default: () => []
    },
    autoScroll: {
      type: Boolean,
      default: true
    },
    messageFilters: {
      type: Array,
      default: () => ['tip', 'chat', 'system']
    },
    showFilterMenu: {
      type: Boolean,
      default: false
    },
    messageSortOrder: {
      type: String,
      default: 'newest'
    },
    showTippersOnly: {
      type: Boolean,
      default: false
    },
    showModeratorsOnly: {
      type: Boolean,
      default: false
    },
    enableTipAmountFilter: {
      type: Boolean,
      default: false
    },
    minTipAmount: {
      type: Number,
      default: 1
    }
  },
  
  template: `
    <div class="messages-tab">
      <div class="events-controls">
        <button @click="$emit('clear-events')" class="clear-btn">Clear</button>
        <button 
          @click="$emit('toggle-auto-scroll')" 
          :class="['auto-scroll-btn', { 'active': autoScroll }]"
        >
          Auto Scroll
        </button>
      </div>
      
      <div class="message-filters">
        <span class="filter-label">Filter:</span>
        <button 
          :class="['message-filter-btn', { 'active': messageFilters.includes('tip') }]" 
          @click="$emit('toggle-message-filter', 'tip')"
        >
          💰 Tips
        </button>
        <button 
          :class="['message-filter-btn', { 'active': messageFilters.includes('chat') }]" 
          @click="$emit('toggle-message-filter', 'chat')"
        >
          💬 Chat
        </button>
        <button 
          :class="['message-filter-btn', { 'active': messageFilters.includes('system') }]" 
          @click="$emit('toggle-message-filter', 'system')"
        >
          ⚙️ System
        </button>
        
        <message-filter-menu
          :show-menu="showFilterMenu"
          :sort-order="messageSortOrder"
          :show-tippers-only="showTippersOnly"
          :show-moderators-only="showModeratorsOnly"
          :enable-tip-amount-filter="enableTipAmountFilter"
          :min-tip-amount="minTipAmount"
          @toggle-filter-menu="$emit('toggle-filter-menu')"
          @update-filters="$emit('update-filters', $event)"
        />
      </div>
      
      <div class="events-container" ref="eventsContainer">
        <div v-if="filteredEvents.length === 0" class="no-events">
          No events to display. Adjust your filters or wait for new events.
        </div>
        <div 
          v-for="event in filteredEvents" 
          :key="event.id" 
          :class="['event-item', event.type]"
        >
          <span class="event-time">{{ formatTime(event.timestamp) }}</span>
          <span class="event-message" v-html="formatMessageWithClickableUsers(event)"></span>
        </div>
      </div>
    </div>
  `,
  
  computed: {
    filteredEvents() {
      return this.$parent.filteredEvents || [];
    }
  },
  
  methods: {
    formatTime(date) {
      const dateObj = typeof date === 'number' ? new Date(date * 1000) : date;
      return dateObj.toLocaleTimeString('en-US', { 
        hour12: false, 
        hour: '2-digit', 
        minute: '2-digit', 
        second: '2-digit' 
      });
    },
    
    formatMessageWithClickableUsers(event) {
      // Use EventParser to make usernames clickable
      if (event.username) {
        return window.EventParser.makeUsernameClickable(event.message, event.username);
      }
      return event.message;
    }
  },
  
  mounted() {
    // Set up auto-scroll
    if (this.autoScroll) {
      this.$nextTick(() => {
        const container = this.$refs.eventsContainer;
        if (container) {
          container.scrollTop = container.scrollHeight;
        }
      });
    }
  },
  
  updated() {
    // Auto-scroll on new events
    if (this.autoScroll) {
      this.$nextTick(() => {
        const container = this.$refs.eventsContainer;
        if (container) {
          container.scrollTop = container.scrollHeight;
        }
      });
    }
  }
};

// Register the component
window.componentLoader.register('messages-tab', MessagesTab);