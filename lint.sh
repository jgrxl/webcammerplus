#!/bin/bash

# WebCammerPlus Linter Script
# This script runs all linters for JavaScript, HTML, and CSS

set -e

echo "🔍 Starting WebCammerPlus Linter Suite..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if source directory exists
if [ ! -d "src" ]; then
    print_warning "Source directory 'src' not found. Creating..."
    mkdir -p src
    print_success "Source directory created"
fi

# Function to run JavaScript linting with ESLint
lint_js() {
    print_status "Running JavaScript linting with ESLint..."
    
    if command -v npx &> /dev/null; then
        if [ -d "src" ] && [ "$(find src -name "*.js" -type f)" ]; then
            npx eslint src/**/*.js || {
                print_error "JavaScript linting failed"
                return 1
            }
            print_success "JavaScript linting completed"
        else
            print_warning "No JavaScript files found in src directory"
        fi
    else
        print_error "npx not found. Please install Node.js and npm"
        return 1
    fi
}

# Function to run HTML linting with HTMLHint
lint_html() {
    print_status "Running HTML linting with HTMLHint..."
    
    if command -v npx &> /dev/null; then
        if [ -d "src" ] && [ "$(find src -name "*.html" -type f)" ]; then
            npx htmlhint src/**/*.html || {
                print_error "HTML linting failed"
                return 1
            }
            print_success "HTML linting completed"
        else
            print_warning "No HTML files found in src directory"
        fi
    else
        print_error "npx not found. Please install Node.js and npm"
        return 1
    fi
}

# Function to run CSS linting with Stylelint
lint_css() {
    print_status "Running CSS linting with Stylelint..."
    
    if command -v npx &> /dev/null; then
        if [ -d "src" ] && [ "$(find src -name "*.css" -type f)" ]; then
            npx stylelint src/**/*.css || {
                print_error "CSS linting failed"
                return 1
            }
            print_success "CSS linting completed"
        else
            print_warning "No CSS files found in src directory"
        fi
    else
        print_error "npx not found. Please install Node.js and npm"
        return 1
    fi
}

# Main execution
main() {
    local exit_code=0
    
    # Run all linters
    lint_js || exit_code=$((exit_code + 1))
    lint_html || exit_code=$((exit_code + 1))
    lint_css || exit_code=$((exit_code + 1))
    
    echo ""
    if [ $exit_code -eq 0 ]; then
        print_success "All linters completed successfully! 🎉"
    else
        print_error "Some linters failed. Please check the output above."
        exit $exit_code
    fi
}

# Run main function
main 