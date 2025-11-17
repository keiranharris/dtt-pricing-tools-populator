#!/usr/bin/env python3
"""Migration State Persistence Utilities.

Handles saving and loading migration state for recovery and resumption.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
from json import JSONDecodeError
from .migration_context import MigrationContext


class StateManager:
    """Manages persistence and recovery of migration state."""
    
    def __init__(self, state_directory: str = ".migration_state"):
        """Initialize state manager.
        
        Args:
            state_directory: Directory to store state files
        """
        self.state_directory = state_directory
        self.ensure_state_directory()
    
    def ensure_state_directory(self) -> None:
        """Ensure state directory exists."""
        if not os.path.exists(self.state_directory):
            os.makedirs(self.state_directory, exist_ok=True)
    
    def save_migration_context(self, context: MigrationContext) -> bool:
        """Save migration context to persistent storage.
        
        Args:
            context: Migration context to save
            
        Returns:
            True if save successful
        """
        try:
            state_data = {
                'old_project_name': context.old_project_name,
                'new_project_name': context.new_project_name,
                'old_onedrive_folder': context.old_onedrive_folder,
                'new_onedrive_folder': context.new_onedrive_folder,
                'github_repository_url': context.github_repository_url,
                'migration_timestamp': context.migration_timestamp.isoformat() if context.migration_timestamp else None,
                'backup_created': context.backup_created,
                'phase_status': context.phase_status,
                'saved_at': datetime.now().isoformat()
            }
            
            state_file = os.path.join(self.state_directory, 'migration_context.json')
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, indent=2)
            
            return True
            
        except (IOError, OSError, JSONDecodeError) as e:
            print(f"Failed to save migration context: {e}")
            return False
    
    def load_migration_context(self) -> Optional[MigrationContext]:
        """Load migration context from persistent storage.
        
        Returns:
            Migration context if found, None otherwise
        """
        state_file = os.path.join(self.state_directory, 'migration_context.json')
        
        if not os.path.exists(state_file):
            return None
        
        try:
            with open(state_file, 'r', encoding='utf-8') as f:
                state_data = json.load(f)
            
            # Reconstruct migration context
            context = MigrationContext(
                old_project_name=state_data['old_project_name'],
                new_project_name=state_data['new_project_name'],
                old_onedrive_folder=state_data['old_onedrive_folder'],
                new_onedrive_folder=state_data['new_onedrive_folder'],
                github_repository_url=state_data.get('github_repository_url', ''),
                backup_created=state_data.get('backup_created', False)
            )
            
            # Restore migration timestamp if available
            if state_data.get('migration_timestamp'):
                context.migration_timestamp = datetime.fromisoformat(state_data['migration_timestamp'])
            
            # Restore phase status
            if state_data.get('phase_status'):
                context.phase_status = state_data['phase_status']
            
            return context
            
        except (IOError, OSError, JSONDecodeError, KeyError) as e:
            print(f"Failed to load migration context: {e}")
            return None
    
    def save_phase_progress(self, phase_name: str, progress_data: Dict[str, Any]) -> bool:
        """Save progress data for a specific migration phase.
        
        Args:
            phase_name: Name of the migration phase
            progress_data: Progress data to save
            
        Returns:
            True if save successful
        """
        try:
            progress_data['saved_at'] = datetime.now().isoformat()
            
            phase_file = os.path.join(self.state_directory, f'{phase_name}_progress.json')
            with open(phase_file, 'w', encoding='utf-8') as f:
                json.dump(progress_data, f, indent=2)
            
            return True
            
        except (IOError, OSError, JSONDecodeError) as e:
            print(f"Failed to save {phase_name} progress: {e}")
            return False
    
    def load_phase_progress(self, phase_name: str) -> Optional[Dict[str, Any]]:
        """Load progress data for a specific migration phase.
        
        Args:
            phase_name: Name of the migration phase
            
        Returns:
            Progress data if found, None otherwise
        """
        phase_file = os.path.join(self.state_directory, f'{phase_name}_progress.json')
        
        if not os.path.exists(phase_file):
            return None
        
        try:
            with open(phase_file, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except (IOError, OSError, JSONDecodeError) as e:
            print(f"Failed to load {phase_name} progress: {e}")
            return None
    
    def save_migration_log(self, log_entry: Dict[str, Any]) -> bool:
        """Save migration log entry.
        
        Args:
            log_entry: Log entry data
            
        Returns:
            True if save successful
        """
        try:
            log_entry['timestamp'] = datetime.now().isoformat()
            
            log_file = os.path.join(self.state_directory, 'migration_log.jsonl')
            with open(log_file, 'a', encoding='utf-8') as f:
                json.dump(log_entry, f)
                f.write('\n')
            
            return True
            
        except (IOError, OSError, JSONDecodeError) as e:
            print(f"Failed to save migration log: {e}")
            return False
    
    def get_migration_logs(self) -> list:
        """Get all migration log entries.
        
        Returns:
            List of log entries
        """
        log_file = os.path.join(self.state_directory, 'migration_log.jsonl')
        
        if not os.path.exists(log_file):
            return []
        
        logs = []
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        logs.append(json.loads(line))
            return logs
            
        except (IOError, OSError, JSONDecodeError) as e:
            print(f"Failed to load migration logs: {e}")
            return []
    
    def cleanup_state_files(self) -> bool:
        """Clean up migration state files after successful completion.
        
        Returns:
            True if cleanup successful
        """
        try:
            import shutil
            if os.path.exists(self.state_directory):
                shutil.rmtree(self.state_directory)
            return True
            
        except (IOError, OSError) as e:
            print(f"Failed to cleanup state files: {e}")
            return False
    
    def has_existing_migration(self) -> bool:
        """Check if there's an existing migration in progress.
        
        Returns:
            True if migration state files exist
        """
        context_file = os.path.join(self.state_directory, 'migration_context.json')
        return os.path.exists(context_file)
    
    def get_migration_status_summary(self) -> Dict[str, Any]:
        """Get summary of current migration status.
        
        Returns:
            Dictionary with migration status information
        """
        context = self.load_migration_context()
        if not context:
            return {'status': 'NO_MIGRATION', 'details': 'No migration in progress'}
        
        logs = self.get_migration_logs()
        
        return {
            'status': 'IN_PROGRESS',
            'context': {
                'old_name': context.old_project_name,
                'new_name': context.new_project_name,
                'progress': context.get_overall_progress()
            },
            'phases': context.phase_status,
            'log_entries': len(logs),
            'last_activity': logs[-1]['timestamp'] if logs else None
        }