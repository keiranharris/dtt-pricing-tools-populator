# Function Interfaces: Spreadsheet Copy and Instantiation

**Feature**: 001-spreadsheet-copy  
**Phase**: 1 - Architecture Design  
**Date**: 2025-10-12  
**Input**: Data model and requirements analysis

## Module Interface Contracts

### file_operations.py

#### discover_template_file()
```python
def discover_template_file(source_dir: Path = Path("10-LATEST-PRICING-TOOLS")) -> SourceFile:
    """
    Discover and validate the Low Complexity template file in source directory.
    
    Args:
        source_dir: Directory to search for template files
        
    Returns:
        SourceFile: Validated template file with version information
        
    Raises:
        FileNotFoundError: If no template file found matching pattern
        ValueError: If multiple matching files found or version extraction fails
        PermissionError: If file is not readable
        
    Side Effects:
        None - read-only operation
        
    Performance:
        O(n) where n = number of files in source directory
        Expected: <100ms for typical directory sizes
    """
```

#### extract_version_from_filename()
```python
def extract_version_from_filename(filename: str) -> str:
    """
    Extract version number from template filename using regex pattern.
    
    Args:
        filename: Template filename (e.g., "FY26 Low Complexity Pricing Tool v1.2.xlsb")
        
    Returns:
        str: Version number (e.g., "1.2")
        
    Raises:
        ValueError: If version pattern not found in filename
        
    Side Effects:
        None - pure function
        
    Performance:
        O(1) - single regex operation
    """
```

#### copy_file_with_metadata()
```python
def copy_file_with_metadata(source: SourceFile, destination: Path) -> OutputFile:
    """
    Copy source file to destination with full metadata preservation.
    
    Args:
        source: Validated source file information
        destination: Target file path (must not exist)
        
    Returns:
        OutputFile: Information about the created file
        
    Raises:
        FileExistsError: If destination file already exists
        PermissionError: If cannot write to destination directory
        OSError: If file copy operation fails
        
    Side Effects:
        Creates new file at destination path
        Preserves original file timestamps and permissions
        
    Performance:
        O(1) relative to file size - streaming copy operation
        Expected: <1s for typical .xlsb files (5-50MB)
    """
```

### cli_interface.py

#### collect_user_input()
```python
def collect_user_input() -> UserInput:
    """
    Prompt user for client name and gig name with validation.
    
    Returns:
        UserInput: Validated user input with sanitized names
        
    Raises:
        KeyboardInterrupt: If user cancels with Ctrl+C
        ValueError: If user provides invalid input after retries
        
    Side Effects:
        Prints prompts to stdout
        Reads from stdin
        May prompt multiple times for invalid input
        
    Performance:
        Depends on user response time
        Validation operations: <1ms
    """
```

#### prompt_for_text()
```python
def prompt_for_text(prompt: str, field_name: str, max_length: int = 50) -> str:
    """
    Prompt user for text input with validation and sanitization.
    
    Args:
        prompt: Text to display to user
        field_name: Name of field for error messages
        max_length: Maximum allowed length
        
    Returns:
        str: Validated and trimmed user input
        
    Raises:
        ValueError: If input is empty after trimming
        KeyboardInterrupt: If user cancels input
        
    Side Effects:
        Prints prompt to stdout
        Reads from stdin
        May re-prompt for invalid input
        
    Performance:
        O(1) for validation operations
    """
```

#### sanitize_user_input()
```python
def sanitize_user_input(text: str) -> str:
    """
    Remove illegal filename characters while preserving readability.
    
    Args:
        text: Raw user input text
        
    Returns:
        str: Sanitized text safe for use in filenames
        
    Side Effects:
        None - pure function
        
    Performance:
        O(n) where n = length of input text
        Expected: <1ms for typical input lengths
    """
```

### naming_utils.py

#### generate_output_filename()
```python
def generate_output_filename(
    user_input: UserInput, 
    source_file: SourceFile, 
    operation_date: datetime
) -> str:
    """
    Generate standardized output filename from inputs.
    
    Args:
        user_input: Validated user input
        source_file: Source template file information
        operation_date: Date for filename timestamp
        
    Returns:
        str: Generated filename following naming convention
        
    Side Effects:
        None - pure function
        
    Performance:
        O(1) - string formatting operations only
    """
```

#### resolve_filename_collision()
```python
def resolve_filename_collision(base_path: Path) -> Path:
    """
    Generate unique filename if collision detected by appending timestamp.
    
    Args:
        base_path: Desired file path that may already exist
        
    Returns:
        Path: Unique file path (original if no collision, timestamped if collision)
        
    Side Effects:
        None - read-only file system check
        
    Performance:
        O(1) - single file existence check
    """
```

