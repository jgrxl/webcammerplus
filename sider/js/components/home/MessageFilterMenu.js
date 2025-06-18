// Message Filter Menu Component
const MessageFilterMenu = {
  name: 'MessageFilterMenu',
  props: {
    showMenu: Boolean,
    sortOrder: String,
    showTippersOnly: Boolean,
    showModeratorsOnly: Boolean,
    enableTipAmountFilter: Boolean,
    minTipAmount: Number
  },
  
  data() {
    return {
      localSortOrder: this.sortOrder,
      localShowTippersOnly: this.showTippersOnly,
      localShowModeratorsOnly: this.showModeratorsOnly,
      localEnableTipAmountFilter: this.enableTipAmountFilter,
      localMinTipAmount: this.minTipAmount
    };
  },
  
  template: `
    <div class="message-filter-menu">
      <button class="filter-menu-btn" @click="$emit('toggle-filter-menu')" title="More filters">
        ⋯
      </button>
      <div v-if="showMenu" class="filter-dropdown">
        <div class="filter-section">
          <h4>Sort Messages</h4>
          <label class="filter-option">
            <input type="radio" v-model="localSortOrder" value="newest" @change="applyFilters">
            <span>Newest First</span>
          </label>
          <label class="filter-option">
            <input type="radio" v-model="localSortOrder" value="oldest" @change="applyFilters">
            <span>Oldest First</span>
          </label>
        </div>
        
        <div class="filter-section">
          <h4>Filter by Users</h4>
          <label class="filter-option">
            <input type="checkbox" v-model="localShowTippersOnly" @change="applyFilters">
            <span>Tippers Only</span>
          </label>
          <label class="filter-option">
            <input type="checkbox" v-model="localShowModeratorsOnly" @change="applyFilters">
            <span>Moderators Only</span>
          </label>
        </div>
        
        <div class="filter-section">
          <h4>Tip Amount Filter</h4>
          <div class="tip-amount-filter">
            <label class="filter-option">
              <input type="checkbox" v-model="localEnableTipAmountFilter" @change="applyFilters">
              <span>Enable tip amount filter</span>
            </label>
            <div v-if="localEnableTipAmountFilter" class="tip-amount-input">
              <label>Minimum tip amount:</label>
              <input 
                type="number" 
                v-model.number="localMinTipAmount" 
                @input="applyFilters"
                min="1" 
                step="1"
              >
            </div>
          </div>
        </div>
        
        <div class="filter-actions">
          <button @click="resetFilters" class="reset-filters-btn">Reset All</button>
        </div>
      </div>
    </div>
  `,
  
  methods: {
    applyFilters() {
      this.$emit('update-filters', {
        sortOrder: this.localSortOrder,
        showTippersOnly: this.localShowTippersOnly,
        showModeratorsOnly: this.localShowModeratorsOnly,
        enableTipAmountFilter: this.localEnableTipAmountFilter,
        minTipAmount: this.localMinTipAmount
      });
    },
    
    resetFilters() {
      this.localSortOrder = 'newest';
      this.localShowTippersOnly = false;
      this.localShowModeratorsOnly = false;
      this.localEnableTipAmountFilter = false;
      this.localMinTipAmount = 1;
      this.applyFilters();
    }
  },
  
  watch: {
    sortOrder(val) { this.localSortOrder = val; },
    showTippersOnly(val) { this.localShowTippersOnly = val; },
    showModeratorsOnly(val) { this.localShowModeratorsOnly = val; },
    enableTipAmountFilter(val) { this.localEnableTipAmountFilter = val; },
    minTipAmount(val) { this.localMinTipAmount = val; }
  }
};

// Register the component
window.componentLoader.register('message-filter-menu', MessageFilterMenu);