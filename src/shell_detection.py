#!/usr/bin/env python3
"""
Shell Detection Utility - Detect current shell environment and validate support.

This module provides utilities for detecting the current shell environment,
validating shell support, and providing shell-specific configuration.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Tuple
from .shell_alias_constants import SUPPORTED_SHELLS, SHELL_CONFIG_FILES, ERROR_MESSAGES


class ShellDetector:
    """Utility class for detecting and validating shell environments."""
    
    @staticmethod
    def detect_current_shell() -> Tuple[str, bool]:
        """
        Detect the current shell environment.
        
        Returns:
            Tuple of (shell_name, is_supported)
        """
        # Check SHELL environment variable first
        shell_env = os.environ.get("SHELL", "").lower()
        
        # Extract shell name from path
        if shell_env:
            shell_name = Path(shell_env).name
            
            # Remove common shell path prefixes
            if shell_name.startswith("bash"):
                shell_name = "bash"
            elif shell_name.startswith("zsh"):
                shell_name = "zsh"
            elif shell_name.startswith("fish"):
                shell_name = "fish"
            
            is_supported = shell_name in SUPPORTED_SHELLS
            return shell_name, is_supported
        
        # Fallback methods if SHELL is not set
        
        # Check for zsh-specific environment variables
        if os.environ.get("ZSH_VERSION"):
            return "zsh", True
            
        # Check for bash-specific environment variables
        if os.environ.get("BASH_VERSION"):
            return "bash", False
            
        # Check parent process (less reliable but useful fallback)
        try:
            # This is a basic check - in a real implementation you might
            # want to use more sophisticated process detection
            import subprocess
            result = subprocess.run(
                ["ps", "-p", str(os.getppid()), "-o", "comm="],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and result.stdout.strip():
                parent_process = result.stdout.strip().lower()
                
                if "zsh" in parent_process:
                    return "zsh", True
                elif "bash" in parent_process:
                    return "bash", False
                elif "fish" in parent_process:
                    return "fish", False
                    
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            pass
        
        # If all detection methods fail, return unknown
        return "unknown", False
    
    @staticmethod
    def get_shell_config_path(shell_name: str) -> Optional[Path]:
        """
        Get the configuration file path for a given shell.
        
        Args:
            shell_name: Name of the shell (e.g., 'zsh', 'bash')
            
        Returns:
            Path to the shell configuration file, or None if unsupported
        """
        return SHELL_CONFIG_FILES.get(shell_name.lower())
    
    @staticmethod
    def validate_shell_support(shell_name: str) -> Tuple[bool, str]:
        """
        Validate if a shell is supported for alias setup.
        
        Args:
            shell_name: Name of the shell to validate
            
        Returns:
            Tuple of (is_supported, error_message)
        """
        if shell_name.lower() in SUPPORTED_SHELLS:
            return True, ""
        
        return False, ERROR_MESSAGES["shell_unsupported"]
    
    @staticmethod
    def check_config_file_accessibility(config_path: Path) -> Tuple[bool, str]:
        """
        Check if shell configuration file is accessible for reading and writing.
        
        Args:
            config_path: Path to the shell configuration file
            
        Returns:
            Tuple of (is_accessible, error_message)
        """
        try:
            # Check if parent directory exists and is writable
            parent_dir = config_path.parent
            if not parent_dir.exists():
                return False, f"Configuration directory does not exist: {parent_dir}"
            
            if not os.access(parent_dir, os.W_OK):
                return False, f"No write permission for directory: {parent_dir}"
            
            # Check file accessibility
            if config_path.exists():
                # File exists - check read/write permissions
                if not os.access(config_path, os.R_OK):
                    return False, f"No read permission for file: {config_path}"
                
                if not os.access(config_path, os.W_OK):
                    return False, f"No write permission for file: {config_path}"
            else:
                # File doesn't exist - that's okay, we'll create it
                pass
            
            return True, ""
            
        except Exception as e:
            return False, f"Error checking file accessibility: {str(e)}"
    
    @staticmethod
    def get_shell_info() -> Dict[str, str]:
        """
        Get comprehensive information about the current shell environment.
        
        Returns:
            Dictionary with shell information
        """
        shell_name, is_supported = ShellDetector.detect_current_shell()
        config_path = ShellDetector.get_shell_config_path(shell_name)
        
        info = {
            "shell_name": shell_name,
            "is_supported": str(is_supported),
            "shell_env": os.environ.get("SHELL", "not_set"),
        }
        
        if config_path:
            info["config_file"] = str(config_path)
            info["config_exists"] = str(config_path.exists())
            
            is_accessible, access_error = ShellDetector.check_config_file_accessibility(config_path)
            info["config_accessible"] = str(is_accessible)
            if access_error:
                info["access_error"] = access_error
        else:
            info["config_file"] = "unknown"
            info["config_exists"] = "false"
            info["config_accessible"] = "false"
        
        # Add shell-specific environment variables
        if shell_name == "zsh":
            info["zsh_version"] = os.environ.get("ZSH_VERSION", "not_set")
        elif shell_name == "bash":
            info["bash_version"] = os.environ.get("BASH_VERSION", "not_set")
        
        return info