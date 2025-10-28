# API Contracts: Dynamic OneDrive Path Configuration

## ConfigurationManager Interface

### load_configuration()

**Purpose**: Load existing path configuration from user's home directory  
**Parameters**: None  
**Returns**: `Optional[PathConfiguration]` - Configuration object if exists, None if not configured  
**Raises**: `ConfigurationError` if file exists but is corrupted  

```python
def load_configuration() -> Optional[PathConfiguration]:
    """Load OneDrive path configuration from user's local file."""
```

### save_configuration(config: PathConfiguration)

**Purpose**: Persist path configuration to user's home directory  
**Parameters**: 
- `config: PathConfiguration` - Configuration object to save
**Returns**: `None`  
**Raises**: `ConfigurationError` if unable to write configuration file  

```python
def save_configuration(config: PathConfiguration) -> None:
    """Save OneDrive path configuration to user's local file."""
```

### validate_configuration(config: PathConfiguration)

**Purpose**: Check if configured paths are currently accessible  
**Parameters**: 
- `config: PathConfiguration` - Configuration to validate
**Returns**: `ValidationResult` - Validation outcome with details  
**Raises**: Never (validation errors returned in result object)  

```python
def validate_configuration(config: PathConfiguration) -> ValidationResult:
    """Validate that configured OneDrive paths are accessible."""
```

### get_configured_paths()

**Purpose**: Get current directory paths for application use  
**Parameters**: None  
**Returns**: `DirectoryPaths` - Object containing all required directory paths  
**Raises**: `ConfigurationError` if no valid configuration exists  

```python
def get_configured_paths() -> DirectoryPaths:
    """Get validated OneDrive directory paths for application use."""
```

## SetupWizard Interface

### start_setup()

**Purpose**: Begin interactive setup process for OneDrive path configuration  
**Parameters**: None  
**Returns**: `PathConfiguration` - Successfully configured and validated paths  
**Raises**: `SetupCancelledError` if user cancels setup, `SetupError` if setup fails  

```python
def start_setup() -> PathConfiguration:
    """Interactive setup wizard for OneDrive path configuration."""
```

### validate_user_path(path: str)

**Purpose**: Validate user-provided OneDrive base path  
**Parameters**: 
- `path: str` - Path provided by user during setup
**Returns**: `ValidationResult` - Validation outcome with specific error details  
**Raises**: Never (validation errors returned in result object)  

```python
def validate_user_path(path: str) -> ValidationResult:
    """Validate user-provided OneDrive base path structure."""
```

## Integration Points with Existing Code

### constants.py Integration

**Modified Function**: `get_directory_paths()`

**Purpose**: Return dynamic paths from configuration or fallback to hardcoded values  
**Parameters**: None  
**Returns**: `DirectoryPaths` - Either configured paths or hardcoded defaults  
**Raises**: `ConfigurationError` if no valid paths available (configured or hardcoded)  

```python
def get_directory_paths() -> DirectoryPaths:
    """Get OneDrive directory paths (configured or hardcoded fallback)."""
```

### CLI Integration Points

**Modified Function**: `main()` in pricing_tool_accelerator.py

**Additional Logic**:
1. Check for existing configuration on startup
2. If no configuration exists, launch setup wizard
3. If configuration exists but invalid, offer reconfiguration
4. Proceed with normal operation using configured paths

**New Command Line Options**:
- `--configure-paths` - Force reconfiguration of OneDrive paths
- `--show-config` - Display current path configuration
- `--validate-paths` - Check current configuration validity

## Error Contracts

### ConfigurationError

**Purpose**: Indicates configuration file operation failures  
**Attributes**:
- `message: str` - User-friendly error description
- `recovery_suggestion: str` - Guidance for resolving the error

### SetupError

**Purpose**: Indicates setup process failures  
**Attributes**:
- `message: str` - User-friendly error description  
- `step: SetupStep` - Setup step where error occurred

### SetupCancelledError

**Purpose**: Indicates user cancelled setup process  
**Attributes**: None (user intentionally cancelled)

### ValidationError  

**Purpose**: Indicates path validation failures with specific details  
**Attributes**:
- `message: str` - User-friendly error description
- `missing_directories: List[str]` - Specific missing subdirectories
- `path_attempted: str` - Path that failed validation