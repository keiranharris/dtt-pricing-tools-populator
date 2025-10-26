# Shell Alias Manager API Contract

**Module**: `src.shell_alias_manager`  
**Purpose**: Core API for shell alias detection, creation, and management  
**Version**: 1.0.0

## Public Interface

### ShellAliasManager Class

**Primary Interface**: Main orchestrator for all alias operations

#### Constructor
```python
def __init__(self, 
    script_path: Optional[Path] = None,
    timeout_seconds: int = 60,
    alias_name: str = "priceup") -> None:
```

**Parameters**:
- `script_path`: Path to pricing_tool_accelerator.py (auto-detected if None)
- `timeout_seconds`: Maximum time for file operations (default: 60)
- `alias_name`: Name of alias to create/manage (default: "priceup")

**Raises**:
- `ValueError`: If script_path is invalid or doesn't exist
- `TypeError`: If parameters are wrong type

#### Core Methods

##### check_and_setup_alias()
```python
def check_and_setup_alias(self) -> AliasOperationResult:
    """
    Main entry point: detect shell, check existing alias, create if needed.
    
    Returns:
        AliasOperationResult with success/failure state and user message
        
    Raises:
        TimeoutError: If operation exceeds timeout_seconds
        OSError: If critical system operations fail
    """
```

**Behavior**:
- Detects shell environment and validates zsh requirement
- Checks if alias already exists and is correct
- Creates/updates alias if needed
- Returns appropriate result with user-facing message
- Guarantees completion within timeout or raises TimeoutError

##### validate_existing_alias()
```python
def validate_existing_alias(self) -> AliasValidationResult:
    """
    Check if alias exists in shell config and points to correct location.
    
    Returns:
        AliasValidationResult with existence and correctness flags
        
    Raises:
        OSError: If shell config file cannot be read
    """
```

##### get_manual_setup_instructions()
```python
def get_manual_setup_instructions(self) -> str:
    """
    Generate manual alias creation instructions for fallback scenarios.
    
    Returns:
        Formatted string with shell commands for manual setup
    """
```

### Data Transfer Objects

#### AliasOperationResult
```python
@dataclass
class AliasOperationResult:
    success: bool
    operation_type: AliasOperationType
    message: str
    error_details: Optional[str] = None
    manual_instructions: Optional[str] = None
```

**Usage**: Primary return type for alias operations
**Fields**:
- `success`: True if operation completed without errors
- `operation_type`: What action was taken (CREATE, UPDATE, VALIDATE, SKIP)
- `message`: User-facing confirmation or error message
- `error_details`: Technical details for debugging (optional)
- `manual_instructions`: Fallback steps if automation failed (optional)

#### AliasValidationResult
```python
@dataclass
class AliasValidationResult:
    exists: bool
    is_correct: bool
    current_command: Optional[str] = None
    expected_command: Optional[str] = None
```

**Usage**: Return type for alias validation checks
**Fields**:
- `exists`: Whether alias is found in shell config
- `is_correct`: Whether existing alias points to correct script path
- `current_command`: Actual alias command if it exists
- `expected_command`: What the alias command should be

### Exception Hierarchy

#### ShellAliasError (Base)
```python
class ShellAliasError(Exception):
    """Base exception for shell alias operations"""
```

#### UnsupportedShellError
```python
class UnsupportedShellError(ShellAliasError):
    """Raised when shell type is not zsh"""
    def __init__(self, detected_shell: str):
        super().__init__(f"Shell '{detected_shell}' not supported. zsh required.")
        self.detected_shell = detected_shell
```

#### AliasPermissionError
```python
class AliasPermissionError(ShellAliasError):
    """Raised when shell config file is not writable"""
    def __init__(self, config_path: Path):
        super().__init__(f"Cannot write to shell config: {config_path}")
        self.config_path = config_path
```

## Integration Contract

### CLI Integration Hook
```python
def setup_shell_alias_if_needed() -> bool:
    """
    Startup hook for main CLI application.
    
    Returns:
        bool: True if main CLI should continue, False if should exit
        
    Side Effects:
        - May create/update alias in ~/.zshrc
        - Prints user messages via logging system
        - Never raises exceptions (catches and logs all errors)
    """
```

**Integration Pattern**:
```python
# In pricing_tool_accelerator.py main()
def main():
    # NEW: Shell alias setup check
    if not setup_shell_alias_if_needed():
        return  # Exit if critical setup failure
        
    # EXISTING: Continue with normal CLI workflow
    configure_logging()
    # ... rest of main()
```

### Logging Interface Contract
```python
# Uses existing logging_config.py patterns
logger.info("✅ Shell alias 'priceup' created successfully")
logger.warning("⚠️  Shell alias exists but points to different location")  
logger.error("❌ Cannot create shell alias: permission denied")
```

**Message Categories**:
- **INFO**: Successful alias creation, usage instructions
- **WARNING**: Non-critical issues (wrong path, already exists)
- **ERROR**: Critical failures with manual fallback instructions

### File System Contract

#### Required Paths
- **Input**: `pricing_tool_accelerator.py` (auto-detected via `__file__`)
- **Output**: `~/.zshrc` (user's zsh configuration file)
- **Temporary**: No temporary files required (atomic in-memory operations)

#### File Format Contract
```bash
# Shell config before alias:
# [existing user configuration]

# Shell config after alias creation:
# [existing user configuration]
# DTT Pricing Tool - START (auto-generated)
alias priceup='python3 /absolute/path/to/pricing_tool_accelerator.py'
# DTT Pricing Tool - END

# Shell config after alias update:
# [existing user configuration] 
# DTT Pricing Tool - START (auto-generated)
alias priceup='python3 /new/absolute/path/to/pricing_tool_accelerator.py'
# DTT Pricing Tool - END
```

**Guarantees**:
- Existing configuration preserved exactly
- Only content between markers is managed
- Atomic write operations (no partial states)
- Safe handling of concurrent access

## Testing Contract

### Unit Test Requirements
```python
# Test all public methods with mocked file system
def test_check_and_setup_alias_creates_new():
def test_check_and_setup_alias_updates_existing():
def test_check_and_setup_alias_skips_correct():
def test_validate_existing_alias_not_found():
def test_validate_existing_alias_wrong_path():
def test_get_manual_setup_instructions():
```

### Integration Test Requirements
```python
# Test with real temporary directories
def test_full_workflow_fresh_zshrc():
def test_full_workflow_existing_zshrc():
def test_permission_denied_scenario():
def test_unsupported_shell_scenario():
```

### Error Scenario Coverage
- Permission denied on ~/.zshrc creation/modification
- Non-zsh shell environment detection
- Script path resolution failures
- Timeout during file operations
- Corrupted or malformed existing ~/.zshrc files

This API contract provides complete interface specification for implementing shell alias auto-setup functionality while maintaining consistency with existing codebase patterns and error handling strategies.