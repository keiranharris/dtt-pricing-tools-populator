#!/usr/bin/env python3
"""Repository Migration Data Model.

Tracks GitHub repository renaming operations and metadata preservation.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass 
class RepositoryMigration:
    """Tracks GitHub repository renaming operation.
    
    Attributes:
        old_name: Original repository name
        new_name: Target repository name
        owner: Repository owner/organization
        migration_completed: Whether renaming is complete
        redirect_url: GitHub redirect URL (automatically created)
        commit_count: Number of commits to preserve
        branch_count: Number of branches to preserve
        tag_count: Number of tags to preserve
    """
    
    old_name: str
    new_name: str 
    owner: str
    migration_completed: bool = False
    redirect_url: str = ""
    commit_count: int = 0
    branch_count: int = 0
    tag_count: int = 0
    
    # State tracking
    _state: str = "PENDING"
    _start_time: Optional[datetime] = None
    _completion_time: Optional[datetime] = None
    _error_message: Optional[str] = None
    
    @property
    def state(self) -> str:
        """Current migration state."""
        return self._state
    
    @property
    def old_url(self) -> str:
        """Original repository URL."""
        return f"https://github.com/{self.owner}/{self.old_name}"
    
    @property
    def new_url(self) -> str:
        """New repository URL.""" 
        return f"https://github.com/{self.owner}/{self.new_name}"
    
    def start_migration(self) -> None:
        """Mark migration as started."""
        self._state = "IN_PROGRESS"
        self._start_time = datetime.now()
        self._error_message = None
    
    def complete_migration(self, redirect_url: str = "") -> None:
        """Mark migration as completed successfully.
        
        Args:
            redirect_url: GitHub's automatic redirect URL
        """
        self._state = "COMPLETED"
        self._completion_time = datetime.now()
        self.migration_completed = True
        if redirect_url:
            self.redirect_url = redirect_url
        else:
            self.redirect_url = self.old_url  # GitHub auto-redirect
    
    def fail_migration(self, error_message: str) -> None:
        """Mark migration as failed.
        
        Args:
            error_message: Description of the failure
        """
        self._state = "FAILED"
        self._completion_time = datetime.now()
        self._error_message = error_message
        self.migration_completed = False
    
    def get_error_message(self) -> Optional[str]:
        """Get error message if migration failed."""
        return self._error_message
    
    def get_duration(self) -> Optional[float]:
        """Get migration duration in seconds if completed."""
        if self._start_time and self._completion_time:
            return (self._completion_time - self._start_time).total_seconds()
        return None
    
    def update_metadata_counts(self, commits: int, branches: int, tags: int) -> None:
        """Update repository metadata counts.
        
        Args:
            commits: Number of commits in repository
            branches: Number of branches in repository  
            tags: Number of tags in repository
        """
        self.commit_count = commits
        self.branch_count = branches
        self.tag_count = tags
    
    def validate_preservation(self, 
                            expected_commits: int, 
                            expected_branches: int, 
                            expected_tags: int) -> bool:
        """Validate that repository metadata was preserved during migration.
        
        Args:
            expected_commits: Expected number of commits
            expected_branches: Expected number of branches
            expected_tags: Expected number of tags
            
        Returns:
            True if all metadata was preserved
        """
        return (self.commit_count == expected_commits and
                self.branch_count == expected_branches and  
                self.tag_count == expected_tags)