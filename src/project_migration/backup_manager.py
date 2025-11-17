#!/usr/bin/env python3
"""Backup Utilities for Rollback Support.

Handles creation and management of backups for rollback capabilities.
"""

import os
import shutil
import tarfile
from datetime import datetime
from typing import List, Optional, Dict, Any
from .migration_logging import get_migration_logger


class BackupManager:
    """Manages backup creation and restoration for migration rollback."""
    
    def __init__(self, backup_directory: str = "migration_backups"):
        """Initialize backup manager.
        
        Args:
            backup_directory: Directory to store backup files
        """
        self.backup_directory = backup_directory
        self.logger = get_migration_logger()
        self.ensure_backup_directory()
        self._backup_manifest: Dict[str, Any] = {}
    
    def ensure_backup_directory(self) -> None:
        """Ensure backup directory exists."""
        if not os.path.exists(self.backup_directory):
            os.makedirs(self.backup_directory, exist_ok=True)
            self.logger.log_debug(f"Created backup directory: {self.backup_directory}")
    
    def create_project_backup(self, project_root: str, backup_name: Optional[str] = None) -> str:
        """Create complete project backup.
        
        Args:
            project_root: Root directory of project to backup
            backup_name: Optional custom backup name
            
        Returns:
            Path to created backup archive
        """
        if backup_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"project_backup_{timestamp}.tar.gz"
        
        backup_path = os.path.join(self.backup_directory, backup_name)
        
        try:
            with tarfile.open(backup_path, 'w:gz') as tar:
                # Add project files while excluding certain directories
                for root, dirs, files in os.walk(project_root):
                    # Skip backup directory itself and other temporary directories
                    dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.migration_state', 'migration_backups', 'migration_logs']]
                    
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, project_root)
                        tar.add(file_path, arcname=arcname)
            
            # Record in manifest
            self._backup_manifest[backup_name] = {
                'type': 'project_backup',
                'source': project_root,
                'created_at': datetime.now().isoformat(),
                'path': backup_path
            }
            
            self.logger.log_backup_created(backup_path, project_root)
            return backup_path
            
        except (IOError, OSError, tarfile.TarError) as e:
            error_msg = f"Failed to create project backup: {str(e)}"
            self.logger.log_error(error_msg)
            raise RuntimeError(error_msg)
    
    def create_file_backup(self, file_path: str, backup_name: Optional[str] = None) -> str:
        """Create backup of individual file.
        
        Args:
            file_path: Path to file to backup
            backup_name: Optional custom backup name
            
        Returns:
            Path to backup file
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if backup_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.basename(file_path)
            backup_name = f"{filename}.backup_{timestamp}"
        
        backup_path = os.path.join(self.backup_directory, backup_name)
        
        try:
            if os.path.isfile(file_path):
                shutil.copy2(file_path, backup_path)
            elif os.path.isdir(file_path):
                shutil.copytree(file_path, backup_path)
            else:
                raise ValueError(f"Unsupported file type: {file_path}")
            
            # Record in manifest
            self._backup_manifest[backup_name] = {
                'type': 'file_backup',
                'source': file_path,
                'created_at': datetime.now().isoformat(),
                'path': backup_path
            }
            
            self.logger.log_backup_created(backup_path, file_path)
            return backup_path
            
        except (IOError, OSError, shutil.Error) as e:
            error_msg = f"Failed to create file backup: {str(e)}"
            self.logger.log_error(error_msg)
            raise RuntimeError(error_msg)
    
    def create_configuration_backup(self, config_files: List[str]) -> str:
        """Create backup of configuration files.
        
        Args:
            config_files: List of configuration file paths
            
        Returns:
            Path to configuration backup archive
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"config_backup_{timestamp}.tar.gz"
        backup_path = os.path.join(self.backup_directory, backup_name)
        
        try:
            with tarfile.open(backup_path, 'w:gz') as tar:
                for config_file in config_files:
                    if os.path.exists(config_file):
                        arcname = os.path.basename(config_file)
                        tar.add(config_file, arcname=arcname)
                        self.logger.log_debug(f"Added to config backup: {config_file}")
            
            # Record in manifest
            self._backup_manifest[backup_name] = {
                'type': 'configuration_backup',
                'source': config_files,
                'created_at': datetime.now().isoformat(),
                'path': backup_path
            }
            
            self.logger.log_backup_created(backup_path, f"{len(config_files)} config files")
            return backup_path
            
        except (IOError, OSError, tarfile.TarError) as e:
            error_msg = f"Failed to create configuration backup: {str(e)}"
            self.logger.log_error(error_msg)
            raise RuntimeError(error_msg)
    
    def restore_project_backup(self, backup_path: str, restore_location: str) -> bool:
        """Restore project from backup.
        
        Args:
            backup_path: Path to backup archive
            restore_location: Location to restore to
            
        Returns:
            True if restoration successful
        """
        if not os.path.exists(backup_path):
            self.logger.log_error(f"Backup file not found: {backup_path}")
            return False
        
        try:
            # Create restore location if it doesn't exist
            if not os.path.exists(restore_location):
                os.makedirs(restore_location, exist_ok=True)
            
            with tarfile.open(backup_path, 'r:gz') as tar:
                tar.extractall(path=restore_location)
            
            self.logger.log_operation("Project restore", True, f"From: {backup_path}")
            return True
            
        except (IOError, OSError, tarfile.TarError) as e:
            self.logger.log_error(f"Failed to restore project backup: {str(e)}")
            return False
    
    def restore_file_backup(self, backup_path: str, restore_path: str) -> bool:
        """Restore file from backup.
        
        Args:
            backup_path: Path to backup file
            restore_path: Path to restore file to
            
        Returns:
            True if restoration successful
        """
        if not os.path.exists(backup_path):
            self.logger.log_error(f"Backup file not found: {backup_path}")
            return False
        
        try:
            # Ensure parent directory exists
            parent_dir = os.path.dirname(restore_path)
            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)
            
            if os.path.isfile(backup_path):
                shutil.copy2(backup_path, restore_path)
            elif os.path.isdir(backup_path):
                if os.path.exists(restore_path):
                    shutil.rmtree(restore_path)
                shutil.copytree(backup_path, restore_path)
            
            self.logger.log_operation("File restore", True, f"From: {backup_path}")
            return True
            
        except (IOError, OSError, shutil.Error) as e:
            self.logger.log_error(f"Failed to restore file backup: {str(e)}")
            return False
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """List all available backups.
        
        Returns:
            List of backup information dictionaries
        """
        backups = []
        for backup_name, info in self._backup_manifest.items():
            if os.path.exists(info['path']):
                backups.append({
                    'name': backup_name,
                    'type': info['type'],
                    'source': info['source'],
                    'created_at': info['created_at'],
                    'path': info['path'],
                    'size_mb': os.path.getsize(info['path']) / (1024 * 1024)
                })
        return backups
    
    def cleanup_old_backups(self, keep_count: int = 5) -> None:
        """Clean up old backup files.
        
        Args:
            keep_count: Number of recent backups to keep
        """
        backups = self.list_backups()
        if len(backups) <= keep_count:
            return
        
        # Sort by creation time
        backups.sort(key=lambda x: x['created_at'], reverse=True)
        
        # Remove old backups
        for backup in backups[keep_count:]:
            try:
                os.remove(backup['path'])
                del self._backup_manifest[backup['name']]
                self.logger.log_debug(f"Cleaned up old backup: {backup['name']}")
            except (IOError, OSError) as e:
                self.logger.log_warning(f"Failed to cleanup backup {backup['name']}: {str(e)}")
    
    def save_manifest(self) -> None:
        """Save backup manifest to file."""
        import json
        
        manifest_path = os.path.join(self.backup_directory, 'backup_manifest.json')
        try:
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(self._backup_manifest, f, indent=2)
        except (IOError, OSError) as e:
            self.logger.log_warning(f"Failed to save backup manifest: {str(e)}")
    
    def load_manifest(self) -> None:
        """Load backup manifest from file."""
        import json
        
        manifest_path = os.path.join(self.backup_directory, 'backup_manifest.json')
        if os.path.exists(manifest_path):
            try:
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    self._backup_manifest = json.load(f)
            except (IOError, OSError, json.JSONDecodeError) as e:
                self.logger.log_warning(f"Failed to load backup manifest: {str(e)}")
                self._backup_manifest = {}
    
    def verify_backup_integrity(self, backup_path: str) -> bool:
        """Verify backup file integrity.
        
        Args:
            backup_path: Path to backup file to verify
            
        Returns:
            True if backup is valid
        """
        if not os.path.exists(backup_path):
            return False
        
        try:
            if backup_path.endswith('.tar.gz'):
                with tarfile.open(backup_path, 'r:gz') as tar:
                    # Try to list contents to verify integrity
                    tar.getnames()
                return True
            else:
                # For individual files, just check if readable
                with open(backup_path, 'rb') as f:
                    f.read(1024)  # Read small chunk to verify
                return True
                
        except (IOError, OSError, tarfile.TarError):
            return False