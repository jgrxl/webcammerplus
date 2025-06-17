#!/usr/bin/env python3
"""Script to clean up unused imports in Python files."""

import os
import subprocess
import sys

def remove_unused_imports(file_path):
    """Remove unused imports from a Python file using autoflake."""
    try:
        # Run autoflake to remove unused imports
        subprocess.run([
            'autoflake',
            '--in-place',
            '--remove-unused-variables',
            '--remove-all-unused-imports',
            file_path
        ], check=True)
        print(f"✅ Cleaned: {file_path}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error cleaning {file_path}: {e}")
    except FileNotFoundError:
        print("❌ autoflake not installed. Install with: pip install autoflake")
        sys.exit(1)

def find_python_files(directory, exclude_dirs=None):
    """Find all Python files in a directory, excluding certain directories."""
    if exclude_dirs is None:
        exclude_dirs = {'.venv', 'venv', '__pycache__', '.git', 'node_modules'}
    
    python_files = []
    for root, dirs, files in os.walk(directory):
        # Remove excluded directories from dirs to prevent walking into them
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    return python_files

def main():
    """Main function to clean imports in all Python files."""
    # Get the server directory
    server_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    print(f"🧹 Cleaning imports in: {server_dir}")
    
    # Find all Python files
    python_files = find_python_files(server_dir)
    
    print(f"📁 Found {len(python_files)} Python files")
    
    # Clean imports in each file
    for file_path in python_files:
        remove_unused_imports(file_path)
    
    print("✨ Import cleanup complete!")

if __name__ == "__main__":
    main()