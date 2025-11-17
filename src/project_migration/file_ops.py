#!/usr/bin/env python3
"""File Operations for Project Migration.

Handles file and directory renaming operations with backup and integrity verification.
"""

import os
import shutil
import re
from typing import List, Dict, Any, Optional
from .file_renaming import FileRenaming
from .migration_logging import get_migration_logger


class FileOperations:
    """Handles file and directory operations for project migration."""
    
    def __init__(self, backup_directory: str = "migration_backups"):
        """Initialize file operations manager.
        
        Args:
            backup_directory: Directory for backup files
        """
        self.backup_directory = backup_directory
        self.logger = get_migration_logger()
        self.ensure_backup_directory()
    
    def ensure_backup_directory(self) -> None:
        """Ensure backup directory exists."""
        if not os.path.exists(self.backup_directory):
            os.makedirs(self.backup_directory, exist_ok=True)
    
    def rename_main_application_file(self, old_name: str = "pricing_tool_accelerator.py", 
                                   new_name: str = "priceup.py") -> FileRenaming:
        """Rename main application file.
        
        Args:
            old_name: Current filename
            new_name: Target filename
            
        Returns:
            FileRenaming object with operation result
        """
        old_path = os.path.abspath(old_name)
        new_path = os.path.abspath(new_name)
        
        renaming = FileRenaming(old_path, new_path, "FILE_RENAME")
        
        if not os.path.exists(old_path):
            renaming._state = "FAILED"
            renaming._error_message = f"Source file not found: {old_path}"
            return renaming
        
        try:
            # Create backup
            if renaming.create_backup(self.backup_directory):
                # Execute rename
                if renaming.execute_rename():
                    self.logger.log_file_operation("RENAME", old_path, new_path, True)
                    renaming.verify_integrity()
                else:
                    self.logger.log_file_operation("RENAME", old_path, new_path, False)
            
        except Exception as e:
            renaming._state = "FAILED"
            renaming._error_message = f"Rename failed: {str(e)}"
            self.logger.log_error(f"File rename failed: {str(e)}", e)
        
        return renaming
    
    def update_local_directory_structure(self, old_project_name: str, new_project_name: str) -> List[FileRenaming]:
        """Update local directory structure to reflect new project name.
        
        Args:
            old_project_name: Original project name
            new_project_name: New project name
            
        Returns:
            List of FileRenaming objects for each operation
        """
        renamings = []
        
        # This would typically rename the project directory itself
        # For safety in the current implementation, we'll just log the intent
        self.logger.log_operation("Directory structure update", True, 
                                f"Would rename {old_project_name} → {new_project_name}")
        
        # In a real migration, you might rename:
        # - The root project directory
        # - Any subdirectories with the old project name
        # - Configuration directories
        
        return renamings
    
    def get_files_to_update(self, root_dir: str, old_name: str) -> List[str]:
        """Get list of files that need content updates.
        
        Args:
            root_dir: Root directory to search
            old_name: Old project name to search for
            
        Returns:
            List of file paths that contain the old name
        """
        files_to_update = []
        
        # File patterns to include
        include_patterns = ['.py', '.md', '.txt', '.json', '.yaml', '.yml', '.sh']
        
        # Directories to exclude
        exclude_dirs = {'.git', '__pycache__', '.pytest_cache', 'node_modules', 
                       '.migration_state', 'migration_backups', 'migration_logs'}
        
        for root, dirs, files in os.walk(root_dir):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                # Check if file has relevant extension
                if any(file.endswith(ext) for ext in include_patterns):
                    file_path = os.path.join(root, file)
                    
                    try:
                        # Check if file contains old project name
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            if old_name in content:
                                files_to_update.append(file_path)
                    except (IOError, OSError):
                        # Skip files that can't be read
                        continue
        
        return files_to_update
    
    def update_file_content(self, file_path: str, old_name: str, new_name: str) -> FileRenaming:
        """Update file content by replacing old project name with new name.
        
        Args:
            file_path: Path to file to update
            old_name: Old project name
            new_name: New project name
            
        Returns:
            FileRenaming object with operation result
        """
        renaming = FileRenaming(file_path, file_path, "CONTENT_UPDATE")
        
        try:
            # Create backup
            if not renaming.create_backup(self.backup_directory):
                return renaming
            
            # Read current content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Track changes made
            changes_made = []
            
            # Replace various forms of the project name
            replacements = [
                (old_name, new_name),  # Direct replacement
                (old_name.replace('-', '_'), new_name.replace('-', '_')),  # Underscore version
                (old_name.replace('-', ''), new_name.replace('-', '')),  # No separator version
            ]
            
            updated_content = content
            for old_pattern, new_pattern in replacements:
                if old_pattern in updated_content:
                    updated_content = updated_content.replace(old_pattern, new_pattern)
                    changes_made.append(f"{old_pattern} → {new_pattern}")
            
            # Only write if changes were made
            if updated_content != content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                
                renaming.checksum_after = renaming.calculate_checksum(file_path)
                renaming._state = "COMPLETED"
                
                for change in changes_made:
                    renaming.add_content_change(change)
                
                self.logger.log_file_operation("CONTENT_UPDATE", file_path, file_path, True)
                self.logger.log_debug(f"Content changes: {', '.join(changes_made)}")
            else:
                # No changes needed
                renaming._state = "COMPLETED"
                self.logger.log_debug(f"No updates needed for {file_path}")
        
        except Exception as e:
            renaming._state = "FAILED"
            renaming._error_message = f"Content update failed: {str(e)}"
            self.logger.log_error(f"Content update failed for {file_path}: {str(e)}", e)
        
        return renaming
    
    def update_all_project_references(self, root_dir: str, old_name: str, new_name: str) -> List[FileRenaming]:
        """Update all project references in files.
        
        Args:
            root_dir: Root directory to process
            old_name: Old project name
            new_name: New project name
            
        Returns:
            List of FileRenaming objects for each file updated
        """
        results = []
        
        self.logger.log_phase_start("content_updates", {
            "root_directory": root_dir,
            "old_name": old_name,
            "new_name": new_name
        })
        
        # Get files that need updating
        files_to_update = self.get_files_to_update(root_dir, old_name)
        
        self.logger.log_operation("File scan", True, f"Found {len(files_to_update)} files to update")
        
        # Update each file
        for file_path in files_to_update:
            renaming = self.update_file_content(file_path, old_name, new_name)
            results.append(renaming)
        
        # Summary
        successful = sum(1 for r in results if r.state == "COMPLETED")
        failed = sum(1 for r in results if r.state == "FAILED")
        
        self.logger.log_phase_complete("content_updates", failed == 0, {
            "total_files": len(results),
            "successful": successful,
            "failed": failed
        })
        
        return results
    
    def rollback_file_operations(self, renamings: List[FileRenaming]) -> bool:
        """Rollback file operations using backups.
        
        Args:
            renamings: List of FileRenaming objects to rollback
            
        Returns:
            True if all rollbacks successful
        """
        success_count = 0
        
        for renaming in renamings:
            if renaming.rollback():
                success_count += 1
                self.logger.log_rollback_operation(f"File rollback", True, renaming.old_path)
            else:
                self.logger.log_rollback_operation(f"File rollback", False, 
                                                 f"{renaming.old_path}: {renaming.get_error_message()}")
        
        all_successful = success_count == len(renamings)
        self.logger.log_operation("Bulk file rollback", all_successful, 
                                f"{success_count}/{len(renamings)} successful")
        
        return all_successful