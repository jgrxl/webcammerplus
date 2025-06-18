// inbox.js - Private Messages Inbox functionality

const API_BASE_URL = 'http://localhost:5000/api/v1';
const WEBSOCKET_URL = 'ws://localhost:5000';

// State management
let currentConversation = null;
let conversations = [];
let messages = [];
let unreadCount = 0;
let socket = null;

// Elements
const conversationsContainer = document.getElementById('conversations-container');
const messagesContainer = document.getElementById('messages-container');
const emptyState = document.getElementById('empty-state');
const conversationView = document.getElementById('conversation-view');
const conversationUsername = document.getElementById('conversation-username');
const totalMessagesSpan = document.getElementById('total-messages');
const unreadCountSpan = document.getElementById('unread-count');
const newMessageIndicator = document.getElementById('new-message-indicator');
const markAllReadBtn = document.getElementById('mark-all-read');
const refreshBtn = document.getElementById('refresh-messages');

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
    await initializeInbox();
    setupEventListeners();
    connectWebSocket();
});

// Get auth token
async function getAuthToken() {
    // In a real implementation, this would get the Auth0 token
    // For now, return a mock token
    return 'mock-auth-token';
}

// Initialize inbox
async function initializeInbox() {
    try {
        await loadInboxStats();
        await loadConversations();
    } catch (error) {
        console.error('Failed to initialize inbox:', error);
        showError('Failed to load inbox. Please try again.');
    }
}

// Load inbox statistics
async function loadInboxStats() {
    try {
        const token = await getAuthToken();
        const response = await fetch(`${API_BASE_URL}/inbox/stats`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) throw new Error('Failed to load stats');

        const stats = await response.json();
        totalMessagesSpan.textContent = stats.total_messages;
        unreadCountSpan.textContent = stats.unread_messages;
        unreadCount = stats.unread_messages;

        // Update browser badge
        if (chrome?.action?.setBadgeText) {
            chrome.action.setBadgeText({
                text: unreadCount > 0 ? unreadCount.toString() : ''
            });
        }
    } catch (error) {
        console.error('Failed to load inbox stats:', error);
    }
}

// Load conversations
async function loadConversations() {
    try {
        const token = await getAuthToken();
        const response = await fetch(`${API_BASE_URL}/inbox/conversations`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) throw new Error('Failed to load conversations');

        conversations = await response.json();
        renderConversations();
    } catch (error) {
        console.error('Failed to load conversations:', error);
        conversationsContainer.innerHTML = '<div class="error-message">Failed to load conversations</div>';
    }
}

// Render conversations list
function renderConversations() {
    if (conversations.length === 0) {
        conversationsContainer.innerHTML = '<div class="empty-state">No conversations yet</div>';
        return;
    }

    conversationsContainer.innerHTML = conversations.map(conv => `
        <div class="conversation-item ${conv.unread_count > 0 ? 'unread' : ''} ${currentConversation === conv.from_user ? 'active' : ''}"
             data-username="${conv.from_user}">
            <div class="conversation-header">
                <span class="username">${conv.from_user}</span>
                ${conv.unread_count > 0 ? `<span class="unread-badge">${conv.unread_count}</span>` : ''}
            </div>
            <div class="last-message">${escapeHtml(conv.last_message)}</div>
            <div class="timestamp">${formatTimestamp(conv.last_message_time)}</div>
        </div>
    `).join('');

    // Add click handlers
    document.querySelectorAll('.conversation-item').forEach(item => {
        item.addEventListener('click', () => {
            const username = item.dataset.username;
            selectConversation(username);
        });
    });
}

// Select and load a conversation
async function selectConversation(username) {
    currentConversation = username;
    
    // Update UI
    document.querySelectorAll('.conversation-item').forEach(item => {
        item.classList.toggle('active', item.dataset.username === username);
    });

    // Show conversation view
    emptyState.style.display = 'none';
    conversationView.style.display = 'block';
    conversationUsername.textContent = username;

    // Load messages
    await loadMessages(username);
}

