#!/usr/bin/env python3
"""
Package installation validation and verification system.

This module provides functionality to:
- Verify successful package installations
- Test import capability of installed packages
- Validate package versions meet requirements
- Provide detailed installation verification reports
"""

import sys
import importlib
import subprocess
import logging
import re
from typing import Dict, List, Optional, Tuple
from .dependency_config import PackageDefinition


class InstallationValidator:
    """Validates successful package installations and import capability."""
    
    def __init__(self):
        """Initialize the installation validator."""
        self.logger = logging.getLogger(__name__)
        
    def validate_package_installation(self, package_def: PackageDefinition) -> Tuple[bool, str]:
        """
        Validate that a package is properly installed and importable.
        
        Args:
            package_def: PackageDefinition object with package details
            
        Returns:
            Tuple of (is_valid, status_message)
        """
        package_name = package_def.name
        import_name = package_def.import_name or package_name
        
        self.logger.debug(f"Validating installation of {package_name}")
        
        # Step 1: Check if package is installed via pip
        pip_installed, pip_message = self._check_pip_package(package_name)
        if not pip_installed:
            return False, f"Package {package_name} not found in pip: {pip_message}"
            
        # Step 2: Test import capability
        import_success, import_message = self._test_import(import_name)
        if not import_success:
            return False, f"Package {package_name} installed but import failed: {import_message}"
            
        # Step 3: Version validation if specified
        if package_def.min_version:
            version_valid, version_message = self._validate_version(
                package_name, package_def.min_version, package_def.max_version
            )
            if not version_valid:
                return False, f"Package {package_name} version issue: {version_message}"
                
        return True, f"Package {package_name} successfully validated"
        
    def validate_multiple_packages(self, package_defs: List[PackageDefinition]) -> Dict[str, Tuple[bool, str]]:
        """
        Validate multiple packages and return comprehensive results.
        
        Args:
            package_defs: List of PackageDefinition objects to validate
            
        Returns:
            Dict mapping package names to (is_valid, status_message) tuples
        """
        results = {}
        
        for package_def in package_defs:
            try:
                is_valid, message = self.validate_package_installation(package_def)
                results[package_def.name] = (is_valid, message)
            except Exception as e:
                results[package_def.name] = (False, f"Validation error: {str(e)}")
                
        return results
        
    def get_installed_version(self, package_name: str) -> Optional[str]:
        """
        Get the currently installed version of a package.
        
        Args:
            package_name: Name of the package
            
        Returns:
            Version string if found, None otherwise
        """
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'show', package_name],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                # Parse version from pip show output
                for line in result.stdout.split('\n'):
                    if line.startswith('Version:'):
                        return line.split(':', 1)[1].strip()
                        
        except Exception as e:
            self.logger.debug(f"Error getting version for {package_name}: {e}")
            
        return None
        
    def _check_pip_package(self, package_name: str) -> Tuple[bool, str]:
        """
        Check if a package is installed via pip.
        
        Args:
            package_name: Name of the package to check
            
        Returns:
            Tuple of (is_installed, status_message)
        """
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'show', package_name],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return True, "Package found in pip"
            else:
                return False, "Package not found in pip"
                
        except subprocess.TimeoutExpired:
            return False, "pip show command timed out"
        except Exception as e:
            return False, f"Error checking pip: {str(e)}"
            
    def _test_import(self, import_name: str) -> Tuple[bool, str]:
        """
        Test if a package can be imported successfully.
        
        Args:
            import_name: Name to use for import
            
        Returns:
            Tuple of (can_import, status_message)
        """
        try:
            # Try importing the package
            importlib.import_module(import_name)
            return True, "Import successful"
            
        except ImportError as e:
            return False, f"Import failed: {str(e)}"
        except Exception as e:
            return False, f"Unexpected import error: {str(e)}"
            
    def _validate_version(self, package_name: str, min_version: str, max_version: Optional[str] = None) -> Tuple[bool, str]:
        """
        Validate that installed package version meets requirements.
        
        Args:
            package_name: Name of the package
            min_version: Minimum required version
            max_version: Maximum allowed version (optional)
            
        Returns:
            Tuple of (version_valid, status_message)
        """
        installed_version = self.get_installed_version(package_name)
        
        if not installed_version:
            return False, "Could not determine installed version"
            
        try:
            # Simple version comparison using tuple parsing
            installed_ver = self._parse_version_tuple(installed_version)
            min_ver = self._parse_version_tuple(min_version)
            
            if installed_ver < min_ver:
                return False, f"Installed version {installed_version} is below minimum {min_version}"
                
            if max_version:
                max_ver = self._parse_version_tuple(max_version)
                if installed_ver > max_ver:
                    return False, f"Installed version {installed_version} is above maximum {max_version}"
                    
            return True, f"Version {installed_version} meets requirements"
            
        except Exception as e:
            return False, f"Error parsing versions: {str(e)}"
            
    def _parse_version_tuple(self, version_string: str) -> Tuple[int, ...]:
        """
        Parse version string into tuple of integers for comparison.
        
        Args:
            version_string: Version string like "1.2.3"
            
        Returns:
            Tuple of version parts as integers
        """
        # Remove common version prefixes and suffixes
        clean_version = re.sub(r'[^\d\.]', '', version_string.split()[0])
        
        # Split by dots and convert to integers
        parts = []
        for part in clean_version.split('.'):
            if part.isdigit():
                parts.append(int(part))
            else:
                # Handle non-numeric parts by taking numeric prefix
                numeric_part = re.match(r'\d+', part)
                if numeric_part:
                    parts.append(int(numeric_part.group()))
                    
        return tuple(parts) if parts else (0,)