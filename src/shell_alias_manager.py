#!/usr/bin/env python3
"""
Shell Alias Manager - Core data models and orchestration for shell alias auto-setup.

This module provides the main orchestration for setting up shell aliases that allow
the pricing tool to be invoked from anywhere via 'priceup' command.
"""

import os
import shlex
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, List, Dict, Tuple, Any
from enum import Enum
from .shell_detection import ShellDetector
from .path_resolution import PathResolver
from .file_manipulation import FileManipulator
from .shell_alias_constants import ERROR_MESSAGES, SUCCESS_MESSAGES
import logging


class ShellType(Enum):
    """Supported shell types for alias setup."""
    ZSH = "zsh"
    UNKNOWN = "unknown"


class SetupResult(Enum):
    """Results of alias setup operations."""
    SUCCESS = "success"
    ALIAS_EXISTS = "alias_exists"
    SHELL_UNSUPPORTED = "shell_unsupported"
    FILE_WRITE_ERROR = "file_write_error"
    VALIDATION_ERROR = "validation_error"


@dataclass
class ShellConfig:
    """Configuration for shell-specific setup."""
    shell_type: ShellType
    config_file: Path
    alias_command: str
    comment_marker: str = "#"
    
    @property
    def config_exists(self) -> bool:
        """Check if the shell configuration file exists."""
        return self.config_file.exists()


class AliasSetupRequest:
    """Request parameters for alias setup."""
    
    def __init__(self, alias_name: str = "priceup", target_script_path: Optional[Path] = None, force_overwrite: bool = False):
        """Initialize alias setup request."""
        if not alias_name:
            raise ValueError("alias_name cannot be empty")
        
        self.alias_name = alias_name
        self.force_overwrite = force_overwrite
        
        # Resolve target script path
        resolved_path = target_script_path if target_script_path is not None else self._resolve_target_script_path()
        
        # Ensure target_script_path is valid
        if resolved_path is None:
            raise ValueError("Could not determine target script path")
            
        self.target_script_path: Path = resolved_path
    
    def _resolve_target_script_path(self) -> Optional[Path]:
        """Resolve the target script path using the PathResolver utility."""
        return PathResolver.resolve_target_script_path()
    
    def _find_repo_root(self, start_path: Path) -> Optional[Path]:
        """Find the repository root by looking for .git directory."""
        current = start_path.resolve()
        
        while current != current.parent:
            if (current / ".git").exists():
                return current
            current = current.parent
        
        return None


@dataclass
class AliasSetupResult:
    """Result of alias setup operation."""
    result: SetupResult
    message: str
    alias_name: str
    target_path: Optional[Path] = None
    config_file: Optional[Path] = None
    backup_created: bool = False
    
    @property
    def success(self) -> bool:
        """Check if the setup was successful."""
        return self.result == SetupResult.SUCCESS
    
    @property
    def already_exists(self) -> bool:
        """Check if alias already exists."""
        return self.result == SetupResult.ALIAS_EXISTS


