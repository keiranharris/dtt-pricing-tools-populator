#!/usr/bin/env python3
"""File Renaming Data Model.

Tracks individual file and directory renaming operations with integrity verification.
"""

import hashlib
import os
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class FileRenaming:
    """Tracks individual file and directory renaming operations.
    
    Attributes:
        old_path: Original file/directory path
        new_path: Target file/directory path
        operation_type: Type: "FILE_RENAME", "DIRECTORY_RENAME", "CONTENT_UPDATE"
        content_changes: List of text replacements made
        backup_path: Location of backup before changes
        checksum_before: File checksum before changes
        checksum_after: File checksum after changes
    """
    
    old_path: str
    new_path: str
    operation_type: str
    content_changes: List[str] = field(default_factory=list)
    backup_path: str = ""
    checksum_before: str = ""
    checksum_after: str = ""
    
    # State tracking
    _state: str = "PENDING"
    _error_message: Optional[str] = None
    
    def __post_init__(self):
        """Validate operation type on initialization."""
        valid_types = ["FILE_RENAME", "DIRECTORY_RENAME", "CONTENT_UPDATE"]
        if self.operation_type not in valid_types:
            raise ValueError(f"Invalid operation type: {self.operation_type}")
    
    @property
    def state(self) -> str:
        """Current operation state."""
        return self._state
    
    def calculate_checksum(self, file_path: str) -> str:
        """Calculate SHA256 checksum of a file.
        
        Args:
            file_path: Path to file to checksum
            
        Returns:
            SHA256 hexadecimal checksum
        """
        if not os.path.isfile(file_path):
            return ""
        
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest()
        except (IOError, OSError):
            return ""
    
    def create_backup(self, backup_location: str) -> bool:
        """Create backup of file before renaming.
        
        Args:
            backup_location: Directory to store backup
            
        Returns:
            True if backup created successfully
        """
        if not os.path.exists(self.old_path):
            self._error_message = f"Source path does not exist: {self.old_path}"
            return False
        
        try:
            import shutil
            backup_name = os.path.basename(self.old_path) + ".backup"
            self.backup_path = os.path.join(backup_location, backup_name)
            
            if os.path.isfile(self.old_path):
                shutil.copy2(self.old_path, self.backup_path)
                self.checksum_before = self.calculate_checksum(self.old_path)
            elif os.path.isdir(self.old_path):
                shutil.copytree(self.old_path, self.backup_path)
            
            return True
            
        except (IOError, OSError, shutil.Error) as e:
            self._error_message = f"Backup creation failed: {str(e)}"
            return False
    
    def validate_rename_target(self) -> bool:
        """Validate that rename target path is available.
        
        Returns:
            True if target path doesn't conflict with existing files
        """
        if os.path.exists(self.new_path):
            self._error_message = f"Target path already exists: {self.new_path}"
            return False
        
        # Check parent directory exists
        parent_dir = os.path.dirname(self.new_path)
        if parent_dir and not os.path.exists(parent_dir):
            try:
                os.makedirs(parent_dir, exist_ok=True)
            except (IOError, OSError) as e:
                self._error_message = f"Cannot create parent directory: {str(e)}"
                return False
        
        return True
    
    def execute_rename(self) -> bool:
        """Execute the file/directory rename operation.
        
        Returns:
            True if rename successful
        """
        if not self.validate_rename_target():
            self._state = "FAILED"
            return False
        
        try:
            os.rename(self.old_path, self.new_path)
            self._state = "COMPLETED"
            
            # Calculate post-rename checksum for files
            if os.path.isfile(self.new_path) and self.operation_type == "FILE_RENAME":
                self.checksum_after = self.calculate_checksum(self.new_path)
            
            return True
            
        except (IOError, OSError) as e:
            self._error_message = f"Rename operation failed: {str(e)}"
            self._state = "FAILED"
            return False
    
    def verify_integrity(self) -> bool:
        """Verify file integrity after rename operation.
        
        Returns:
            True if file integrity is preserved
        """
        if self.operation_type == "DIRECTORY_RENAME":
            # For directories, just check existence
            return os.path.isdir(self.new_path)
        
        if self.operation_type == "FILE_RENAME":
            # For file renames, checksums should match
            if self.checksum_before and self.checksum_after:
                return self.checksum_before == self.checksum_after
            else:
                # Recalculate if missing
                self.checksum_after = self.calculate_checksum(self.new_path)
                return self.checksum_before == self.checksum_after
        
        if self.operation_type == "CONTENT_UPDATE":
            # For content updates, checksums will differ but file should exist
            return os.path.isfile(self.new_path) and bool(self.checksum_after)
        
        return False
    
    def add_content_change(self, change_description: str) -> None:
        """Add description of content change made.
        
        Args:
            change_description: Description of the text replacement
        """
        self.content_changes.append(change_description)
    
    def rollback(self) -> bool:
        """Rollback the rename operation using backup.
        
        Returns:
            True if rollback successful
        """
        if not self.backup_path or not os.path.exists(self.backup_path):
            self._error_message = "No backup available for rollback"
            return False
        
        try:
            import shutil
            
            # Remove current file/directory if it exists
            if os.path.exists(self.new_path):
                if os.path.isfile(self.new_path):
                    os.remove(self.new_path)
                else:
                    shutil.rmtree(self.new_path)
            
            # Restore from backup
            if os.path.isfile(self.backup_path):
                shutil.copy2(self.backup_path, self.old_path)
            else:
                shutil.copytree(self.backup_path, self.old_path)
            
            self._state = "ROLLEDBACK"
            return True
            
        except (IOError, OSError, shutil.Error) as e:
            self._error_message = f"Rollback failed: {str(e)}"
            return False
    
    def get_error_message(self) -> Optional[str]:
        """Get error message if operation failed."""
        return self._error_message