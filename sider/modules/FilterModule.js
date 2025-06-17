// Filter Module for Message Filtering
class FilterModule {
  constructor() {
    this.filters = {
      messageTypes: ['tip', 'chat', 'system'],
      sortOrder: 'newest',
      showTippersOnly: false,
      showModeratorsOnly: false,
      enableTipAmountFilter: false,
      minTipAmount: 1
    };
    
    this.categoryMap = {
      'tip': 'tip',
      'chat': 'chat',
      'system': 'system',
      'user_join': 'system',
      'user_leave': 'system',
      'media_purchase': 'system',
      'private': 'system',
      'private_message': 'system',
      'error': 'system'
    };
  }

  getFilters() {
    return { ...this.filters };
  }

  updateFilters(updates) {
    Object.assign(this.filters, updates);
  }

  toggleMessageType(type) {
    const index = this.filters.messageTypes.indexOf(type);
    if (index > -1) {
      this.filters.messageTypes.splice(index, 1);
    } else {
      this.filters.messageTypes.push(type);
    }
  }

  resetFilters() {
    this.filters = {
      messageTypes: ['tip', 'chat', 'system'],
      sortOrder: 'newest',
      showTippersOnly: false,
      showModeratorsOnly: false,
      enableTipAmountFilter: false,
      minTipAmount: 1
    };
  }

  getEventCategory(eventType) {
    return this.categoryMap[eventType] || 'system';
  }

  filterEvents(events) {
    if (this.filters.messageTypes.length === 0) return [];
    
    let filtered = events.filter(event => {
      // Type filtering
      const eventCategory = this.getEventCategory(event.type);
      if (!this.filters.messageTypes.includes(eventCategory)) return false;

      // Tippers only filter
      if (this.filters.showTippersOnly && eventCategory !== 'tip') return false;

      // Moderators only filter
      if (this.filters.showModeratorsOnly) {
        const isModerator = event.message && (
          event.message.includes('Moderator') || 
          event.username === 'ModeratorX' ||
          event.userStatus === 'Moderator'
        );
        if (!isModerator) return false;
      }

      // Tip amount filter
      if (this.filters.enableTipAmountFilter && eventCategory === 'tip') {
        const amount = event.amount || 0;
        if (amount < this.filters.minTipAmount) return false;
      }

      return true;
    });

    // Apply sorting
    if (this.filters.sortOrder === 'oldest') {
      filtered = filtered.slice().reverse();
    }

    return filtered;
  }

  // Get filter summary for UI
  getActiveFilterCount() {
    let count = 0;
    if (this.filters.showTippersOnly) count++;
    if (this.filters.showModeratorsOnly) count++;
    if (this.filters.enableTipAmountFilter) count++;
    if (this.filters.sortOrder !== 'newest') count++;
    return count;
  }

  // Export current filter state
  exportFilterState() {
    return JSON.stringify(this.filters);
  }

  // Import filter state
  importFilterState(jsonString) {
    try {
      const imported = JSON.parse(jsonString);
      this.filters = { ...this.filters, ...imported };
      return true;
    } catch (error) {
      console.error('Failed to import filter state:', error);
      return false;
    }
  }
}

// Export as singleton
window.filterModule = new FilterModule();