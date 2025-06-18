# WebCammerPlus Server Tests

This directory contains integration and functional tests that span multiple components.

## Test Organization

### Co-located Unit Tests
Unit tests are placed next to the code they test for better maintainability:
- **`services/*_test.py`** - Tests for service modules
- **`routes/*_test.py`** - Tests for route handlers
- **`client/*_test.py`** - Tests for client modules

### Tests in This Directory

#### `/integration` - Integration Tests
Tests for component interactions and external service integrations:
- **`test_all_endpoints.py`** - Comprehensive API endpoint testing
- **`test_integration.py`** - External service integration (Novita AI, etc.)
- **`test_websocket.py`** - WebSocket/Socket.IO integration

#### `/functional` - Functional Tests
End-to-end tests for specific features:
- **`test_current_user.py`** - User authentication and profile features
- **`test_inbox_api.py`** - Inbox/messaging functionality
- **`test_fixes.py`** - Regression tests for bug fixes

## Running Tests

```bash
# Run all tests (includes co-located tests)
pytest

# Run only integration/functional tests
pytest tests/

# Run specific test category
pytest tests/integration/
pytest tests/functional/

# Run service tests
pytest services/

# Run route tests
pytest routes/

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest services/influx_db_service_write_test.py
```

## Test Structure Benefits

- **Unit tests** are co-located with code for easy discovery
- **Integration tests** remain separate as they test multiple components
- **Functional tests** test complete features end-to-end

## Writing Tests

- Place unit tests next to the code they test (e.g., `service.py` → `service_test.py`)
- Integration tests go in `tests/integration/`
- Functional/feature tests go in `tests/functional/`
- Use descriptive test names: `test_<feature>_<scenario>_<expected_result>`
- Mock external dependencies in unit tests
- Use real services (with test data) in integration tests