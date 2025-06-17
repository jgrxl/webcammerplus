// State Manager Service
class StateManager {
  constructor() {
    this.state = {
      // Events and Messages
      events: [],
      eventIdCounter: 1,
      maxEvents: 1000,
      
      // User Statistics Cache
      userStatsCache: new Map(),
      userStatsCacheDuration: 300000, // 5 minutes
      userStatsLoading: new Set(),
      
      // Conversation Cache
      conversationsCache: [],
      conversationsCacheTime: 0,
      conversationsCacheDuration: 30000, // 30 seconds
      
      // Tipper Statistics
      topTippers: [],
      tippersLastRefresh: 0,
      tippersRefreshInterval: 10000, // 10 seconds
      
      // Online Users
      onlineUsers: new Map(),
      
      // Debounce Timers
      debounceTimers: new Map()
    };
  }

  // Event Management
  addEvent(type, message, timestamp = new Date(), username = null, data = {}) {
    const event = {
      id: this.state.eventIdCounter++,
      type,
      message,
      timestamp,
      username,
      ...data
    };
    
    this.state.events.push(event);
    
    // Limit events array size
    if (this.state.events.length > this.state.maxEvents) {
      this.state.events = this.state.events.slice(-this.state.maxEvents);
    }
    
    return event;
  }

  getEvents() {
    return this.state.events;
  }

  clearEvents() {
    this.state.events = [];
    this.state.eventIdCounter = 1;
  }

  // User Stats Cache Management
  getUserStats(username) {
    const cached = this.state.userStatsCache.get(username);
    if (cached && Date.now() - cached.timestamp < this.state.userStatsCacheDuration) {
      return cached.data;
    }
    return null;
  }

  setUserStats(username, stats) {
    this.state.userStatsCache.set(username, {
      data: stats,
      timestamp: Date.now()
    });
  }

  isLoadingUserStats(username) {
    return this.state.userStatsLoading.has(username);
  }

  setLoadingUserStats(username, loading) {
    if (loading) {
      this.state.userStatsLoading.add(username);
    } else {
      this.state.userStatsLoading.delete(username);
    }
  }

  clearUserStatsCache() {
    this.state.userStatsCache.clear();
    this.state.userStatsLoading.clear();
  }

  // Conversation Cache Management
  getConversationsCache() {
    const now = Date.now();
    if (this.state.conversationsCache.length > 0 && 
        now - this.state.conversationsCacheTime < this.state.conversationsCacheDuration) {
      return this.state.conversationsCache;
    }
    return null;
  }

  setConversationsCache(conversations) {
    this.state.conversationsCache = conversations;
    this.state.conversationsCacheTime = Date.now();
  }

  // Online Users Management
  addOnlineUser(username, userData = {}) {
    this.state.onlineUsers.set(username, {
      username,
      status: userData.status || 'Regular',
      joinedAt: Date.now(),
      ...userData
    });
  }

  removeOnlineUser(username) {
    this.state.onlineUsers.delete(username);
  }

  getOnlineUsers() {
    return Array.from(this.state.onlineUsers.values());
  }

  getOnlineUsersCount() {
    return this.state.onlineUsers.size;
  }

  isUserOnline(username) {
    return this.state.onlineUsers.has(username);
  }

  // Tipper Management
  updateTopTippers(tippers) {
    this.state.topTippers = tippers;
    this.state.tippersLastRefresh = Date.now();
  }

  getTopTippers() {
    return this.state.topTippers;
  }

  shouldRefreshTippers() {
    return Date.now() - this.state.tippersLastRefresh > this.state.tippersRefreshInterval;
  }

  // Debounce Helper
  debounce(key, callback, delay) {
    // Clear existing timer
    if (this.state.debounceTimers.has(key)) {
      clearTimeout(this.state.debounceTimers.get(key));
    }
    
    // Set new timer
    const timerId = setTimeout(() => {
      callback();
      this.state.debounceTimers.delete(key);
    }, delay);
    
    this.state.debounceTimers.set(key, timerId);
  }

  // Clear all debounce timers
  clearAllDebounceTimers() {
    this.state.debounceTimers.forEach(timerId => clearTimeout(timerId));
    this.state.debounceTimers.clear();
  }

  // Get state summary for debugging
  getStateSummary() {
    return {
      eventsCount: this.state.events.length,
      onlineUsersCount: this.state.onlineUsers.size,
      cachedUserStats: this.state.userStatsCache.size,
      loadingUserStats: this.state.userStatsLoading.size,
      topTippersCount: this.state.topTippers.length,
      conversationsCached: this.state.conversationsCache.length > 0
    };
  }
}

// Export as singleton
window.stateManager = new StateManager();