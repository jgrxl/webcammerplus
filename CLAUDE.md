# WebCammerPlus - Project Context & Development Guide

## 🚀 Project Overview

**WebCammerPlus** is a comprehensive SaaS platform that provides AI-powered translation, content generation, and real-time analytics for adult webcam platforms (specifically Chaturbate). The system combines a Flask-based API backend with a Vue.js browser extension frontend, offering subscription-based AI services with real-time data processing capabilities.

## 🛠 Tech Stack Overview

### Backend (Python/Flask)
- **Primary Language:** Python 3.13
- **Web Framework:** Flask 3.1.1 with Flask-RESTx for API documentation
- **Real-time:** Flask-SocketIO 5.5.1 for WebSocket connections
- **Database:** InfluxDB 2.7 (time-series data for analytics)
- **Authentication:** Auth0 OAuth 2.0 + JWT tokens
- **Payments:** Stripe integration for subscriptions
- **AI Services:** Novita AI API for translations/text generation
- **Containerization:** Docker & Docker Compose
- **Code Quality:** Black, Flake8, MyPy, Bandit, pytest

### Frontend (Vue.js/TypeScript)
- **Framework:** Vue.js 3.4.0 with TypeScript
- **Build Tool:** Vite 5.0.0
- **Styling:** Tailwind CSS 4.1.10
- **Authentication:** Auth0 SPA SDK
- **Architecture:** Browser extension (Manifest V3)
- **Real-time:** WebSocket client for live updates

### Infrastructure & Services
- **Database:** InfluxDB (containerized)
- **Payment Processing:** Stripe
- **Authentication:** Auth0
- **AI Services:** Novita AI API
- **Development:** Docker Compose orchestration

## 📋 Essential Commands

### Quick Development Reference
```bash
# Environment Setup
python3 --version                    # Verify Python 3.13
pip3 install -r requirements.txt     # Install dependencies
pip3 install -r requirements-dev.txt # Install dev tools
cp .env.example .env                 # Create environment file

# Docker Services
docker-compose up -d                 # Start InfluxDB
docker ps                           # Verify containers running
curl -f http://localhost:8086/health # Test InfluxDB connectivity

# Application
python3 app.py                       # Start Flask development server
# Navigate to http://localhost:5000   # Access API documentation

# Frontend (in sider directory)
cd sider
npm install                          # Install dependencies  
npm run dev                          # Start development server
npm run build                        # Build for production
```

### Quality Assurance Pipeline
```bash
# Pre-commit Quality Checks (MANDATORY before commits)
black .                              # 1. Format code
isort .                              # 2. Sort imports  
flake8 . --count --statistics        # 3. Lint code
bandit -r . -f txt                   # 4. Security scan
safety check                         # 5. Vulnerability check
mypy . --ignore-missing-imports      # 6. Type checking (optional)
```

### Testing Commands
```bash
# Python Tests
PYTHONPATH=$PWD pytest --tb=short -v                    # Run all tests
PYTHONPATH=$PWD pytest services/helper_test.py -v       # Run specific test
pytest --cov=. --cov-report=html                        # Coverage report

# Integration Testing
python3 -c "from client.influx_client import InfluxDBClient; InfluxDBClient(); print('✅ DB OK')"
python3 -c "from app import create_app; create_app(); print('✅ App OK')"
```

### Git Workflow
```bash
# Conventional Commits Format
git commit -m "feat(api): add real-time translation endpoint"
git commit -m "fix(auth): resolve Auth0 token validation issue"
git commit -m "docs(setup): update Docker configuration guide"
git commit -m "test(websocket): add unit tests for real-time events"

# Deployment
git push origin main                 # Deploy to production
```

## 🏗 Standard Development Workflow

### 1. Analysis Phase
- **Context Gathering:** Review existing Flask routes and Vue components
- **Architecture Understanding:** Study the WebSocket event flow and InfluxDB schema
- **Integration Points:** Understand Auth0, Stripe, and AI service integrations
- **Testing Review:** Check pytest structure and WebSocket testing patterns
- **Environment Verification:** Ensure InfluxDB is running and .env is configured
- **Planning:** Document changes in clear, measurable todo items

### 2. Planning Review & Validation
- **Architecture Alignment:** Confirm approach fits Flask-SocketIO + Vue.js structure
- **Security Considerations:** Verify Auth0 JWT handling and Stripe webhook validation
- **Performance Impact:** Consider effects on real-time WebSocket performance
- **Subscription Model:** Ensure changes respect usage limits per tier
- **Integration Dependencies:** Account for Auth0, Stripe, InfluxDB, and AI API constraints

