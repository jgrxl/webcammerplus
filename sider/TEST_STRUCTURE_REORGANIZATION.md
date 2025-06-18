# Test Structure Reorganization Summary

## Overview
Reorganized the JavaScript test structure in the sider directory to follow Jest conventions and clearly separate unit tests from manual browser tests.

## Changes Made

### 1. Directory Renaming
- **OLD:** `tests/` (manual browser test files)
- **NEW:** `tests-manual/` (clarifies these are manual browser tests)

### 2. Test Directory Restructure
- **OLD:** `test/` (Jest unit tests)
- **NEW:** `__tests__/` (Jest convention)

### 3. New Directory Structure
```
__tests__/                  # Jest unit tests
├── core/                   # Tests for js/core/
├── services/               # Tests for js/services/
│   └── api.test.js        # Moved from test/
├── helpers/                # Tests for js/helpers/
├── modules/                # Tests for js/modules/
├── components/             # Tests for js/components/
├── popup.test.js          # Moved from test/
├── simple.test.js         # Moved from test/
└── setup.js               # Moved from test/

tests-manual/               # Manual browser tests (renamed from tests/)
├── analytics/
├── api/
├── components/
├── integration/
├── utils/
├── index.html
└── README.md
```

### 4. Configuration Updates
Updated `jest.config.js`:
- Changed test match pattern from `**/test/**/*.test.js` to `**/__tests__/**/*.test.js`
- Updated setup file path from `./test/setup.js` to `./__tests__/setup.js`

### 5. Code Updates
Fixed import path in `popup.test.js`:
- Changed from `../popup.js` to `../js/popup.js` to reflect correct relative path

## Benefits
1. **Clarity:** Clear distinction between automated Jest tests and manual browser tests
2. **Convention:** Follows Jest convention of using `__tests__` directory
3. **Organization:** Test structure mirrors source code structure for easier navigation
4. **Scalability:** Easy to add tests for specific modules in their respective directories

## Next Steps
To add new tests:
1. **Unit tests:** Create `.test.js` files in the appropriate subdirectory under `__tests__/`
2. **Manual tests:** Add HTML test files to `tests-manual/` in the appropriate category

## Running Tests
```bash
# Run all Jest unit tests
npm test

# Run tests with coverage
npm test -- --coverage

# Run specific test file
npm test -- __tests__/services/api.test.js
```