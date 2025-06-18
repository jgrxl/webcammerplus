// EventParser.test.js

describe('EventParser', () => {
  let EventParser;
  
  beforeEach(() => {
    // Load the module
    require('./EventParser.js');
    EventParser = window.EventParser;
  });

  describe('parseEvent', () => {
    it('should parse tip event correctly', () => {
      const event = {
        type: 'tip',
        username: 'JohnDoe',
        amount: 100,
        message: 'Thanks for the show!'
      };
      
      const parsed = EventParser.parseEvent(event);
      
      expect(parsed.type).toBe('tip');
      expect(parsed.username).toBe('JohnDoe');
      expect(parsed.amount).toBe(100);
      expect(parsed.message).toBe('Thanks for the show!');
    });

    it('should extract username from message if not provided', () => {
      const event = {
        type: 'tip',
        message: 'BigSpender tipped 50 tokens'
      };
      
      const parsed = EventParser.parseEvent(event);
      
      expect(parsed.username).toBe('BigSpender');
      expect(parsed.amount).toBe(50);
    });

    it('should handle emojis in username', () => {
      const event = {
        type: 'tip',
        message: '💰RichGuy💰 tipped 200 tokens'
      };
      
      const parsed = EventParser.parseEvent(event);
      
      expect(parsed.username).toBe('RichGuy');
      expect(parsed.amount).toBe(200);
    });
  });

  describe('formatEventMessage', () => {
    it('should format tip message correctly', () => {
      const event = {
        type: 'tip',
        username: 'User1',
        amount: 25
      };
      
      const message = EventParser.formatEventMessage(event);
      
      expect(message).toBe('User1 tipped 25 tokens');
    });

    it('should format chat message correctly', () => {
      const event = {
        type: 'chat',
        username: 'User2',
        message: 'Hello everyone!'
      };
      
      const message = EventParser.formatEventMessage(event);
      
      expect(message).toBe('User2: Hello everyone!');
    });
  });

  describe('cleanUsername', () => {
    it('should remove special characters from username', () => {
      expect(EventParser.cleanUsername('User@123!')).toBe('User123');
      expect(EventParser.cleanUsername('💎VIP💎')).toBe('VIP');
      expect(EventParser.cleanUsername('user_name-123')).toBe('user_name-123');
    });

    it('should handle null/undefined usernames', () => {
      expect(EventParser.cleanUsername(null)).toBe(null);
      expect(EventParser.cleanUsername(undefined)).toBe(null);
      expect(EventParser.cleanUsername('')).toBe(null);
    });

    it('should reject system usernames', () => {
      expect(EventParser.cleanUsername('System')).toBe(null);
      expect(EventParser.cleanUsername('SYSTEM')).toBe(null);
      expect(EventParser.cleanUsername('system')).toBe(null);
    });
  });
});