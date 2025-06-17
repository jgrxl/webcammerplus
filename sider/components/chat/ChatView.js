// Chat View Component
const ChatView = {
  name: 'ChatView',
  props: {
    messages: {
      type: Array,
      default: () => []
    },
    isTyping: {
      type: Boolean,
      default: false
    }
  },
  
  data() {
    return {
      currentMessage: ''
    };
  },
  
  template: `
    <div class="chat-content">
      <div class="content-header">
        <h1>AI Assistant</h1>
      </div>
      
      <!-- Messages Area -->
      <div class="messages-area" ref="messagesArea">
        <div v-for="message in messages" :key="message.id" :class="['message', message.type]">
          <div class="message-content">{{ message.text }}</div>
          <div class="message-time">{{ formatTime(message.timestamp) }}</div>
        </div>
        
        <!-- Typing Indicator -->
        <div v-if="isTyping" class="message ai typing">
          <div class="typing-indicator">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
          </div>
        </div>
      </div>
      
      <!-- Chat Input -->
      <div class="chat-input">
        <div class="input-container">
          <textarea 
            v-model="currentMessage" 
            @keydown="handleKeyPress"
            :disabled="isTyping"
            class="message-input" 
            placeholder="Type your message..."
            rows="1">
          </textarea>
          <button 
            @click="sendMessage" 
            :disabled="!currentMessage.trim() || isTyping"
            class="send-button">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
  `,
  
  methods: {
    formatTime(timestamp) {
      return new Date(timestamp).toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit' 
      });
    },
    
    handleKeyPress(event) {
      if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        this.sendMessage();
      }
    },
    
    sendMessage() {
      if (!this.currentMessage.trim() || this.isTyping) return;
      
      this.$emit('send-message', this.currentMessage.trim());
      this.currentMessage = '';
    },
    
    scrollToBottom() {
      this.$nextTick(() => {
        const messagesArea = this.$refs.messagesArea;
        if (messagesArea) {
          messagesArea.scrollTop = messagesArea.scrollHeight;
        }
      });
    }
  },
  
  watch: {
    messages() {
      this.scrollToBottom();
    },
    isTyping() {
      this.scrollToBottom();
    }
  },
  
  mounted() {
    this.scrollToBottom();
  }
};

// Register the component
window.componentLoader.register('chat-view', ChatView);