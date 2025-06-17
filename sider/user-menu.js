// User Menu Component for WebCammer+
class UserMenu {
    constructor() {
        this.isAuthenticated = false;
        this.user = null;
        this.api = new WebCammerAPI();
        this.lastSubscriptionLoad = 0;
        this.subscriptionLoadDebounce = 5000; // 5 seconds
        this.init();
    }

    async init() {
        await this.checkAuthStatus();
        this.createMenuHTML();
        this.bindEvents();
        // Trigger Vue component refresh if available
        this.syncWithVueComponent();
    }

    syncWithVueComponent() {
        // Removed to prevent circular dependency
        // Vue component will manage its own auth state
    }

    async refresh() {
        await this.checkAuthStatus();
        this.createMenuHTML();
        // Only update subscription if authenticated
        if (this.isAuthenticated) {
            this.loadSubscriptionInfo();
        }
        this.syncWithVueComponent();
    }

    async checkAuthStatus() {
        try {
            const auth0Service = await getAuth0Service();
            this.isAuthenticated = auth0Service.isAuthenticated;
            this.user = auth0Service.user;
        } catch (error) {
            console.error('Auth status check failed:', error);
            this.isAuthenticated = false;
            this.user = null;
        }
    }

    createMenuHTML() {
        // Don't create the floating menu - we'll integrate with the sidebar instead
        this.addStyles();
        this.createSidebarDropdown();
    }

    createSidebarDropdown() {
        // Remove existing dropdown if it exists
        const existingDropdown = document.getElementById('sidebar-user-dropdown');
        if (existingDropdown) {
            existingDropdown.remove();
        }

        if (!this.isAuthenticated) {
            return; // No dropdown needed when not authenticated
        }

        const dropdownHTML = `
            <div id="sidebar-user-dropdown" class="sidebar-user-dropdown" style="display: none;">
                <div class="menu-header">
                    <img src="${this.user?.picture || 'https://via.placeholder.com/48x48?text=U'}" alt="User Avatar" class="menu-avatar">
                    <div class="menu-user-info">
                        <div class="menu-user-name">${this.user?.name || 'User'}</div>
                        <div class="menu-user-email">${this.user?.email || ''}</div>
                    </div>
                </div>
                
                <div class="menu-divider"></div>
                
                <div class="menu-section">
                    <div class="menu-section-title">Account</div>
                    <a href="/profile.html" class="menu-item">
                        <span class="menu-icon">👤</span>
                        Account Settings
                    </a>
                    <div class="menu-item" onclick="userMenu.showSubscriptionModal()">
                        <span class="menu-icon">💳</span>
                        Subscription Settings
                        <span class="subscription-badge" id="subscription-badge">Loading...</span>
                    </div>
                    <a href="/subscription.html" class="menu-item">
                        <span class="menu-icon">⬆️</span>
                        Upgrade Plan
                    </a>
                </div>
                
                <div class="menu-divider"></div>
                
                <div class="menu-section">
                    <div class="menu-item" onclick="userMenu.showUsageModal()">
                        <span class="menu-icon">📊</span>
                        Usage & Limits
                    </div>
                    <a href="/docs/" target="_blank" class="menu-item">
                        <span class="menu-icon">📖</span>
                        API Documentation
                    </a>
                </div>
                
                <div class="menu-divider"></div>
                
                <div class="menu-item logout-item" onclick="userMenu.logout()">
                    <span class="menu-icon">🚪</span>
                    Sign Out
                </div>
            </div>

            <!-- Subscription Modal -->
            <div class="modal-overlay" id="subscription-modal" style="display: none;" onclick="userMenu.closeModal('subscription-modal')">
                <div class="modal-content" onclick="event.stopPropagation()">
                    <div class="modal-header">
                        <h3>Subscription Settings</h3>
                        <button class="modal-close" onclick="userMenu.closeModal('subscription-modal')">&times;</button>
                    </div>
                    <div class="modal-body" id="subscription-modal-content">
                        <div class="loading">Loading subscription details...</div>
                    </div>
                </div>
            </div>

            <!-- Usage Modal -->
            <div class="modal-overlay" id="usage-modal" style="display: none;" onclick="userMenu.closeModal('usage-modal')">
                <div class="modal-content" onclick="event.stopPropagation()">
                    <div class="modal-header">
                        <h3>Usage & Limits</h3>
                        <button class="modal-close" onclick="userMenu.closeModal('usage-modal')">&times;</button>
                    </div>
                    <div class="modal-body" id="usage-modal-content">
                        <div class="loading">Loading usage data...</div>
                    </div>
                </div>
            </div>
        `;

        // Add dropdown to sidebar area
        const sidebar = document.querySelector('.sidebar');
        if (sidebar) {
            sidebar.insertAdjacentHTML('afterend', dropdownHTML);
        } else {
            document.body.insertAdjacentHTML('beforeend', dropdownHTML);
        }
    }

