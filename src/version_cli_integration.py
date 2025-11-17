#!/usr/bin/env python3
"""Version Control CLI Integration.

Handles version display and update checking in the CLI interface.
"""

import sys
from typing import Optional
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from version_manager import VersionManager, VersionInfo
except ImportError:
    # Fallback for when version_manager is not available
    class VersionManager:
        def get_current_version(self) -> str:
            return "1.0.0"
        
        def display_version_info(self) -> str:
            return "🚀 PriceUp v1.0.0"
        
        def check_for_updates(self, force_check: bool = False) -> Optional[object]:
            return None
        
        def prompt_for_update_confirmation(self, version_info) -> bool:
            return True


def display_version_on_startup() -> str:
    """Display version information on application startup.
    
    Returns:
        Formatted version string
    """
    try:
        version_manager = VersionManager()
        return version_manager.display_version_info()
    except Exception:
        return "🚀 PriceUp v1.0.0"


def check_for_updates_interactive() -> bool:
    """Check for updates and prompt user if newer version available.
    
    Returns:
        True if user wants to continue with current version, False to exit
    """
    try:
        version_manager = VersionManager()
        
        # Check for updates
        update_info = version_manager.check_for_updates()
        
        if update_info:
            # Newer version available, prompt user
            return version_manager.prompt_for_update_confirmation(update_info)
        else:
            # No update available or check failed, continue normally
            return True
            
    except Exception as e:
        # If version checking fails, continue normally
        print(f"Note: Could not check for updates ({e})")
        return True


def handle_version_flag() -> bool:
    """Handle --version and -v command line flags.
    
    Returns:
        True if version flag was processed (should exit), False otherwise
    """
    # Check for version flag before any other argument processing
    for arg in sys.argv[1:]:
        if arg in ['--version', '-v']:
            try:
                version_manager = VersionManager()
                print(version_manager.get_current_version())
            except Exception:
                print("1.0.0")
            return True
    return False


def integrate_version_display_and_checks() -> bool:
    """Integrate version display and update checks into application startup.
    
    This should be called at the very beginning of the main application.
    
    Returns:
        True if application should continue, False if it should exit
    """
    # Handle version flag first
    if handle_version_flag():
        return False
    
    # Display version on startup
    version_info = display_version_on_startup()
    print(version_info)
    
    # Check for updates and get user confirmation if needed
    should_continue = check_for_updates_interactive()
    
    return should_continue


if __name__ == "__main__":
    # For testing
    print("Version CLI Integration Test")
    print(f"Startup display: {display_version_on_startup()}")
    
    if not handle_version_flag():
        print("Version flag not processed")
    
    print(f"Update check: {check_for_updates_interactive()}")