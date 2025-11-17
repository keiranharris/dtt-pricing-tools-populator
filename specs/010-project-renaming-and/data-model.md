# Data Model: Project Renaming and Rebranding

**Date**: 2025-11-18  
**Feature**: Project Renaming and Rebranding

## Core Entities

### MigrationContext
**Purpose**: Central configuration and state tracking for the renaming process

**Attributes**:
- `old_project_name: str` - Original project name ("priceup")
- `new_project_name: str` - Target project name ("priceup")
- `old_onedrive_folder: str` - Original OneDrive folder name ("_PricingToolAccel")
- `new_onedrive_folder: str` - Target OneDrive folder name ("_priceup")
- `github_repository_url: str` - Current GitHub repository URL
- `migration_timestamp: datetime` - When migration was initiated
- `backup_created: bool` - Whether backup configurations exist
- `phase_status: Dict[str, str]` - Status of each migration phase

**Validation Rules**:
- `new_project_name` must be valid GitHub repository name
- `new_onedrive_folder` must be valid folder name
- All name fields must be non-empty strings

### RepositoryMigration
**Purpose**: Tracks GitHub repository renaming operation

**Attributes**:
- `old_name: str` - Original repository name
- `new_name: str` - Target repository name
- `owner: str` - Repository owner/organization
- `migration_completed: bool` - Whether renaming is complete
- `redirect_url: str` - GitHub redirect URL (automatically created)
- `commit_count: int` - Number of commits to preserve
- `branch_count: int` - Number of branches to preserve
- `tag_count: int` - Number of tags to preserve

**State Transitions**:
- `PENDING` → `IN_PROGRESS` → `COMPLETED` or `FAILED`

### OneDriveMigration
**Purpose**: Tracks OneDrive folder renaming coordination

**Attributes**:
- `old_folder_path: str` - Original folder path
- `new_folder_path: str` - Target folder path
- `administrator_contact: str` - OneDrive admin for coordination
- `team_members: List[str]` - Users requiring access preservation
- `migration_scheduled: datetime` - When folder rename is scheduled
- `permissions_preserved: bool` - Whether team access maintained
- `content_integrity_verified: bool` - Whether all files transferred

**State Transitions**:
- `PLANNING` → `SCHEDULED` → `EXECUTING` → `COMPLETED` or `FAILED`

### FileRenaming
**Purpose**: Tracks individual file and directory renaming operations

**Attributes**:
- `old_path: str` - Original file/directory path
- `new_path: str` - Target file/directory path
- `operation_type: str` - Type: "FILE_RENAME", "DIRECTORY_RENAME", "CONTENT_UPDATE"
- `content_changes: List[str]` - List of text replacements made
- `backup_path: str` - Location of backup before changes
- `checksum_before: str` - File checksum before changes
- `checksum_after: str` - File checksum after changes

**Validation Rules**:
- Checksums must be calculated for content integrity
- Backup must exist before applying changes
- New path must not conflict with existing files

### UserConfiguration
**Purpose**: Tracks individual user configuration updates

**Attributes**:
- `user_identifier: str` - User name or ID
- `config_file_path: str` - Path to user's configuration file
- `old_onedrive_path: str` - Original OneDrive path in config
- `new_onedrive_path: str` - Updated OneDrive path in config
- `shell_alias_status: str` - Status of shell alias ("PRESERVED", "UPDATED", "MISSING")
- `migration_completed: bool` - Whether user migration is complete
- `backup_created: bool` - Whether configuration backup exists

**State Transitions**:
- `DETECTED` → `BACKED_UP` → `UPDATED` → `VALIDATED` or `FAILED`

## Relationships

```
MigrationContext (1) ──── (1) RepositoryMigration
MigrationContext (1) ──── (1) OneDriveMigration
MigrationContext (1) ──── (*) FileRenaming
MigrationContext (1) ──── (*) UserConfiguration

OneDriveMigration (1) ──── (*) UserConfiguration
```

## Data Flow

1. **Initialization**: Create `MigrationContext` with source and target names
2. **Repository Phase**: Create `RepositoryMigration` and execute GitHub renaming
3. **OneDrive Phase**: Create `OneDriveMigration` and coordinate folder renaming
4. **File Phase**: Create multiple `FileRenaming` entries for each file/directory operation
5. **User Phase**: Create `UserConfiguration` entries for each user requiring updates
6. **Validation**: Verify all entities are in completed state

## Storage Considerations

- All migration state stored in temporary JSON files for recovery
- Backup configurations stored with timestamp-based naming
- Migration logs stored for audit trail and troubleshooting
- Rollback data maintained until migration confirmed successful

## Error Handling

- Each entity tracks error states and error messages
- Partial failures allow for selective retry operations
- Complete rollback supported through backup data
- Migration can be resumed from any failed phase