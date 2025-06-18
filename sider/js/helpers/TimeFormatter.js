// Time Formatter Helper
class TimeFormatter {
  
  // Format time for display (HH:MM:SS)
  static formatTime(date) {
    const dateObj = typeof date === 'number' ? new Date(date * 1000) : new Date(date);
    return dateObj.toLocaleTimeString('en-US', { 
      hour12: false, 
      hour: '2-digit', 
      minute: '2-digit', 
      second: '2-digit' 
    });
  }

  // Format time for chat messages (HH:MM)
  static formatChatTime(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  }

  // Format relative time (e.g., "2 hours ago")
  static formatTimeAgo(timestamp) {
    if (!timestamp) return 'Never';
    
    const date = typeof timestamp === 'string' ? new Date(timestamp) : 
                 typeof timestamp === 'number' ? new Date(timestamp) : timestamp;
    const now = new Date();
    const diff = now - date;

    if (diff < 0) return 'Just now'; // Future dates
    if (diff < 60000) return 'Just now'; // Less than 1 minute
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`; // Less than 1 hour
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`; // Less than 1 day
    if (diff < 604800000) return `${Math.floor(diff / 86400000)}d ago`; // Less than 1 week
    
    return date.toLocaleDateString();
  }

  // Format timestamp for inbox/messages
  static formatInboxTimestamp(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;

    // Today: show time
    if (diff < 86400000 && date.getDate() === now.getDate()) {
      return this.formatChatTime(timestamp);
    }
    
    // This week: show day name
    if (diff < 604800000) {
      return date.toLocaleDateString('en-US', { weekday: 'short' });
    }
    
    // Older: show date
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  }

  // Format duration (e.g., "2h 30m")
  static formatDuration(seconds) {
    if (seconds < 60) return `${seconds}s`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m`;
    
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    
    if (minutes === 0) return `${hours}h`;
    return `${hours}h ${minutes}m`;
  }

  // Get greeting based on time of day
  static getTimeGreeting() {
    const hour = new Date().getHours();
    
    if (hour < 12) return 'Good morning';
    if (hour < 17) return 'Good afternoon';
    if (hour < 21) return 'Good evening';
    return 'Good night';
  }

  // Check if date is today
  static isToday(date) {
    const today = new Date();
    const compareDate = new Date(date);
    
    return compareDate.getDate() === today.getDate() &&
           compareDate.getMonth() === today.getMonth() &&
           compareDate.getFullYear() === today.getFullYear();
  }

  // Check if date is within last N days
  static isWithinDays(date, days) {
    const compareDate = new Date(date);
    const now = new Date();
    const diff = now - compareDate;
    
    return diff < (days * 86400000); // days in milliseconds
  }
}

// Export for use
window.TimeFormatter = TimeFormatter;