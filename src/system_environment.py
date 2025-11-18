#!/usr/bin/env python3
"""
System environment detection and compatibility checking for dependency management.

This module provides functionality to:
- Detect Python environment details (version, installation path)
- Check pip availability and permissions
- Identify platform-specific requirements
- Determine installation capabilities and constraints
"""

import sys
import subprocess
import platform
import pathlib
import logging
from typing import Dict, Optional, Tuple, List


class SystemEnvironment:
    """Detects and manages Python environment information for dependency management."""
    
    def __init__(self):
        """Initialize system environment detector."""
        self.logger = logging.getLogger(__name__)
        self._environment_cache = {}
        
    def get_python_info(self) -> Dict[str, str]:
        """
        Get comprehensive Python environment information.
        
        Returns:
            Dict containing Python version, executable path, and platform info
        """
        if 'python_info' in self._environment_cache:
            return self._environment_cache['python_info']
            
        info = {
            'version': sys.version,
            'version_info': '.'.join(map(str, sys.version_info[:3])),
            'executable': sys.executable,
            'platform': platform.platform(),
            'system': platform.system(),
            'architecture': platform.machine(),
            'python_implementation': platform.python_implementation()
        }
        
        self._environment_cache['python_info'] = info
        return info
        
    def check_pip_availability(self) -> Tuple[bool, Optional[str]]:
        """
        Check if pip is available and accessible.
        
        Returns:
            Tuple of (is_available, pip_path or error_message)
        """
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pip', '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return True, result.stdout.strip()
            else:
                return False, f"pip check failed: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return False, "pip check timed out"
        except Exception as e:
            return False, f"pip check error: {str(e)}"
            
    def check_installation_permissions(self) -> Dict[str, bool]:
        """
        Check what types of package installations are possible.
        
        Returns:
            Dict indicating available installation methods
        """
        permissions = {
            'user_install': True,  # --user flag
            'system_install': False,  # requires admin
            'virtual_env': self._is_in_virtual_env()
        }
        
        # Try to determine if we can do system installs
        try:
            # Test write access to site-packages directory
            import site
            for site_dir in site.getsitepackages():
                site_path = pathlib.Path(site_dir)
                if site_path.exists():
                    permissions['system_install'] = site_path.is_dir() and \
                        self._can_write_to_directory(site_path)
                    break
        except Exception:
            # If we can't determine, assume no system permissions
            permissions['system_install'] = False
            
        return permissions
        
    def get_platform_specific_guidance(self) -> Dict[str, List[str]]:
        """
        Get platform-specific installation guidance for fallback scenarios.
        
        Returns:
            Dict with installation commands and guidance for the current platform
        """
        system = platform.system().lower()
        
        guidance = {
            'user_install_cmd': [sys.executable, '-m', 'pip', 'install', '--user'],
            'system_install_cmd': [sys.executable, '-m', 'pip', 'install'],
            'platform_notes': []
        }
        
        if system == 'darwin':  # macOS
            guidance['platform_notes'] = [
                "On macOS, you may need to use --user flag for installations",
                "If using Homebrew Python, system installs should work",
                "For permission issues, try: pip install --user <package>"
            ]
        elif system == 'windows':
            guidance['platform_notes'] = [
                "On Windows, you may need to run terminal as Administrator",
                "For user installs, use: pip install --user <package>",
                "Check Windows Store Python vs. traditional Python installation"
            ]
        elif system == 'linux':
            guidance['platform_notes'] = [
                "On Linux, system packages may require sudo",
                "User installs recommended: pip install --user <package>",
                "Check if using system Python or custom installation"
            ]
            
        return guidance
        
    def _is_in_virtual_env(self) -> bool:
        """Check if running in a virtual environment."""
        return (
            hasattr(sys, 'real_prefix') or  # virtualenv
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)  # venv
        )
        
    def _can_write_to_directory(self, directory: pathlib.Path) -> bool:
        """Check if we can write to a directory."""
        try:
            test_file = directory / '.write_test'
            test_file.touch()
            test_file.unlink()
            return True
        except (PermissionError, OSError):
            return False