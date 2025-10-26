#!/usr/bin/env python3
"""
Cross-platform script to build the HED Web Tools documentation locally using Sphinx.

Usage:
    python build_docs.py

This script works on Windows, macOS, and Linux. It will:
1. Install documentation dependencies
2. Build the documentation with Sphinx
3. Display the path to view the built documentation

The script automatically detects the platform and uses appropriate commands.
"""

import os
import platform
import subprocess
import sys


def main():
    """Build the documentation using Sphinx."""
    print(f"Building HED Web Tools documentation with Sphinx on {platform.system()}...")

    # Check if we're in the right directory
    if not os.path.exists("docs/conf.py"):
        print(
            "Error: docs/conf.py not found. Please run this script from the project root."
        )
        sys.exit(1)

    try:
        # Install requirements
        print("Installing main and documentation requirements...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            check=True,
        )
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "docs/requirements.txt"],
            check=True,
        )

        # Build the documentation
        print("Building documentation with Sphinx...")
        # Use sphinx.cmd.build module instead of sphinx-build command
        subprocess.run(
            [sys.executable, "-m", "sphinx", "-b", "html", "docs", "docs/_build/html"],
            check=True,
        )

        print("Documentation built successfully!")

        # Provide platform-specific instructions for viewing
        docs_path = os.path.abspath("docs/_build/html/index.html")
        print(f"Documentation location: {docs_path}")

        if platform.system() == "Windows":
            print("To view: Open the file in your browser or run:")
            print(f"  start {docs_path}")
        elif platform.system() == "Darwin":  # macOS
            print("To view: Open the file in your browser or run:")
            print(f"  open {docs_path}")
        else:  # Linux and others
            print("To view: Open the file in your browser or run:")
            print(f"  xdg-open {docs_path}")

        print("\nAlternatively, serve locally with:")
        print("  python -m http.server 8000 -d docs/_build/html")
        print("  Then visit: http://localhost:8000")

    except subprocess.CalledProcessError as e:
        print(f"Error building documentation: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("Error: sphinx module not found. Please install sphinx:")
        print("pip install -r docs/requirements.txt")
        sys.exit(1)


if __name__ == "__main__":
    main()
