#!/usr/bin/env python3
"""
Shell Alias Setup Entry Point - Main script for setting up shell aliases.

This script provides the main entry point for the shell alias auto-setup functionality.
It can be run directly or imported as a module.
"""

import sys
from pathlib import Path

# Add the src directory to the Python path for imports
src_dir = Path(__file__).parent / "src"
if src_dir not in [Path(p) for p in sys.path]:
    sys.path.insert(0, str(src_dir))

from src.shell_alias_cli import main

if __name__ == "__main__":
    main()