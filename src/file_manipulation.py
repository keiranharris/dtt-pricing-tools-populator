#!/usr/bin/env python3
"""
File Manipulation Utility - Safe file operations for shell configuration.

This module provides safe and reliable file operations for managing shell
configuration files, including backup creation, content modification,
and atomic writes.
"""

import os
import shutil
from pathlib import Path
from typing import Optional, List, Tuple
from datetime import datetime
from .shell_alias_constants import (
    ALIAS_START_MARKER,
    ALIAS_END_MARKER,
    BACKUP_EXTENSION,
    MAX_BACKUP_FILES,
    ERROR_MESSAGES
)


class FileManipulator:
    """Utility class for safe file manipulation operations."""
    
    @staticmethod
    def create_backup(file_path: Path, backup_suffix: Optional[str] = None) -> Tuple[bool, Optional[Path], str]:
        """
        Create a backup of the specified file.
        
        Args:
            file_path: Path to the file to backup
            backup_suffix: Optional suffix for backup file
            
        Returns:
            Tuple of (success, backup_path, message)
        """
        try:
            if not file_path.exists():
                return True, None, "No backup needed - file does not exist"
            
            # Generate backup filename
            if backup_suffix:
                backup_path = file_path.with_suffix(file_path.suffix + f".{backup_suffix}")
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = file_path.with_suffix(file_path.suffix + f"{BACKUP_EXTENSION}_{timestamp}")
            
            # Create backup
            shutil.copy2(file_path, backup_path)
            
            # Clean up old backups
            FileManipulator._cleanup_old_backups(file_path)
            
            return True, backup_path, f"Backup created: {backup_path}"
            
        except Exception as e:
            return False, None, f"Failed to create backup: {str(e)}"
    
    @staticmethod
    def _cleanup_old_backups(original_file: Path) -> None:
        """Clean up old backup files, keeping only the most recent ones."""
        try:
            parent_dir = original_file.parent
            file_stem = original_file.stem
            
            # Find all backup files for this original file
            backup_files = []
            for file_path in parent_dir.glob(f"{file_stem}*{BACKUP_EXTENSION}*"):
                if file_path != original_file:
                    backup_files.append(file_path)
            
            # Sort by modification time (newest first)
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Remove excess backup files
            for old_backup in backup_files[MAX_BACKUP_FILES:]:
                try:
                    old_backup.unlink()
                except Exception:
                    pass  # Ignore errors removing old backups
                    
        except Exception:
            pass  # Ignore cleanup errors
    
    @staticmethod
    def read_file_content(file_path: Path) -> Tuple[bool, str, str]:
        """
        Safely read file content with error handling.
        
        Args:
            file_path: Path to the file to read
            
        Returns:
            Tuple of (success, content, error_message)
        """
        try:
            if not file_path.exists():
                return True, "", ""
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return True, content, ""
            
        except Exception as e:
            return False, "", f"Failed to read file {file_path}: {str(e)}"
    
    @staticmethod
    def write_file_content(file_path: Path, content: str, create_backup: bool = True) -> Tuple[bool, Optional[Path], str]:
        """
        Safely write content to file with optional backup.
        
        Args:
            file_path: Path to the file to write
            content: Content to write to the file
            create_backup: Whether to create a backup before writing
            
        Returns:
            Tuple of (success, backup_path, message)
        """
        backup_path = None
        
        try:
            # Create backup if requested and file exists
            if create_backup and file_path.exists():
                success, backup_path, backup_msg = FileManipulator.create_backup(file_path)
                if not success:
                    return False, None, backup_msg
            
            # Ensure parent directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write content atomically using a temporary file
            temp_path = file_path.with_suffix(file_path.suffix + ".tmp")
            
            with open(temp_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Atomic move
            temp_path.replace(file_path)
            
            return True, backup_path, "File written successfully"
            
        except Exception as e:
            # Clean up temporary file if it exists
            temp_path = file_path.with_suffix(file_path.suffix + ".tmp")
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except Exception:
                    pass
            
            return False, backup_path, f"Failed to write file: {str(e)}"
    
    @staticmethod
    def extract_managed_section(content: str) -> Tuple[Optional[str], str]:
        """
        Extract the managed alias section from file content.
        
        Args:
            content: File content to analyze
            
        Returns:
            Tuple of (managed_section, content_without_section)
        """
        lines = content.split('\n')
        managed_section_lines = []
        filtered_lines = []
        
        in_managed_section = False
        
        for line in lines:
            if ALIAS_START_MARKER in line:
                in_managed_section = True
                managed_section_lines.append(line)
            elif ALIAS_END_MARKER in line:
                managed_section_lines.append(line)
                in_managed_section = False
            elif in_managed_section:
                managed_section_lines.append(line)
            else:
                filtered_lines.append(line)
        
        if managed_section_lines:
            managed_section = '\n'.join(managed_section_lines)
            content_without_section = '\n'.join(filtered_lines)
            return managed_section, content_without_section
        
        return None, content
    
    @staticmethod
    def create_managed_alias_section(alias_name: str, script_path: Path) -> str:
        """
        Create a managed alias section with proper formatting.
        
        Args:
            alias_name: Name of the alias to create
            script_path: Path to the target script
            
        Returns:
            Formatted alias section string
        """
        import shlex
        
        escaped_script_path = shlex.quote(str(script_path))
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return f"""
{ALIAS_START_MARKER} -----------------------------------
# This allows running '{alias_name}' from anywhere to access the pricing tool (Generated on: {timestamp})
alias {alias_name}='python3 {escaped_script_path}'
{ALIAS_END_MARKER} -------------------------------------"""
    
    @staticmethod
    def update_shell_config(
        config_path: Path, 
        alias_name: str, 
        script_path: Path,
        force_overwrite: bool = False
    ) -> Tuple[bool, Optional[Path], str]:
        """
        Update shell configuration file with the new alias.
        
        Args:
            config_path: Path to the shell configuration file
            alias_name: Name of the alias to create
            script_path: Path to the target script
            force_overwrite: Whether to overwrite existing alias
            
        Returns:
            Tuple of (success, backup_path, message)
        """
        try:
            # Read existing content
            success, existing_content, error_msg = FileManipulator.read_file_content(config_path)
            if not success:
                return False, None, error_msg
            
            # Check for existing alias (if not forcing overwrite)
            if not force_overwrite and FileManipulator._check_for_existing_alias(existing_content, alias_name):
                return False, None, ERROR_MESSAGES["alias_exists"].format(alias=alias_name)
            
            # Extract managed section
            managed_section, content_without_section = FileManipulator.extract_managed_section(existing_content)
            
            # Create new managed section
            new_managed_section = FileManipulator.create_managed_alias_section(alias_name, script_path)
            
            # Combine content
            if content_without_section.strip():
                new_content = content_without_section.rstrip() + new_managed_section + '\n'
            else:
                new_content = new_managed_section.lstrip() + '\n'
            
            # Write updated content
            success, backup_path, write_msg = FileManipulator.write_file_content(
                config_path, new_content, create_backup=True
            )
            
            if success:
                return True, backup_path, f"Successfully updated {config_path}"
            else:
                return False, backup_path, write_msg
            
        except Exception as e:
            return False, None, f"Failed to update shell config: {str(e)}"
    
    @staticmethod
    def _check_for_existing_alias(content: str, alias_name: str) -> bool:
        """
        Check if an alias with the given name already exists in the content.
        
        Args:
            content: File content to check
            alias_name: Alias name to search for
            
        Returns:
            True if alias exists, False otherwise
        """
        # Check for our managed section first
        if ALIAS_START_MARKER in content and ALIAS_END_MARKER in content:
            return True
        
        # Check for any existing alias with the same name
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith(f"alias {alias_name}="):
                return True
        
        return False
    
    @staticmethod
    def validate_file_permissions(file_path: Path) -> Tuple[bool, str]:
        """
        Validate that we have appropriate permissions for file operations.
        
        Args:
            file_path: Path to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            parent_dir = file_path.parent
            
            # Check parent directory exists and is writable
            if not parent_dir.exists():
                return False, f"Parent directory does not exist: {parent_dir}"
            
            if not os.access(parent_dir, os.W_OK):
                return False, f"No write permission for directory: {parent_dir}"
            
            # If file exists, check read/write permissions
            if file_path.exists():
                if not os.access(file_path, os.R_OK):
                    return False, f"No read permission for file: {file_path}"
                
                if not os.access(file_path, os.W_OK):
                    return False, f"No write permission for file: {file_path}"
            
            return True, ""
            
        except Exception as e:
            return False, f"Error validating permissions: {str(e)}"
    
    @staticmethod
    def get_file_info(file_path: Path) -> dict:
        """
        Get comprehensive information about a file for debugging.
        
        Args:
            file_path: Path to analyze
            
        Returns:
            Dictionary with file information
        """
        info = {
            "path": str(file_path),
            "exists": file_path.exists(),
        }
        
        try:
            if file_path.exists():
                stat = file_path.stat()
                info.update({
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "readable": os.access(file_path, os.R_OK),
                    "writable": os.access(file_path, os.W_OK),
                    "is_file": file_path.is_file(),
                    "is_dir": file_path.is_dir(),
                })
                
                # Check for managed section
                success, content, _ = FileManipulator.read_file_content(file_path)
                if success:
                    info["has_managed_section"] = ALIAS_START_MARKER in content and ALIAS_END_MARKER in content
                    info["line_count"] = len(content.split('\n'))
                
            else:
                parent_dir = file_path.parent
                info.update({
                    "parent_exists": parent_dir.exists(),
                    "parent_writable": os.access(parent_dir, os.W_OK) if parent_dir.exists() else False,
                })
                
        except Exception as e:
            info["error"] = str(e)
        
        return info