# Data Model: Shell Alias Auto-Setup

**Feature**: Shell Alias Auto-Setup for Easy Access  
**Date**: 2025-10-26  
**Status**: Implementation Ready

## Core Entities

### ShellEnvironment

**Purpose**: Represents the user's shell configuration and capabilities

**Attributes**:
- `shell_type: str` - Detected shell type (e.g., "zsh", "bash", "fish")
- `shell_path: Path` - Path to shell executable
- `config_file: Path` - Path to shell configuration file (~/.zshrc)
- `is_supported: bool` - Whether shell type is supported (zsh-only)

**Validation Rules**:
- `shell_type` must be "zsh" for feature to proceed
- `config_file` must be writable or creatable
- `shell_path` must be valid executable

**State Transitions**:
1. **Unknown** → **Detected** (shell type identification)
2. **Detected** → **Validated** (zsh requirement check)
3. **Validated** → **Ready** (config file access confirmed)

### ShellAlias

**Purpose**: Represents the 'priceup' shell alias configuration

**Attributes**:
- `name: str` - Alias name ("priceup")
- `command: str` - Full command with escaped path
- `script_path: Path` - Resolved absolute path to pricing_tool_accelerator.py
- `markers: Tuple[str, str]` - Start and end comment markers for safe identification
- `exists: bool` - Whether alias currently exists in config file
- `is_correct: bool` - Whether existing alias points to correct path

**Validation Rules**:
- `name` must be valid shell identifier (alphanumeric + underscore)
- `command` must be properly shell-escaped
- `script_path` must be absolute and point to existing file
- `markers` must be unique and contain feature identifier

**Identity Rules**:
- Uniqueness determined by `name` within shell configuration
- Correctness determined by comparing `command` with expected value

### AliasOperation

**Purpose**: Represents a single alias management operation

**Attributes**:
- `operation_type: AliasOperationType` - Type of operation (CREATE, UPDATE, VALIDATE, SKIP)
- `target_alias: ShellAlias` - Alias being operated on
- `shell_env: ShellEnvironment` - Target shell environment
- `success: bool` - Whether operation completed successfully
- `message: str` - User-facing result message
- `error_details: Optional[str]` - Technical error information if failed

**State Transitions**:
1. **Planned** → **Executing** (operation begins)
2. **Executing** → **Completed** (success) | **Failed** (error)
3. **Failed** → **Retried** (if applicable) | **Aborted**

## Relationships

### ShellEnvironment ↔ ShellAlias
- **One-to-Many**: One shell environment can contain multiple aliases
- **Dependency**: Alias operations require valid shell environment
- **Constraint**: Only supported shells can have aliases created

### AliasOperation → ShellAlias
- **Many-to-One**: Multiple operations can target same alias (create, update, validate)
- **Lifecycle**: Operations modify alias state and existence
- **Atomicity**: Each operation is atomic (success/failure, no partial states)

### AliasOperation → ShellEnvironment  
- **Many-to-One**: Operations require shell environment context
- **Validation**: Operations validate environment before execution
- **Error Propagation**: Environment issues cause operation failures

## Enumerations

### AliasOperationType
```python
class AliasOperationType(Enum):
    CREATE = "create"      # Create new alias in config file
    UPDATE = "update"      # Update existing alias with new path
    VALIDATE = "validate"  # Check if existing alias is correct
    SKIP = "skip"          # No operation needed (already exists and correct)
```

### ShellType
```python
class ShellType(Enum):
    ZSH = "zsh"           # Supported shell
    BASH = "bash"         # Unsupported (error condition)
    FISH = "fish"         # Unsupported (error condition)
    UNKNOWN = "unknown"   # Undetected shell (error condition)
```

### OperationResult
```python
class OperationResult(Enum):
    SUCCESS = "success"                    # Operation completed successfully
    ALREADY_EXISTS = "already_exists"      # Alias exists and is correct (no-op)
    PERMISSION_DENIED = "permission_denied" # Cannot write to config file
    UNSUPPORTED_SHELL = "unsupported_shell" # Shell type not supported
    FILE_NOT_FOUND = "file_not_found"      # Script path doesn't exist
    TIMEOUT = "timeout"                    # Operation exceeded 60-second limit
```

## Data Flow

### Alias Creation Workflow
1. **Detection Phase**: `ShellEnvironment` creation and validation
2. **Resolution Phase**: `ShellAlias` creation with resolved paths
3. **Operation Planning**: `AliasOperation` creation based on current state
4. **Execution Phase**: File modification and result capture
5. **Feedback Phase**: User message generation from operation result

### State Validation Chain
1. Shell detection → Shell validation → Config access → Alias resolution → Operation execution
2. Each step validates prerequisites before proceeding
3. Failures at any step provide specific error messages and remediation steps
4. Success path leads to user confirmation and usage instructions

## Persistence

### File-Based Storage
- **Primary**: `~/.zshrc` file with comment-delimited alias blocks
- **Format**: Plain text shell configuration with structured comments
- **Atomicity**: Read-entire-file → modify-in-memory → write-entire-file pattern
- **Safety**: Temporary backup during modification, rollback on failure

### In-Memory Representation
- **Transient**: All entities exist only during operation execution
- **No Caching**: Fresh detection and validation on each run for accuracy
- **Stateless**: No persistent state between application invocations
- **Idempotent**: Same inputs always produce same outputs

## Error Handling

### Validation Failures
- **Shell Type**: Clear error with instructions to switch to zsh
- **Permissions**: Error message with manual alias creation instructions
- **Path Resolution**: Error with repository location verification steps

### Recovery Strategies
- **Graceful Degradation**: Main application continues if alias setup fails
- **Fallback Instructions**: Manual alias creation commands for all error cases
- **No Data Loss**: Configuration file corruption prevention through atomic writes

This data model provides the foundation for implementing shell alias auto-setup while maintaining consistency with existing codebase patterns and constitutional requirements.