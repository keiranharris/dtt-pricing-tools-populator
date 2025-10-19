# Data Model: Spreadsheet Copy and Instantiation

**Feature**: 001-spreadsheet-copy  
**Phase**: 1 - Architecture Design  
**Date**: 2025-10-12  
**Input**: Research findings and requirements from spec.md

## Core Data Entities

### UserInput
**Purpose**: Represents user-provided information for spreadsheet customization

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class UserInput:
    """User-provided information for spreadsheet customization"""
    client_name: str
    gig_name: str
    
    def __post_init__(self):
        """Validate required fields are provided"""
        if not self.client_name or not self.client_name.strip():
            raise ValueError("Client name is required")
        if not self.gig_name or not self.gig_name.strip():
            raise ValueError("Gig name is required")
    
    @property
    def sanitized_client_name(self) -> str:
        """Client name with illegal filename characters removed"""
        return _sanitize_filename_component(self.client_name)
    
    @property
    def sanitized_gig_name(self) -> str:
        """Gig name with illegal filename characters removed"""
        return _sanitize_filename_component(self.gig_name)
```

### SourceFile
**Purpose**: Represents the template file to be copied

```python
from pathlib import Path
from dataclasses import dataclass

@dataclass
class SourceFile:
    """Template file information and metadata"""
    path: Path
    original_name: str
    version: str
    file_size: int
    
    @classmethod
    def from_discovery(cls, source_path: Path) -> 'SourceFile':
        """Create SourceFile from discovered template file"""
        if not source_path.exists():
            raise FileNotFoundError(f"Source file not found: {source_path}")
        
        return cls(
            path=source_path,
            original_name=source_path.name,
            version=_extract_version(source_path.name),
            file_size=source_path.stat().st_size
        )
    
    @property
    def formatted_version(self) -> str:
        """Version formatted for output filename (e.g., 'V1.2')"""
        return f"V{self.version}"
```

### OutputFile
**Purpose**: Represents the created spreadsheet file and operation result

```python
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class OutputFile:
    """Created file information and operation metadata"""
    path: Path
    filename: str
    created_timestamp: datetime
    collision_suffix: Optional[str] = None
    finder_opened: bool = False
    
    @property
    def success(self) -> bool:
        """True if file was successfully created"""
        return self.path.exists()
    
    @property
    def display_name(self) -> str:
        """Filename for user display"""
        return self.path.name
    
    @property
    def had_collision(self) -> bool:
        """True if filename collision was resolved"""
        return self.collision_suffix is not None
```

### FileOperation
**Purpose**: Represents the complete copy operation with context

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class FileOperation:
    """Complete file copy operation context and results"""
    user_input: UserInput
    source_file: SourceFile
    output_file: Optional[OutputFile]
    operation_date: datetime
    success: bool = False
    error_message: Optional[str] = None
    
    @property
    def generated_filename(self) -> str:
        """Generate output filename based on inputs"""
        date_str = self.operation_date.strftime("%Y%m%d")
        client = self.user_input.sanitized_client_name
        gig = self.user_input.sanitized_gig_name
        version = self.source_file.formatted_version
        return f"{date_str} - {client} - {gig} (LowComp{version}).xlsb"
```

## Data Flow Architecture

### Input Processing Flow
```
CLI Input → UserInput → Validation → Sanitization
```

### File Discovery Flow
```
Source Directory → File Search → SourceFile → Version Extraction
```

### Copy Operation Flow
```
UserInput + SourceFile → Filename Generation → Collision Check → File Copy → OutputFile
```

### System Integration Flow
```
OutputFile → Finder Integration → Operation Complete
```

## Validation Rules

### UserInput Validation
```python
def validate_user_input(client_name: str, gig_name: str) -> UserInput:
    """Validate and create UserInput with proper error handling"""
    # Remove leading/trailing whitespace
    client_clean = client_name.strip() if client_name else ""
    gig_clean = gig_name.strip() if gig_name else ""
    
    # Check for empty inputs
    if not client_clean:
        raise ValueError("Client name cannot be empty")
    if not gig_clean:
        raise ValueError("Gig name cannot be empty")
    
    # Check length limits (conservative Windows path limit consideration)
    if len(client_clean) > 50:
        raise ValueError("Client name too long (max 50 characters)")
    if len(gig_clean) > 50:
        raise ValueError("Gig name too long (max 50 characters)")
    
    return UserInput(client_name=client_clean, gig_name=gig_clean)
```

