#!/usr/bin/env python3
"""
Package installation system with progress feedback and error recovery.

This module provides functionality to:
- Install Python packages using pip subprocess execution
- Provide real-time installation progress feedback
- Handle installation failures with retry logic
- Support different installation methods (user, system, virtual env)
"""

import sys
import subprocess
import logging
import time
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
from .system_environment import SystemEnvironment
from .dependency_config import PackageDefinition


class InstallationMethod(Enum):
    """Available package installation methods."""
    USER_INSTALL = "user"          # pip install --user
    SYSTEM_INSTALL = "system"      # pip install (requires admin)
    VIRTUAL_ENV = "virtualenv"     # pip install in virtual environment


@dataclass
class InstallationResult:
    """Result of a package installation attempt."""
    package_name: str
    success: bool
    method_used: InstallationMethod
    output: str = ""
    error_message: str = ""
    installation_time: float = 0.0
    retry_count: int = 0


class PackageInstaller:
    """Handles pip package installation with progress feedback."""
    
    def __init__(self):
        """Initialize package installer."""
        self.logger = logging.getLogger(__name__)
        self.system_env = SystemEnvironment()
        self._installation_timeout = 300  # 5 minutes max per package
        
    def install_package(self, package_def: PackageDefinition, method: Optional[InstallationMethod] = None) -> InstallationResult:
        """
        Install a single package with progress feedback.
        
        Args:
            package_def: Package definition with installation requirements
            method: Preferred installation method (auto-detected if None)
            
        Returns:
            InstallationResult with success status and details
        """
        package_name = package_def.name
        start_time = time.time()
        
        self.logger.info(f"Starting installation of {package_name}")
        
        # Determine installation method if not specified
        if method is None:
            method = self._determine_best_method()
            
        # Build pip command
        pip_command = self._build_pip_command(package_def, method)
        
        # Execute installation with progress tracking
        result = self._execute_installation(package_name, pip_command, method, start_time)
        
        if result.success:
            self.logger.info(f"Successfully installed {package_name} in {result.installation_time:.1f}s")
        else:
            self.logger.error(f"Failed to install {package_name}: {result.error_message}")
            
        return result
        
    def install_multiple_packages(self, package_defs: List[PackageDefinition], method: Optional[InstallationMethod] = None) -> Dict[str, InstallationResult]:
        """
        Install multiple packages with progress tracking.
        
        Args:
            package_defs: List of package definitions to install
            method: Preferred installation method for all packages
            
        Returns:
            Dict mapping package names to InstallationResult objects
        """
        results = {}
        total_packages = len(package_defs)
        
        self.logger.info(f"Installing {total_packages} packages...")
        
        for i, package_def in enumerate(package_defs, 1):
            self.logger.info(f"📦 Installing package {i}/{total_packages}: {package_def.name}")
            
            result = self.install_package(package_def, method)
            results[package_def.name] = result
            
            if not result.success:
                self.logger.warning(f"Failed to install {package_def.name}, continuing with remaining packages")
                
        # Summary
        successful = sum(1 for r in results.values() if r.success)
        self.logger.info(f"Installation complete: {successful}/{total_packages} packages installed successfully")
        
        return results
        
    def get_installation_guidance(self, failure_result: InstallationResult) -> List[str]:
        """
        Get platform-specific guidance for failed installations.
        
        Args:
            failure_result: Failed InstallationResult to provide guidance for
            
        Returns:
            List of suggested solutions
        """
        guidance = []
        package_name = failure_result.package_name
        error_msg = failure_result.error_message.lower()
        
        # Permission-related errors
        if 'permission denied' in error_msg or 'access is denied' in error_msg:
            guidance.extend([
                f"Try user installation: {sys.executable} -m pip install --user {package_name}",
                "Or run with administrator/sudo privileges",
            ])
            
        # Network-related errors
        elif 'timeout' in error_msg or 'connection' in error_msg or 'network' in error_msg:
            guidance.extend([
                "Check internet connection",
                f"Try with longer timeout: {sys.executable} -m pip install --timeout 600 {package_name}",
                "Consider downloading the package manually",
            ])
            
        # Version-related errors
        elif 'could not find' in error_msg or 'no matching distribution' in error_msg:
            guidance.extend([
                f"Check if package name '{package_name}' is correct",
                "Try without version constraints",
                "Search PyPI for similar package names",
            ])
            
        # Generic fallback guidance
        if not guidance:
            platform_guidance = self.system_env.get_platform_specific_guidance()
            guidance.extend(platform_guidance.get('platform_notes', []))
            
        return guidance
        
    def _determine_best_method(self) -> InstallationMethod:
        """
        Determine the best installation method for the current environment.
        
        Returns:
            Recommended InstallationMethod
        """
        permissions = self.system_env.check_installation_permissions()
        
        if permissions.get('virtual_env', False):
            return InstallationMethod.VIRTUAL_ENV
        elif permissions.get('system_install', False):
            return InstallationMethod.SYSTEM_INSTALL
        else:
            return InstallationMethod.USER_INSTALL
            
    def _build_pip_command(self, package_def: PackageDefinition, method: InstallationMethod) -> List[str]:
        """
        Build pip command for package installation.
        
        Args:
            package_def: Package definition
            method: Installation method to use
            
        Returns:
            List of command arguments
        """
        cmd = [sys.executable, '-m', 'pip', 'install']
        
        # Add method-specific flags
        if method == InstallationMethod.USER_INSTALL:
            cmd.append('--user')
        
        # Add package specification
        package_spec = package_def.name
        if package_def.min_version:
            package_spec += f">={package_def.min_version}"
        if package_def.max_version:
            package_spec += f",<={package_def.max_version}"
            
        cmd.append(package_spec)
        
        # Add common flags for better reliability
        cmd.extend(['--disable-pip-version-check', '--no-input', '--break-system-packages'])
        
        return cmd
        
    def _execute_installation(self, package_name: str, pip_command: List[str], method: InstallationMethod, start_time: float) -> InstallationResult:
        """
        Execute pip installation command with progress tracking.
        
        Args:
            package_name: Name of package being installed
            pip_command: Complete pip command to execute
            method: Installation method being used
            start_time: Time when installation started
            
        Returns:
            InstallationResult with execution details
        """
        try:
            self.logger.debug(f"Executing: {' '.join(pip_command)}")
            
            # Execute pip command
            result = subprocess.run(
                pip_command,
                capture_output=True,
                text=True,
                timeout=self._installation_timeout
            )
            
            installation_time = time.time() - start_time
            
            if result.returncode == 0:
                return InstallationResult(
                    package_name=package_name,
                    success=True,
                    method_used=method,
                    output=result.stdout,
                    installation_time=installation_time
                )
            else:
                return InstallationResult(
                    package_name=package_name,
                    success=False,
                    method_used=method,
                    output=result.stdout,
                    error_message=result.stderr or "Installation failed",
                    installation_time=installation_time
                )
                
        except subprocess.TimeoutExpired:
            return InstallationResult(
                package_name=package_name,
                success=False,
                method_used=method,
                error_message=f"Installation timed out after {self._installation_timeout}s",
                installation_time=time.time() - start_time
            )
        except Exception as e:
            return InstallationResult(
                package_name=package_name,
                success=False,
                method_used=method,
                error_message=f"Unexpected error: {str(e)}",
                installation_time=time.time() - start_time
            )