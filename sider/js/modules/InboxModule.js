// Inbox Module for Message Management
class InboxModule {
  constructor() {
    this.conversations = [];
    this.currentConversation = null;
    this.currentMessages = [];
    this.unreadCount = 0;
    this.loadingMessages = false;
    this.lastConversationsLoadTime = 0;
    this.conversationsLoadInterval = 30000; // 30 seconds
  }

  async loadInboxData() {
    const authState = window.authModule.getAuthState();
    if (!authState.isAuthenticated) {
      console.warn('User not authenticated, skipping inbox load');
      return { stats: null, conversations: [] };
    }

    try {
      const [stats, conversations] = await Promise.all([
        window.apiService.getInboxStats(),
        this.loadConversations()
      ]);

      this.unreadCount = stats.unread_messages || 0;
      return { stats, conversations };
    } catch (error) {
      console.error('Failed to load inbox data:', error);
      return { stats: null, conversations: [] };
    }
  }

  async loadConversations(forceRefresh = false) {
    const now = Date.now();
    const timeSinceLastLoad = now - this.lastConversationsLoadTime;
    
    // Use cache if available and not forcing refresh
    if (!forceRefresh && this.conversations.length > 0 && timeSinceLastLoad < this.conversationsLoadInterval) {
      return this.conversations;
    }

    try {
      const conversations = await window.apiService.getConversations();
      this.conversations = conversations;
      this.lastConversationsLoadTime = now;
      return conversations;
    } catch (error) {
      console.error('Failed to load conversations:', error);
      return this.conversations; // Return cached if available
    }
  }

  async selectConversation(username) {
    this.currentConversation = username;
    this.currentMessages = [];
    return await this.loadMessages(username);
  }

  async loadMessages(username) {
    if (!username) return [];
    
    this.loadingMessages = true;
    
    try {
      const messages = await window.apiService.getMessages(username);
      this.currentMessages = messages;
      
      // Auto-mark as read
      await this.markConversationAsRead(username);
      
      return messages;
    } catch (error) {
      console.error('Failed to load messages:', error);
      return [];
    } finally {
      this.loadingMessages = false;
    }
  }

  async markConversationAsRead(username) {
    if (!username || !this.currentMessages.length) return;

    try {
      const unreadMessages = this.currentMessages.filter(msg => !msg.is_read && !msg.is_sent);
      
      for (const msg of unreadMessages) {
        await window.apiService.markMessageAsRead(msg.id);
      }
      
      // Update local state
      this.currentMessages.forEach(msg => {
        if (!msg.is_sent) msg.is_read = true;
      });
      
      // Update unread count
      const conversation = this.conversations.find(c => c.from_user === username);
      if (conversation) {
        this.unreadCount -= conversation.unread_count || 0;
        conversation.unread_count = 0;
      }
      
      return true;
    } catch (error) {
      console.error('Failed to mark messages as read:', error);
      return false;
    }
  }

  handleNewPrivateMessage(data) {
    // Update unread count
    this.unreadCount++;
    
    // Update conversation if it exists
    const existingConv = this.conversations.find(c => c.from_user === data.from_username);
    if (existingConv) {
      existingConv.last_message = data.message;
      existingConv.last_message_time = new Date().toISOString();
      existingConv.unread_count = (existingConv.unread_count || 0) + 1;
    } else {
      // Add new conversation
      this.conversations.unshift({
        from_user: data.from_username,
        last_message: data.message,
        last_message_time: new Date().toISOString(),
        unread_count: 1
      });
    }
    
    // If viewing this conversation, load the new message
    if (this.currentConversation === data.from_username) {
      this.loadMessages(data.from_username);
    }
  }

  getInboxState() {
    return {
      conversations: this.conversations,
      currentConversation: this.currentConversation,
      currentMessages: this.currentMessages,
      unreadCount: this.unreadCount,
      loadingMessages: this.loadingMessages
    };
  }

  clearInboxCache() {
    this.conversations = [];
    this.lastConversationsLoadTime = 0;
  }
}

// Export as singleton
window.inboxModule = new InboxModule();