# Repository Migration Contract

**Date**: 2025-11-18  
**Type**: Service Interface Contract  
**Purpose**: Defines GitHub repository renaming operations

## Interface: GitHubRepositoryMigrator

### Core Operations

#### `rename_repository(old_name: str, new_name: str, owner: str) -> RepositoryRenameResult`
**Purpose**: Rename GitHub repository and set up automatic redirects

**Parameters**:
- `old_name`: Current repository name
- `new_name`: Target repository name  
- `owner`: Repository owner (user or organization)

**Returns**: `RepositoryRenameResult` with operation details

**Preconditions**:
- Repository must exist and be accessible
- User must have admin permissions
- Target name must be available
- Target name must be valid GitHub repository name

**Postconditions**:
- Repository renamed to new name
- Automatic redirect configured from old name
- All branches, tags, and history preserved
- Repository settings maintained
- Collaborator access preserved

**Errors**:
- `RepositoryNotFoundError`: If repository doesn't exist
- `InsufficientPermissionsError`: If user lacks admin access
- `NameUnavailableError`: If target name already exists
- `InvalidNameError`: If target name violates GitHub naming rules
- `GitHubAPIError`: If GitHub API operation fails

#### `verify_repository_accessibility(owner: str, name: str) -> AccessibilityResult`
**Purpose**: Verify repository can be accessed after renaming

**Parameters**:
- `owner`: Repository owner
- `name`: Repository name to verify

**Returns**: `AccessibilityResult` with access status

**Preconditions**:
- Repository name must be provided
- Network connectivity must be available

**Postconditions**:
- Repository accessibility confirmed or issues identified
- Clone URLs validated
- Redirect functionality verified

**Errors**:
- `NetworkError`: If GitHub cannot be reached
- `RepositoryAccessError`: If repository is not accessible

#### `preserve_repository_metadata(owner: str, old_name: str, new_name: str) -> MetadataResult`
**Purpose**: Ensure all repository metadata is preserved during renaming

**Parameters**:
- `owner`: Repository owner
- `old_name`: Original repository name
- `new_name`: New repository name

**Returns**: `MetadataResult` with preservation status

**Preconditions**:
- Repository must exist with the new name
- User must have read access to repository metadata

**Postconditions**:
- All branches verified as preserved
- All tags verified as preserved  
- All releases verified as preserved
- Issue and PR history verified as preserved
- Repository settings verified as preserved

**Errors**:
- `MetadataIncompleteError`: If some metadata is missing
- `HistoryCorruptionError`: If repository history is damaged

### Information Gathering

#### `get_repository_info(owner: str, name: str) -> RepositoryInfo`
**Purpose**: Retrieve comprehensive repository information

**Returns**: Repository details including branches, tags, collaborators, settings

#### `check_name_availability(owner: str, name: str) -> bool`
**Purpose**: Check if target repository name is available

#### `estimate_rename_duration(owner: str, name: str) -> timedelta`
**Purpose**: Estimate time required for repository renaming operation

## Data Contracts

### RepositoryRenameResult
```python
@dataclass
class RepositoryRenameResult:
    success: bool
    old_name: str
    new_name: str
    redirect_url: str
    rename_timestamp: datetime
    branches_preserved: int
    tags_preserved: int
    releases_preserved: int
    error_message: Optional[str]
```

### AccessibilityResult
```python
@dataclass
class AccessibilityResult:
    accessible: bool
    clone_urls: Dict[str, str]  # ssh, https, etc.
    redirect_working: bool
    response_time_ms: int
    error_message: Optional[str]
```

### MetadataResult
```python
@dataclass
class MetadataResult:
    complete: bool
    branches_count: int
    tags_count: int
    releases_count: int
    collaborators_count: int
    issues_count: int
    prs_count: int
    missing_items: List[str]
```

### RepositoryInfo
```python
@dataclass
class RepositoryInfo:
    name: str
    owner: str
    description: str
    private: bool
    archived: bool
    default_branch: str
    branches: List[str]
    tags: List[str]
    releases: List[str]
    collaborators: List[str]
    size_kb: int
    created_at: datetime
    updated_at: datetime
```

## Implementation Requirements

### Authentication
- Must support GitHub Personal Access Tokens
- Must support GitHub App authentication
- Token must have repository administration scope
- Should handle token expiration gracefully

### Rate Limiting
- Must respect GitHub API rate limits
- Should implement exponential backoff for retries
- Must provide rate limit status information
- Should queue operations when near rate limits

### Error Handling
- Must provide detailed error messages
- Should distinguish between transient and permanent failures
- Must support retry logic for transient failures
- Should provide rollback guidance for failures

### Logging
- Must log all API calls with timestamps
- Should log response times and status codes
- Must log error details for debugging
- Should provide audit trail for operations

## State Transitions

```
PENDING → VALIDATING_PERMISSIONS → CHECKING_AVAILABILITY → 
INITIATING_RENAME → VERIFYING_REDIRECT → VALIDATING_METADATA → 
COMPLETED or FAILED
```

Each transition must be atomic and traceable for rollback purposes.

## Security Considerations

- API tokens must be handled securely
- Repository access must be verified before operations
- Operations must be logged for audit purposes
- Sensitive data must not be logged in plain text

## Performance Considerations  

- Operations should be designed for minimal GitHub API usage
- Metadata verification should be batched where possible
- Large repositories may require extended timeouts
- Progress reporting should be provided for long operations