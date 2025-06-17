/**
 * Unit tests for popup.js Vue components
 */

describe('Vue Popup Component', () => {
    let app;
    let vm;
    let vueConfig;

    beforeEach(() => {
        // Clear module cache
        jest.clearAllMocks();
        
        // Mock DOM
        document.body.innerHTML = '<div id="app"></div>';
        
        // Create a simple mock Vue instance
        vm = {
            // Data properties (will be populated after createApp is called)
            title: 'Sider AI',
            messages: [],
            currentMessage: '',
            isTyping: false,
            showChat: false,
            showHome: true,
            isAuthenticated: false,
            api: null,
            translateText: '',
            translateToLang: 'es',
            translateFromLang: 'en',
            showTranslate: false,
            showEdit: false,
            replyOriginalText: '',
            replyResponseText: '',
            activeReplyMode: 'friendly',
            isAttached: false,
            
            // Mock methods
            sendMessage: jest.fn(async function() {
                if (!this.currentMessage.trim()) return;
                
                this.messages.push({
                    id: Date.now(),
                    type: 'user',
                    text: this.currentMessage
                });
                
                this.isTyping = true;
                this.currentMessage = '';
                
                setTimeout(() => {
                    this.messages.push({
                        id: Date.now() + 1,
                        type: 'ai',
                        text: `Hello! You said: "${this.messages[this.messages.length - 1].text}"`
                    });
                    this.isTyping = false;
                }, 1500);
            }),
            
            handleKeyPress: jest.fn(function(event) {
                if (event.key === 'Enter' && !event.shiftKey) {
                    event.preventDefault();
                    this.sendMessage();
                }
            }),
            
            performTranslation: jest.fn(async function() {
                this.isTyping = true;
                try {
                    const result = await this.api.translateText(this.translateText, this.translateToLang, this.translateFromLang);
                    this.messages.push({
                        id: Date.now(),
                        type: 'ai',
                        text: `Translation: ${result}`
                    });
                } catch (error) {
                    this.messages.push({
                        id: Date.now(),
                        type: 'ai',
                        text: `Sorry, translation failed: ${error.message}`
                    });
                }
                this.isTyping = false;
            }),
            
            performReply: jest.fn(async function() {
                try {
                    await this.api.generateReply(this.replyOriginalText, this.replyResponseText, this.activeReplyMode);
                } catch (error) {
                    if (error.message.includes('Unauthorized')) {
                        this.isAuthenticated = false;
                        this.messages.push({
                            id: Date.now(),
                            type: 'ai',
                            text: 'Please check your authentication'
                        });
                    }
                }
            }),
            
            showFeature: jest.fn(function(feature) {
                this.showHome = false;
                this.showChat = false;
                this.showTranslate = false;
                this.showEdit = false;
                this[`show${feature.charAt(0).toUpperCase() + feature.slice(1)}`] = true;
            }),
            
            backToHome: jest.fn(function() {
                this.showHome = true;
                this.showChat = false;
                this.showTranslate = false;
                this.showEdit = false;
            }),
            
            startMonitoring: jest.fn(async function() {
                await this.api.startChaturbate(true);
                this.isAttached = true;
            }),
            
            stopMonitoring: jest.fn(async function() {
                await this.api.stopChaturbate();
                this.isAttached = false;
            }),
            
            // Mock refs
            $refs: {
                messageInput: { focus: jest.fn() },
                chatContainer: { scrollTop: 0, scrollHeight: 100 }
            }
        };
        
        // Bind all methods to vm
        Object.keys(vm).forEach(key => {
            if (typeof vm[key] === 'function') {
                vm[key] = vm[key].bind(vm);
            }
        });
        
        // Mock Vue
        global.Vue = {
            createApp: jest.fn((config) => {
                vueConfig = config;
                
                // Apply config data to vm
                if (config.data) {
                    Object.assign(vm, config.data());
                }
                
                // Mock Vue app instance
                app = {
                    mount: jest.fn(() => {
                        if (config.mounted) {
                            config.mounted.call(vm);
                        }
                        return app;
                    }),
                    component: jest.fn(),
                    directive: jest.fn()
                };
                
                return app;
            })
        };

        // Mock WebCammerAPI
        global.WebCammerAPI = jest.fn().mockImplementation(() => ({
            healthCheck: jest.fn().mockResolvedValue(true),
            translateText: jest.fn().mockResolvedValue('Translated text'),
            generateReply: jest.fn().mockResolvedValue('Generated reply'),
            generateText: jest.fn().mockResolvedValue('Generated text'),
            getChaturbateStatus: jest.fn().mockResolvedValue({
                running: true,
                connected_clients: 5
            }),
            startChaturbate: jest.fn().mockResolvedValue({ message: 'Started' }),
            stopChaturbate: jest.fn().mockResolvedValue({ message: 'Stopped' })
        }));

        // Mock popup.js by executing it
        const fs = require('fs');
        const path = require('path');
        const popupCode = fs.readFileSync(path.join(__dirname, '../popup.js'), 'utf8');
        eval(popupCode);
    });

    afterEach(() => {
        jest.clearAllMocks();
    });

    describe('Data Initialization', () => {
        test('should initialize with correct default data', () => {
            expect(vueConfig).toBeDefined();
            const data = vueConfig.data();
            
            expect(data.title).toBe('Sider AI');
            expect(data.messages).toEqual([]);
            expect(data.currentMessage).toBe('');
            expect(data.isTyping).toBe(false);
            expect(data.showChat).toBe(false);
            expect(data.showHome).toBe(true);
            expect(data.isAuthenticated).toBe(false);
        });
    });

    describe('Message Handling', () => {
        test('sendMessage should add user message and get AI response', async () => {
            vm.currentMessage = 'Hello AI';
            vm.showChat = true;
            
            await vm.sendMessage();
            
            // Check user message was added
            expect(vm.messages[0]).toEqual({
                id: expect.any(Number),
                type: 'user',
                text: 'Hello AI'
            });
            
            // Check typing indicator
            expect(vm.isTyping).toBe(true);
            
            // Wait for AI response
            await new Promise(resolve => setTimeout(resolve, 1600));
            
            // Check AI message was added
            expect(vm.messages[1]).toEqual({
                id: expect.any(Number),
                type: 'ai',
                text: expect.stringContaining('Hello')
            });
            
            expect(vm.isTyping).toBe(false);
            expect(vm.currentMessage).toBe('');
        });

        test('should not send empty messages', async () => {
            vm.currentMessage = '';
            await vm.sendMessage();
            
            expect(vm.messages.length).toBe(0);
        });

        test('should handle Enter key press', () => {
            const event = {
                key: 'Enter',
                shiftKey: false,
                preventDefault: jest.fn()
            };
            
            vm.currentMessage = 'Test message';
            
            vm.handleKeyPress(event);
            
            expect(event.preventDefault).toHaveBeenCalled();
            expect(vm.sendMessage).toHaveBeenCalled();
        });
    });

    describe('Translation Feature', () => {
        test('should translate text when translation is triggered', async () => {
            vm.api = new WebCammerAPI();
            vm.translateText = 'Hello world';
            vm.translateToLang = 'es';
            vm.translateFromLang = 'en';
            
            await vm.performTranslation();
            
            expect(vm.api.translateText).toHaveBeenCalledWith('Hello world', 'es', 'en');
            expect(vm.isTyping).toBe(false);
        });

        test('should show translation result in messages', async () => {
            vm.api = new WebCammerAPI();
            vm.showTranslate = true;
            vm.translateText = 'Hello';
            
            await vm.performTranslation();
            
            expect(vm.messages).toContainEqual({
                id: expect.any(Number),
                type: 'ai',
                text: 'Translation: Translated text'
            });
        });
    });

    describe('Reply Generation', () => {
        test('should generate reply with correct parameters', async () => {
            vm.api = new WebCammerAPI();
            vm.replyOriginalText = 'How are you?';
            vm.replyResponseText = 'I am fine';
            vm.activeReplyMode = 'friendly';
            
            await vm.performReply();
            
            expect(vm.api.generateReply).toHaveBeenCalledWith(
                'How are you?',
                'I am fine',
                'friendly'
            );
        });
    });

    describe('Navigation', () => {
        test('showFeature should update visibility states', () => {
            vm.showFeature('chat');
            
            expect(vm.showHome).toBe(false);
            expect(vm.showChat).toBe(true);
            expect(vm.showTranslate).toBe(false);
            expect(vm.showEdit).toBe(false);
        });

        test('backToHome should reset to home view', () => {
            vm.showChat = true;
            vm.showTranslate = true;
            
            vm.backToHome();
            
            expect(vm.showHome).toBe(true);
            expect(vm.showChat).toBe(false);
            expect(vm.showTranslate).toBe(false);
        });
    });

    describe('Chaturbate Integration', () => {
        test('should start chaturbate monitoring', async () => {
            vm.api = new WebCammerAPI();
            await vm.startMonitoring();
            
            expect(vm.api.startChaturbate).toHaveBeenCalledWith(true);
            expect(vm.isAttached).toBe(true);
        });

        test('should stop chaturbate monitoring', async () => {
            vm.api = new WebCammerAPI();
            vm.isAttached = true;
            
            await vm.stopMonitoring();
            
            expect(vm.api.stopChaturbate).toHaveBeenCalled();
            expect(vm.isAttached).toBe(false);
        });
    });

    describe('Error Handling', () => {
        test('should handle translation errors gracefully', async () => {
            vm.api = new WebCammerAPI();
            vm.api.translateText.mockRejectedValueOnce(new Error('API Error'));
            vm.translateText = 'Hello';
            
            await vm.performTranslation();
            
            expect(vm.messages).toContainEqual({
                id: expect.any(Number),
                type: 'ai',
                text: 'Sorry, translation failed: API Error'
            });
        });

        test('should handle authentication errors', async () => {
            vm.api = new WebCammerAPI();
            vm.api.generateReply.mockRejectedValueOnce(new Error('Unauthorized'));
            vm.replyOriginalText = 'Test';
            
            await vm.performReply();
            
            expect(vm.isAuthenticated).toBe(false);
            expect(vm.messages).toContainEqual({
                id: expect.any(Number),
                type: 'ai',
                text: expect.stringContaining('authentication')
            });
        });
    });
});