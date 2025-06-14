// Vue 3 Chat Interface using render functions (no template compiler needed)
document.addEventListener('DOMContentLoaded', function() {
  const { createApp, h } = Vue;
  
  // Initialize Novita API service
  const novitaAPI = new NovitaAPI();
  
  // Initialize Auth0 service
  const auth0Service = new Auth0Service();
  
  createApp({
    data() {
      return {
        title: 'Sider AI',
        messages: [],
        currentMessage: '',
        isTyping: false,
        messageIdCounter: 1,
        showChat: false,
        isAuthenticated: false,
        user: null,
        showEdit: false,
        editContent: '',
        activeEditTab: 'write', // 'write' or 'reply'
        replyOriginalText: '',
        replyResponseText: '',
        activeReplyMode: 'comment', // 'comment', 'email', 'message'
        showTranslate: false,
        translateText: '',
        translateFromLang: 'auto',
        translateToLang: 'en',
        showHome: false,
        activeHomeTab: 'dashboard' // 'dashboard', 'top-tippers', 'analytics', 'settings'
      }
    },
    
    render() {
      return h('div', { id: 'app' }, [
        // Main Layout
        h('div', { class: 'main-layout' }, [
          // Main Content
          h('div', { class: 'main-content' }, [
            h('h1', 'Sider AI Clone'),
            h('p', 'Welcome to your AI assistant application.')
          ]),
          
          // Sidebar
          h('div', { class: 'sidebar' }, [
            // Top icons
            h('div', { class: 'sidebar-top' }, [
              h('div', { 
                class: 'sidebar-icon home-icon',
                onClick: this.toggleHome,
                title: 'Home Dashboard'
              }, [
                // Home icon SVG
                h('svg', {
                  width: 24,
                  height: 24,
                  viewBox: '0 0 24 24',
                  fill: 'none',
                  stroke: 'currentColor',
                  'stroke-width': 2
                }, [
                  h('path', { d: 'M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z' }),
                  h('polyline', { points: '9,22 9,12 15,12 15,22' })
                ])
              ]),
              h('div', { 
                class: 'sidebar-icon chat-icon',
                onClick: this.toggleChat,
                title: 'Chat'
              }, [
                // Chat icon SVG
                h('svg', {
                  width: 24,
                  height: 24,
                  viewBox: '0 0 24 24',
                  fill: 'none',
                  stroke: 'currentColor',
                  'stroke-width': 2
                }, [
                  h('path', { d: 'M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z' })
                ])
              ]),
              h('div', { 
                class: 'sidebar-icon edit-icon',
                onClick: this.toggleEdit,
                title: 'Edit & Write'
              }, [
                // Edit icon SVG
                h('svg', {
                  width: 24,
                  height: 24,
                  viewBox: '0 0 24 24',
                  fill: 'none',
                  stroke: 'currentColor',
                  'stroke-width': 2
                }, [
                  h('path', { d: 'M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7' }),
                  h('path', { d: 'M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z' })
                ])
              ]),
              h('div', { 
                class: 'sidebar-icon translate-icon',
                onClick: this.toggleTranslate,
                title: 'Translate'
              }, [
                // Translate icon SVG
                h('svg', {
                  width: 24,
                  height: 24,
                  viewBox: '0 0 24 24',
                  fill: 'none',
                  stroke: 'currentColor',
                  'stroke-width': 2
                }, [
                  h('path', { d: 'M5 8l6 6M4 14l6-6M2 5h12M7 2h1l8 22M17 8h5M23 8v1a4 4 0 0 1-4 4' })
                ])
              ])
            ]),
            
            // Bottom icons
            h('div', { class: 'sidebar-bottom' }, [
              h('div', { 
                class: ['sidebar-icon', 'profile-icon', this.isAuthenticated ? 'authenticated' : 'unauthenticated'],
                onClick: this.toggleAuth,
                title: this.isAuthenticated ? `Logout ${this.user?.name || 'User'}` : 'Login'
              }, [
                this.isAuthenticated ? 
                  // User avatar or logged in icon
                  this.user?.picture ? 
                    h('img', {
                      src: this.user.picture,
                      alt: this.user.name,
                      style: 'width: 24px; height: 24px; border-radius: 50%; object-fit: cover;'
                    }) :
                    h('svg', {
                      width: 24,
                      height: 24,
                      viewBox: '0 0 24 24',
                      fill: 'currentColor',
                      stroke: 'none'
                    }, [
                      h('path', { d: 'M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2' }),
                      h('circle', { cx: '12', cy: '7', r: '4' })
                    ])
                : 
                  // Login icon
                  h('svg', {
                    width: 24,
                    height: 24,
                    viewBox: '0 0 24 24',
                    fill: 'none',
                    stroke: 'currentColor',
                    'stroke-width': 2
                  }, [
                    h('path', { d: 'M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4' }),
                    h('polyline', { points: '10,17 15,12 10,7' }),
                    h('line', { x1: '15', y1: '12', x2: '3', y2: '12' })
                  ])
              ])
            ])
          ])
        ]),
        
        // Chat Modal
        this.showChat ? h('div', { 
          class: 'chat-modal',
          onClick: (e) => { if (e.target === e.currentTarget) this.toggleChat(); }
        }, [
          h('div', { class: 'chat-container' }, [
            // Chat Header
            h('div', { class: 'header' }, [
              h('h1', this.title),
              h('div', { style: 'display: flex; align-items: center;' }, [
                h('div', { class: 'status-dot' }),
                h('button', {
                  onClick: this.toggleChat,
                  style: 'background: none; border: none; color: white; margin-left: 10px; cursor: pointer; font-size: 18px;'
                }, '×')
              ])
            ]),
            
            // Messages Area
            h('div', { 
              class: 'messages-area',
              ref: 'messagesArea'
            }, [
              // Welcome State (when no messages)
              this.messages.length === 0 ? 
                h('div', { class: 'welcome-state' }, [
                  h('div', { class: 'welcome-icon' }, '🤖'),
                  h('div', { class: 'welcome-text' }, 'Welcome to Sider AI'),
                  h('div', { class: 'welcome-subtitle' }, 'Start a conversation to get help with anything')
                ]) : null,
              
              // Messages
              ...this.messages.map(message => 
                h('div', {
                  key: message.id,
                  class: ['message', message.type]
                }, message.text)
              ),
              
              // Typing Indicator
              this.isTyping ? 
                h('div', { class: 'typing-indicator' }, [
                  h('span', 'AI is typing'),
                  h('div', { class: 'typing-dots' }, [
                    h('div', { class: 'typing-dot' }),
                    h('div', { class: 'typing-dot' }),
                    h('div', { class: 'typing-dot' })
                  ])
                ]) : null
            ]),
            
            // Chat Input
            h('div', { class: 'chat-input' }, [
              h('div', { class: 'input-container' }, [
                h('textarea', {
                  class: 'message-input',
                  placeholder: 'Type your message...',
                  rows: 1,
                  value: this.currentMessage,
                  onInput: (e) => { this.currentMessage = e.target.value; },
                  onKeypress: this.handleKeyPress
                }),
                h('button', {
                  class: 'send-button',
                  disabled: !this.currentMessage.trim() || this.isTyping,
                  onClick: this.sendMessage
                }, [
                  h('svg', {
                    width: 20,
                    height: 20,
                    viewBox: '0 0 24 24',
                    fill: 'none',
                    stroke: 'currentColor',
                    'stroke-width': 2
                  }, [
                    h('path', { d: 'M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z' })
                  ])
                ])
              ])
            ])
          ])
        ]) : null,
        
        // Edit Modal
        this.showEdit ? h('div', { 
          class: 'edit-modal',
          onClick: (e) => { if (e.target === e.currentTarget) this.toggleEdit(); }
        }, [
          h('div', { class: 'edit-container' }, [
            // Edit Header
            h('div', { class: 'edit-header' }, [
              h('div', { class: 'edit-tabs' }, [
                h('div', { 
                  class: ['edit-tab', this.activeEditTab === 'write' ? 'active' : ''],
                  onClick: () => this.switchEditTab('write')
                }, 'Write'),
                h('div', { 
                  class: ['edit-tab', this.activeEditTab === 'reply' ? 'active' : ''],
                  onClick: () => this.switchEditTab('reply')
                }, 'Reply')
              ]),
              h('button', {
                onClick: this.toggleEdit,
                class: 'close-button'
              }, '×')
            ]),
            
            // Edit Content - conditional based on active tab
            this.activeEditTab === 'write' ? 
              // Write Tab Content
              h('div', { class: 'edit-content' }, [
                // Writing modes
                h('div', { class: 'writing-modes' }, [
                  h('div', { class: 'mode-button active' }, 'Essay'),
                  h('div', { class: 'mode-button' }, 'Paragraph'),
                  h('div', { class: 'mode-button' }, 'Email'),
                  h('div', { class: 'mode-button' }, 'Ideas')
                ]),
                
                // Settings
                h('div', { class: 'writing-settings' }, [
                  h('select', { class: 'setting-select' }, [
                    h('option', 'Formal'),
                    h('option', 'Casual'),
                    h('option', 'Professional')
                  ]),
                  h('select', { class: 'setting-select' }, [
                    h('option', 'Short'),
                    h('option', 'Medium'),
                    h('option', 'Long')
                  ]),
                  h('select', { class: 'setting-select' }, [
                    h('option', 'English'),
                    h('option', 'Spanish'),
                    h('option', 'French')
                  ])
                ]),
                
                // Text area
                h('div', { class: 'edit-textarea-container' }, [
                  h('textarea', {
                    class: 'edit-textarea',
                    placeholder: 'Enter the topic you want to write about...',
                    value: this.editContent,
                    onInput: (e) => { this.editContent = e.target.value; }
                  })
                ]),
                
                // Submit button
                h('div', { class: 'edit-actions' }, [
                  h('button', { 
                    class: 'submit-button',
                    onClick: this.generateContent
                  }, 'Submit')
                ])
              ])
            :
              // Reply Tab Content
              h('div', { class: 'edit-content' }, [
                // Reply modes
                h('div', { class: 'writing-modes' }, [
                  h('div', { 
                    class: ['mode-button', this.activeReplyMode === 'comment' ? 'active' : ''],
                    onClick: () => this.switchReplyMode('comment')
                  }, 'Comment'),
                  h('div', { 
                    class: ['mode-button', this.activeReplyMode === 'email' ? 'active' : ''],
                    onClick: () => this.switchReplyMode('email')
                  }, 'Email'),
                  h('div', { 
                    class: ['mode-button', this.activeReplyMode === 'message' ? 'active' : ''],
                    onClick: () => this.switchReplyMode('message')
                  }, 'Message')
                ]),
                
                // Settings
                h('div', { class: 'writing-settings' }, [
                  h('select', { class: 'setting-select' }, [
                    h('option', 'Formal'),
                    h('option', 'Casual'),
                    h('option', 'Professional')
                  ]),
                  h('select', { class: 'setting-select' }, [
                    h('option', 'Short'),
                    h('option', 'Medium'),
                    h('option', 'Long')
                  ]),
                  h('select', { class: 'setting-select' }, [
                    h('option', 'English'),
                    h('option', 'Spanish'),
                    h('option', 'French')
                  ])
                ]),
                
                // Original text area (for text to reply to)
                h('div', { class: 'reply-original-container' }, [
                  h('textarea', {
                    class: 'reply-original-textarea',
                    placeholder: 'Enter the original text you want to reply to',
                    value: this.replyOriginalText,
                    onInput: (e) => { this.replyOriginalText = e.target.value; }
                  })
                ]),
                
                // Response text area
                h('div', { class: 'reply-response-container' }, [
                  h('textarea', {
                    class: 'reply-response-textarea',
                    placeholder: 'Describe the general idea of your response',
                    value: this.replyResponseText,
                    onInput: (e) => { this.replyResponseText = e.target.value; }
                  })
                ]),
                
                // Submit button
                h('div', { class: 'edit-actions' }, [
                  h('button', { 
                    class: 'submit-button',
                    onClick: this.generateReply
                  }, 'Submit')
                ])
              ])
          ])
        ]) : null,
        
        // Translate Modal
        this.showTranslate ? h('div', { 
          class: 'translate-modal',
          onClick: (e) => { if (e.target === e.currentTarget) this.toggleTranslate(); }
        }, [
          h('div', { class: 'translate-container' }, [
            // Translate Header
            h('div', { class: 'translate-header' }, [
              h('h1', { class: 'translate-title' }, 'Translate'),
              h('button', {
                onClick: this.toggleTranslate,
                class: 'close-button'
              }, '×')
            ]),
            
            // Translate Content
            h('div', { class: 'translate-content' }, [
              // Language selection
              h('div', { class: 'language-selection' }, [
                h('div', { class: 'language-selector' }, [
                  h('select', { 
                    class: 'from-language-select',
                    value: this.translateFromLang,
                    onChange: (e) => { this.translateFromLang = e.target.value; }
                  }, [
                    h('option', { value: 'auto' }, 'Auto Detect'),
                    h('option', { value: 'en' }, 'English'),
                    h('option', { value: 'es' }, 'Spanish'),
                    h('option', { value: 'fr' }, 'French'),
                    h('option', { value: 'de' }, 'German'),
                    h('option', { value: 'it' }, 'Italian'),
                    h('option', { value: 'pt' }, 'Portuguese'),
                    h('option', { value: 'ru' }, 'Russian'),
                    h('option', { value: 'zh' }, 'Chinese'),
                    h('option', { value: 'ja' }, 'Japanese'),
                    h('option', { value: 'ko' }, 'Korean')
                  ])
                ]),
                
                h('div', { class: 'arrow-icon' }, '→'),
                
                h('div', { class: 'language-selector' }, [
                  h('select', { 
                    class: 'to-language-select',
                    value: this.translateToLang,
                    onChange: (e) => { this.translateToLang = e.target.value; }
                  }, [
                    h('option', { value: 'en' }, 'English'),
                    h('option', { value: 'es' }, 'Spanish'),
                    h('option', { value: 'fr' }, 'French'),
                    h('option', { value: 'de' }, 'German'),
                    h('option', { value: 'it' }, 'Italian'),
                    h('option', { value: 'pt' }, 'Portuguese'),
                    h('option', { value: 'ru' }, 'Russian'),
                    h('option', { value: 'zh' }, 'Chinese'),
                    h('option', { value: 'ja' }, 'Japanese'),
                    h('option', { value: 'ko' }, 'Korean')
                  ])
                ])
              ]),
              
              // Text input area
              h('div', { class: 'translate-input-container' }, [
                h('textarea', {
                  class: 'translate-input',
                  placeholder: 'Type or paste text here...',
                  value: this.translateText,
                  onInput: (e) => { this.translateText = e.target.value; }
                })
              ]),
              
              // Translate button
              h('div', { class: 'translate-actions' }, [
                h('button', { 
                  class: 'translate-button',
                  onClick: this.performTranslation,
                  disabled: !this.translateText.trim()
                }, 'Translate')
              ])
            ])
          ])
        ]) : null,
        
        // Home Modal
        this.showHome ? h('div', { 
          class: 'home-modal',
          onClick: (e) => { if (e.target === e.currentTarget) this.toggleHome(); }
        }, [
          h('div', { class: 'home-container' }, [
            // Home Header
            h('div', { class: 'home-header' }, [
              h('h1', { class: 'home-title' }, 'Chaturbate Model Helper'),
              h('button', {
                onClick: this.toggleHome,
                class: 'close-button'
              }, '×')
            ]),
            
            // Home Tabs
            h('div', { class: 'home-tabs' }, [
              h('div', { 
                class: ['home-tab', this.activeHomeTab === 'dashboard' ? 'active' : ''],
                onClick: () => this.switchHomeTab('dashboard')
              }, 'Dashboard'),
              h('div', { 
                class: ['home-tab', this.activeHomeTab === 'top-tippers' ? 'active' : ''],
                onClick: () => this.switchHomeTab('top-tippers')
              }, 'Top Tippers'),
              h('div', { 
                class: ['home-tab', this.activeHomeTab === 'analytics' ? 'active' : ''],
                onClick: () => this.switchHomeTab('analytics')
              }, 'Analytics'),
              h('div', { 
                class: ['home-tab', this.activeHomeTab === 'settings' ? 'active' : ''],
                onClick: () => this.switchHomeTab('settings')
              }, 'Settings')
            ]),
            
            // Home Content based on active tab
            h('div', { class: 'home-content' }, [
              this.activeHomeTab === 'dashboard' ? 
                this.renderDashboard() :
              this.activeHomeTab === 'top-tippers' ?
                this.renderTopTippers() :
              this.activeHomeTab === 'analytics' ?
                this.renderAnalytics() :
                this.renderSettings()
            ])
          ])
        ]) : null
      ]);
    },
    
    methods: {
      sendMessage() {
        if (!this.currentMessage.trim() || this.isTyping) return;
        
        // Add user message
        const userMessage = {
          id: this.messageIdCounter++,
          text: this.currentMessage.trim(),
          type: 'user',
          timestamp: new Date()
        };
        
        this.messages.push(userMessage);
        const messageText = this.currentMessage.trim();
        this.currentMessage = '';
        
        // Scroll to bottom
        this.$nextTick(() => {
          this.scrollToBottom();
        });
        
        // Get AI response
        this.getAIResponse(messageText);
      },
      
      async getAIResponse(userMessage) {
        this.isTyping = true;
        
        try {
          // Call real Novita API
          const aiResponseText = await novitaAPI.chat(userMessage);
          
          const aiMessage = {
            id: this.messageIdCounter++,
            text: aiResponseText,
            type: 'ai',
            timestamp: new Date()
          };
          
          this.messages.push(aiMessage);
          
        } catch (error) {
          // Fail gracefully with user-friendly error
          // console.error('Error in getAIResponse:', error);
          const errorMessage = {
            id: this.messageIdCounter++,
            text: `Sorry, I'm having trouble connecting. Error: ${error.message}`,
            type: 'ai',
            timestamp: new Date()
          };
          
          this.messages.push(errorMessage);
        } finally {
          this.isTyping = false;
          
          // Scroll to bottom
          this.$nextTick(() => {
            this.scrollToBottom();
          });
        }
      },
      
      handleKeyPress(event) {
        if (event.key === 'Enter' && !event.shiftKey) {
          event.preventDefault();
          this.sendMessage();
        }
      },
      
      scrollToBottom() {
        const messagesArea = this.$refs.messagesArea;
        if (messagesArea) {
          messagesArea.scrollTop = messagesArea.scrollHeight;
        }
      },
      
      toggleChat() {
        this.showChat = !this.showChat;
      },
      
      async toggleAuth() {
        if (this.isAuthenticated) {
          await this.logout();
        } else {
          await this.login();
        }
      },
      
      async login() {
        try {
          await auth0Service.login();
        } catch (error) {
          console.error('Login failed:', error);
        }
      },
      
      async logout() {
        try {
          await auth0Service.logout();
          this.isAuthenticated = false;
          this.user = null;
        } catch (error) {
          console.error('Logout failed:', error);
        }
      },
      
      async checkAuthStatus() {
        this.isAuthenticated = auth0Service.isAuthenticated;
        this.user = auth0Service.user;
      },
      
      toggleEdit() {
        this.showEdit = !this.showEdit;
      },
      
      async generateContent() {
        if (!this.editContent.trim()) return;
        
        try {
          // You can integrate with your AI service here
          const response = await novitaAPI.generateText(this.editContent);
          // Handle the response - maybe show it in a new modal or copy to clipboard
          console.log('Generated content:', response);
        } catch (error) {
          console.error('Content generation error:', error);
        }
      },
      
      switchEditTab(tab) {
        this.activeEditTab = tab;
      },
      
      switchReplyMode(mode) {
        this.activeReplyMode = mode;
      },
      
      async generateReply() {
        if (!this.replyOriginalText.trim() || !this.replyResponseText.trim()) return;
        
        try {
          // Generate AI reply based on original text and response idea
          const prompt = `Reply to this ${this.activeReplyMode}: "${this.replyOriginalText}" with the following idea: "${this.replyResponseText}"`;
          const response = await novitaAPI.generateText(prompt);
          console.log('Generated reply:', response);
        } catch (error) {
          console.error('Reply generation error:', error);
        }
      },
      
      toggleTranslate() {
        this.showTranslate = !this.showTranslate;
      },
      
      async performTranslation() {
        if (!this.translateText.trim()) return;
        
        try {
          // Prepare request payload for local API
          const payload = {
            text: this.translateText,
            to_lang: this.translateToLang
          };
          
          // Add from_lang if not auto-detect
          if (this.translateFromLang !== 'auto') {
            payload.from_lang = this.translateFromLang;
          }
          
          // Call local translation API
          const response = await fetch('http://localhost:5000/translate/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
          });
          
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
          
          const result = await response.json();
          console.log('Translation result:', result);
          
          if (result.success) {
            // You could show the result in a new area or copy to clipboard
            alert(`Translation: ${result.translation}`);
          } else {
            throw new Error('Translation failed');
          }
          
        } catch (error) {
          console.error('Translation error:', error);
          alert(`Translation failed: ${error.message}`);
        }
      },
      
      getLanguageName(code) {
        const languages = {
          'auto': 'Auto Detect',
          'en': 'English',
          'es': 'Spanish', 
          'fr': 'French',
          'de': 'German',
          'it': 'Italian',
          'pt': 'Portuguese',
          'ru': 'Russian',
          'zh': 'Chinese',
          'ja': 'Japanese',
          'ko': 'Korean'
        };
        return languages[code] || code;
      },
      
      toggleHome() {
        this.showHome = !this.showHome;
      },
      
      switchHomeTab(tab) {
        this.activeHomeTab = tab;
      },
      
      renderDashboard() {
        return h('div', { class: 'dashboard-content' }, [
          h('div', { class: 'stats-grid' }, [
            h('div', { class: 'stat-card' }, [
              h('div', { class: 'stat-value' }, '127'),
              h('div', { class: 'stat-label' }, 'Active Viewers'),
              h('div', { class: 'stat-trend up' }, '+12%')
            ]),
            h('div', { class: 'stat-card' }, [
              h('div', { class: 'stat-value' }, '$234'),
              h('div', { class: 'stat-label' }, 'Today\'s Earnings'),
              h('div', { class: 'stat-trend up' }, '+8%')
            ]),
            h('div', { class: 'stat-card' }, [
              h('div', { class: 'stat-value' }, '3.2k'),
              h('div', { class: 'stat-label' }, 'Total Tokens'),
              h('div', { class: 'stat-trend down' }, '-3%')
            ])
          ]),
          h('div', { class: 'recent-activity' }, [
            h('h3', 'Recent Activity'),
            h('div', { class: 'activity-item' }, '🎁 BigTipper just tipped 500 tokens'),
            h('div', { class: 'activity-item' }, '👋 New follower: ModelFan123'),
            h('div', { class: 'activity-item' }, '💬 PrivateShow request from VIP_User')
          ])
        ]);
      },
      
      renderTopTippers() {
        return h('div', { class: 'top-tippers-content' }, [
          h('div', { class: 'tippers-header' }, [
            h('h3', 'Top Tippers This Week'),
            h('select', { class: 'time-filter' }, [
              h('option', 'This Week'),
              h('option', 'This Month'),
              h('option', 'All Time')
            ])
          ]),
          h('div', { class: 'tippers-list' }, [
            h('div', { class: 'tipper-item' }, [
              h('div', { class: 'tipper-rank' }, '1'),
              h('div', { class: 'tipper-info' }, [
                h('div', { class: 'tipper-name' }, 'BigSpender2024'),
                h('div', { class: 'tipper-total' }, '2,500 tokens')
              ]),
              h('div', { class: 'tipper-badge' }, '👑')
            ]),
            h('div', { class: 'tipper-item' }, [
              h('div', { class: 'tipper-rank' }, '2'),
              h('div', { class: 'tipper-info' }, [
                h('div', { class: 'tipper-name' }, 'GenerousViewer'),
                h('div', { class: 'tipper-total' }, '1,800 tokens')
              ]),
              h('div', { class: 'tipper-badge' }, '💎')
            ]),
            h('div', { class: 'tipper-item' }, [
              h('div', { class: 'tipper-rank' }, '3'),
              h('div', { class: 'tipper-info' }, [
                h('div', { class: 'tipper-name' }, 'SupportiveFan'),
                h('div', { class: 'tipper-total' }, '1,200 tokens')
              ]),
              h('div', { class: 'tipper-badge' }, '⭐')
            ])
          ])
        ]);
      },
      
      renderAnalytics() {
        return h('div', { class: 'analytics-content' }, [
          h('h3', 'Performance Analytics'),
          h('div', { class: 'analytics-placeholder' }, [
            h('div', { class: 'chart-placeholder' }, [
              h('div', { class: 'placeholder-text' }, '📊 Earnings Chart'),
              h('div', { class: 'placeholder-desc' }, 'Weekly earnings trends will appear here')
            ]),
            h('div', { class: 'chart-placeholder' }, [
              h('div', { class: 'placeholder-text' }, '👥 Viewer Analytics'),
              h('div', { class: 'placeholder-desc' }, 'Peak viewing hours and demographics')
            ])
          ])
        ]);
      },
      
      renderSettings() {
        return h('div', { class: 'settings-content' }, [
          h('h3', 'Model Helper Settings'),
          h('div', { class: 'settings-section' }, [
            h('label', { class: 'setting-label' }, 'Notification Preferences'),
            h('div', { class: 'setting-options' }, [
              h('label', { class: 'checkbox-label' }, [
                h('input', { type: 'checkbox', checked: true }),
                h('span', 'New tips notifications')
              ]),
              h('label', { class: 'checkbox-label' }, [
                h('input', { type: 'checkbox', checked: true }),
                h('span', 'Goal reminders')
              ]),
              h('label', { class: 'checkbox-label' }, [
                h('input', { type: 'checkbox' }),
                h('span', 'Private show requests')
              ])
            ])
          ]),
          h('div', { class: 'settings-section' }, [
            h('label', { class: 'setting-label' }, 'Auto-responses'),
            h('textarea', { 
              class: 'settings-textarea',
              placeholder: 'Enter your auto-thank you message for tips...'
            })
          ])
        ]);
      }
    },
    
    async mounted() {
      // Check authentication status
      await this.checkAuthStatus();
      
      // Add welcome message after component mounts
      setTimeout(() => {
        const welcomeMessage = {
          id: this.messageIdCounter++,
          text: 'Hello! I\'m your AI assistant. How can I help you today?',
          type: 'ai',
          timestamp: new Date()
        };
        this.messages.push(welcomeMessage);
      }, 500);
    }
  }).mount('#app');
});