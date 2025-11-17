#!/usr/bin/env python3
"""Release Management Script.

Handles version bumping and release preparation for the project.
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from version_manager import VersionManager


def create_new_release(release_notes: str = "") -> bool:
    """Create a new release with incremented version.
    
    Args:
        release_notes: Optional release notes
        
    Returns:
        True if release created successfully
    """
    version_manager = VersionManager()
    
    # Generate next version
    next_version = version_manager.generate_next_version()
    
    print(f"Creating new release: v{next_version}")
    
    # Update VERSION file
    if not version_manager.set_version(next_version):
        print("❌ Failed to update VERSION file")
        return False
    
    # Stage VERSION file
    try:
        subprocess.run(["git", "add", "VERSION"], check=True)
        print("✅ Staged VERSION file")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to stage VERSION file: {e}")
        return False
    
    # Create commit
    commit_message = f"release: Version {next_version}"
    if release_notes:
        commit_message += f"\n\n{release_notes}"
    
    try:
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        print(f"✅ Created commit for v{next_version}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create commit: {e}")
        return False
    
    # Create Git tag
    try:
        subprocess.run(["git", "tag", "-a", f"v{next_version}", "-m", f"Release {next_version}"], check=True)
        print(f"✅ Created tag v{next_version}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create tag: {e}")
        return False
    
    print(f"\n🎉 Release v{next_version} created successfully!")
    print(f"To push to remote:")
    print(f"  git push origin main")
    print(f"  git push origin v{next_version}")
    
    return True


def show_version_info():
    """Display current version information."""
    version_manager = VersionManager()
    
    current_version = version_manager.get_current_version()
    next_version = version_manager.generate_next_version()
    
    print(f"Current version: {current_version}")
    print(f"Next version: {next_version}")
    
    # Show version validation
    is_valid = version_manager.validate_version_format(current_version)
    print(f"Version format valid: {'✅' if is_valid else '❌'}")


def main():
    """Main script entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Release Management Script")
    parser.add_argument("--info", action="store_true", help="Show version information")
    parser.add_argument("--release", action="store_true", help="Create new release")
    parser.add_argument("--notes", type=str, help="Release notes for new release")
    parser.add_argument("--check-updates", action="store_true", help="Check for available updates")
    
    args = parser.parse_args()
    
    version_manager = VersionManager()
    
    if args.info:
        show_version_info()
    elif args.check_updates:
        print("Checking for updates...")
        update_info = version_manager.check_for_updates(force_check=True)
        if update_info:
            print(f"📢 Update available: v{update_info.version}")
            if update_info.github_url:
                print(f"Release page: {update_info.github_url}")
        else:
            print("✅ No updates available")
    elif args.release:
        release_notes = args.notes or ""
        success = create_new_release(release_notes)
        if not success:
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()