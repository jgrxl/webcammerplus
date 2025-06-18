// FilterModule.test.js

// Since FilterModule is a singleton on window, we need to test it differently
describe('FilterModule', () => {
  let filterModule;
  let originalFilters;

  beforeEach(() => {
    // Load the module
    require('./FilterModule.js');
    filterModule = window.filterModule;
    
    // Save original state
    originalFilters = filterModule.getFilters();
    
    // Reset to defaults for each test
    filterModule.resetFilters();
  });

  afterEach(() => {
    // Clean up
    filterModule.resetFilters();
  });

  describe('toggleMessageType', () => {
    it('should toggle message types on and off', () => {
      // Initially all types should be included
      expect(filterModule.filters.messageTypes).toContain('tip');
      
      // Toggle off
      filterModule.toggleMessageType('tip');
      expect(filterModule.filters.messageTypes).not.toContain('tip');
      
      // Toggle back on
      filterModule.toggleMessageType('tip');
      expect(filterModule.filters.messageTypes).toContain('tip');
    });
  });

  describe('updateFilters', () => {
    it('should update filter settings', () => {
      filterModule.updateFilters({
        showTippersOnly: true,
        minTipAmount: 50,
        sortOrder: 'desc'
      });
      
      expect(filterModule.filters.showTippersOnly).toBe(true);
      expect(filterModule.filters.minTipAmount).toBe(50);
      expect(filterModule.filters.sortOrder).toBe('desc');
    });

    it('should not override unspecified filters', () => {
      const originalTypes = [...filterModule.filters.messageTypes];
      
      filterModule.updateFilters({
        showTippersOnly: true
      });
      
      expect(filterModule.filters.messageTypes).toEqual(originalTypes);
    });
  });

  describe('filterEvents', () => {
    const testEvents = [
      { id: 1, type: 'tip', message: 'User1 tipped 100', amount: 100, username: 'User1', timestamp: new Date('2024-01-01T10:00:00') },
      { id: 2, type: 'chat', message: 'User2: Hello', username: 'User2', timestamp: new Date('2024-01-01T10:01:00') },
      { id: 3, type: 'tip', message: 'User3 tipped 25', amount: 25, username: 'User3', timestamp: new Date('2024-01-01T10:02:00') },
      { id: 4, type: 'system', message: 'Room subject changed', timestamp: new Date('2024-01-01T10:03:00') }
    ];

    it('should filter by message types', () => {
      filterModule.toggleMessageType('chat');
      filterModule.toggleMessageType('system');
      
      const filtered = filterModule.filterEvents(testEvents);
      
      expect(filtered).toHaveLength(2);
      expect(filtered.every(e => e.type === 'tip')).toBe(true);
    });

    it('should filter by minimum tip amount', () => {
      filterModule.updateFilters({
        enableTipAmountFilter: true,
        minTipAmount: 50
      });
      
      const filtered = filterModule.filterEvents(testEvents);
      
      expect(filtered).toHaveLength(3); // Only the 25 token tip is filtered out
      expect(filtered.find(e => e.amount === 25)).toBeUndefined();
    });

    it('should show only tippers when enabled', () => {
      filterModule.updateFilters({
        showTippersOnly: true
      });
      
      const filtered = filterModule.filterEvents(testEvents);
      
      expect(filtered).toHaveLength(2);
      expect(filtered.every(e => e.type === 'tip')).toBe(true);
    });

    it('should sort events by timestamp', () => {
      filterModule.updateFilters({
        sortOrder: 'desc'
      });
      
      const filtered = filterModule.filterEvents(testEvents);
      
      expect(filtered[0].id).toBe(4); // Most recent first
      expect(filtered[filtered.length - 1].id).toBe(1); // Oldest last
    });

    it('should handle empty events array', () => {
      const filtered = filterModule.filterEvents([]);
      
      expect(filtered).toEqual([]);
    });

    it('should handle null/undefined events', () => {
      expect(filterModule.filterEvents(null)).toEqual([]);
      expect(filterModule.filterEvents(undefined)).toEqual([]);
    });
  });

  describe('resetFilters', () => {
    it('should reset all filters to defaults', () => {
      // Change some filters
      filterModule.updateFilters({
        showTippersOnly: true,
        minTipAmount: 100,
        sortOrder: 'desc'
      });
      filterModule.toggleMessageType('chat');
      
      // Reset
      filterModule.resetFilters();
      
      // Check all are back to defaults
      expect(filterModule.filters.showTippersOnly).toBe(false);
      expect(filterModule.filters.minTipAmount).toBe(0);
      expect(filterModule.filters.sortOrder).toBe('asc');
      expect(filterModule.filters.messageTypes).toContain('chat');
    });
  });
});