// Load messages for a conversation
async function loadMessages(username) {
    try {
        messagesContainer.innerHTML = '<div class="loading">Loading messages...</div>';

        const token = await getAuthToken();
        const response = await fetch(`${API_BASE_URL}/inbox/conversations/${username}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) throw new Error('Failed to load messages');

        messages = await response.json();
        renderMessages();

        // Mark messages as read
        markConversationAsRead(username);
    } catch (error) {
        console.error('Failed to load messages:', error);
        messagesContainer.innerHTML = '<div class="error-message">Failed to load messages</div>';
    }
}

// Render messages
function renderMessages() {
    if (messages.length === 0) {
        messagesContainer.innerHTML = '<div class="empty-state">No messages in this conversation</div>';
        return;
    }

    messagesContainer.innerHTML = messages.map(msg => `
        <div class="message ${msg.is_sent ? 'sent' : 'received'}">
            <div class="message-text">${escapeHtml(msg.message)}</div>
            <div class="message-time">${formatTimestamp(msg.timestamp)}</div>
        </div>
    `).join('');

    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Mark conversation as read
async function markConversationAsRead(username) {
    try {
        const token = await getAuthToken();
        const unreadMessages = messages.filter(msg => !msg.is_read && !msg.is_sent);

        for (const msg of unreadMessages) {
            await fetch(`${API_BASE_URL}/inbox/messages/${msg.id}/read`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
        }

        // Update stats and conversations
        await loadInboxStats();
        await loadConversations();
    } catch (error) {
        console.error('Failed to mark messages as read:', error);
    }
}

// Setup event listeners
function setupEventListeners() {
    markAllReadBtn.addEventListener('click', async () => {
        try {
            const token = await getAuthToken();
            const response = await fetch(`${API_BASE_URL}/inbox/mark-all-read`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                await loadInboxStats();
                await loadConversations();
                if (currentConversation) {
                    await loadMessages(currentConversation);
                }
            }
        } catch (error) {
            console.error('Failed to mark all as read:', error);
        }
    });

    refreshBtn.addEventListener('click', async () => {
        if (currentConversation) {
            await loadMessages(currentConversation);
        }
    });

    newMessageIndicator.addEventListener('click', () => {
        newMessageIndicator.classList.remove('show');
        initializeInbox();
    });
}

// WebSocket connection for real-time updates
function connectWebSocket() {
    const socketUrl = `${WEBSOCKET_URL}/chaturbate`;
    
    // Use Socket.IO client if available
    if (typeof io !== 'undefined') {
        socket = io(socketUrl);
        
        socket.on('connect', () => {
            console.log('Connected to WebSocket');
        });

        socket.on('private_message', (data) => {
            handleNewPrivateMessage(data);
        });

        socket.on('disconnect', () => {
            console.log('Disconnected from WebSocket');
        });
    } else {
        console.warn('Socket.IO client not loaded, real-time updates disabled');
    }
}

// Handle new private message
function handleNewPrivateMessage(data) {
    console.log('New private message:', data);

    // Show notification
    if (!document.hasFocus()) {
        newMessageIndicator.classList.add('show');
        
        // Browser notification if permitted
        if (Notification.permission === 'granted') {
            new Notification('New Private Message', {
                body: `${data.from_username}: ${data.message}`,
                icon: '/icon-128.png'
            });
        }
    }

    // Update stats
    unreadCount++;
    unreadCountSpan.textContent = unreadCount;

    // Update conversations if visible
    if (document.hasFocus()) {
        loadConversations();
        
        // Update current conversation if it's the sender
        if (currentConversation === data.from_username) {
            loadMessages(currentConversation);
        }
    }
}

// Utility functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;

    if (diff < 60000) { // Less than 1 minute
        return 'Just now';
    } else if (diff < 3600000) { // Less than 1 hour
        return `${Math.floor(diff / 60000)}m ago`;
    } else if (diff < 86400000) { // Less than 1 day
        return `${Math.floor(diff / 3600000)}h ago`;
    } else if (diff < 604800000) { // Less than 1 week
        return `${Math.floor(diff / 86400000)}d ago`;
    } else {
        return date.toLocaleDateString();
    }
}

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    document.body.appendChild(errorDiv);
    
    setTimeout(() => {
        errorDiv.remove();
    }, 5000);
}

// Request notification permission
if ('Notification' in window && Notification.permission === 'default') {
    Notification.requestPermission();
}