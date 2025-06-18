# WebCammer+ Sider Folder Structure

```
sider/
├── assets/                    # Static assets
│   └── popup.css             # Main stylesheet
│
├── js/                       # All JavaScript code (tests co-located)
│   ├── core/                # Core services
│   │   ├── auth0-service.js # Auth0 integration
│   │   ├── novita-api.js    # AI service integration
│   │   └── user-menu.js     # User menu logic
│   │
│   ├── components/          # Vue.js components
│   │   ├── analytics/      # Analytics components
│   │   ├── chat/          # Chat components
│   │   ├── common/        # Shared components
│   │   ├── edit/          # Edit/Write components
│   │   ├── home/          # Home view components
│   │   ├── inbox/         # Inbox components
│   │   ├── sidebar/       # Sidebar components
│   │   ├── translate/     # Translation components
│   │   ├── App.js         # Legacy app component
│   │   ├── AppRefactored.js # Refactored app
│   │   ├── AppUltraSlim.js  # Ultra slim app
│   │   └── component-loader.js # Component registration
│   │
│   ├── helpers/            # Utility functions
│   │   ├── EventParser.js  # Parse Chaturbate events
│   │   ├── EventParser.test.js # Tests for EventParser
│   │   └── TimeFormatter.js # Time formatting
│   │
│   ├── modules/            # Business logic modules
│   │   ├── AuthModule.js   # Authentication logic
│   │   ├── ChatModule.js   # Chat functionality
│   │   ├── FilterModule.js # Message filtering
│   │   ├── FilterModule.test.js # Tests for FilterModule
│   │   └── InboxModule.js  # Inbox management
│   │
│   ├── services/           # Service layer
│   │   ├── ApiService.js   # API communication
│   │   ├── ApiService.test.js # Tests for ApiService
│   │   ├── StateManager.js # State management
│   │   └── WebSocketService.js # WebSocket handling
│   │
│   ├── inbox.js            # Inbox page logic
│   ├── popup.js            # Main popup logic
│   ├── popup.test.js       # Tests for popup.js
│   ├── test-popup.js       # Popup test utilities
│   └── verify-platform-status.js # Platform verification
│
├── lib/                      # Third-party libraries
│   └── vue.js               # Vue.js framework
│
├── pages/                    # User-facing pages
│   ├── inbox.html           # Private messages interface
│   ├── profile.html         # User profile management
│   └── subscription.html    # Subscription plans
│
├── public/                   # Extension assets
│   └── icons/               # Extension icons
│
├── tests-manual/             # Manual browser tests (HTML files)
│   ├── api/                 # API testing pages
│   ├── analytics/           # Analytics testing pages
│   ├── components/          # Component testing pages
│   ├── integration/         # Integration testing pages
│   ├── utils/               # Debug utilities
│   ├── index.html           # Test dashboard
│   └── README.md            # Manual test documentation
│
├── tools/                    # Development tools
│   └── platform-launcher.html # Service status dashboard
│
├── DEPRECATED/              # Old/archived versions
│   ├── index-legacy.html    # Original popup version
│   ├── index-modular.html   # Modular version
│   └── index-refactored.html # Refactored version
│
└── Root files
    └── index.html           # Main extension popup (entry point)
```

## Directory Organization Principles

### `/js` - JavaScript Code
All JavaScript code is organized under this directory:
- **`/core`**: Core services that are used across the application
- **`/components`**: Vue.js components organized by feature
- **`/helpers`**: Pure utility functions with no side effects
- **`/modules`**: Business logic that orchestrates components and services
- **`/services`**: Singleton services for external communication

### `/assets` - Static Assets
CSS files and other static resources.

### `/lib` - Third-party Libraries
External libraries that are not managed by npm.

### `/tests` - Test Suite
Comprehensive test files organized by type with a central dashboard.

### Root Directory
Contains only HTML entry points and configuration files for a clean structure.

## Benefits of This Structure

1. **Clean Root Directory**: Only HTML files and config at the root
2. **Logical Organization**: JavaScript grouped by functionality
3. **Easy Navigation**: Clear hierarchy makes finding files simple
4. **Scalability**: Easy to add new features in appropriate directories
5. **Separation of Concerns**: Clear boundaries between different types of code
6. **No Build Step Required**: Structure optimized for browser extension that loads files directly

## Why No `src` Directory?

This is a browser extension that:
- Loads JavaScript files directly without bundling
- Uses Vue.js from CDN
- Doesn't require TypeScript compilation
- Has no build process for the extension itself

Therefore, we use a simpler structure with `js/` for code and `assets/` for styles, rather than a `src/` directory which is typically used for source code that needs compilation.

## Import Path Examples

```javascript
// From an HTML file in root
<script src="js/core/auth0-service.js"></script>
<script src="js/components/home/HomeView.js"></script>

// From a test file
<script src="../js/services/ApiService.js"></script>

// From within JS files (relative paths)
import { EventParser } from '../helpers/EventParser.js';
```