### 3. Implementation Protocol
- **Environment First:** Verify Docker services are running (`docker ps`)
- **Incremental Development:** Work through features one endpoint/component at a time
- **Real-time Testing:** Test WebSocket connections during development
- **Database Verification:** Check InfluxDB queries and data integrity
- **Integration Testing:** Verify Auth0 flows and Stripe webhooks
- **Quality Monitoring:** Run complete quality pipeline before commits

### 4. Quality Gates (MANDATORY - NO EXCEPTIONS)
```bash
# Complete quality pipeline (must pass before any commit):
docker ps                            # 1. Verify services running
python3 -c "from app import create_app; create_app()"  # 2. App loads
black . && isort .                   # 3. Format code
flake8 . --count --statistics        # 4. Lint checks  
bandit -r . -f txt                   # 5. Security scan
safety check                         # 6. Vulnerability check
pytest --tb=short                    # 7. Run tests
git status                           # 8. Review changes - VERIFY NO SECRETS
```
**CRITICAL:** If ANY step fails, fix before proceeding. No exceptions.

### 🔒 SECURITY & SECRETS PROTECTION (MANDATORY)
**BEFORE EVERY COMMIT:** Verify git status shows NO sensitive data:
- ❌ NO API keys or tokens in code
- ❌ NO .env files with real credentials
- ❌ NO Stripe secrets or webhook endpoints
- ❌ NO Auth0 client secrets
- ❌ NO database passwords or connection strings
- ✅ All secrets must be in `.env` (gitignored) or environment variables

```bash
# Quick security check before commit:
git status | grep -E "\.env$|_SECRET|_KEY|password|token" && echo "⚠️  SECRETS DETECTED - DO NOT COMMIT" || echo "✅ Safe to commit"
```

## 🏛 Architecture & Code Organization

### Backend Structure (Flask)
```
server/
├── app.py                    # Main Flask application + API namespaces
├── client/                   # External service clients
│   ├── influx_client.py     # InfluxDB client wrapper
│   ├── chaturbate_client_*  # Chaturbate integration
│   └── models.py            # Data models
├── routes/                   # API endpoint definitions
│   ├── auth_route.py        # Auth0 authentication
│   ├── subscription_route.py # Stripe subscription management
│   ├── translate_route.py   # AI translation services
│   ├── reply_route.py       # AI reply generation
│   ├── write_route.py       # AI content generation
│   ├── chaturbate_route.py  # WebSocket + Chaturbate events
│   └── influx_route.py      # Analytics queries
├── services/                 # Business logic layer
│   ├── influx_db_service.py # Data analytics
│   ├── user_service.py      # User management
│   ├── stripe_service.py    # Payment processing
│   └── *_service.py         # AI service integrations
├── models/                   # Data models
│   ├── user.py              # User and subscription models
│   └── subscription_tiers.py # Tier definitions and limits
├── utils/                    # Utility functions
│   ├── auth.py              # Auth0 JWT validation
│   └── query_builder.py     # InfluxDB query builder
└── docker-compose.yml       # InfluxDB container setup
```

### Frontend Structure (Vue.js)
```
sider/
├── src/
│   ├── components/          # Vue.js components
│   ├── stores/              # State management
│   └── types/               # TypeScript definitions
├── public/                  # Browser extension manifest
├── build.js                 # Build configuration
└── package.json             # Dependencies
```

### Key Architectural Patterns
- **RESTful API:** Flask-RESTx with automatic OpenAPI documentation
- **WebSocket Communication:** Real-time events via Flask-SocketIO
- **Time-Series Analytics:** InfluxDB for real-time data storage and querying
- **OAuth Authentication:** Auth0 integration with JWT validation
- **Subscription Management:** Stripe webhooks for subscription lifecycle
- **Microservice Communication:** Service layer for external API integration
- **Browser Extension:** Vue.js SPA packaged as Chrome extension

### Data Flow Architecture
1. **Authentication Flow:** Frontend → Auth0 → Backend JWT validation
2. **API Requests:** Frontend → Flask REST API → Service Layer → External APIs
3. **Real-time Events:** Chaturbate → WebSocket Handler → InfluxDB → Frontend
4. **Payment Flow:** Frontend → Stripe Checkout → Webhooks → Subscription Service
5. **Analytics:** InfluxDB Query → Service Layer → REST API → Frontend

## 🔧 Development Environment Setup

