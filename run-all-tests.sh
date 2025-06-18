#!/bin/bash

# WebCammer+ Complete Test Suite Runner
# Runs all tests: Python backend, JavaScript frontend, and reports on manual tests

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Project root
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║          WebCammer+ Complete Test Suite Runner                ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Track test results
TOTAL_SUITES=0
PASSED_SUITES=0
FAILED_SUITES=0
SKIPPED_SUITES=0

# Log file for detailed output
LOG_FILE="$PROJECT_ROOT/test-results-$(date +%Y%m%d-%H%M%S).log"
echo "Detailed output will be saved to: $LOG_FILE"
echo ""

# Function to run a test suite
run_test_suite() {
    local name=$1
    local command=$2
    local directory=$3
    
    ((TOTAL_SUITES++))
    
    echo -e "${CYAN}[$TOTAL_SUITES] Running: $name${NC}"
    echo "Directory: $directory"
    echo "Command: $command"
    
    cd "$directory"
    
    # Run the test and capture output
    if $command >> "$LOG_FILE" 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC}"
        ((PASSED_SUITES++))
        # Show summary if available
        if [[ "$command" == *"pytest"* ]]; then
            tail -n 10 "$LOG_FILE" | grep -E "(passed|failed|warnings|errors)" | tail -n 1 || true
        elif [[ "$command" == *"npm test"* ]]; then
            tail -n 20 "$LOG_FILE" | grep -E "(Test Suites:|Tests:|Snapshots:)" | tail -n 3 || true
        fi
    else
        echo -e "${RED}✗ FAILED${NC}"
        ((FAILED_SUITES++))
        # Show last few lines of error
        echo -e "${RED}Last error output:${NC}"
        tail -n 5 "$LOG_FILE"
    fi
    
    cd "$PROJECT_ROOT"
    echo ""
}

# Function to check prerequisites
check_prerequisites() {
    echo -e "${YELLOW}Checking prerequisites...${NC}"
    
    local missing=0
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}✗ Python 3 not found${NC}"
        ((missing++))
    else
        echo -e "${GREEN}✓ Python $(python3 --version)${NC}"
    fi
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        echo -e "${RED}✗ Node.js not found${NC}"
        ((missing++))
    else
        echo -e "${GREEN}✓ Node.js $(node --version)${NC}"
    fi
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}✗ Docker not found${NC}"
        ((missing++))
    else
        echo -e "${GREEN}✓ Docker $(docker --version | cut -d' ' -f3 | sed 's/,$//')${NC}"
    fi
    
    if [ $missing -gt 0 ]; then
        echo -e "${RED}Please install missing prerequisites before running tests.${NC}"
        exit 1
    fi
    
    echo ""
}

# Function to ensure services are running
ensure_services() {
    echo -e "${YELLOW}Ensuring required services are running...${NC}"
    
    # Check if Docker daemon is running
    if ! docker info > /dev/null 2>&1; then
        echo -e "${RED}Docker daemon is not running. Please start Docker.${NC}"
        exit 1
    fi
    
    # Check InfluxDB
    if ! docker ps | grep -q influxdb; then
        echo -e "${YELLOW}Starting InfluxDB...${NC}"
        cd "$PROJECT_ROOT/server"
        docker-compose up -d influxdb
        sleep 5
        cd "$PROJECT_ROOT"
    fi
    
    echo -e "${GREEN}✓ Services ready${NC}"
    echo ""
}