#### validate_filename_length()
```python
def validate_filename_length(filename: str, max_length: int = 255) -> bool:
    """
    Validate filename length against system limits.
    
    Args:
        filename: Generated filename to validate
        max_length: Maximum allowed filename length
        
    Returns:
        bool: True if filename length is acceptable
        
    Raises:
        ValueError: If filename exceeds maximum length
        
    Side Effects:
        None - pure function
        
    Performance:
        O(1) - simple length check
    """
```

### system_integration.py

#### open_file_in_finder()
```python
def open_file_in_finder(file_path: Path) -> bool:
    """
    Open Finder with specified file selected (macOS only).
    
    Args:
        file_path: Path to file to select in Finder
        
    Returns:
        bool: True if Finder opened successfully, False otherwise
        
    Raises:
        None - graceful failure handling
        
    Side Effects:
        Launches Finder application
        Changes focus to Finder window
        Selects specified file
        
    Performance:
        Depends on system responsiveness
        Expected: 1-2 seconds for UI operations
    """
```

#### check_system_requirements()
```python
def check_system_requirements() -> Dict[str, bool]:
    """
    Verify system requirements for all features.
    
    Returns:
        Dict[str, bool]: Status of each requirement
            - 'python_version': Python 3.11+ available
            - 'macos': Running on macOS
            - 'source_dir_exists': Source directory exists
            - 'output_dir_writable': Output directory is writable
        
    Side Effects:
        None - read-only system checks
        
    Performance:
        O(1) - simple system property checks
    """
```

#### ensure_output_directory()
```python
def ensure_output_directory(output_dir: Path = Path("20-OUTPUT")) -> bool:
    """
    Ensure output directory exists and is writable.
    
    Args:
        output_dir: Directory to verify/create
        
    Returns:
        bool: True if directory is ready for use
        
    Raises:
        PermissionError: If cannot create directory or no write permission
        
    Side Effects:
        May create directory if it doesn't exist
        
    Performance:
        O(1) - single directory operation
    """
```

## Main Entry Point Contract

### pricing_tool_accelerator.py

#### main()
```python
def main() -> int:
    """
    Main entry point for spreadsheet copy operation.
    
    Returns:
        int: Exit code (0 = success, 1 = error)
        
    Side Effects:
        - Prompts user for input
        - Creates new spreadsheet file
        - Opens Finder with file selected
        - Prints status messages
        
    Error Handling:
        All exceptions caught and converted to user-friendly messages
        Exit code indicates success/failure for shell integration
    """
```

## Error Handling Contracts

### Common Error Types
All functions use consistent error handling patterns:

```python
class TemplateError(Exception):
    """Errors related to template file operations"""
    pass

class UserInputError(Exception):
    """Errors related to user input validation"""
    pass

class SystemError(Exception):
    """Errors related to system operations"""
    pass
```

### Error Response Format
```python
@dataclass
class OperationResult:
    """Standardized result format for all operations"""
    success: bool
    data: Optional[Any] = None
    error_message: Optional[str] = None
    error_type: Optional[str] = None
```

## Integration Contracts

### Module Dependencies
```
cli_interface.py     → No dependencies (stdlib only)
naming_utils.py      → No dependencies (stdlib only) 
file_operations.py   → Depends on: naming_utils
system_integration.py → Depends on: file_operations
main entry point     → Depends on: all modules
```

### Data Flow Contracts
```
UserInput → naming_utils → filename generation
SourceFile → file_operations → file discovery/validation  
UserInput + SourceFile → file_operations → OutputFile
OutputFile → system_integration → Finder integration
```

## Performance Contracts

### Response Time Requirements
- **User Input Collection**: Immediate response to prompts
- **File Discovery**: <100ms for typical directories
- **File Copy**: <1s per file for typical .xlsb sizes
- **Finder Integration**: <2s for UI operations

### Memory Usage
- **Peak Memory**: <50MB during operation
- **Streaming Operations**: No full file loading into memory
- **Cleanup**: All temporary resources released after operation

### Scalability Considerations
- Single file operations only (no batch processing in this feature)
- Directory scanning limited to template files only
- No persistent state or caching required

## Testing Contracts

### Unit Test Requirements
Each function must have tests covering:
- Happy path with valid inputs
- Error conditions with invalid inputs  
- Edge cases and boundary conditions
- Performance within specified limits

### Integration Test Requirements
- End-to-end workflow testing
- File system integration testing
- User interface integration testing
- Error scenario testing

### Mock Requirements
- File system operations must be mockable
- User input must be mockable
- System commands must be mockable
- Time/date functions must be mockable