### SourceFile Validation
```python
def validate_source_file(file_path: Path) -> SourceFile:
    """Validate source file exists and is accessible"""
    if not file_path.exists():
        raise FileNotFoundError(f"Template file not found: {file_path}")
    
    if not file_path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")
    
    if file_path.suffix.lower() != '.xlsb':
        raise ValueError(f"Expected .xlsb file, got: {file_path.suffix}")
    
    # Check file is readable
    try:
        file_path.stat()
    except PermissionError:
        raise PermissionError(f"Cannot read template file: {file_path}")
    
    return SourceFile.from_discovery(file_path)
```

## Error Handling Data

### OperationError
**Purpose**: Structured error information for user feedback

```python
from enum import Enum
from dataclasses import dataclass

class ErrorType(Enum):
    SOURCE_FILE_NOT_FOUND = "source_not_found"
    DESTINATION_NOT_WRITABLE = "destination_not_writable"
    VERSION_EXTRACTION_FAILED = "version_extraction_failed"
    INVALID_USER_INPUT = "invalid_input"
    FILE_COPY_FAILED = "copy_failed"
    SYSTEM_INTEGRATION_FAILED = "system_failed"

@dataclass
class OperationError:
    """Structured error information for user guidance"""
    error_type: ErrorType
    message: str
    technical_details: str
    user_guidance: str
    
    @classmethod
    def source_not_found(cls, expected_path: Path) -> 'OperationError':
        return cls(
            error_type=ErrorType.SOURCE_FILE_NOT_FOUND,
            message="Template file not found",
            technical_details=f"Expected file at: {expected_path}",
            user_guidance="Verify the template file exists in /10-LATEST-PRICING-TOOLS/"
        )
    
    @classmethod
    def invalid_input(cls, field_name: str, reason: str) -> 'OperationError':
        return cls(
            error_type=ErrorType.INVALID_USER_INPUT,
            message=f"Invalid {field_name}",
            technical_details=reason,
            user_guidance=f"Please provide a valid {field_name}"
        )
```

## Data Persistence

### No Persistent Storage Required
- All data is transient and operation-specific
- No database or configuration files needed
- State exists only during operation execution

### File System as Storage
- Input: Template files in `/10-LATEST-PRICING-TOOLS/`
- Output: Generated files in `/20-OUTPUT/`
- No additional data storage requirements

## Configuration Data

### System Constants
```python
from pathlib import Path

class SystemConfig:
    """System-wide configuration constants"""
    SOURCE_DIR = Path("10-LATEST-PRICING-TOOLS")
    OUTPUT_DIR = Path("20-OUTPUT")
    TEMPLATE_PATTERN = "Low Complexity"
    EXPECTED_EXTENSION = ".xlsb"
    DATE_FORMAT = "%Y%m%d"
    TIMESTAMP_FORMAT = "%H%M%S"
    MAX_FILENAME_LENGTH = 255  # Conservative limit
```

## Data Transformation Pipeline

### Input → Filename Transformation
```
"Acme Corp" + "Digital Transform" + "2025-10-12" + "V1.2"
    ↓ sanitization
"Acme Corp" + "Digital Transform" + "20251012" + "V1.2"
    ↓ assembly
"20251012 - Acme Corp - Digital Transform (LowCompV1.2).xlsb"
```

### Collision Resolution Transformation
```
"20251012 - Acme Corp - Digital Transform (LowCompV1.2).xlsb"
    ↓ collision detected
"20251012 - Acme Corp - Digital Transform (LowCompV1.2)_143022.xlsb"
```

## Type System Integration

### Type Hints and Validation
All data models include comprehensive type hints for:
- Static type checking with mypy
- IDE autocompletion and error detection
- Runtime validation where appropriate
- Clear API contracts between modules

### Protocol Definitions
```python
from typing import Protocol

class FileOperationProtocol(Protocol):
    """Protocol for file operation implementations"""
    def copy_file(self, source: SourceFile, destination: Path) -> OutputFile:
        ...
    
    def discover_template(self, source_dir: Path) -> SourceFile:
        ...
```

This data model provides the foundation for type-safe, well-structured implementation of the spreadsheet copy functionality.