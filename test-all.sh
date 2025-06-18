#!/bin/bash

# WebCammer+ Comprehensive Test Suite Runner
# This script runs all tests across the entire project

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}       WebCammer+ Comprehensive Test Suite${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# Track overall test results
TESTS_PASSED=0
TESTS_FAILED=0

# Function to run a test suite
run_test_suite() {
    local name=$1
    local command=$2
    local directory=$3
    
    echo -e "${YELLOW}Running $name...${NC}"
    echo "Directory: $directory"
    echo "Command: $command"
    echo ""
    
    cd "$directory"
    if eval "$command"; then
        echo -e "${GREEN}✓ $name PASSED${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ $name FAILED${NC}"
        ((TESTS_FAILED++))
    fi
    echo ""
    cd - > /dev/null
}

# Function to check if services are running
check_services() {
    echo -e "${YELLOW}Checking required services...${NC}"
    
    # Check if Docker is running
    if ! docker info > /dev/null 2>&1; then
        echo -e "${RED}Docker is not running. Please start Docker first.${NC}"
        exit 1
    fi
    
    # Check if InfluxDB is running
    if ! docker ps | grep -q influxdb; then
        echo -e "${YELLOW}Starting InfluxDB...${NC}"
        cd server && docker-compose up -d && cd ..
        sleep 5
    fi
    
    echo -e "${GREEN}✓ Services are ready${NC}"
    echo ""
}

# Main test execution
main() {
    # Check services first
    check_services
    
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}1. Python Backend Tests${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    
    # Run Python tests
    run_test_suite "Python Unit Tests" "python -m pytest services/ routes/ client/ -v" "server"
    run_test_suite "Python Integration Tests" "python -m pytest tests/integration/ -v" "server"
    run_test_suite "Python Functional Tests" "python -m pytest tests/functional/ -v" "server"
    
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}2. JavaScript Frontend Tests${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    
    # Check if npm dependencies are installed
    if [ ! -d "sider/node_modules" ]; then
        echo -e "${YELLOW}Installing JavaScript dependencies...${NC}"
        cd sider && npm install && cd ..
    fi
    
    # Run JavaScript tests
    run_test_suite "JavaScript Unit Tests" "npm test" "sider"
    
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}3. Manual Test Pages Status${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    
    # Check manual test files
    echo -e "${YELLOW}Checking manual test files...${NC}"
    
    # Count test files
    HTML_TESTS=$(find sider/tests-manual -name "*.html" -type f | wc -l)
    echo "Found $HTML_TESTS manual HTML test files"
    
    # List main test categories
    echo ""
    echo "Manual test categories available:"
    for dir in sider/tests-manual/*/; do
        if [ -d "$dir" ]; then
            dirname=$(basename "$dir")
            count=$(find "$dir" -name "*.html" -type f | wc -l)
            echo "  - $dirname: $count test files"
        fi
    done
    
    echo ""
    echo -e "${GREEN}✓ Manual test dashboard available at: sider/tests-manual/index.html${NC}"
    ((TESTS_PASSED++))
    
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}4. Linting and Code Quality${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    
    # Python linting
    run_test_suite "Python Linting (flake8)" "flake8 . --count --statistics --exclude=.venv,__pycache__" "server"
    run_test_suite "Python Security (bandit)" "bandit -r . -f txt -x .venv,tests" "server"
    
    # JavaScript linting (if ESLint is configured)
    if [ -f "sider/.eslintrc.json" ] || [ -f "sider/.eslintrc.js" ]; then
        run_test_suite "JavaScript Linting" "npm run lint" "sider"
    else
        echo -e "${YELLOW}ESLint not configured, skipping JavaScript linting${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}Test Summary${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    
    TOTAL_TESTS=$((TESTS_PASSED + TESTS_FAILED))
    echo "Total test suites run: $TOTAL_TESTS"
    echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
    echo -e "${RED}Failed: $TESTS_FAILED${NC}"
    
    if [ $TESTS_FAILED -eq 0 ]; then
        echo ""
        echo -e "${GREEN}🎉 All tests passed successfully!${NC}"
        exit 0
    else
        echo ""
        echo -e "${RED}❌ Some tests failed. Please check the output above.${NC}"
        exit 1
    fi
}

# Run main function
main