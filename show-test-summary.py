#!/usr/bin/env python3
"""
WebCammer+ Test Summary Reporter
Shows a comprehensive overview of all tests in the project
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from collections import defaultdict

# ANSI color codes
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
CYAN = '\033[0;36m'
MAGENTA = '\033[0;35m'
NC = '\033[0m'  # No Color

def print_header(title):
    """Print a formatted header"""
    print(f"\n{BLUE}{'='*60}{NC}")
    print(f"{BLUE}{title:^60}{NC}")
    print(f"{BLUE}{'='*60}{NC}\n")

def find_python_tests(root_dir):
    """Find all Python test files"""
    tests = defaultdict(list)
    server_dir = root_dir / 'server'
    
    if not server_dir.exists():
        return tests
    
    # Patterns to look for
    patterns = ['*_test.py', 'test_*.py']
    
    for pattern in patterns:
        for test_file in server_dir.rglob(pattern):
            if '.venv' not in str(test_file) and '__pycache__' not in str(test_file):
                relative_path = test_file.relative_to(server_dir)
                category = str(relative_path.parent).split('/')[0] if '/' in str(relative_path) else 'root'
                tests[category].append(str(relative_path))
    
    return tests

def find_javascript_tests(root_dir):
    """Find all JavaScript test files"""
    tests = defaultdict(list)
    sider_dir = root_dir / 'sider'
    
    if not sider_dir.exists():
        return tests
    
    for test_file in sider_dir.rglob('*.test.js'):
        if 'node_modules' not in str(test_file):
            relative_path = test_file.relative_to(sider_dir)
            if str(relative_path).startswith('js/'):
                category = str(relative_path.parent).replace('js/', '') or 'root'
            else:
                category = str(relative_path.parent) or 'root'
            tests[category].append(str(relative_path))
    
    return tests

def find_manual_tests(root_dir):
    """Find all manual HTML test files"""
    tests = defaultdict(list)
    manual_dir = root_dir / 'sider' / 'tests-manual'
    
    if not manual_dir.exists():
        return tests
    
    for test_file in manual_dir.rglob('*.html'):
        if test_file.name != 'index.html':
            relative_path = test_file.relative_to(manual_dir)
            category = str(relative_path.parent) or 'root'
            tests[category].append(str(relative_path))
    
    return tests

def count_test_functions(file_path):
    """Count test functions in a file"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            
        # Python tests
        if file_path.suffix == '.py':
            import re
            # Count def test_ and def test_ methods
            test_count = len(re.findall(r'def\s+test_\w+', content))
            return test_count
            
        # JavaScript tests
        elif file_path.suffix == '.js':
            # Count it() and test() calls
            import re
            it_count = len(re.findall(r'\bit\s*\(', content))
            test_count = len(re.findall(r'\btest\s*\(', content))
            return it_count + test_count
            
    except Exception:
        return 0

def main():
    """Main function"""
    project_root = Path(__file__).parent
    
    print(f"{CYAN}WebCammer+ Test Summary Report{NC}")
    print(f"{CYAN}Project Root: {project_root}{NC}")
    
    # Python Tests
    print_header("Python Tests")
    python_tests = find_python_tests(project_root)
    
    total_py_files = 0
    total_py_tests = 0
    
    for category in sorted(python_tests.keys()):
        files = python_tests[category]
        print(f"{YELLOW}{category}:{NC}")
        for file in sorted(files):
            file_path = project_root / 'server' / file
            test_count = count_test_functions(file_path)
            total_py_tests += test_count
            print(f"  • {file} ({test_count} tests)")
            total_py_files += 1
        print()
    
    print(f"{GREEN}Total: {total_py_files} files, ~{total_py_tests} test functions{NC}")
    
    # JavaScript Tests
    print_header("JavaScript Tests")
    js_tests = find_javascript_tests(project_root)
    
    total_js_files = 0
    total_js_tests = 0
    
    for category in sorted(js_tests.keys()):
        files = js_tests[category]
        print(f"{YELLOW}{category}:{NC}")
        for file in sorted(files):
            file_path = project_root / 'sider' / file
            test_count = count_test_functions(file_path)
            total_js_tests += test_count
            print(f"  • {file} ({test_count} tests)")
            total_js_files += 1
        print()
    
    print(f"{GREEN}Total: {total_js_files} files, ~{total_js_tests} test functions{NC}")
    
    # Manual Browser Tests
    print_header("Manual Browser Tests")
    manual_tests = find_manual_tests(project_root)
    
    total_manual_files = 0
    
    for category in sorted(manual_tests.keys()):
        files = manual_tests[category]
        print(f"{YELLOW}{category}:{NC}")
        for file in sorted(files):
            print(f"  • {file}")
            total_manual_files += 1
        print()
    
    print(f"{GREEN}Total: {total_manual_files} HTML test files{NC}")
    
    # Summary
    print_header("Overall Summary")
    print(f"📊 Python Backend:")
    print(f"   • Test files: {total_py_files}")
    print(f"   • Test functions: ~{total_py_tests}")
    print()
    print(f"🌐 JavaScript Frontend:")
    print(f"   • Test files: {total_js_files}")
    print(f"   • Test functions: ~{total_js_tests}")
    print()
    print(f"🖱️  Manual Tests:")
    print(f"   • HTML test files: {total_manual_files}")
    print()
    print(f"{MAGENTA}Total test files: {total_py_files + total_js_files + total_manual_files}{NC}")
    print(f"{MAGENTA}Total automated tests: ~{total_py_tests + total_js_tests}{NC}")
    
    # Quick commands
    print_header("Quick Test Commands")
    print("🐍 Python tests:")
    print("   cd server && python -m pytest -v")
    print()
    print("🟨 JavaScript tests:")
    print("   cd sider && npm test")
    print()
    print("🌐 Manual tests:")
    print(f"   open {project_root}/sider/tests-manual/index.html")
    print()
    print("🚀 Run all tests:")
    print(f"   {project_root}/run-all-tests.sh")

if __name__ == "__main__":
    main()