#!/usr/bin/env python3
"""User Configuration Data Model.

Tracks individual user configuration updates during project migration.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class UserConfiguration:
    """Tracks individual user configuration updates.
    
    Attributes:
        user_identifier: User name or ID
        config_file_path: Path to user's configuration file
        old_onedrive_path: Original OneDrive path in config
        new_onedrive_path: Updated OneDrive path in config
        shell_alias_status: Status of shell alias ("PRESERVED", "UPDATED", "MISSING")
        migration_completed: Whether user migration is complete
        backup_created: Whether configuration backup exists
    """
    
    user_identifier: str
    config_file_path: str
    old_onedrive_path: str
    new_onedrive_path: str
    shell_alias_status: str = "MISSING"
    migration_completed: bool = False
    backup_created: bool = False
    
    # State tracking
    _state: str = "DETECTED"
    _backup_path: str = ""
    _error_message: Optional[str] = None
    
    def __post_init__(self):
        """Validate shell alias status on initialization."""
        valid_statuses = ["PRESERVED", "UPDATED", "MISSING"]
        if self.shell_alias_status not in valid_statuses:
            raise ValueError(f"Invalid shell alias status: {self.shell_alias_status}")
    
    @property
    def state(self) -> str:
        """Current migration state."""
        return self._state
    
    @property
    def backup_path(self) -> str:
        """Configuration backup file path."""
        return self._backup_path
    
    def create_backup(self) -> bool:
        """Create backup of user configuration.
        
        Returns:
            True if backup created successfully
        """
        import os
        import shutil
        from datetime import datetime
        
        if not os.path.exists(self.config_file_path):
            # Config file doesn't exist, no backup needed
            self.backup_created = True
            self._state = "BACKED_UP"
            return True
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{os.path.basename(self.config_file_path)}.backup_{timestamp}"
            backup_dir = os.path.dirname(self.config_file_path)
            self._backup_path = os.path.join(backup_dir, backup_name)
            
            shutil.copy2(self.config_file_path, self._backup_path)
            self.backup_created = True
            self._state = "BACKED_UP"
            return True
            
        except (IOError, OSError) as e:
            self._error_message = f"Backup creation failed: {str(e)}"
            return False
    
    def update_onedrive_path(self) -> bool:
        """Update OneDrive path in user configuration.
        
        Returns:
            True if update successful
        """
        import os
        
        if not os.path.exists(self.config_file_path):
            # No config file exists, create one with new path
            try:
                self._create_new_config_file()
                self._state = "UPDATED"
                return True
            except Exception as e:
                self._error_message = f"Config creation failed: {str(e)}"
                return False
        
        try:
            # Read current config
            with open(self.config_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Replace old OneDrive path with new path
            updated_content = content.replace(self.old_onedrive_path, self.new_onedrive_path)
            
            # Write updated config
            with open(self.config_file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            self._state = "UPDATED"
            return True
            
        except (IOError, OSError) as e:
            self._error_message = f"OneDrive path update failed: {str(e)}"
            return False
    
    def _create_new_config_file(self) -> None:
        """Create new configuration file with updated OneDrive path."""
        import os
        import json
        
        # Ensure parent directory exists
        parent_dir = os.path.dirname(self.config_file_path)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)
        
        # Create basic config with new OneDrive path
        config_data = {
            "onedrive_path": self.new_onedrive_path,
            "project_name": "priceup",
            "created_by_migration": True
        }
        
        with open(self.config_file_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2)
    
    def validate_configuration(self) -> bool:
        """Validate that configuration update was successful.
        
        Returns:
            True if configuration contains new OneDrive path
        """
        import os
        
        if not os.path.exists(self.config_file_path):
            return False
        
        try:
            with open(self.config_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if new OneDrive path is present and old path is removed
            has_new_path = self.new_onedrive_path in content
            has_old_path = self.old_onedrive_path in content
            
            is_valid = has_new_path and not has_old_path
            
            if is_valid:
                self._state = "VALIDATED" 
                self.migration_completed = True
            
            return is_valid
            
        except (IOError, OSError) as e:
            self._error_message = f"Configuration validation failed: {str(e)}"
            return False
    
    def update_shell_alias_status(self, status: str) -> None:
        """Update shell alias status.
        
        Args:
            status: New status ("PRESERVED", "UPDATED", "MISSING")
        """
        valid_statuses = ["PRESERVED", "UPDATED", "MISSING"]
        if status not in valid_statuses:
            raise ValueError(f"Invalid shell alias status: {status}")
        
        self.shell_alias_status = status
    
    def rollback_configuration(self) -> bool:
        """Rollback configuration changes using backup.
        
        Returns:
            True if rollback successful
        """
        import os
        import shutil
        
        if not self._backup_path or not os.path.exists(self._backup_path):
            self._error_message = "No backup available for rollback"
            return False
        
        try:
            shutil.copy2(self._backup_path, self.config_file_path)
            self._state = "ROLLEDBACK"
            self.migration_completed = False
            return True
            
        except (IOError, OSError) as e:
            self._error_message = f"Configuration rollback failed: {str(e)}"
            return False
    
    def cleanup_backup(self) -> bool:
        """Clean up backup file after successful migration.
        
        Returns:
            True if cleanup successful
        """
        import os
        
        if not self._backup_path or not os.path.exists(self._backup_path):
            return True  # Nothing to clean up
        
        try:
            os.remove(self._backup_path)
            return True
        except (IOError, OSError):
            return False  # Non-critical failure
    
    def get_error_message(self) -> Optional[str]:
        """Get error message if migration failed."""
        return self._error_message
    
    def is_migration_successful(self) -> bool:
        """Check if user migration completed successfully."""
        return (self.migration_completed and 
                self._state in ["VALIDATED"] and
                self.shell_alias_status in ["PRESERVED", "UPDATED"])