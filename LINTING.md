# WebCammerPlus Linting Setup

This document explains the comprehensive linting and code quality setup for the WebCammerPlus project.

## Overview

This project uses multiple linters to maintain code quality across different file types:

- **JavaScript/TypeScript**: ESLint + Prettier
- **HTML**: HTMLHint
- **CSS/SCSS**: Stylelint
- **Python**: Black + Flake8 + isort + mypy + Bandit

## Quick Start

### Install Dependencies

```bash
# Install Node.js dependencies
npm install

# Install Python dependencies  
pip install -r lint-requirements.txt
```

### Run All Linters

```bash
# Run all linters
npm run lint

# Run specific linters
npm run lint:js      # JavaScript/TypeScript
npm run lint:html    # HTML files
npm run lint:css     # CSS/SCSS files
```

### Auto-fix Issues

```bash
# Auto-fix JavaScript issues
npm run lint:js:fix

# Auto-fix CSS issues  
npm run lint:css:fix

# Format all files with Prettier
npm run format

# Format Python files with Black
black .

# Fix Python imports with isort
isort .
```

## Linter Configuration

### ESLint (.eslintrc.js)

**Purpose**: Lint JavaScript/TypeScript files
**Rules**: 
- ES2021 syntax support
- No unused variables (warning)
- Prefer const over let
- Single quotes for strings
- No semicolons
- 2-space indentation

**Covered Files**: `**/*.js`, `**/*.ts`, `**/*.vue`

### HTMLHint (.htmlhintrc)

**Purpose**: Lint HTML files for markup quality
**Key Rules**:
- Require alt attributes on images
- Enforce lowercase attributes
- Require DOCTYPE declaration
- Validate HTML5 structure
- Check for duplicate IDs

**Covered Files**: `**/*.html`

### Stylelint (.stylelintrc.json)

**Purpose**: Lint CSS/SCSS files
**Key Rules**:
- Standard CSS formatting
- Alphabetical property ordering
- Consistent indentation (2 spaces)
- Double quotes for strings
- No duplicate selectors
- Color format consistency

**Covered Files**: `**/*.css`, `**/*.scss`, `**/*.sass`, `**/*.vue`

### Python Linting

#### Black (pyproject.toml)
**Purpose**: Code formatting
- Line length: 88 characters
- Python 3.8+ compatibility
- Automatic formatting

#### Flake8 (.flake8)
**Purpose**: Style guide enforcement
- Max line length: 88 characters
- Complexity limit: 10
- Import order checking
- Docstring conventions

#### isort (pyproject.toml)
**Purpose**: Import sorting
- Black-compatible formatting
- Grouped imports (stdlib, third-party, first-party)
- Trailing commas

#### mypy (pyproject.toml)
**Purpose**: Type checking
- Static type analysis
- Return type warnings
- Missing import handling

#### Bandit (.bandit)
**Purpose**: Security linting
- Security vulnerability detection
- Safe defaults for testing
- JSON output for CI/CD

## GitHub Actions Integration

The linting setup automatically runs on:
- Push to main/develop branches
- Pull requests to main/develop branches

### Workflow File

See `.github/workflows/quality-check.yml` for the complete CI/CD pipeline.

**Jobs**:
1. **lint-and-format**: Runs all linters and formatters
2. **test-linting-rules**: Verifies linter configurations

## IDE Integration

### VS Code

Install these extensions for optimal development experience:

```json
{
  "recommendations": [
    "esbenp.prettier-vscode",
    "dbaeumer.vscode-eslint", 
    "stylelint.vscode-stylelint",
    "ms-python.black-formatter",
    "ms-python.flake8",
    "ms-python.isort",
    "ms-python.mypy-type-checker"
  ]
}
```

### VS Code Settings

Add to your workspace settings:

```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "python.defaultInterpreterPath": "./venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "eslint.validate": ["javascript", "typescript", "vue"],
  "css.validate": false,
  "scss.validate": false,
  "stylelint.validate": ["css", "scss", "vue"]
}
```

## Pre-commit Hooks (Optional)

To run linters before every commit, install pre-commit:

```bash
pip install pre-commit
pre-commit install
```

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/pre-commit/mirrors-eslint
    rev: v8.45.0
    hooks:
      - id: eslint
        files: \\.(js|ts|vue)$
        
  - repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
      - id: black
      
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
      
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
```

## Troubleshooting

### Common Issues

1. **ESLint parser errors**: Make sure @babel/eslint-parser is installed
2. **Stylelint not finding files**: Check file extensions in npm scripts
3. **Python import errors**: Verify PYTHONPATH includes project root
4. **Prettier conflicts**: Ensure prettier rules don't conflict with other linters

### Disable Rules

#### ESLint
```javascript
/* eslint-disable no-console */
console.log('Debug message')
/* eslint-enable no-console */
```

#### Flake8
```python
# noqa: E501 (line too long)
very_long_line = "This line exceeds the character limit but is necessary"
```

#### Stylelint
```css
/* stylelint-disable property-no-unknown */
.special-property {
  -webkit-special: value;
}
/* stylelint-enable property-no-unknown */
```

## Customization

### Adding New Rules

1. Update configuration files (`.eslintrc.js`, `.stylelintrc.json`, etc.)
2. Test changes locally with `npm run lint`
3. Update this documentation
4. Ensure CI/CD pipeline passes

### Project-Specific Overrides

Each linter supports project-specific overrides in their configuration files. See the individual config files for examples.

## Performance

The complete linting suite typically runs in:
- **Local development**: 10-30 seconds
- **CI/CD pipeline**: 2-5 minutes

For faster development, run individual linters on specific files:

```bash
npx eslint src/specific-file.js
npx stylelint src/specific-file.css
black src/specific-file.py
```

## Contributing

When contributing to this project:

1. Ensure all linters pass before submitting PR
2. Use auto-fix capabilities when possible
3. Add linting rules for new file types
4. Update this documentation for configuration changes

## Support

For linting setup issues:
- Check GitHub Actions logs for CI failures
- Verify local development environment matches CI setup
- Reference individual linter documentation for advanced configuration