    getAuthenticatedMenuHTML() {
        const avatarUrl = this.user?.picture || 'https://via.placeholder.com/40x40?text=U';
        const userName = this.user?.name || 'User';
        const userEmail = this.user?.email || '';

        return `
            <div class="user-menu-trigger" id="user-menu-trigger">
                <img src="${avatarUrl}" alt="User Avatar" class="user-avatar">
                <span class="user-name">${userName}</span>
                <svg class="dropdown-arrow" width="12" height="12" viewBox="0 0 12 12">
                    <path d="M2 4l4 4 4-4" stroke="currentColor" stroke-width="2" fill="none"/>
                </svg>
            </div>
            
            <div class="user-menu-dropdown" id="user-menu-dropdown" style="display: none;">
                <div class="menu-header">
                    <img src="${avatarUrl}" alt="User Avatar" class="menu-avatar">
                    <div class="menu-user-info">
                        <div class="menu-user-name">${userName}</div>
                        <div class="menu-user-email">${userEmail}</div>
                    </div>
                </div>
                
                <div class="menu-divider"></div>
                
                <div class="menu-section">
                    <div class="menu-section-title">Account</div>
                    <a href="/profile.html" class="menu-item">
                        <span class="menu-icon">👤</span>
                        Account Settings
                    </a>
                    <div class="menu-item" onclick="userMenu.showSubscriptionModal()">
                        <span class="menu-icon">💳</span>
                        Subscription Settings
                        <span class="subscription-badge" id="subscription-badge">Loading...</span>
                    </div>
                    <a href="/subscription.html" class="menu-item">
                        <span class="menu-icon">⬆️</span>
                        Upgrade Plan
                    </a>
                </div>
                
                <div class="menu-divider"></div>
                
                <div class="menu-section">
                    <div class="menu-item" onclick="userMenu.showUsageModal()">
                        <span class="menu-icon">📊</span>
                        Usage & Limits
                    </div>
                    <a href="/docs/" target="_blank" class="menu-item">
                        <span class="menu-icon">📖</span>
                        API Documentation
                    </a>
                </div>
                
                <div class="menu-divider"></div>
                
                <div class="menu-item logout-item" onclick="userMenu.logout()">
                    <span class="menu-icon">🚪</span>
                    Sign Out
                </div>
            </div>

            <!-- Subscription Modal -->
            <div class="modal-overlay" id="subscription-modal" style="display: none;" onclick="userMenu.closeModal('subscription-modal')">
                <div class="modal-content" onclick="event.stopPropagation()">
                    <div class="modal-header">
                        <h3>Subscription Settings</h3>
                        <button class="modal-close" onclick="userMenu.closeModal('subscription-modal')">&times;</button>
                    </div>
                    <div class="modal-body" id="subscription-modal-content">
                        <div class="loading">Loading subscription details...</div>
                    </div>
                </div>
            </div>

            <!-- Usage Modal -->
            <div class="modal-overlay" id="usage-modal" style="display: none;" onclick="userMenu.closeModal('usage-modal')">
                <div class="modal-content" onclick="event.stopPropagation()">
                    <div class="modal-header">
                        <h3>Usage & Limits</h3>
                        <button class="modal-close" onclick="userMenu.closeModal('usage-modal')">&times;</button>
                    </div>
                    <div class="modal-body" id="usage-modal-content">
                        <div class="loading">Loading usage data...</div>
                    </div>
                </div>
            </div>
        `;
    }

    getUnauthenticatedMenuHTML() {
        return `
            <div class="user-menu-trigger login-trigger" onclick="userMenu.login()">
                <span class="login-text">Sign In</span>
            </div>
        `;
    }

