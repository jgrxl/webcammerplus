// Analytics View Component - Rankings Page
const AnalyticsView = {
  name: 'AnalyticsView',
  
  data() {
    return {
      // Loading states
      loading: false,
      loadingTippers: false,
      
      // Time periods
      periods: [
        { value: 1, label: 'Today' },
        { value: 7, label: 'This Week' },
        { value: 30, label: 'This Month' },
        { value: 365, label: 'This Year' }
      ],
      selectedPeriod: 7,
      
      // Rankings data
      tippers: [],
      totalTips: 0,
      
      // Refresh
      lastRefresh: null,
      refreshInterval: null
    };
  },
  
  mounted() {
    // Load initial data
    this.loadRankings();
    
    // Auto-refresh every 60 seconds
    this.refreshInterval = setInterval(() => {
      this.loadRankings();
    }, 60000);
  },
  
  beforeUnmount() {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
    }
  },
  
  methods: {
    async loadRankings() {
      this.loadingTippers = true;
      
      try {
        // Fetch tippers from API
        const [tippersResult, tipsResult] = await Promise.all([
          window.apiService.getTippers(this.selectedPeriod, 50),
          window.apiService.getTotalTips(this.selectedPeriod)
        ]);
        
        if (tippersResult.success) {
          this.tippers = tippersResult.tippers || [];
        }
        
        if (tipsResult.success) {
          this.totalTips = tipsResult.total_tokens || 0;
        }
        
        this.lastRefresh = new Date();
      } catch (error) {
        console.error('Failed to load rankings:', error);
      } finally {
        this.loadingTippers = false;
      }
    },
    
    async changePeriod(days) {
      this.selectedPeriod = days;
      await this.loadRankings();
    },
    
    async refreshData() {
      this.loading = true;
      await this.loadRankings();
      this.loading = false;
    },
    
    getRankBadge(index) {
      const badges = ['👑', '🥈', '🥉'];
      return badges[index] || '';
    },
    
    getRankClass(index) {
      if (index === 0) return 'gold';
      if (index === 1) return 'silver';
      if (index === 2) return 'bronze';
      return '';
    },
    
    formatNumber(num) {
      if (!num) return '0';
      return new Intl.NumberFormat('en-US').format(num);
    },
    
    formatCurrency(tokens) {
      const usd = tokens * 0.05; // $0.05 per token
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2
      }).format(usd);
    },
    
    formatTimeAgo(date) {
      if (!date) return 'Never';
      const now = new Date();
      const diff = now - new Date(date);
      const minutes = Math.floor(diff / 60000);
      
      if (minutes < 1) return 'Just now';
      if (minutes < 60) return `${minutes}m ago`;
      if (minutes < 1440) return `${Math.floor(minutes / 60)}h ago`;
      return `${Math.floor(minutes / 1440)}d ago`;
    },
    
    getTopTipper() {
      return this.tippers[0] || null;
    },
    
    getTipperPercentage(tokens) {
      if (!this.totalTips) return 0;
      return ((tokens / this.totalTips) * 100).toFixed(1);
    },
    
    async viewUserProfile(username) {
      // Emit event to parent to handle user profile view
      this.$emit('view-user', username);
    }
  },
  
  template: `
    <div class="rankings-view">
      <!-- Header -->
      <div class="rankings-header">
        <h2>🏆 Top Tippers Ranking</h2>
        <div class="header-actions">
          <span v-if="lastRefresh" class="last-refresh">
            Last updated: {{ formatTimeAgo(lastRefresh) }}
          </span>
          <button 
            @click="refreshData" 
            :disabled="loading"
            class="refresh-btn"
          >
            <span v-if="loading">🔄 Loading...</span>
            <span v-else>🔄 Refresh</span>
          </button>
        </div>
      </div>
      
      <!-- Period Selector -->
      <div class="period-selector">
        <button
          v-for="period in periods"
          :key="period.value"
          @click="changePeriod(period.value)"
          :class="['period-btn', { active: selectedPeriod === period.value }]"
        >
          {{ period.label }}
        </button>
      </div>
      
      <!-- Summary Stats -->
      <div class="summary-stats" v-if="!loadingTippers">
        <div class="stat-card">
          <div class="stat-label">Total Tips</div>
          <div class="stat-value">{{ formatNumber(totalTips) }} tokens</div>
          <div class="stat-subtext">{{ formatCurrency(totalTips) }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Top Tippers</div>
          <div class="stat-value">{{ tippers.length }}</div>
          <div class="stat-subtext">Unique users</div>
        </div>
        <div class="stat-card" v-if="getTopTipper()">
          <div class="stat-label">#1 Tipper</div>
          <div class="stat-value">{{ getTopTipper().username }}</div>
          <div class="stat-subtext">{{ formatNumber(getTopTipper().total_tokens) }} tokens</div>
        </div>
      </div>
      
      <!-- Loading State -->
      <div v-if="loadingTippers" class="loading-container">
        <div class="loading-spinner">⏳</div>
        <p>Loading rankings...</p>
      </div>
      
      <!-- Rankings Table -->
      <div v-else-if="tippers.length > 0" class="rankings-table">
        <div class="table-header">
          <div class="rank-col">Rank</div>
          <div class="user-col">Username</div>
          <div class="tokens-col">Tokens</div>
          <div class="amount-col">Amount</div>
          <div class="share-col">Share</div>
        </div>
        
        <div 
          v-for="(tipper, index) in tippers" 
          :key="tipper.username"
          :class="['table-row', getRankClass(index)]"
        >
          <div class="rank-col">
            <span class="rank-number">#{{ index + 1 }}</span>
            <span class="rank-badge">{{ getRankBadge(index) }}</span>
          </div>
          <div class="user-col">
            <span class="username" @click="viewUserProfile(tipper.username)">
              {{ tipper.username }}
            </span>
          </div>
          <div class="tokens-col">
            <span class="token-amount">{{ formatNumber(tipper.total_tokens) }}</span>
          </div>
          <div class="amount-col">
            <span class="usd-amount">{{ formatCurrency(tipper.total_tokens) }}</span>
          </div>
          <div class="share-col">
            <div class="share-bar">
              <div 
                class="share-fill" 
                :style="{ width: getTipperPercentage(tipper.total_tokens) + '%' }"
              ></div>
              <span class="share-percent">{{ getTipperPercentage(tipper.total_tokens) }}%</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Empty State -->
      <div v-else class="empty-state">
        <div class="empty-icon">🏆</div>
        <h3>No tippers yet</h3>
        <p>Rankings will appear here once users start tipping</p>
      </div>
    </div>
  `,
  
  style: `
    <style>
    .rankings-view {
      display: flex;
      flex-direction: column;
      height: 100%;
      padding: 0;
      background: transparent;
      overflow-y: auto;
    }
    
    /* Header */
    .rankings-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
    }
    
    .rankings-header h2 {
      font-size: 24px;
      font-weight: 700;
      color: #1f2937;
      margin: 0;
    }
    
    .header-actions {
      display: flex;
      align-items: center;
      gap: 16px;
    }
    
    .last-refresh {
      font-size: 14px;
      color: #64748b;
    }
    
    .refresh-btn {
      padding: 8px 16px;
      background: white;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      font-size: 14px;
      font-weight: 500;
      color: #334155;
      cursor: pointer;
      transition: all 0.2s;
    }
    
    .refresh-btn:hover:not(:disabled) {
      background: #f1f5f9;
      border-color: #cbd5e1;
    }
    
    .refresh-btn:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
    
    /* Period Selector */
    .period-selector {
      display: flex;
      gap: 8px;
      margin-bottom: 24px;
      background: white;
      padding: 8px;
      border-radius: 12px;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    .period-btn {
      flex: 1;
      padding: 10px 16px;
      background: transparent;
      border: none;
      border-radius: 8px;
      font-size: 14px;
      font-weight: 600;
      color: #64748b;
      cursor: pointer;
      transition: all 0.2s;
    }
    
    .period-btn:hover {
      background: #f1f5f9;
      color: #334155;
    }
    
    .period-btn.active {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
    }
    
    /* Summary Stats */
    .summary-stats {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 16px;
      margin-bottom: 24px;
    }
    
    .stat-card {
      background: white;
      padding: 20px;
      border-radius: 12px;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
      text-align: center;
    }
    
    .stat-label {
      font-size: 14px;
      color: #64748b;
      margin-bottom: 8px;
    }
    
    .stat-value {
      font-size: 24px;
      font-weight: 700;
      color: #1f2937;
      margin-bottom: 4px;
    }
    
    .stat-subtext {
      font-size: 14px;
      color: #10b981;
      font-weight: 500;
    }
    
    /* Loading State */
    .loading-container {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-height: 300px;
      color: #64748b;
    }
    
    .loading-spinner {
      font-size: 48px;
      margin-bottom: 16px;
      animation: pulse 1.5s ease-in-out infinite;
    }
    
    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.5; }
    }
    
    /* Rankings Table */
    .rankings-table {
      background: white;
      border-radius: 12px;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
      overflow: hidden;
    }
    
    .table-header {
      display: flex;
      align-items: center;
      padding: 16px 20px;
      background: #f8fafc;
      border-bottom: 2px solid #e2e8f0;
      font-size: 12px;
      font-weight: 600;
      text-transform: uppercase;
      color: #64748b;
    }
    
    .table-row {
      display: flex;
      align-items: center;
      padding: 16px 20px;
      border-bottom: 1px solid #f1f5f9;
      transition: all 0.2s;
    }
    
    .table-row:hover {
      background: #f8fafc;
    }
    
    .table-row.gold {
      background: linear-gradient(90deg, #fef3c7 0%, transparent 100%);
    }
    
    .table-row.silver {
      background: linear-gradient(90deg, #e0e7ff 0%, transparent 100%);
    }
    
    .table-row.bronze {
      background: linear-gradient(90deg, #fed7aa 0%, transparent 100%);
    }
    
    /* Table Columns */
    .rank-col {
      width: 80px;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    
    .user-col {
      flex: 1;
      min-width: 0;
    }
    
    .tokens-col {
      width: 120px;
      text-align: right;
    }
    
    .amount-col {
      width: 120px;
      text-align: right;
    }
    
    .share-col {
      width: 150px;
    }
    
    /* Rank Styling */
    .rank-number {
      font-weight: 700;
      color: #334155;
    }
    
    .rank-badge {
      font-size: 20px;
    }
    
    /* Username */
    .username {
      font-weight: 600;
      color: #1f2937;
      cursor: pointer;
      transition: color 0.2s;
    }
    
    .username:hover {
      color: #667eea;
      text-decoration: underline;
    }
    
    /* Token Amount */
    .token-amount {
      font-weight: 600;
      color: #334155;
    }
    
    /* USD Amount */
    .usd-amount {
      font-weight: 500;
      color: #10b981;
    }
    
    /* Share Bar */
    .share-bar {
      position: relative;
      height: 20px;
      background: #f1f5f9;
      border-radius: 10px;
      overflow: hidden;
    }
    
    .share-fill {
      position: absolute;
      left: 0;
      top: 0;
      height: 100%;
      background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
      transition: width 0.3s ease;
    }
    
    .share-percent {
      position: relative;
      display: block;
      text-align: center;
      font-size: 11px;
      font-weight: 600;
      color: #334155;
      line-height: 20px;
    }
    
    /* Empty State */
    .empty-state {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-height: 300px;
      padding: 40px;
      text-align: center;
    }
    
    .empty-icon {
      font-size: 64px;
      margin-bottom: 16px;
    }
    
    .empty-state h3 {
      font-size: 20px;
      font-weight: 600;
      color: #1f2937;
      margin: 0 0 8px 0;
    }
    
    .empty-state p {
      font-size: 14px;
      color: #64748b;
      margin: 0;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
      .rankings-view {
        padding: 16px;
      }
      
      .period-selector {
        flex-wrap: wrap;
      }
      
      .period-btn {
        min-width: calc(50% - 4px);
      }
      
      .summary-stats {
        grid-template-columns: 1fr;
      }
      
      .table-header,
      .table-row {
        font-size: 12px;
        padding: 12px 16px;
      }
      
      .share-col {
        display: none;
      }
    }
    </style>
  `
};

// Register the component
window.componentLoader.register('analytics-view', AnalyticsView);