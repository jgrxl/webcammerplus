# Deprecated Index Files

This folder contains older versions of the index.html file that have been superseded by the ultra-slim architecture.

## Files

- **index-legacy.html** - The original monolithic version with all code inline
- **index-modular.html** - First attempt at modularization with separate component files
- **index-refactored.html** - Refactored version with improved structure

## Current Architecture

The main `index.html` now uses the ultra-slim architecture which provides:
- Minimal HTML with dynamic component loading
- Better separation of concerns
- Improved maintainability
- Easier testing

## Usage

These files are kept for reference only. If you need to rollback for any reason:

```bash
# Copy the desired version back to index.html
cp index-legacy.html ../index.html
```

However, it's recommended to use and improve the current ultra-slim architecture instead of reverting to older versions.