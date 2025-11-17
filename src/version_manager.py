#!/usr/bin/env python3
"""Version Management System.

Handles semantic versioning with date-based format: YYYY.MM.DD_N
Where N is an incrementing integer for releases on the same day.
"""

import os
import json
import urllib.request
import urllib.error
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class VersionInfo:
    """Version information structure."""
    version: str
    release_date: str
    is_latest: bool
    release_notes: Optional[str] = None
    github_url: Optional[str] = None


class VersionManager:
    """Manages version numbering, releases, and update checking."""
    
    def __init__(self, github_repo: str = "keiranharris/priceup"):
        """Initialize version manager.
        
        Args:
            github_repo: GitHub repository in format "owner/repo"
        """
        self.github_repo = github_repo
        self.version_file = Path("VERSION")
        self.cache_file = Path.home() / ".priceup_version_cache.json"
        self._version_cache: Optional[Dict[str, Any]] = None
        self._cache_max_age_hours = 24
    
    def get_current_version(self) -> str:
        """Get the current application version.
        
        Returns:
            Current version string (e.g., "2025.11.18_1")
        """
        if self.version_file.exists():
            return self.version_file.read_text().strip()
        else:
            # Default to today's first release if no version file exists
            return self.generate_initial_version()
    
    def generate_initial_version(self) -> str:
        """Generate initial version for today.
        
        Returns:
            Version string for today's first release
        """
        today = datetime.now().strftime("%Y.%m.%d")
        return f"{today}_1"
    
    def generate_next_version(self) -> str:
        """Generate the next version number for today.
        
        Returns:
            Next version string for today
        """
        today = datetime.now().strftime("%Y.%m.%d")
        current_version = self.get_current_version()
        
        # Parse current version
        if "_" in current_version:
            version_date, version_num = current_version.split("_", 1)
            try:
                current_num = int(version_num)
            except ValueError:
                current_num = 0
        else:
            version_date = ""
            current_num = 0
        
        # If it's the same day, increment the number
        if version_date == today:
            next_num = current_num + 1
        else:
            # New day, start with 1
            next_num = 1
        
        return f"{today}_{next_num}"
    
    def set_version(self, version: str) -> bool:
        """Set the current version.
        
        Args:
            version: Version string to set
            
        Returns:
            True if version was set successfully
        """
        try:
            self.version_file.write_text(version)
            return True
        except IOError as e:
            print(f"Failed to set version: {e}")
            return False
    
    def validate_version_format(self, version: str) -> bool:
        """Validate version format.
        
        Args:
            version: Version string to validate
            
        Returns:
            True if version format is valid
        """
        import re
        pattern = r'^\d{4}\.\d{2}\.\d{2}_\d+$'
        return bool(re.match(pattern, version))
    
    def check_for_updates(self, force_check: bool = False) -> Optional[VersionInfo]:
        """Check for available updates from GitHub releases.
        
        Args:
            force_check: Force check even if cache is valid
            
        Returns:
            VersionInfo if newer version available, None otherwise
        """
        try:
            # Check cache first
            if not force_check and self._is_cache_valid():
                cached_data = self._load_cache()
                if cached_data and not cached_data.get('has_update', False):
                    return None
            
            latest_release = self._get_latest_github_release()
            if not latest_release:
                return None
            
            latest_version = latest_release.get('tag_name', '').lstrip('v')
            current_version = self.get_current_version()
            
            if self._is_version_newer(latest_version, current_version):
                version_info = VersionInfo(
                    version=latest_version,
                    release_date=latest_release.get('published_at', ''),
                    is_latest=True,
                    release_notes=latest_release.get('body', ''),
                    github_url=latest_release.get('html_url', '')
                )
                
                # Update cache
                self._save_cache({
                    'has_update': True,
                    'latest_version': latest_version,
                    'release_info': latest_release,
                    'checked_at': datetime.now().isoformat()
                })
                
                return version_info
            else:
                # No update available, cache this result
                self._save_cache({
                    'has_update': False,
                    'current_version': current_version,
                    'checked_at': datetime.now().isoformat()
                })
                return None
                
        except Exception as e:
            print(f"Failed to check for updates: {e}")
            return None
    
    def _get_latest_github_release(self) -> Optional[Dict[str, Any]]:
        """Get latest release from GitHub API.
        
        Returns:
            Release data dictionary or None
        """
        try:
            url = f"https://api.github.com/repos/{self.github_repo}/releases/latest"
            
            req = urllib.request.Request(url)
            req.add_header('Accept', 'application/vnd.github.v3+json')
            req.add_header('User-Agent', 'PriceUp-Version-Checker/1.0')
            
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    data = response.read().decode('utf-8')
                    return json.loads(data)
                else:
                    return None
                    
        except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, OSError):
            return None
    
    def _is_version_newer(self, version1: str, version2: str) -> bool:
        """Compare two versions to see if version1 is newer than version2.
        
        Args:
            version1: First version string
            version2: Second version string
            
        Returns:
            True if version1 is newer than version2
        """
        def parse_version(version: str) -> Tuple[str, int]:
            """Parse version string into date and number components."""
            if "_" in version:
                date_part, num_part = version.split("_", 1)
                try:
                    num = int(num_part)
                except ValueError:
                    num = 0
                return date_part, num
            else:
                return version, 0
        
        date1, num1 = parse_version(version1)
        date2, num2 = parse_version(version2)
        
        # Compare dates first
        if date1 != date2:
            return date1 > date2
        
        # Same date, compare numbers
        return num1 > num2
    
    def _is_cache_valid(self) -> bool:
        """Check if version check cache is still valid.
        
        Returns:
            True if cache is valid and within max age
        """
        if not self.cache_file.exists():
            return False
        
        try:
            cached_data = self._load_cache()
            if not cached_data:
                return False
            
            checked_at = datetime.fromisoformat(cached_data.get('checked_at', ''))
            age_hours = (datetime.now() - checked_at).total_seconds() / 3600
            
            return age_hours < self._cache_max_age_hours
            
        except (KeyError, ValueError, TypeError):
            return False
    
    def _load_cache(self) -> Optional[Dict[str, Any]]:
        """Load version check cache from file.
        
        Returns:
            Cached data dictionary or None
        """
        try:
            if self.cache_file.exists():
                return json.loads(self.cache_file.read_text())
            return None
        except (IOError, json.JSONDecodeError):
            return None
    
    def _save_cache(self, data: Dict[str, Any]) -> None:
        """Save version check cache to file.
        
        Args:
            data: Data to cache
        """
        try:
            self.cache_file.parent.mkdir(exist_ok=True)
            self.cache_file.write_text(json.dumps(data, indent=2))
        except IOError:
            pass  # Cache failure is non-critical
    
    def prompt_for_update_confirmation(self, version_info: VersionInfo) -> bool:
        """Prompt user for update confirmation.
        
        Args:
            version_info: Information about available update
            
        Returns:
            True if user wants to continue with current version
        """
        print(f"\n🔄 A new version of this code is available!")
        print(f"Current version: {self.get_current_version()}")
        print(f"Latest version: {version_info.version}")
        
        if version_info.github_url:
            print(f"Release page: {version_info.github_url}")
        
        print(f"\nTo update, run: git pull && git checkout v{version_info.version}")
        print(f"Or visit: https://github.com/{self.github_repo}/releases")
        
        while True:
            response = input("\nThere is a new version available. Are you sure you want to run with your old version? (y/n): ").strip().lower()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                print("Please update to the latest version before continuing.")
                return False
            else:
                print("Please enter 'y' for yes or 'n' for no.")
    
    def display_version_info(self) -> str:
        """Display current version information.
        
        Returns:
            Formatted version string for display
        """
        current_version = self.get_current_version()
        return f"🚀 PriceUp v{current_version}"
    
    def create_release_info(self, version: str, release_notes: str = "") -> Dict[str, Any]:
        """Create release information for GitHub.
        
        Args:
            version: Version string
            release_notes: Release notes content
            
        Returns:
            Release information dictionary
        """
        return {
            'tag_name': f"v{version}",
            'target_commitish': 'main',
            'name': f"Release {version}",
            'body': release_notes or f"Release {version}",
            'draft': False,
            'prerelease': False
        }
    
    def get_version_history(self) -> List[VersionInfo]:
        """Get version history from GitHub releases.
        
        Returns:
            List of VersionInfo objects for all releases
        """
        try:
            url = f"https://api.github.com/repos/{self.github_repo}/releases"
            
            req = urllib.request.Request(url)
            req.add_header('Accept', 'application/vnd.github.v3+json')
            req.add_header('User-Agent', 'PriceUp-Version-Checker/1.0')
            
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    data = response.read().decode('utf-8')
                    releases = json.loads(data)
                    
                    version_history = []
                    for release in releases:
                        version = release.get('tag_name', '').lstrip('v')
                        version_info = VersionInfo(
                            version=version,
                            release_date=release.get('published_at', ''),
                            is_latest=release == releases[0],  # First in list is latest
                            release_notes=release.get('body', ''),
                            github_url=release.get('html_url', '')
                        )
                        version_history.append(version_info)
                    
                    return version_history
                else:
                    return []
                    
        except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, OSError):
            return []