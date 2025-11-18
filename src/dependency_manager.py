#!/usr/bin/env python3
"""
Dependency management system for automatic installation and validation of Python packages.

This module provides the core infrastructure for:
- Detecting missing Python dependencies
- Automatically installing packages using pip
- Validating successful installations
- Integrating with the existing logging and error handling systems
"""

import logging
from typing import Dict, List, Optional, Tuple, Set
import subprocess
import json
import pathlib
from .dependency_config import DependencyConfig, PackageDefinition
from .system_environment import SystemEnvironment
from .installation_validator import InstallationValidator
from .dependency_detector import DependencyDetector
from .package_installer import PackageInstaller, InstallationResult


class DependencyManager:
    """Core orchestrator for all dependency management operations."""
    
    def __init__(self, config_path: str = "dependencies.json"):
        """
        Initialize the dependency manager.
        
        Args:
            config_path: Path to the dependency configuration file
        """
        self.config_path = pathlib.Path(config_path)
        self.logger = logging.getLogger(__name__)
        
        # Initialize component managers
        self.config_manager = DependencyConfig(str(config_path))
        self.system_env = SystemEnvironment()
        self.validator = InstallationValidator()
        self.detector = DependencyDetector()
        self.installer = PackageInstaller()
        
    def check_dependencies(self) -> bool:
        """
        Check all dependencies and install missing ones.
        
        Returns:
            bool: True if all dependencies are satisfied, False otherwise
        """
        self.logger.info("Starting dependency check...")
        
        # Check if startup checking is enabled
        if not self.config_manager.is_startup_check_enabled():
            self.logger.debug("Dependency checking disabled in configuration")
            return True
            
        try:
            # Get required packages
            required_packages = self.config_manager.get_required_packages()
            if not required_packages:
                self.logger.info("No required dependencies configured")
                return True
                
            self.logger.info(f"Checking {len(required_packages)} required dependencies")
            
            # Validate existing installations
            package_defs = self.config_manager.get_package_definitions()
            missing_packages = []
            
            for package_name in required_packages:
                package_def = package_defs.get(package_name)
                if not package_def:
                    self.logger.warning(f"Package definition missing for {package_name}")
                    continue
                    
                is_valid, message = self.validator.validate_package_installation(package_def)
                if not is_valid:
                    self.logger.info(f"Package {package_name} needs installation: {message}")
                    missing_packages.append(package_def)
                else:
                    self.logger.debug(f"Package {package_name} is valid: {message}")
                    
            if not missing_packages:
                self.logger.info("All dependencies satisfied")
                self.config_manager.update_last_check_time()
                return True
                
            # Install missing packages (will be implemented in User Story tasks)
            self.logger.info(f"Found {len(missing_packages)} missing dependencies")
            return self._handle_missing_dependencies(missing_packages)
            
        except Exception as e:
            self.logger.error(f"Error during dependency check: {e}")
            return False
            
    def _handle_missing_dependencies(self, missing_packages: List[PackageDefinition]) -> bool:
        """
        Handle installation of missing dependencies.
        
        Args:
            missing_packages: List of PackageDefinition objects that need installation
            
        Returns:
            bool: True if all packages were successfully installed
        """
        self.logger.info(f"Installing {len(missing_packages)} missing dependencies...")
        
        try:
            # Install missing packages
            installation_results = self.installer.install_multiple_packages(missing_packages)
            
            # Check results
            successful_installs = []
            failed_installs = []
            
            for package_name, result in installation_results.items():
                if result.success:
                    successful_installs.append(package_name)
                    self.logger.info(f"✅ Successfully installed {package_name}")
                else:
                    failed_installs.append((package_name, result))
                    self.logger.error(f"❌ Failed to install {package_name}: {result.error_message}")
                    
                    # Provide installation guidance for failures
                    guidance = self.installer.get_installation_guidance(result)
                    if guidance:
                        self.logger.info(f"💡 Suggested solutions for {package_name}:")
                        for suggestion in guidance:
                            self.logger.info(f"   - {suggestion}")
                            
            # Validate successful installations
            if successful_installs:
                self.logger.info("Verifying installed packages...")
                for package_name in successful_installs:
                    package_def = next((p for p in missing_packages if p.name == package_name), None)
                    if package_def:
                        is_valid, message = self.validator.validate_package_installation(package_def)
                        if not is_valid:
                            self.logger.warning(f"⚠️  Package {package_name} installed but validation failed: {message}")
                        else:
                            self.logger.debug(f"✅ Package {package_name} validated successfully")
                            
            # Update last check time if any installs succeeded
            if successful_installs:
                self.config_manager.update_last_check_time()
                
            # Return True if all packages were successfully installed
            all_successful = len(failed_installs) == 0
            
            if all_successful:
                self.logger.info("🎉 All dependencies installed successfully!")
            else:
                self.logger.warning(f"⚠️  {len(failed_installs)} dependencies could not be installed automatically")
                
            return all_successful
            
        except Exception as e:
            self.logger.error(f"Unexpected error during dependency installation: {e}")
            return False
        
    def get_system_info(self) -> Dict:
        """Get comprehensive system environment information."""
        try:
            python_info = self.system_env.get_python_info()
            pip_available, pip_info = self.system_env.check_pip_availability()
            permissions = self.system_env.check_installation_permissions()
            
            return {
                'python_info': python_info,
                'pip_available': pip_available,
                'pip_info': pip_info,
                'installation_permissions': permissions
            }
        except Exception as e:
            self.logger.error(f"Error getting system info: {e}")
            return {}
            
    def _load_config(self) -> Dict:
        """Load dependency configuration from JSON file."""
        return self.config_manager.load_config()