    addStyles() {
        const styles = `
            <style id="user-menu-styles">
                .user-menu-container {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    z-index: 1000;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                }

                .user-menu-trigger {
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    background: rgba(255, 255, 255, 0.95);
                    border-radius: 25px;
                    padding: 8px 16px;
                    cursor: pointer;
                    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
                    backdrop-filter: blur(10px);
                    transition: all 0.2s ease;
                    border: 2px solid transparent;
                }

                .user-menu-trigger:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 6px 25px rgba(0, 0, 0, 0.15);
                    border-color: #667eea;
                }

                .user-avatar {
                    width: 32px;
                    height: 32px;
                    border-radius: 50%;
                    border: 2px solid #667eea;
                }

                .user-name {
                    font-weight: 600;
                    color: #2d3748;
                    max-width: 120px;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    white-space: nowrap;
                }

                .dropdown-arrow {
                    color: #718096;
                    transition: transform 0.2s ease;
                }

                .user-menu-trigger.active .dropdown-arrow {
                    transform: rotate(180deg);
                }

                .login-trigger {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                }

                .login-text {
                    font-weight: 600;
                    color: white;
                }

                .sidebar-user-dropdown {
                    position: fixed;
                    top: 80px;
                    left: 150px;
                    background: white;
                    border-radius: 12px;
                    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
                    backdrop-filter: blur(20px);
                    min-width: 280px;
                    overflow: hidden;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    z-index: 1000;
                }

                .menu-header {
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    display: flex;
                    align-items: center;
                    gap: 12px;
                }

                .menu-avatar {
                    width: 48px;
                    height: 48px;
                    border-radius: 50%;
                    border: 3px solid rgba(255, 255, 255, 0.3);
                }

                .menu-user-name {
                    font-weight: 600;
                    font-size: 1.1rem;
                }

                .menu-user-email {
                    opacity: 0.9;
                    font-size: 0.9rem;
                }

                .menu-divider {
                    height: 1px;
                    background: #e2e8f0;
                    margin: 8px 0;
                }

                .menu-section {
                    padding: 8px 0;
                }

                .menu-section-title {
                    padding: 8px 20px;
                    font-size: 0.75rem;
                    font-weight: 600;
                    color: #718096;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }

                .menu-item {
                    display: flex;
                    align-items: center;
                    gap: 12px;
                    padding: 12px 20px;
                    color: #2d3748;
                    text-decoration: none;
                    cursor: pointer;
                    transition: background-color 0.2s ease;
                    position: relative;
                }

                .menu-item:hover {
                    background: #f7fafc;
                }

                .menu-icon {
                    font-size: 1.1rem;
                    width: 20px;
                    text-align: center;
                }

                .subscription-badge {
                    margin-left: auto;
                    padding: 2px 8px;
                    border-radius: 12px;
                    font-size: 0.75rem;
                    font-weight: 600;
                    text-transform: uppercase;
                }

                .badge-free {
                    background: #e2e8f0;
                    color: #4a5568;
                }

                .badge-pro {
                    background: #bee3f8;
                    color: #2b6cb0;
                }

                .badge-max {
                    background: #c6f6d5;
                    color: #276749;
                }

                .logout-item {
                    color: #e53e3e;
                }

                .logout-item:hover {
                    background: #fed7d7;
                }

                .modal-overlay {
                    position: fixed;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: rgba(0, 0, 0, 0.5);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    z-index: 2000;
                }

                .modal-content {
                    background: white;
                    border-radius: 12px;
                    max-width: 500px;
                    width: 90%;
                    max-height: 80vh;
                    overflow-y: auto;
                    box-shadow: 0 25px 50px rgba(0, 0, 0, 0.2);
                }

                .modal-header {
                    padding: 20px;
                    border-bottom: 1px solid #e2e8f0;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }

                .modal-header h3 {
                    color: #2d3748;
                    font-size: 1.25rem;
                    font-weight: 600;
                }

                .modal-close {
                    background: none;
                    border: none;
                    font-size: 1.5rem;
                    cursor: pointer;
                    color: #718096;
                    padding: 0;
                    width: 30px;
                    height: 30px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    border-radius: 50%;
                    transition: background-color 0.2s ease;
                }

                .modal-close:hover {
                    background: #f7fafc;
                }

                .modal-body {
                    padding: 20px;
                }

                .loading {
                    text-align: center;
                    padding: 20px;
                    color: #718096;
                }

                .usage-item {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 12px 0;
                    border-bottom: 1px solid #e2e8f0;
                }

                .usage-item:last-child {
                    border-bottom: none;
                }

                .usage-label {
                    font-weight: 500;
                    color: #4a5568;
                }

                .usage-bar {
                    flex: 1;
                    margin: 0 16px;
                    height: 8px;
                    background: #e2e8f0;
                    border-radius: 4px;
                    overflow: hidden;
                }

                .usage-fill {
                    height: 100%;
                    background: linear-gradient(90deg, #667eea, #764ba2);
                    border-radius: 4px;
                    transition: width 0.3s ease;
                }

                .usage-text {
                    font-size: 0.875rem;
                    color: #718096;
                    min-width: 80px;
                    text-align: right;
                }

                .subscription-info {
                    background: #f7fafc;
                    border-radius: 8px;
                    padding: 16px;
                    margin-bottom: 20px;
                }

                .subscription-tier {
                    font-size: 1.25rem;
                    font-weight: 600;
                    color: #2d3748;
                    margin-bottom: 8px;
                }

                .subscription-status {
                    display: inline-block;
                    padding: 4px 12px;
                    border-radius: 20px;
                    font-size: 0.875rem;
                    font-weight: 600;
                    text-transform: uppercase;
                }

                .btn {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 12px 24px;
                    font-weight: 600;
                    cursor: pointer;
                    transition: transform 0.2s ease;
                    text-decoration: none;
                    display: inline-block;
                    text-align: center;
                    margin-top: 16px;
                }

                .btn:hover {
                    transform: translateY(-2px);
                }

                .btn-secondary {
                    background: rgba(0, 0, 0, 0.1);
                    color: #4a5568;
                }

                @media (max-width: 768px) {
                    .user-menu-container {
                        top: 15px;
                        right: 15px;
                    }

                    .user-menu-dropdown {
                        min-width: 260px;
                    }

                    .modal-content {
                        width: 95%;
                        margin: 20px;
                    }
                }
            </style>
        `;

        // Remove existing styles
        const existingStyles = document.getElementById('user-menu-styles');
        if (existingStyles) {
            existingStyles.remove();
        }

        document.head.insertAdjacentHTML('beforeend', styles);
    }