class ShellAliasManager:
    """Main orchestrator for shell alias setup operations."""
    
    def __init__(self):
        """Initialize the shell alias manager."""
        self.current_shell = self._detect_shell()
    
    def setup_alias(self, request: AliasSetupRequest) -> AliasSetupResult:
        """
        Set up shell alias based on the provided request.
        
        Enhanced with comprehensive logging integration (T022).
        
        Args:
            request: Configuration for alias setup
            
        Returns:
            AliasSetupResult with operation status and details
        """
        logger = logging.getLogger(__name__)
        logger.info(f"Starting shell alias setup for '{request.alias_name}'")
        
        try:
            # Validate shell support (T020: unsupported shell error handling)
            shell_name, is_supported = ShellDetector.detect_current_shell()
            logger.info(f"Detected shell: {shell_name}, supported: {is_supported}")
            
            if not is_supported:
                logger.error(f"Unsupported shell detected: {shell_name}")
                manual_instructions = self.get_manual_setup_instructions(request.alias_name, request.target_script_path)
                detailed_message = f"{ERROR_MESSAGES['shell_unsupported']}\n\nDetected shell: {shell_name}\n{manual_instructions}"
                
                return AliasSetupResult(
                    result=SetupResult.SHELL_UNSUPPORTED,
                    message=detailed_message,
                    alias_name=request.alias_name
                )
            
            # Get shell config path
            config_path = ShellDetector.get_shell_config_path(shell_name)
            logger.info(f"Shell config path: {config_path}")
            
            if not config_path:
                logger.error("Could not determine shell configuration file path")
                return AliasSetupResult(
                    result=SetupResult.SHELL_UNSUPPORTED,
                    message="Could not determine shell configuration file",
                    alias_name=request.alias_name
                )
            
            # Validate target script
            is_valid, validation_error = PathResolver.validate_script_path(request.target_script_path)
            if not is_valid:
                return AliasSetupResult(
                    result=SetupResult.VALIDATION_ERROR,
                    message=validation_error,
                    alias_name=request.alias_name
                )
            
            # Validate file permissions (T021: permission error handling)
            is_accessible, access_error = FileManipulator.validate_file_permissions(config_path)
            if not is_accessible:
                manual_instructions = self.get_manual_setup_instructions(request.alias_name, request.target_script_path)
                detailed_message = f"Permission Error: {access_error}\n{manual_instructions}"
                
                return AliasSetupResult(
                    result=SetupResult.FILE_WRITE_ERROR,
                    message=detailed_message,
                    alias_name=request.alias_name
                )
            
            # Check if alias already exists and is current (T011-T012: idempotency validation)
            existing_alias_check = self._check_existing_alias_status(
                config_path, 
                request.alias_name, 
                request.target_script_path
            )
            
            if existing_alias_check["exists"] and existing_alias_check["is_current"] and not request.force_overwrite:
                # Alias exists and is correct - silent success (T011: silent operation)
                logger.info(f"Alias '{request.alias_name}' already exists and is current - no action needed")
                return AliasSetupResult(
                    result=SetupResult.ALIAS_EXISTS,
                    message="Alias is already configured correctly",
                    alias_name=request.alias_name,
                    target_path=request.target_script_path,
                    config_file=config_path,
                    backup_created=False
                )
            elif existing_alias_check["exists"] and not existing_alias_check["is_current"] and not request.force_overwrite:
                # Alias exists but is outdated - provide helpful message (T013: repository movement)
                current_path = existing_alias_check.get("current_path")
                if current_path and not existing_alias_check.get("path_valid", True):
                    message = f"Alias '{request.alias_name}' points to missing script: {current_path}. Use --force to update."
                else:
                    message = ERROR_MESSAGES["alias_exists"].format(alias=request.alias_name)
                
                return AliasSetupResult(
                    result=SetupResult.ALIAS_EXISTS,
                    message=message,
                    alias_name=request.alias_name,
                    config_file=config_path
                )
            
            # Update shell configuration (force overwrite since we've validated the need)
            success, backup_path, message = FileManipulator.update_shell_config(
                config_path,
                request.alias_name,
                request.target_script_path,
                force_overwrite=True  # We've already done the validation above
            )
            
            if success:
                logger.info(f"Successfully created shell alias '{request.alias_name}' pointing to {request.target_script_path}")
                return AliasSetupResult(
                    result=SetupResult.SUCCESS,
                    message=SUCCESS_MESSAGES["alias_created"].format(alias=request.alias_name),
                    alias_name=request.alias_name,
                    target_path=request.target_script_path,
                    config_file=config_path,
                    backup_created=backup_path is not None
                )
            else:
                # Check if it's an existing alias error
                if "already exists" in message:
                    return AliasSetupResult(
                        result=SetupResult.ALIAS_EXISTS,
                        message=message,
                        alias_name=request.alias_name,
                        config_file=config_path
                    )
                else:
                    return AliasSetupResult(
                        result=SetupResult.FILE_WRITE_ERROR,
                        message=message,
                        alias_name=request.alias_name
                    )
                
        except Exception as e:
            logger.error(f"Unexpected error during shell alias setup: {str(e)}", exc_info=True)
            manual_instructions = self.get_manual_setup_instructions(request.alias_name, request.target_script_path)
            detailed_message = f"Unexpected error during setup: {str(e)}\n{manual_instructions}"
            
            return AliasSetupResult(
                result=SetupResult.VALIDATION_ERROR,
                message=detailed_message,
                alias_name=request.alias_name
            )
    
    def _detect_shell(self) -> ShellConfig:
        """Detect the current shell and return appropriate configuration."""
        shell_name, is_supported = ShellDetector.detect_current_shell()
        config_path = ShellDetector.get_shell_config_path(shell_name)
        
        if is_supported and config_path:
            return ShellConfig(
                shell_type=ShellType.ZSH if shell_name == "zsh" else ShellType.UNKNOWN,
                config_file=config_path,
                alias_command="alias"
            )
        
        # Default to unknown shell
        return ShellConfig(
            shell_type=ShellType.UNKNOWN,
            config_file=Path("/dev/null"),  # Invalid path
            alias_command="unknown"
        )
    
    def _check_existing_alias_status(self, config_path: Path, alias_name: str, expected_script_path: Path) -> Dict[str, Any]:
        """
        Check if alias exists and is current with expected script path.
        
        Enhanced for T013-T015: Repository flexibility and path validation
        
        Args:
            config_path: Path to shell configuration file
            alias_name: Name of alias to check
            expected_script_path: Expected script path for the alias
            
        Returns:
            Dict with 'exists', 'is_current', and 'path_valid' boolean flags
        """
        try:
            # Read config file
            success, content, error_msg = FileManipulator.read_file_content(config_path)
            if not success:
                return {"exists": False, "is_current": False, "path_valid": False}
            
            # Extract managed section
            managed_section, _ = FileManipulator.extract_managed_section(content)
            
            if not managed_section:
                # Check for any existing alias with same name (unmanaged)
                if self._has_unmanaged_alias(content, alias_name):
                    return {"exists": True, "is_current": False, "path_valid": False}
                return {"exists": False, "is_current": False, "path_valid": True}
            
            # Extract current script path from existing alias (T014: path validation)
            current_script_path = self._extract_script_path_from_alias(managed_section, alias_name)
            
            # Validate current script path still exists (T013: detect moved repositories)
            path_valid = current_script_path is not None and current_script_path.exists()
            
            # Check if managed alias is current
            expected_command = PathResolver.create_portable_alias_command(expected_script_path, alias_name)
            is_current = self._is_alias_current(managed_section, expected_command) and path_valid
            
            return {
                "exists": True, 
                "is_current": is_current,
                "path_valid": path_valid,
                "current_path": str(current_script_path) if current_script_path else None
            }
            
        except Exception:
            return {"exists": False, "is_current": False, "path_valid": False}
    
    def _has_unmanaged_alias(self, content: str, alias_name: str) -> bool:
        """Check if there's an unmanaged alias with the given name."""
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith(f"alias {alias_name}="):
                return True
        return False
    
    def _extract_script_path_from_alias(self, managed_section: str, alias_name: str) -> Optional[Path]:
        """
        Extract the script path from an existing alias in the managed section.
        
        Args:
            managed_section: The managed alias section content
            alias_name: Name of the alias to extract path from
            
        Returns:
            Path to the script if found, None otherwise
        """
        try:
            lines = managed_section.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith(f'alias {alias_name}='):
                    # Extract path from: alias priceup='python3 /path/to/script.py'
                    # Find the part between quotes after 'python3 '
                    if 'python3 ' in line:
                        # Split on python3 and take the part after it
                        python_part = line.split('python3 ', 1)[1]
                        # Remove trailing quote and any extra characters
                        script_path_str = python_part.rstrip("'\"")
                        
                        # Handle shlex quoted paths
                        import shlex
                        try:
                            # If it's a quoted string, unquote it
                            if script_path_str.startswith("'") or script_path_str.startswith('"'):
                                script_path_str = shlex.split(script_path_str)[0]
                        except ValueError:
                            pass  # Not a properly quoted string, use as is
                        
                        return Path(script_path_str)
            
            return None
            
        except Exception:
            return None

    def _is_alias_current(self, managed_section: str, expected_command: str) -> bool:
        """
        Check if the managed alias section contains the expected command.
        
        Args:
            managed_section: The managed alias section content
            expected_command: The expected alias command
            
        Returns:
            True if the alias is current, False otherwise
        """
        try:
            # Extract just the alias command from both
            expected_alias_line = expected_command.strip()
            
            lines = managed_section.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('alias '):
                    # Normalize whitespace and compare
                    current_alias = ' '.join(line.split())
                    expected_alias = ' '.join(expected_alias_line.split())
                    
                    return current_alias == expected_alias
            
            return False
            
        except Exception:
            return False
    
    def get_manual_setup_instructions(self, alias_name: str = "priceup", script_path: Optional[Path] = None) -> str:
        """
        Generate manual setup instructions for users when automatic setup fails.
        
        Args:
            alias_name: Name of the alias to create
            script_path: Path to the target script (auto-detected if None)
            
        Returns:
            Formatted manual setup instructions
        """
        if script_path is None:
            script_path = PathResolver.resolve_target_script_path()
            
        if not script_path:
            script_path = Path.cwd() / "pricing_tool_accelerator.py"
        
        import shlex
        escaped_path = shlex.quote(str(script_path))
        
        instructions = f"""
Manual Shell Alias Setup Instructions
====================================

If automatic setup failed, you can create the alias manually:

1. Copy and paste this command into your terminal:

   echo "alias {alias_name}='python3 {escaped_path}'" >> ~/.zshrc

2. Reload your shell configuration:

   source ~/.zshrc

3. Test the alias:

   {alias_name}

Alternative method (if above doesn't work):
1. Open ~/.zshrc in a text editor:

   open -e ~/.zshrc

2. Add this line at the end of the file:

   alias {alias_name}='python3 {escaped_path}'

3. Save the file and restart Terminal

Verification:
- Run 'alias | grep {alias_name}' to verify the alias exists
- Run '{alias_name}' from any directory to test functionality
"""
        return instructions