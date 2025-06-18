// Event Parser Helper
class EventParser {
  
  // Parse Chaturbate event and extract relevant information
  static parseEvent(data) {
    const parsed = {
      type: data.type || 'unknown',
      username: null,
      message: '',
      amount: null,
      timestamp: data.timestamp || Date.now() / 1000,
      raw: data
    };

    // Extract username and message based on event type
    switch (data.type) {
      case 'tip':
        parsed.username = data.username || data.from_username || this.extractUsernameFromMessage(data.message, 'tip');
        parsed.amount = data.amount || this.extractAmountFromMessage(data.message);
        parsed.message = data.message || `${parsed.username} tipped ${parsed.amount} tokens`;
        break;

      case 'chat':
        parsed.username = data.username || data.from_username || this.extractUsernameFromMessage(data.message, 'chat');
        parsed.message = data.message || '';
        break;

      case 'private_message':
      case 'private':
        parsed.username = data.from_username || data.username || 'Unknown';
        parsed.message = data.message || 'Private message received';
        break;

      case 'user_join':
        parsed.username = data.username || this.extractUsernameFromMessage(data.message, 'join');
        parsed.message = data.message || `${parsed.username} joined the room`;
        break;

      case 'user_leave':
        parsed.username = data.username || this.extractUsernameFromMessage(data.message, 'leave');
        parsed.message = data.message || `${parsed.username} left the room`;
        break;

      case 'media_purchase':
        parsed.username = data.username || data.buyer || 'Unknown';
        parsed.message = data.message || `${parsed.username} purchased media`;
        break;

      case 'system':
      case 'error':
        parsed.message = data.message || data.error || 'System message';
        break;

      default:
        parsed.message = data.message || JSON.stringify(data);
    }

    return parsed;
  }

  // Extract username from message string
  static extractUsernameFromMessage(message, eventType) {
    if (!message || typeof message !== 'string') return null;

    let username = null;
    
    switch (eventType) {
      case 'tip':
        // Match patterns like "JohnDoe tipped 50 tokens"
        const tipMatch = message.match(/^([^\s]+)\s+tipped/i);
        if (tipMatch) username = tipMatch[1];
        break;

      case 'chat':
        // Match patterns like "JohnDoe: Hello everyone"
        const chatMatch = message.match(/^([^:]+):\s*/);
        if (chatMatch) username = chatMatch[1];
        break;

      case 'join':
        // Match patterns like "JohnDoe joined the room"
        const joinMatch = message.match(/^([^\s]+)\s+joined/i);
        if (joinMatch) username = joinMatch[1];
        break;

      case 'leave':
        // Match patterns like "JohnDoe left the room"
        const leaveMatch = message.match(/^([^\s]+)\s+left/i);
        if (leaveMatch) username = leaveMatch[1];
        break;
    }

    // Clean and validate username
    if (username) {
      username = this.cleanUsername(username);
    }

    return username;
  }

  // Extract tip amount from message
  static extractAmountFromMessage(message) {
    if (!message || typeof message !== 'string') return null;

    // Match patterns like "tipped 50 tokens" or "50 tokens"
    const amountMatch = message.match(/(\d+)\s*tokens?/i);
    return amountMatch ? parseInt(amountMatch[1]) : null;
  }

  // Clean username by removing special characters and emojis
  static cleanUsername(username) {
    if (!username) return null;

    // Remove emojis and special characters, keep only alphanumeric and underscores
    let cleaned = username.replace(/[^\w\s_-]/g, '').trim();
    
    // Remove extra spaces
    cleaned = cleaned.replace(/\s+/g, ' ');
    
    // If nothing left after cleaning or it's a system user, return null
    if (!cleaned || cleaned.toLowerCase() === 'system') {
      return null;
    }

    return cleaned;
  }

  // Format event message for display
  static formatEventMessage(parsedEvent) {
    let message = '';
    
    switch (parsedEvent.type) {
      case 'tip':
        message = `💰 ${parsedEvent.username || 'Anonymous'} tipped ${parsedEvent.amount || '?'} tokens`;
        if (parsedEvent.message && !parsedEvent.message.includes('tipped')) {
          message += `: ${parsedEvent.message}`;
        }
        break;

      case 'chat':
        message = `💬 ${parsedEvent.username || 'Anonymous'}: ${parsedEvent.message}`;
        break;

      case 'private_message':
      case 'private':
        message = `📧 Private message from ${parsedEvent.username || 'Unknown'}`;
        if (parsedEvent.message) {
          message += `: ${parsedEvent.message}`;
        }
        break;

      case 'user_join':
        message = `👋 ${parsedEvent.username || 'Someone'} joined the room`;
        break;

      case 'user_leave':
        message = `👋 ${parsedEvent.username || 'Someone'} left the room`;
        break;

      case 'media_purchase':
        message = `🎬 ${parsedEvent.username || 'Someone'} purchased media`;
        break;

      case 'system':
        message = `⚙️ ${parsedEvent.message}`;
        break;

      case 'error':
        message = `❌ ${parsedEvent.message}`;
        break;

      default:
        message = parsedEvent.message || 'Unknown event';
    }

    return message;
  }

  // Make username clickable in HTML
  static makeUsernameClickable(message, username, clickHandler = 'handleUserClick') {
    if (!username || !message) return message;

    const escapedUsername = username.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const regex = new RegExp(`\\b${escapedUsername}\\b`, 'g');
    
    return message.replace(regex, 
      `<span class="clickable-username" onclick="window.vueApp.${clickHandler}('${username}')">${username}</span>`
    );
  }
}

// Export for use
window.EventParser = EventParser;