    bindEvents() {
        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            const dropdown = document.getElementById('sidebar-user-dropdown');
            const profileIcon = document.querySelector('.sidebar .profile-icon');
            
            if (dropdown && !dropdown.contains(e.target) && !profileIcon?.contains(e.target)) {
                this.closeDropdown();
            }
        });

        // Prevent dropdown from closing when clicking inside
        const dropdown = document.getElementById('sidebar-user-dropdown');
        if (dropdown) {
            dropdown.addEventListener('click', (e) => {
                e.stopPropagation();
            });
        }

        // Load subscription info
        if (this.isAuthenticated) {
            this.loadSubscriptionInfo();
        }
    }

    toggleDropdown() {
        const dropdown = document.getElementById('sidebar-user-dropdown');
        
        if (!dropdown) {
            return; // No dropdown to toggle
        }

        if (dropdown.style.display === 'none') {
            dropdown.style.display = 'block';
        } else {
            dropdown.style.display = 'none';
        }
    }

    closeDropdown() {
        const dropdown = document.getElementById('sidebar-user-dropdown');

        if (dropdown) {
            dropdown.style.display = 'none';
        }
    }

    async loadSubscriptionInfo() {
        // Only load subscription info if authenticated
        if (!this.isAuthenticated) {
            console.log('User not authenticated, skipping subscription info load');
            this.updateSubscriptionBadge('free');
            return;
        }

        // Debounce to prevent rapid API calls
        const now = Date.now();
        if (now - this.lastSubscriptionLoad < this.subscriptionLoadDebounce) {
            console.log('Skipping subscription load - too soon since last load');
            return;
        }
        this.lastSubscriptionLoad = now;

        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 3000); // 3 second timeout
            
            const baseURL = window.location.origin.includes('localhost') ? 'http://localhost:5000' : window.location.origin;
            const response = await fetch(`${baseURL}/api/v1/auth/usage`, {
                headers: await this.api.getAuthHeaders(),
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            if (response.ok) {
                // Check if response is JSON
                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('application/json')) {
                    const data = await response.json();
                    this.updateSubscriptionBadge(data.tier);
                } else {
                    console.warn('Server returned non-JSON response, using default subscription info');
                    this.updateSubscriptionBadge('free');
                }
            } else if (response.status === 401) {
                console.log('User not authenticated (401), using default subscription info');
                this.updateSubscriptionBadge('free');
            } else if (response.status === 500) {
                console.warn('Server error (500) - this usually means authentication is required');
                this.updateSubscriptionBadge('free');
            } else {
                console.warn(`Server returned ${response.status}, using default subscription info`);
                this.updateSubscriptionBadge('free');
            }
        } catch (error) {
            if (error.name === 'AbortError') {
                console.warn('Subscription request timed out - server may be unavailable');
            } else {
                console.warn('Failed to load subscription info:', error.message);
            }
            this.updateSubscriptionBadge('free');
        }
    }

    updateSubscriptionBadge(tier) {
        const badge = document.getElementById('subscription-badge');
        if (badge) {
            badge.textContent = tier.toUpperCase();
            badge.className = `subscription-badge badge-${tier}`;
        }
    }

    async showSubscriptionModal() {
        const modal = document.getElementById('subscription-modal');
        const content = document.getElementById('subscription-modal-content');

        modal.style.display = 'flex';
        content.innerHTML = '<div class="loading">Loading subscription details...</div>';

        try {
            const baseURL = window.location.origin.includes('localhost') ? 'http://localhost:5000' : window.location.origin;
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout
            
            const [usageResponse, statusResponse] = await Promise.all([
                fetch(`${baseURL}/api/v1/auth/usage`, { 
                    headers: await this.api.getAuthHeaders(),
                    signal: controller.signal
                }),
                fetch(`${baseURL}/api/v1/subscription/status`, { 
                    headers: await this.api.getAuthHeaders(),
                    signal: controller.signal
                })
            ]);

            clearTimeout(timeoutId);

            // Check if responses are JSON before parsing
            const usageContentType = usageResponse.headers.get('content-type');
            const statusContentType = statusResponse.headers.get('content-type');

            if (usageResponse.ok && statusResponse.ok && 
                usageContentType?.includes('application/json') &&
                statusContentType?.includes('application/json')) {
                
                const usage = await usageResponse.json();
                const status = await statusResponse.json();
                content.innerHTML = this.getSubscriptionModalContent(usage, status);
            } else {
                content.innerHTML = '<div class="error">Server is currently unavailable. Please try again later.</div>';
            }
        } catch (error) {
            if (error.name === 'AbortError') {
                content.innerHTML = '<div class="error">Request timed out. Please check your connection.</div>';
            } else {
                content.innerHTML = '<div class="error">Server is currently unavailable. Please try again later.</div>';
            }
        }

        this.closeDropdown();
    }

    getSubscriptionModalContent(usage, status) {
        return `
            <div class="subscription-info">
                <div class="subscription-tier">${usage.tier_display_name} Plan</div>
                <span class="subscription-status badge-${usage.tier}">${status.status}</span>
                ${status.tier !== 'free' ? `
                    <div style="margin-top: 12px; font-size: 0.9rem; color: #718096;">
                        ${status.billing_cycle ? `Billing: ${status.billing_cycle}` : ''}
                        ${status.current_period_end ? `<br>Next billing: ${new Date(status.current_period_end * 1000).toLocaleDateString()}` : ''}
                    </div>
                ` : ''}
            </div>

            <div class="usage-stats">
                <h4 style="margin-bottom: 16px; color: #2d3748;">Current Usage</h4>
                ${Object.entries(usage.usage).map(([key, data]) => {
                    const percentage = data.limit === 'unlimited' ? 0 : (data.used / data.limit) * 100;
                    const limitText = data.limit === 'unlimited' ? '∞' : data.limit;
                    
                    return `
                        <div class="usage-item">
                            <span class="usage-label">${this.formatUsageLabel(key)}</span>
                            <div class="usage-bar">
                                <div class="usage-fill" style="width: ${Math.min(percentage, 100)}%"></div>
                            </div>
                            <span class="usage-text">${data.used} / ${limitText}</span>
                        </div>
                    `;
                }).join('')}
            </div>

            <div style="text-align: center; margin-top: 20px;">
                ${status.tier === 'free' ? `
                    <a href="/subscription.html" class="btn">Upgrade Plan</a>
                ` : `
                    <button class="btn btn-secondary" onclick="userMenu.manageBilling()">Manage Billing</button>
                `}
            </div>
        `;
    }

    async showUsageModal() {
        const modal = document.getElementById('usage-modal');
        const content = document.getElementById('usage-modal-content');

        modal.style.display = 'flex';
        content.innerHTML = '<div class="loading">Loading usage data...</div>';

        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout
            
            const baseURL = window.location.origin.includes('localhost') ? 'http://localhost:5000' : window.location.origin;
            const response = await fetch(`${baseURL}/api/v1/auth/usage`, {
                headers: await this.api.getAuthHeaders(),
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            if (response.ok) {
                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('application/json')) {
                    const usage = await response.json();
                    content.innerHTML = this.getUsageModalContent(usage);
                } else {
                    content.innerHTML = '<div class="error">Server returned invalid response format.</div>';
                }
            } else {
                content.innerHTML = '<div class="error">Server is currently unavailable.</div>';
            }
        } catch (error) {
            if (error.name === 'AbortError') {
                content.innerHTML = '<div class="error">Request timed out. Please check your connection.</div>';
            } else {
                content.innerHTML = '<div class="error">Server is currently unavailable. Please try again later.</div>';
            }
        }

        this.closeDropdown();
    }

    getUsageModalContent(usage) {
        return `
            <div style="margin-bottom: 20px;">
                <h4 style="color: #2d3748; margin-bottom: 8px;">${usage.tier_display_name} Plan</h4>
                <p style="color: #718096; font-size: 0.9rem;">
                    Current period started: ${new Date(usage.current_period_start).toLocaleDateString()}
                </p>
            </div>

            ${Object.entries(usage.usage).map(([key, data]) => {
                const percentage = data.limit === 'unlimited' ? 0 : (data.used / data.limit) * 100;
                const limitText = data.limit === 'unlimited' ? '∞' : data.limit;
                
                return `
                    <div class="usage-item">
                        <span class="usage-label">${this.formatUsageLabel(key)}</span>
                        <div class="usage-bar">
                            <div class="usage-fill" style="width: ${Math.min(percentage, 100)}%"></div>
                        </div>
                        <span class="usage-text">${data.used} / ${limitText}</span>
                    </div>
                `;
            }).join('')}

            <div style="margin-top: 20px; padding: 16px; background: #f7fafc; border-radius: 8px; font-size: 0.9rem; color: #718096;">
                <strong>Available Features:</strong><br>
                ${Object.entries(usage.features).map(([key, enabled]) => 
                    `• ${this.formatFeatureLabel(key)}: ${enabled ? '✅ Enabled' : '❌ Disabled'}`
                ).join('<br>')}
            </div>

            ${usage.tier === 'free' ? `
                <div style="text-align: center; margin-top: 20px;">
                    <a href="/subscription.html" class="btn">Upgrade for More Usage</a>
                </div>
            ` : ''}
        `;
    }

    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'none';
        }
    }

    async manageBilling() {
        try {
            const baseURL = window.location.origin.includes('localhost') ? 'http://localhost:5000' : window.location.origin;
            const response = await fetch(`${baseURL}/api/v1/subscription/billing-portal`, {
                method: 'POST',
                headers: await this.api.getAuthHeaders(),
                body: JSON.stringify({
                    return_url: window.location.href
                })
            });

            if (response.ok) {
                const data = await response.json();
                window.location.href = data.portal_url;
            } else {
                alert('Failed to open billing portal. Please try again.');
            }
        } catch (error) {
            console.error('Billing portal error:', error);
            alert('Failed to open billing portal. Please try again.');
        }
    }

    async login() {
        try {
            const auth0Service = await getAuth0Service();
            await auth0Service.login();
        } catch (error) {
            console.error('Login failed:', error);
        }
    }

    async logout() {
        try {
            const auth0Service = await getAuth0Service();
            await auth0Service.logout();
            // Update local state
            this.isAuthenticated = false;
            this.user = null;
            // Remove dropdown
            this.createMenuHTML();
            // Refresh Vue component if available
            if (window.vueApp && window.vueApp.checkAuthStatus) {
                await window.vueApp.checkAuthStatus();
            }
        } catch (error) {
            console.error('Logout failed:', error);
        }
    }

    formatUsageLabel(key) {
        const labels = {
            translations: 'Translations',
            replies: 'Reply Generation',
            writes: 'Text Generation',
            influx_queries: 'Analytics Queries'
        };
        return labels[key] || key;
    }

    formatFeatureLabel(key) {
        const labels = {
            api_access: 'API Access',
            priority_support: 'Priority Support',
            custom_styles: 'Custom Styles',
            batch_operations: 'Batch Operations'
        };
        return labels[key] || key;
    }
}

// Global instance
let userMenu = null;

// Initialize user menu when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    userMenu = new UserMenu();
    window.userMenu = userMenu; // Make globally accessible
});

// Export for use in other files
window.UserMenu = UserMenu;