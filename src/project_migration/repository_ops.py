#!/usr/bin/env python3
"""GitHub Repository Operations.

Handles GitHub repository renaming and metadata preservation operations.
"""

import subprocess
import json
import re
from typing import Dict, Any, Optional, List
from .repository_migration import RepositoryMigration
from .migration_logging import get_migration_logger


class GitHubRepositoryMigrator:
    """Handles GitHub repository renaming operations."""
    
    def __init__(self):
        """Initialize GitHub repository migrator."""
        self.logger = get_migration_logger()
    
    def rename_repository(self, old_name: str, new_name: str, owner: str) -> RepositoryMigration:
        """Rename GitHub repository and set up automatic redirects.
        
        Args:
            old_name: Current repository name
            new_name: Target repository name
            owner: Repository owner (user or organization)
            
        Returns:
            RepositoryMigration object with operation results
        """
        migration = RepositoryMigration(old_name, new_name, owner)
        
        try:
            # Validate repository exists and is accessible
            if not self._verify_repository_exists(owner, old_name):
                migration.fail_migration(f"Repository {owner}/{old_name} not found or not accessible")
                return migration
            
            # Check if target name is available
            if self._check_repository_exists(owner, new_name):
                migration.fail_migration(f"Target repository name {owner}/{new_name} already exists")
                return migration
            
            # Get repository metadata before rename
            metadata = self._get_repository_metadata(owner, old_name)
            if metadata:
                migration.update_metadata_counts(
                    commits=metadata.get('commit_count', 0),
                    branches=metadata.get('branch_count', 0),
                    tags=metadata.get('tag_count', 0)
                )
            
            migration.start_migration()
            self.logger.log_phase_start("repository_rename", {
                "old_name": old_name,
                "new_name": new_name,
                "owner": owner
            })
            
            # Execute repository rename using GitHub API
            success = self._execute_repository_rename(owner, old_name, new_name)
            
            if success:
                # Verify rename was successful
                if self._verify_repository_exists(owner, new_name):
                    redirect_url = f"https://github.com/{owner}/{old_name}"
                    migration.complete_migration(redirect_url)
                    self.logger.log_github_operation("rename", f"{owner}/{old_name}", f"{owner}/{new_name}", True)
                    
                    # Verify metadata preservation
                    new_metadata = self._get_repository_metadata(owner, new_name)
                    if new_metadata and metadata:
                        preserved = migration.validate_preservation(
                            metadata.get('commit_count', 0),
                            metadata.get('branch_count', 0),
                            metadata.get('tag_count', 0)
                        )
                        if not preserved:
                            self.logger.log_warning("Repository metadata may not have been fully preserved")
                else:
                    migration.fail_migration("Repository rename appeared to succeed but new repository not found")
            else:
                migration.fail_migration("Failed to execute repository rename operation")
            
        except Exception as e:
            migration.fail_migration(f"Repository rename failed with exception: {str(e)}")
            self.logger.log_error("Repository rename failed", e)
        
        return migration
    
    def _verify_repository_exists(self, owner: str, name: str) -> bool:
        """Verify repository exists and is accessible."""
        try:
            cmd = ["gh", "api", f"repos/{owner}/{name}"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.returncode == 0
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Try with curl if gh CLI not available
            return self._verify_with_curl(owner, name)
    
    def _verify_with_curl(self, owner: str, name: str) -> bool:
        """Verify repository using curl as fallback."""
        try:
            import urllib.request
            url = f"https://api.github.com/repos/{owner}/{name}"
            with urllib.request.urlopen(url) as response:
                return response.status == 200
        except:
            return False
    
    def _check_repository_exists(self, owner: str, name: str) -> bool:
        """Check if repository name already exists."""
        return self._verify_repository_exists(owner, name)
    
    def _get_repository_metadata(self, owner: str, name: str) -> Optional[Dict[str, Any]]:
        """Get repository metadata including commits, branches, tags."""
        try:
            # Get basic repository info
            cmd = ["gh", "api", f"repos/{owner}/{name}"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            repo_data = json.loads(result.stdout)
            
            # Get branches count
            branches_cmd = ["gh", "api", f"repos/{owner}/{name}/branches", "--paginate"]
            branches_result = subprocess.run(branches_cmd, capture_output=True, text=True)
            branch_count = 0
            if branches_result.returncode == 0:
                try:
                    branches_data = json.loads(branches_result.stdout)
                    branch_count = len(branches_data) if isinstance(branches_data, list) else 0
                except json.JSONDecodeError:
                    pass
            
            # Get tags count  
            tags_cmd = ["gh", "api", f"repos/{owner}/{name}/tags", "--paginate"]
            tags_result = subprocess.run(tags_cmd, capture_output=True, text=True)
            tag_count = 0
            if tags_result.returncode == 0:
                try:
                    tags_data = json.loads(tags_result.stdout)
                    tag_count = len(tags_data) if isinstance(tags_data, list) else 0
                except json.JSONDecodeError:
                    pass
            
            return {
                'commit_count': repo_data.get('size', 0),  # Size is approximate
                'branch_count': branch_count,
                'tag_count': tag_count,
                'default_branch': repo_data.get('default_branch', 'main'),
                'private': repo_data.get('private', False)
            }
            
        except (subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError):
            self.logger.log_warning(f"Could not retrieve metadata for {owner}/{name}")
            return None
    
    def _execute_repository_rename(self, owner: str, old_name: str, new_name: str) -> bool:
        """Execute the repository rename using GitHub API."""
        try:
            # Use GitHub CLI to rename repository
            cmd = ["gh", "api", f"repos/{owner}/{old_name}", "-X", "PATCH", "-f", f"name={new_name}"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            if result.returncode == 0:
                self.logger.log_debug(f"GitHub API rename successful: {old_name} → {new_name}")
                return True
            else:
                self.logger.log_error(f"GitHub API rename failed: {result.stderr}")
                return False
                
        except subprocess.CalledProcessError as e:
            self.logger.log_error(f"GitHub API command failed: {e.stderr}")
            return False
        except FileNotFoundError:
            self.logger.log_error("GitHub CLI (gh) not found. Please install GitHub CLI.")
            return False
    
    def verify_repository_accessibility(self, owner: str, name: str) -> Dict[str, Any]:
        """Verify repository can be accessed after renaming."""
        result = {
            'accessible': False,
            'clone_urls': {},
            'redirect_working': False,
            'response_time_ms': 0,
            'error_message': None
        }
        
        try:
            import time
            start_time = time.time()
            
            # Check repository accessibility
            if self._verify_repository_exists(owner, name):
                result['accessible'] = True
                
                # Get clone URLs
                cmd = ["gh", "api", f"repos/{owner}/{name}"]
                repo_result = subprocess.run(cmd, capture_output=True, text=True)
                if repo_result.returncode == 0:
                    repo_data = json.loads(repo_result.stdout)
                    result['clone_urls'] = {
                        'ssh': repo_data.get('ssh_url', ''),
                        'https': repo_data.get('clone_url', ''),
                        'git': repo_data.get('git_url', '')
                    }
            else:
                result['error_message'] = f"Repository {owner}/{name} not accessible"
            
            end_time = time.time()
            result['response_time_ms'] = int((end_time - start_time) * 1000)
            
        except Exception as e:
            result['error_message'] = f"Accessibility check failed: {str(e)}"
        
        return result
    
    def update_local_remote_url(self, old_name: str, new_name: str, owner: str) -> bool:
        """Update local repository remote URL.
        
        Args:
            old_name: Old repository name
            new_name: New repository name  
            owner: Repository owner
            
        Returns:
            True if update successful
        """
        try:
            new_url = f"https://github.com/{owner}/{new_name}.git"
            cmd = ["git", "remote", "set-url", "origin", new_url]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            if result.returncode == 0:
                self.logger.log_operation("Local remote URL update", True, f"Updated to {new_url}")
                return True
            else:
                self.logger.log_operation("Local remote URL update", False, result.stderr)
                return False
                
        except subprocess.CalledProcessError as e:
            self.logger.log_error(f"Failed to update local remote URL: {e.stderr}")
            return False
        except FileNotFoundError:
            self.logger.log_error("Git command not found")
            return False
    
    def validate_github_cli_access(self) -> bool:
        """Validate GitHub CLI is installed and authenticated."""
        try:
            # Check if gh is installed
            result = subprocess.run(["gh", "--version"], capture_output=True, text=True)
            if result.returncode != 0:
                return False
            
            # Check if authenticated
            auth_result = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True)
            return auth_result.returncode == 0
            
        except FileNotFoundError:
            return False