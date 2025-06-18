# WebCammer+ Test Suite

This directory contains all test files for the WebCammer+ browser extension, organized by category.

## Test Dashboard

Open `index.html` in your browser to access the test dashboard with links to all available tests.

## Directory Structure

```
tests/
├── api/              # API endpoint testing
├── analytics/        # Analytics feature tests
├── components/       # UI component tests
├── integration/      # End-to-end integration tests
├── utils/           # Debug and utility tools
└── index.html       # Test dashboard
```

## Test Categories

### 🟢 API Testing (`/api`)
- **test-all-frontend-api-calls.html** - Comprehensive API endpoint testing
- **test-platform-status.html** - Platform status endpoint verification

### 🟡 Analytics (`/analytics`)
- **test-analytics-api.html** - Analytics API integration tests
- **test-analytics.html** - Analytics UI component tests

### 🔴 Integration (`/integration`)
- **test-integration.html** - End-to-end integration testing
- **test-popup-integration.html** - Popup with backend service integration

### 🔵 UI Components (`/components`)
- **test-popup.html** - Basic popup functionality
- **test-popup-external.html** - Popup with external connections
- **test-refactor.html** - Refactored component testing
- **test-tippers-tab.html** - Tippers tab specific tests
- **user-menu-demo.html** - User menu component demo

### ⚙️ Utilities (`/utils`)
- **debug-popup.html** - Debug utility for Vue.js integration

## Running Tests

1. **Backend Requirements**:
   ```bash
   # Start InfluxDB
   docker-compose up -d
   
   # Start Flask backend
   python3 app.py
   ```

2. **Open Test Dashboard**:
   - Navigate to `/sider/tests/index.html` in your browser
   - Click on any test card to run that specific test

3. **Direct Test Access**:
   - You can also open any test file directly in your browser
   - Example: `file:///path/to/sider/tests/test-analytics.html`

## Test Environment

All tests are configured to:
- Use the refactored modular architecture
- Connect to local backend (http://localhost:5000)
- Include proper error handling and logging
- Provide visual feedback for test results

## Adding New Tests

1. Create your test file in this directory
2. Use the existing test files as templates
3. Update the test dashboard (`index.html`) to include your new test
4. Follow the naming convention: `test-[feature-name].html`