### Prerequisites
```bash
# Required Software
python3 --version    # Python 3.13.0
docker --version     # Docker 28.1.1
node --version       # Node.js 18+ (for frontend)

# Required Services
docker-compose up -d  # Start InfluxDB
```

### Environment Configuration
```bash
# Backend Setup
cp .env.example .env
# Edit .env with your credentials:
# - Auth0 domain, client ID, audience
# - Stripe secret key and webhook secret  
# - InfluxDB connection details (auto-configured for Docker)
# - Novita AI API key

# Frontend Setup
cd sider
cp .env.example .env
# Configure Auth0 client-side settings
```

### Service Dependencies
- **InfluxDB:** `http://localhost:8086` (auto-configured via Docker)
- **Auth0:** Requires domain and client configuration
- **Stripe:** Requires API keys and webhook endpoint setup
- **Novita AI:** Requires API key for translation services

## 🧪 Testing Strategy

### Test Organization
- **Unit Tests:** Individual service and utility testing
- **Integration Tests:** Database and external service integration
- **WebSocket Tests:** Real-time communication testing
- **API Tests:** Endpoint functionality validation

### Test Environment
```bash
# Test Database
docker-compose up -d  # Ensure InfluxDB is running

# Run Tests
PYTHONPATH=$PWD pytest --tb=short -v        # All tests
PYTHONPATH=$PWD pytest services/ -v         # Service tests
PYTHONPATH=$PWD pytest routes/ -v           # API tests
```

### Testing Best Practices
- **Mock External APIs:** Use pytest fixtures for Auth0, Stripe, AI services
- **Database Isolation:** Each test uses clean InfluxDB state
- **WebSocket Testing:** Mock SocketIO connections for real-time features
- **Subscription Testing:** Mock Stripe webhooks and payment flows

## 🚀 Deployment & CI/CD

### Development Deployment
```bash
# Backend
python3 app.py              # Flask development server (port 5000)

# Frontend  
cd sider && npm run dev     # Vite development server

# Services
docker-compose up -d        # InfluxDB container
```

### Production Considerations
- **Environment Variables:** All secrets via environment configuration
- **Database:** InfluxDB with persistent volumes and backup strategy
- **WebSocket Scaling:** Consider Redis adapter for multi-instance deployments
- **CDN:** Static asset delivery for browser extension files
- **Monitoring:** InfluxDB metrics and Flask application monitoring

### CI/CD Pipeline
```bash
# Pre-commit Hooks (Recommended)
pre-commit install

# Quality Gates
black . && isort .           # Code formatting
flake8 . --statistics        # Linting
bandit -r .                  # Security scanning
pytest --cov=80             # Test coverage
```

## 🔍 Debugging & Troubleshooting

### Common Issues & Solutions

#### InfluxDB Connection Issues
```bash
# Check container status
docker ps | grep influx

# Restart container
docker-compose down && docker-compose up -d

# Test connectivity
curl -f http://localhost:8086/health

# Check logs
docker logs webcammer-influxdb
```

#### Auth0 Authentication Issues
```bash
# Verify environment variables
echo $AUTH0_DOMAIN
echo $AUTH0_CLIENT_ID

# Test JWT validation
python3 -c "from utils.auth import verify_token; print('Auth OK')"

# Check Auth0 logs via dashboard
```

#### Stripe Integration Issues
```bash
# Test API connectivity
echo $STRIPE_SECRET_KEY | head -c 20  # Verify key format

# Webhook testing
stripe listen --forward-to localhost:5000/api/v1/subscription/webhook

# Check webhook signatures
tail -f logs/stripe_webhooks.log
```

#### WebSocket Connection Issues
```bash
# Check SocketIO server
python3 -c "from app import create_app; app = create_app(); print('SocketIO OK')"

# Test WebSocket endpoint
wscat -c ws://localhost:5000/socket.io/?transport=websocket

# Monitor real-time events
tail -f logs/websocket.log
```

### Performance Monitoring
```bash
# Database performance
docker exec webcammer-influxdb influx query 'SHOW MEASUREMENTS'

# Memory usage
python3 -m memory_profiler app.py

# Request timing
curl -w "@curl-format.txt" http://localhost:5000/api/v1/auth/profile
```

### Emergency Recovery
```bash
# Complete environment reset
docker-compose down -v      # Remove volumes
docker-compose up -d        # Fresh InfluxDB
pip3 install -r requirements.txt  # Reinstall dependencies
python3 app.py              # Verify startup
```

## 🎯 Engineering Principles

