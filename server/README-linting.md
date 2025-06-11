# Python Linting Setup for WebCammerPlus

This directory contains a comprehensive Python linting setup to ensure code quality, consistency, and security for the WebCammerPlus server.

## 🚀 Quick Start

### 1. Install Development Dependencies
```bash
cd server
pip install -r requirements-dev.txt
```

### 2. Run All Linters
```bash
python lint.py
```

### 3. Auto-fix Formatting Issues
```bash
python lint.py --fix
```

### 4. Setup Pre-commit Hooks (Optional but Recommended)
```bash
pre-commit install
```

## 🛠️ Linting Tools Included

### **Black** - Code Formatter
- **Purpose**: Automatic code formatting
- **Config**: `pyproject.toml`
- **Run**: `black .`
- **Check only**: `black --check --diff .`

### **isort** - Import Sorter
- **Purpose**: Organize and sort imports
- **Config**: `pyproject.toml`
- **Run**: `isort .`
- **Check only**: `isort --check-only --diff .`

### **flake8** - Style Guide Enforcement
- **Purpose**: PEP 8 style guide compliance
- **Config**: `.flake8`
- **Run**: `flake8 .`

### **pylint** - Code Analysis
- **Purpose**: Code quality and style analysis
- **Config**: `pyproject.toml`
- **Run**: `pylint .`

### **mypy** - Static Type Checking
- **Purpose**: Type checking and validation
- **Config**: `pyproject.toml`
- **Run**: `mypy .`

### **bandit** - Security Scanner
- **Purpose**: Security vulnerability detection
- **Config**: `pyproject.toml`
- **Run**: `bandit -r .`

### **safety** - Dependency Scanner
- **Purpose**: Check for vulnerable dependencies
- **Run**: `safety check`

## 📋 Individual Tool Usage

### Format Code
```bash
# Format all Python files
black .

# Check formatting without changing files
black --check --diff .
```

### Sort Imports
```bash
# Sort imports in all files
isort .

# Check import sorting without changing files
isort --check-only --diff .
```

### Style Checking
```bash
# Run flake8 style checks
flake8 .

# Run pylint analysis
pylint .
```

### Type Checking
```bash
# Run mypy type checking
mypy .
```

### Security Scanning
```bash
# Run bandit security scan
bandit -r .

# Check dependencies for vulnerabilities
safety check
```

## 🔧 Configuration Files

### `pyproject.toml`
- Central configuration for Black, isort, mypy, and pylint
- Modern Python tooling standard
- Consistent settings across all tools

### `.flake8`
- flake8-specific configuration
- Ignores conflicts with Black formatting
- Excludes common directories

### `.pre-commit-config.yaml`
- Pre-commit hooks configuration
- Automatically runs linting on commits
- Ensures code quality before it reaches the repository

## 🎯 Pre-commit Hooks

Pre-commit hooks automatically run linting tools before each commit, ensuring code quality:

### Setup
```bash
pre-commit install
```

### Run Manually
```bash
# Run on all files
pre-commit run --all-files

# Run specific hook
pre-commit run black
```

### Skip Hooks (Emergency Only)
```bash
git commit --no-verify -m "Emergency fix"
```

## 📊 Linting Report

The `lint.py` script provides a comprehensive report:

```
Linting Report
==================================================
Black           ✓ PASS
isort           ✓ PASS
flake8          ✓ PASS
pylint          ✓ PASS
mypy            ✓ PASS
bandit          ✓ PASS
safety          ✓ PASS
--------------------------------------------------
Overall: 7/7 checks passed
🎉 All checks passed!
```

## 🚨 Common Issues and Solutions

### Import Errors
```bash
# If you get import errors, install type stubs
pip install types-requests types-PyYAML
```

### Black/isort Conflicts
- Both tools are configured to work together
- Black formatting takes precedence
- isort is configured with `profile = "black"`

### mypy False Positives
- External libraries are configured to ignore missing imports
- Add `# type: ignore` comments for unavoidable issues
- Use `@typing.no_type_check` decorator for complex functions

### pylint Warnings
- Common warnings are disabled in configuration
- Focus on important issues like unused imports and undefined variables

## 🔄 CI/CD Integration

The linting tools are designed to work with CI/CD pipelines:

```yaml
# Example GitHub Actions step
- name: Run Python Linting
  run: |
    cd server
    pip install -r requirements-dev.txt
    python lint.py
```

## 📝 Best Practices

1. **Run linting before committing**: Use pre-commit hooks or manual `python lint.py`
2. **Fix formatting issues**: Use `python lint.py --fix` for automatic fixes
3. **Address security issues**: Review bandit and safety reports
4. **Type your code**: Use type hints and run mypy regularly
5. **Keep dependencies updated**: Run `safety check` regularly

## 🆘 Troubleshooting

### Tool Not Found
```bash
# Install missing tools
pip install -r requirements-dev.txt
```

### Configuration Issues
- Check that `pyproject.toml` is in the server directory
- Ensure `.flake8` is in the server directory
- Verify Python version compatibility (3.8+)

### Performance Issues
- Exclude large directories in configuration files
- Use `--skip` flags for specific tools when needed
- Consider running tools individually for large codebases

## 📚 Additional Resources

- [Black Documentation](https://black.readthedocs.io/)
- [isort Documentation](https://pycqa.github.io/isort/)
- [flake8 Documentation](https://flake8.pycqa.org/)
- [pylint Documentation](https://pylint.pycqa.org/)
- [mypy Documentation](https://mypy.readthedocs.io/)
- [bandit Documentation](https://bandit.readthedocs.io/)
- [pre-commit Documentation](https://pre-commit.com/) 