# Main execution
main() {
    # Initial setup
    check_prerequisites
    ensure_services
    
    # Create log file
    touch "$LOG_FILE"
    echo "Test run started at: $(date)" >> "$LOG_FILE"
    echo "========================================" >> "$LOG_FILE"
    
    # Python Backend Tests
    echo -e "${MAGENTA}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${MAGENTA}                    Python Backend Tests                        ${NC}"
    echo -e "${MAGENTA}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    
    # Check Python environment
    if [ -d "$PROJECT_ROOT/server/.venv" ]; then
        echo "Using virtual environment: server/.venv"
        PYTHON_CMD="$PROJECT_ROOT/server/.venv/bin/python"
        PYTEST_CMD="$PROJECT_ROOT/server/.venv/bin/pytest"
    else
        PYTHON_CMD="python3"
        PYTEST_CMD="python3 -m pytest"
    fi
    
    # Run Python tests
    run_test_suite "Python Service Tests" "$PYTEST_CMD services/ -v" "$PROJECT_ROOT/server"
    run_test_suite "Python Route Tests" "$PYTEST_CMD routes/ -v" "$PROJECT_ROOT/server"
    run_test_suite "Python Client Tests" "$PYTEST_CMD client/ -v" "$PROJECT_ROOT/server"
    run_test_suite "Python Integration Tests" "$PYTEST_CMD tests/integration/ -v" "$PROJECT_ROOT/server"
    run_test_suite "Python Functional Tests" "$PYTEST_CMD tests/functional/ -v" "$PROJECT_ROOT/server"
    
    # JavaScript Frontend Tests
    echo -e "${MAGENTA}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${MAGENTA}                  JavaScript Frontend Tests                     ${NC}"
    echo -e "${MAGENTA}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    
    # Check if npm dependencies are installed
    if [ ! -d "$PROJECT_ROOT/sider/node_modules" ]; then
        echo -e "${YELLOW}Installing JavaScript dependencies...${NC}"
        cd "$PROJECT_ROOT/sider"
        npm install
        cd "$PROJECT_ROOT"
    fi
    
    # Run JavaScript tests
    run_test_suite "JavaScript Unit Tests" "npm test" "$PROJECT_ROOT/sider"
    
    # Code Quality Checks
    echo -e "${MAGENTA}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${MAGENTA}                    Code Quality Checks                         ${NC}"
    echo -e "${MAGENTA}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    
    # Python code quality
    if command -v flake8 &> /dev/null || [ -f "$PROJECT_ROOT/server/.venv/bin/flake8" ]; then
        FLAKE8_CMD="${PROJECT_ROOT}/server/.venv/bin/flake8"
        [ -f "$FLAKE8_CMD" ] || FLAKE8_CMD="flake8"
        run_test_suite "Python Linting (flake8)" "$FLAKE8_CMD . --count --statistics --exclude=.venv,__pycache__" "$PROJECT_ROOT/server"
    else
        echo -e "${YELLOW}Skipping Python linting (flake8 not installed)${NC}"
        ((SKIPPED_SUITES++))
    fi
    
    # Manual Test Report
    echo -e "${MAGENTA}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${MAGENTA}                    Manual Test Report                          ${NC}"
    echo -e "${MAGENTA}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    
    # Count manual tests
    echo -e "${CYAN}Manual Browser Tests Available:${NC}"
    
    total_manual=0
    for category in api analytics components integration utils; do
        if [ -d "$PROJECT_ROOT/sider/tests-manual/$category" ]; then
            count=$(find "$PROJECT_ROOT/sider/tests-manual/$category" -name "*.html" -type f | wc -l | tr -d ' ')
            echo "  • $category: $count test files"
            ((total_manual += count))
        fi
    done
    
    echo ""
    echo "Total manual test files: $total_manual"
    echo -e "${GREEN}✓ Test dashboard: file://$PROJECT_ROOT/sider/tests-manual/index.html${NC}"
    echo ""
    
    # Final Summary
    echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                        Test Summary                           ║${NC}"
    echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    echo "Total test suites run: $TOTAL_SUITES"
    echo -e "${GREEN}✓ Passed: $PASSED_SUITES${NC}"
    echo -e "${RED}✗ Failed: $FAILED_SUITES${NC}"
    echo -e "${YELLOW}○ Skipped: $SKIPPED_SUITES${NC}"
    echo ""
    
    # Coverage report locations
    echo -e "${CYAN}Coverage Reports:${NC}"
    echo "  • Python: $PROJECT_ROOT/server/htmlcov/index.html"
    echo "  • JavaScript: $PROJECT_ROOT/sider/coverage/lcov-report/index.html"
    echo ""
    
    echo "Detailed log: $LOG_FILE"
    echo ""
    
    if [ $FAILED_SUITES -eq 0 ]; then
        echo -e "${GREEN}🎉 All tests passed successfully!${NC}"
        exit 0
    else
        echo -e "${RED}❌ $FAILED_SUITES test suite(s) failed. Check the log for details.${NC}"
        exit 1
    fi
}

# Run main function
main "$@"