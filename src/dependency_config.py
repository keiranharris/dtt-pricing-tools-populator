#!/usr/bin/env python3
"""
Configuration management for dependency definitions and settings.

This module provides functionality to:
- Load and validate dependency configurations
- Manage package definitions with version requirements
- Handle configuration updates and caching
- Provide default configurations for common packages
"""

import json
import pathlib
import logging
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict


@dataclass
class PackageDefinition:
    """Represents a single package dependency definition."""
    name: str
    min_version: Optional[str] = None
    max_version: Optional[str] = None
    import_name: Optional[str] = None
    required_for: Optional[List[str]] = None
    installation_notes: Optional[str] = None
    optional: bool = False


class DependencyConfig:
    """Manages dependency configuration loading, validation, and caching."""
    
    def __init__(self, config_path: str = "dependencies.json"):
        """
        Initialize dependency configuration manager.
        
        Args:
            config_path: Path to the JSON configuration file
        """
        self.config_path = pathlib.Path(config_path)
        self.logger = logging.getLogger(__name__)
        self._config_cache = None
        self._packages_cache = {}
        
    def load_config(self) -> Dict:
        """
        Load the complete dependency configuration from JSON file.
        
        Returns:
            Dict containing the full configuration
        """
        if self._config_cache is not None:
            return self._config_cache
            
        try:
            if not self.config_path.exists():
                self.logger.warning(f"Configuration file not found: {self.config_path}")
                self._config_cache = self._get_default_config()
                return self._config_cache
                
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                
            # Validate configuration structure
            self._validate_config(config)
            self._config_cache = config
            return config
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in configuration file: {e}")
            return self._get_default_config()
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
            return self._get_default_config()
            
    def get_package_definitions(self) -> Dict[str, PackageDefinition]:
        """
        Get all package definitions as PackageDefinition objects.
        
        Returns:
            Dict mapping package names to PackageDefinition objects
        """
        if self._packages_cache:
            return self._packages_cache
            
        config = self.load_config()
        packages = {}
        
        for name, package_data in config.get('packages', {}).items():
            try:
                packages[name] = PackageDefinition(
                    name=name,
                    min_version=package_data.get('min_version'),
                    max_version=package_data.get('max_version'),
                    import_name=package_data.get('import_name', name),
                    required_for=package_data.get('required_for', []),
                    installation_notes=package_data.get('installation_notes'),
                    optional=package_data.get('optional', False)
                )
            except Exception as e:
                self.logger.error(f"Error parsing package definition for {name}: {e}")
                continue
                
        self._packages_cache = packages
        return packages
        
    def get_required_packages(self) -> Set[str]:
        """
        Get set of all required (non-optional) package names.
        
        Returns:
            Set of required package names
        """
        packages = self.get_package_definitions()
        return {name for name, pkg in packages.items() if not pkg.optional}
        
    def get_package_by_import_name(self, import_name: str) -> Optional[PackageDefinition]:
        """
        Find package definition by its import name.
        
        Args:
            import_name: The name used to import the package
            
        Returns:
            PackageDefinition if found, None otherwise
        """
        packages = self.get_package_definitions()
        for package in packages.values():
            if package.import_name == import_name:
                return package
        return None
        
    def is_startup_check_enabled(self) -> bool:
        """
        Check if dependency checking should occur on startup.
        
        Returns:
            True if startup checking is enabled
        """
        config = self.load_config()
        return config.get('check_on_startup', True)
        
    def get_python_version_requirement(self) -> Optional[str]:
        """
        Get the minimum Python version requirement.
        
        Returns:
            Python version string or None
        """
        config = self.load_config()
        return config.get('python_version')
        
    def update_last_check_time(self) -> None:
        """Update the last dependency check timestamp in the configuration."""
        try:
            config = self.load_config()
            from datetime import datetime
            config['last_checked'] = datetime.now().isoformat()
            
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
                
            # Clear cache to force reload
            self._config_cache = None
            self._packages_cache = {}
            
        except Exception as e:
            self.logger.error(f"Error updating last check time: {e}")
            
    def _validate_config(self, config: Dict) -> None:
        """
        Validate the structure of a configuration dictionary.
        
        Args:
            config: Configuration dictionary to validate
            
        Raises:
            ValueError: If configuration is invalid
        """
        if not isinstance(config, dict):
            raise ValueError("Configuration must be a dictionary")
            
        if 'packages' not in config:
            raise ValueError("Configuration must contain 'packages' section")
            
        if not isinstance(config['packages'], dict):
            raise ValueError("'packages' section must be a dictionary")
            
        # Validate each package definition
        for name, package_data in config['packages'].items():
            if not isinstance(package_data, dict):
                raise ValueError(f"Package definition for '{name}' must be a dictionary")
                
    def _get_default_config(self) -> Dict:
        """
        Get default configuration when file is missing or invalid.
        
        Returns:
            Default configuration dictionary
        """
        return {
            "packages": {
                "xlwings": {
                    "min_version": "0.24.0",
                    "import_name": "xlwings",
                    "required_for": ["excel_operations"],
                    "installation_notes": "Required for Excel file manipulation"
                }
            },
            "python_version": "3.11+",
            "last_updated": "2025-11-18",
            "check_on_startup": True
        }