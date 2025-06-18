// Chat Module for AI Assistant
class ChatModule {
  constructor() {
    this.messages = [];
    this.messageIdCounter = 1;
    this.isTyping = false;
    this.typingTimeout = null;
  }

  addMessage(text, type = 'user') {
    const message = {
      id: this.messageIdCounter++,
      text: text.trim(),
      type: type,
      timestamp: new Date()
    };
    
    this.messages.push(message);
    
    // Limit message history
    if (this.messages.length > 100) {
      this.messages = this.messages.slice(-100);
    }
    
    return message;
  }

  async sendUserMessage(text) {
    if (!text.trim() || this.isTyping) return null;
    
    // Add user message
    const userMessage = this.addMessage(text, 'user');
    
    // Simulate AI response
    this.simulateAIResponse(text);
    
    return userMessage;
  }

  simulateAIResponse(userMessage) {
    this.setTyping(true);
    
    // Clear any existing timeout
    if (this.typingTimeout) {
      clearTimeout(this.typingTimeout);
    }
    
    // Simulate typing delay
    const delay = 1000 + Math.random() * 2000; // 1-3 seconds
    
    this.typingTimeout = setTimeout(() => {
      const response = this.generateAIResponse(userMessage);
      this.addMessage(response, 'ai');
      this.setTyping(false);
      this.typingTimeout = null;
    }, delay);
  }

  generateAIResponse(userMessage) {
    const responses = [
      `I understand you said: "${userMessage}". How can I help you further?`,
      `That's an interesting question about "${userMessage}". Let me think about that...`,
      `Thank you for asking about "${userMessage}". Here's what I think...`,
      `Great question! Regarding "${userMessage}", I'd suggest...`,
      `I'd be happy to help with "${userMessage}". Here's my perspective...`
    ];
    
    // Add some context-aware responses
    if (userMessage.toLowerCase().includes('hello') || userMessage.toLowerCase().includes('hi')) {
      return `Hello! ${window.TimeFormatter.getTimeGreeting()}! How can I assist you today?`;
    }
    
    if (userMessage.toLowerCase().includes('help')) {
      return 'I can help you with translations, content generation, and managing your Chaturbate stream. What would you like to do?';
    }
    
    if (userMessage.toLowerCase().includes('translate')) {
      return 'I can translate messages for you. Just switch to the Translate tab and enter the text you want to translate!';
    }
    
    return responses[Math.floor(Math.random() * responses.length)];
  }

  setTyping(isTyping) {
    this.isTyping = isTyping;
  }

  clearChat() {
    this.messages = [];
    this.messageIdCounter = 1;
    this.isTyping = false;
    
    if (this.typingTimeout) {
      clearTimeout(this.typingTimeout);
      this.typingTimeout = null;
    }
  }

  getChatState() {
    return {
      messages: this.messages,
      isTyping: this.isTyping
    };
  }

  getMessageCount() {
    return this.messages.length;
  }

  getLastMessage() {
    return this.messages[this.messages.length - 1] || null;
  }

  addWelcomeMessage() {
    this.addMessage("Hello! I'm your AI assistant. How can I help you today?", 'ai');
  }
}

// Export as singleton
window.chatModule = new ChatModule();