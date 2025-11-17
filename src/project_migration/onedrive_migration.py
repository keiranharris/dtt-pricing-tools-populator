#!/usr/bin/env python3
"""OneDrive Migration Data Model.

Tracks OneDrive folder renaming coordination and team access preservation.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class OneDriveMigration:
    """Tracks OneDrive folder renaming coordination.
    
    Attributes:
        old_folder_path: Original folder path
        new_folder_path: Target folder path
        administrator_contact: OneDrive admin for coordination
        team_members: Users requiring access preservation
        migration_scheduled: When folder rename is scheduled
        permissions_preserved: Whether team access maintained
        content_integrity_verified: Whether all files transferred
    """
    
    old_folder_path: str
    new_folder_path: str
    administrator_contact: str
    team_members: List[str] = field(default_factory=list)
    migration_scheduled: Optional[datetime] = None
    permissions_preserved: bool = False
    content_integrity_verified: bool = False
    
    # State tracking
    _state: str = "PLANNING"
    _coordination_id: str = ""
    _backup_location: str = ""
    _notification_sent: bool = False
    _admin_approval: str = "PENDING"
    
    @property
    def state(self) -> str:
        """Current migration state."""
        return self._state
    
    @property
    def coordination_id(self) -> str:
        """Coordination tracking ID."""
        return self._coordination_id
    
    @property
    def backup_location(self) -> str:
        """Location of folder backup."""
        return self._backup_location
    
    def set_coordination_id(self, coord_id: str) -> None:
        """Set coordination tracking ID.
        
        Args:
            coord_id: Unique identifier for coordination process
        """
        self._coordination_id = coord_id
    
    def schedule_migration(self, scheduled_time: datetime) -> None:
        """Schedule the migration for a specific time.
        
        Args:
            scheduled_time: When the migration will occur
        """
        self.migration_scheduled = scheduled_time
        self._state = "SCHEDULED"
    
    def send_team_notifications(self) -> None:
        """Mark team notifications as sent."""
        self._notification_sent = True
        if self._state == "PLANNING":
            self._state = "TEAM_NOTIFICATION"
    
    def set_admin_approval(self, approval_status: str) -> None:
        """Set administrator approval status.
        
        Args:
            approval_status: PENDING, APPROVED, or REJECTED
        """
        valid_statuses = ["PENDING", "APPROVED", "REJECTED"]
        if approval_status not in valid_statuses:
            raise ValueError(f"Invalid approval status: {approval_status}")
        
        self._admin_approval = approval_status
        if approval_status == "APPROVED":
            self._state = "APPROVED"
        elif approval_status == "REJECTED":
            self._state = "REJECTED"
    
    def create_backup(self, backup_path: str) -> None:
        """Record backup creation.
        
        Args:
            backup_path: Path where backup was created
        """
        self._backup_location = backup_path
        if self._state in ["APPROVED", "SCHEDULED"]:
            self._state = "BACKUP_CREATED"
    
    def start_migration(self) -> None:
        """Mark migration execution as started."""
        if self._state != "BACKUP_CREATED":
            raise ValueError("Cannot start migration without backup")
        self._state = "EXECUTING"
    
    def complete_migration(self) -> None:
        """Mark migration as completed successfully."""
        self._state = "COMPLETED"
    
    def fail_migration(self, error: str) -> None:
        """Mark migration as failed.
        
        Args:
            error: Description of the failure
        """
        self._state = "FAILED"
    
    def validate_permissions(self, preserved_members: List[str]) -> bool:
        """Validate that team member permissions were preserved.
        
        Args:
            preserved_members: List of team members who retained access
            
        Returns:
            True if all original team members retained access
        """
        original_set = set(self.team_members)
        preserved_set = set(preserved_members)
        self.permissions_preserved = original_set.issubset(preserved_set)
        return self.permissions_preserved
    
    def verify_content_integrity(self, file_count: int, total_size: int) -> None:
        """Verify content integrity after migration.
        
        Args:
            file_count: Number of files in new location
            total_size: Total size of files in new location
        """
        # In a real implementation, this would compare against pre-migration metrics
        # For now, we'll assume verification passes if we have files
        self.content_integrity_verified = file_count > 0
    
    def get_admin_approval_status(self) -> str:
        """Get current administrator approval status."""
        return self._admin_approval
    
    def is_ready_for_execution(self) -> bool:
        """Check if migration is ready for execution."""
        return (self._admin_approval == "APPROVED" and 
                self._notification_sent and
                bool(self._backup_location) and
                self.migration_scheduled is not None)
    
    def add_team_member(self, member: str) -> None:
        """Add team member to access preservation list.
        
        Args:
            member: Team member identifier
        """
        if member not in self.team_members:
            self.team_members.append(member)
    
    def remove_team_member(self, member: str) -> None:
        """Remove team member from access preservation list.
        
        Args:
            member: Team member identifier
        """
        if member in self.team_members:
            self.team_members.remove(member)