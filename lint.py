#!/usr/bin/env python3
"""
Comprehensive Python linting script for WebCammerPlus server.
Runs all linting tools and provides a unified report.
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Dict

# Color codes for terminal output
class Colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"


class Linter:
    def __init__(self, name: str, command: List[str], description: str):
        self.name = name
        self.command = command
        self.description = description
        self.success = False
        self.output = ""
        self.error_count = 0

    def run(self, cwd: str) -> bool:
        """Run the linter and return success status."""
        print(f"{Colors.BLUE}Running {self.name}...{Colors.END}")
        print(f"{Colors.CYAN}{self.description}{Colors.END}")

        try:
            result = subprocess.run(
                self.command,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                check=False,  # W1510: subprocess.run used without explicitly defining 'check'
            )

            self.output = result.stdout + result.stderr
            self.success = result.returncode == 0

            if self.success:
                print(f"{Colors.GREEN}✓ {self.name} passed{Colors.END}")
            else:
                print(f"{Colors.RED}✗ {self.name} failed{Colors.END}")
                print(self.output)

            return self.success

        except subprocess.TimeoutExpired:
            print(f"{Colors.RED}✗ {self.name} timed out{Colors.END}")
            return False
        except FileNotFoundError:
            print(
                f"{Colors.RED}✗ {self.name} not found. Install with: "
                f"pip install -r requirements-dev.txt{Colors.END}"
            )
            return False
        except Exception as e:  # W0718: Catching too general exception (B001)
            # This broad exception is caught to ensure the linting script continues
            # even if an unexpected error occurs with a linter, providing a full report.
            print(f"{Colors.RED}✗ {self.name} error: {e}{Colors.END}")
            return False


def setup_linters() -> List[Linter]:
    """Setup all linters with their configurations."""
    return [
        Linter(
            "Black",
            ["black", "--check", "--diff", "."],
            "Code formatting check",
        ),
        Linter(
            "isort",
            ["isort", "--check-only", "--diff", "."],
            "Import sorting check",
        ),
        Linter("flake8", ["flake8", "."], "Style guide enforcement"),
        Linter(
            "pylint",
            ["pylint", "--rcfile=pyproject.toml", "."],
            "Code analysis and style check",
        ),
        Linter("mypy", ["mypy", "."], "Static type checking"),
        Linter(
            "bandit", ["bandit", "-r", ".", "-f", "json"], "Security vulnerability scan"
        ),
        Linter(
            "safety", ["safety", "check", "--json"], "Dependency vulnerability check"
        ),
    ]


def run_linters(linters: List[Linter], cwd: str) -> Dict[str, bool]:
    """Run all linters and return results."""
    results = {}

    for linter in linters:
        results[linter.name] = linter.run(cwd)
        print()  # Add spacing between linters

    return results


def format_code(cwd: str) -> bool: # W0613: Removed unused argument 'linters'
    """Run code formatters (Black and isort) to fix formatting issues."""
    print(f"{Colors.PURPLE}{Colors.BOLD}Running code formatters...{Colors.END}")

    formatters = [
        Linter("Black", ["black", "."], "Code formatting"),
        Linter("isort", ["isort", "."], "Import sorting"),
    ]

    success = True
    for formatter in formatters:
        if not formatter.run(cwd):
            success = False

    return success


def generate_report(results: Dict[str, bool]) -> bool:
    """Generate a summary report of all linting results."""
    print(f"\n{Colors.BOLD}{Colors.UNDERLINE}Linting Report{Colors.END}")
    print("=" * 50)

    passed = sum(1 for success in results.values() if success)
    total = len(results)

    for name, success in results.items():
        status = (
            f"{Colors.GREEN}✓ PASS{Colors.END}"
            if success
            else f"{Colors.RED}✗ FAIL{Colors.END}"
        )
        print(f"{name:<15} {status}")

    print("-" * 50)
    print(f"Overall: {passed}/{total} checks passed")

    if passed == total:
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 All checks passed!{Colors.END}")
        return True

    print(
        f"{Colors.RED}{Colors.BOLD}❌ Some checks failed. Run with --fix to "
        f"auto-fix formatting issues.{Colors.END}"
    )
    return False


def main() -> None:
    """Main function to run the linting process."""
    # Get the current directory (should be the server directory)
    current_dir = Path.cwd()

    # Check if we're in the server directory by looking for key files
    if (
        not (current_dir / "app.py").exists()
        and not (current_dir / "requirements.txt").exists()
    ):
        print(
            f"{Colors.RED}Error: This script should be run from the server "
            f"directory{Colors.END}"
        )
        print(f"{Colors.YELLOW}Current directory: {current_dir}{Colors.END}")
        sys.exit(1)

    # Check if --fix flag is provided
    fix_mode = "--fix" in sys.argv

    if fix_mode:
        print(
            f"{Colors.YELLOW}Running in fix mode - will auto-format code{Colors.END}\n"
        )
        linters = setup_linters()
        success = format_code(str(current_dir))
        if success:
            print(f"{Colors.GREEN}Code formatting completed successfully!{Colors.END}")
        else:
            print(f"{Colors.RED}Code formatting failed!{Colors.END}")
            sys.exit(1)
    else:
        # Run all linters
        linters = setup_linters()
        results = run_linters(linters, str(current_dir))

        # Generate report
        all_passed = generate_report(results)

        if not all_passed:
            print(f"\n{Colors.YELLOW}To auto-fix formatting issues, run:{Colors.END}")
            print(f"{Colors.CYAN}python lint.py --fix{Colors.END}")
            sys.exit(1)


if __name__ == "__main__":
    main() 