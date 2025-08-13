#!/usr/bin/env python3
"""
Script to build the HED Web Tools documentation locally.
"""

import subprocess
import sys
import os

def main():
    """Build the documentation using MkDocs."""
    print("Building HED Web Tools documentation...")

    # Check if we're in the right directory
    if not os.path.exists('mkdocs.yml'):
        print("Error: mkdocs.yml not found. Please run this script from the project root.")
        sys.exit(1)

    try:
        # Install requirements
        print("Installing documentation requirements...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'docs/requirements.txt'],
                      check=True)

        # Build the documentation
        print("Building documentation with MkDocs...")
        subprocess.run(['mkdocs', 'build'], check=True)

        print("Documentation built successfully!")
        print("Open 'site/index.html' in your browser to view the documentation.")

    except subprocess.CalledProcessError as e:
        print(f"Error building documentation: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("Error: mkdocs command not found. Please install mkdocs:")
        print("pip install -r docs/requirements.txt")
        sys.exit(1)

if __name__ == "__main__":
    main()