### Core Development Values
- **SECURITY FIRST:** Protect user data and API credentials
- **REAL-TIME PERFORMANCE:** Optimize WebSocket and database operations
- **SUBSCRIPTION INTEGRITY:** Ensure accurate usage tracking and billing
- **EXTERNAL SERVICE RESILIENCE:** Handle Auth0, Stripe, and AI API failures gracefully
- **USER EXPERIENCE:** Maintain responsive real-time updates
- **MAINTAINABLE CODE:** Follow Flask and Vue.js best practices

### Architecture Decision Framework
1. Does this maintain real-time performance requirements?
2. Is this compatible with the subscription/usage model?
3. Does this handle external service failures appropriately?
4. Will this scale with multiple concurrent WebSocket connections?
5. Is this testable with mocked external dependencies?
6. Does this follow Flask-RESTx and Vue.js conventions?

### Code Quality Standards
- **Type Safety:** Python type hints, TypeScript for frontend
- **Security:** Bandit scanning, secret management
- **Performance:** InfluxDB query optimization, WebSocket efficiency  
- **Testing:** Unit tests, integration tests, WebSocket testing
- **Documentation:** OpenAPI specs, inline code documentation

## 🔐 Security Considerations

### Authentication & Authorization
- **Auth0 Integration:** OAuth 2.0 with JWT token validation
- **API Security:** Bearer token authentication for all endpoints
- **Session Management:** Secure session handling with proper logout
- **CORS Configuration:** Restricted origins for browser extension

### Data Protection
- **Subscription Data:** Secure Stripe customer information handling
- **Usage Tracking:** Encrypted storage of user activity metrics
- **Real-time Data:** Secure WebSocket connections with authentication
- **Database Security:** InfluxDB access controls and connection encryption

### Secret Management
- **Environment Variables:** All sensitive configuration via .env
- **API Key Rotation:** Support for Auth0, Stripe, and AI service key updates
- **Webhook Security:** Stripe signature verification for payment events
- **Development Secrets:** Separate credentials for development/production

## 🚀 Feature Development Guide

### Adding New API Endpoints
1. **Route Definition:** Create endpoint in appropriate route file
2. **Service Logic:** Implement business logic in service layer
3. **Authentication:** Add Auth0 JWT validation decorator
4. **Usage Tracking:** Implement subscription tier limits
5. **Testing:** Unit tests with mocked dependencies
6. **Documentation:** OpenAPI schema definition

### WebSocket Event Handling
1. **Event Registration:** Add handler to chaturbate_route.py
2. **Data Processing:** Parse and validate incoming events
3. **Database Storage:** Store events in InfluxDB with proper schema
4. **Real-time Broadcast:** Emit updates to connected clients
5. **Testing:** Mock WebSocket connections and event flows

### Subscription Feature Integration
1. **Tier Validation:** Check user subscription level
2. **Usage Enforcement:** Implement rate limiting per tier
3. **Billing Integration:** Connect with Stripe subscription management
4. **Analytics Tracking:** Monitor usage patterns in InfluxDB
5. **User Experience:** Provide clear upgrade prompts

---

## 📝 Final Notes

**WebCammerPlus is a real-time SaaS platform** - every change must prioritize:

1. **Data Security** (Auth0, Stripe, user privacy)
2. **Real-time Performance** (WebSocket optimization, InfluxDB efficiency)
3. **Subscription Integrity** (accurate usage tracking, billing)
4. **Service Reliability** (external API resilience, error handling)
5. **User Experience** (responsive UI, seamless real-time updates)

**When in doubt:** Test with Docker services running, verify external integrations, and always run the complete quality pipeline. The platform handles sensitive user data and payment information - thorough development practices are essential.

## 🤖 Claude Code Behavior Rules

### ABSOLUTE REQUIREMENTS:
1. **NEVER commit without running the complete quality pipeline**
2. **NEVER commit API keys, tokens, or sensitive credentials**
3. **ALWAYS verify Docker services are running before development**
4. **MUST test WebSocket functionality for real-time features**
5. **STOP immediately if external service integrations fail**
6. **Always validate subscription tier limits for new features**

### Communication Standards:
- **Architecture Decisions:** Explain choices for Flask vs WebSocket implementations
- **Integration Updates:** Document changes to Auth0, Stripe, or AI service flows  
- **Performance Considerations:** Report any impacts on real-time capabilities
- **Security Reviews:** Highlight any changes affecting authentication or data handling
- **Testing Coverage:** Ensure WebSocket and external service mocking