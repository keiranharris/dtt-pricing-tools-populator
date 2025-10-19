# Data Model: Excel Data Population from Constants

**Feature**: 002-excel-data-population  
**Phase**: 1 - Architecture Design  
**Date**: 2025-10-12  
**Input**: Research findings and requirements from spec.md

## Core Data Entities

### ConstantsData
**Purpose**: Represents data read from the constants file

```python
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

@dataclass
class ConstantsData:
    """Data structure for constants file information"""
    file_path: Path
    field_mappings: Dict[str, str]  # field_name -> field_value
    sheet_name: str = "Pricing Setup"
    last_modified: Optional[float] = None
    
    @classmethod
    def from_file(cls, file_path: Path) -> 'ConstantsData':
        """Load constants data from Excel file"""
        if not file_path.exists():
            raise FileNotFoundError(f"Constants file not found: {file_path}")
        
        mappings = _read_field_mappings(file_path)
        return cls(
            file_path=file_path,
            field_mappings=mappings,
            sheet_name="Pricing Setup",
            last_modified=file_path.stat().st_mtime
        )
    
    @property
    def field_count(self) -> int:
        """Number of field mappings available"""
        return len(self.field_mappings)
    
    @property
    def is_valid(self) -> bool:
        """True if constants data is loaded and usable"""
        return bool(self.field_mappings)
```

### FieldMatch
**Purpose**: Represents a potential match between constants and target fields

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class FieldMatch:
    """Information about a field matching attempt"""
    source_field_name: str      # Field name from constants file
    source_value: str           # Value from constants file
    target_field_name: str      # Matched field name in target
    target_cell_address: str    # Excel cell coordinate (e.g., "B15")
    match_confidence: float     # Confidence score 0.0-1.0
    match_method: str           # Algorithm used ("core_content", "sequence_match", etc.)
    
    @property
    def is_high_confidence(self) -> bool:
        """True if match confidence is above threshold"""
        return self.match_confidence >= 0.80
    
    @property
    def is_acceptable(self) -> bool:
        """True if match is acceptable for automatic population"""
        return self.match_confidence >= 0.65
    
    def __str__(self) -> str:
        """Human-readable match description"""
        return f"{self.source_field_name} -> {self.target_field_name} ({self.match_confidence:.2f})"
```

### TargetField
**Purpose**: Represents a field discovered in the target spreadsheet

```python
from dataclasses import dataclass
from enum import Enum

class FieldType(Enum):
    TEXT = "text"
    DROPDOWN = "dropdown"
    FORMULA = "formula"
    PROTECTED = "protected"

@dataclass
class TargetField:
    """Information about a field in the target spreadsheet"""
    field_name: str
    cell_address: str
    field_type: FieldType
    current_value: Optional[str] = None
    has_validation: bool = False
    is_writable: bool = True
    
    @classmethod
    def from_cell(cls, cell, cell_address: str) -> 'TargetField':
        """Create TargetField from Excel cell object"""
        field_type = _detect_field_type(cell)
        return cls(
            field_name=str(cell.value) if cell.value else "",
            cell_address=cell_address,
            field_type=field_type,
            current_value=str(cell.value) if cell.value else None,
            has_validation=bool(cell.data_validation),
            is_writable=not cell.protection.locked
        )
    
    @property
    def can_populate(self) -> bool:
        """True if field can be populated with data"""
        return (self.is_writable and 
                self.field_type in [FieldType.TEXT, FieldType.DROPDOWN])
```

### PopulationOperation
**Purpose**: Represents a single data population operation

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class PopulationOperation:
    """Information about a field population operation"""
    field_match: FieldMatch
    target_field: TargetField
    attempted_at: datetime
    success: bool = False
    error_message: Optional[str] = None
    previous_value: Optional[str] = None
    
    @property
    def was_overwritten(self) -> bool:
        """True if an existing value was overwritten"""
        return (self.previous_value is not None and 
                self.previous_value.strip() != "")
    
    def __str__(self) -> str:
        """Human-readable operation description"""
        status = "✓" if self.success else "✗"
        return f"{status} {self.field_match.source_field_name} -> {self.field_match.target_field_name}"
```

### PopulationResult
**Purpose**: Represents the complete result of a data population session

```python
from dataclasses import dataclass
from typing import List, Dict
from datetime import datetime

@dataclass
class PopulationResult:
    """Complete result of data population operation"""
    constants_data: ConstantsData
    target_file_path: Path
    operations: List[PopulationOperation]
    started_at: datetime
    completed_at: Optional[datetime] = None
    overall_success: bool = False
    
    @property
    def successful_operations(self) -> List[PopulationOperation]:
        """Operations that completed successfully"""
        return [op for op in self.operations if op.success]
    
    @property
    def failed_operations(self) -> List[PopulationOperation]:
        """Operations that failed"""
        return [op for op in self.operations if not op.success]
    
    @property
    def success_rate(self) -> float:
        """Percentage of successful operations"""
        if not self.operations:
            return 0.0
        return len(self.successful_operations) / len(self.operations) * 100
    
    @property
    def summary(self) -> str:
        """Human-readable summary"""
        total = len(self.operations)
        successful = len(self.successful_operations)
        return f"Populated {successful}/{total} fields ({self.success_rate:.1f}% success)"
```

## Configuration Data Models

### PopulationConfig
**Purpose**: Configuration settings for the population process

```python
from dataclasses import dataclass
from pathlib import Path

@dataclass
class PopulationConfig:
    """Configuration for data population operations"""
    constants_filename: str = "lowcomplexity_const_KHv1.xlsx"
    constants_directory: Path = Path("00-CONSTANTS")
    target_sheet_name: str = "Pricing Setup"
    match_threshold: float = 0.80
    enable_population: bool = True
    log_all_matches: bool = True
    backup_before_population: bool = False
    
    @property
    def constants_file_path(self) -> Path:
        """Full path to constants file"""
        return self.constants_directory / self.constants_filename
    
    def validate(self) -> List[str]:
        """Validate configuration and return any issues"""
        issues = []
        
        if not self.constants_directory.exists():
            issues.append(f"Constants directory not found: {self.constants_directory}")
        
        if not self.constants_file_path.exists():
            issues.append(f"Constants file not found: {self.constants_file_path}")
        
        if not 0.0 <= self.match_threshold <= 1.0:
            issues.append(f"Match threshold must be 0.0-1.0, got: {self.match_threshold}")
        
        return issues
```

## Matching Algorithm Data

### MatchingStrategy
**Purpose**: Encapsulates field matching algorithms and their parameters

```python
from dataclasses import dataclass
from typing import Callable, Any
from enum import Enum

class MatchingMethod(Enum):
    CORE_CONTENT = "core_content"
    SEQUENCE_MATCH = "sequence_match"
    EXACT_MATCH = "exact_match"
    FUZZY_MATCH = "fuzzy_match"

@dataclass
class MatchingStrategy:
    """Configuration for field matching algorithms"""
    primary_method: MatchingMethod = MatchingMethod.CORE_CONTENT
    fallback_method: MatchingMethod = MatchingMethod.SEQUENCE_MATCH
    case_sensitive: bool = False
    strip_chars: int = 2  # Characters to strip for core content
    min_core_length: int = 4
    
    def calculate_match_score(self, source: str, target: str) -> float:
        """Calculate match score using configured strategy"""
        # Primary method
        score = self._apply_method(self.primary_method, source, target)
        
        # Fallback if primary score is low
        if score < 0.5:
            fallback_score = self._apply_method(self.fallback_method, source, target)
            score = max(score, fallback_score * 0.8)  # Weight fallback lower
        
        return score
    
    def _apply_method(self, method: MatchingMethod, source: str, target: str) -> float:
        """Apply specific matching method"""
        if method == MatchingMethod.CORE_CONTENT:
            return _core_content_match(source, target, self.strip_chars, self.min_core_length)
        elif method == MatchingMethod.SEQUENCE_MATCH:
            return _sequence_match(source, target, self.case_sensitive)
        elif method == MatchingMethod.EXACT_MATCH:
            return _exact_match(source, target, self.case_sensitive)
        else:
            return 0.0
```

## Error Handling Data

### PopulationError
**Purpose**: Structured error information for population failures

```python
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Any

class ErrorType(Enum):
    CONSTANTS_FILE_NOT_FOUND = "constants_not_found"
    TARGET_FILE_ACCESS_ERROR = "target_access_error"
    SHEET_NOT_FOUND = "sheet_not_found"
    FIELD_WRITE_ERROR = "field_write_error"
    MATCH_CONFIDENCE_LOW = "match_confidence_low"
    PERMISSION_DENIED = "permission_denied"
    FILE_CORRUPTION = "file_corruption"

@dataclass
class PopulationError:
    """Structured error information for population failures"""
    error_type: ErrorType
    message: str
    technical_details: str
    field_name: Optional[str] = None
    cell_address: Optional[str] = None
    suggested_action: Optional[str] = None
    
    @classmethod
    def constants_not_found(cls, file_path: Path) -> 'PopulationError':
        return cls(
            error_type=ErrorType.CONSTANTS_FILE_NOT_FOUND,
            message="Constants file not found",
            technical_details=f"Expected file at: {file_path}",
            suggested_action="Verify constants file exists and filename is correct"
        )
    
    @classmethod
    def field_write_failed(cls, field_name: str, cell_address: str, reason: str) -> 'PopulationError':
        return cls(
            error_type=ErrorType.FIELD_WRITE_ERROR,
            message=f"Failed to populate field: {field_name}",
            technical_details=reason,
            field_name=field_name,
            cell_address=cell_address,
            suggested_action="Check field type and permissions"
        )
```

## Data Validation Models

### ValidationRule
**Purpose**: Rules for validating data before population

```python
from dataclasses import dataclass
from typing import Callable, Any, List
from abc import ABC, abstractmethod

@dataclass
class ValidationRule:
    """Rule for validating field data before population"""
    field_pattern: str              # Regex pattern for field names
    value_validator: Callable[[str], bool]  # Function to validate values
    error_message: str              # Message if validation fails
    required: bool = False          # Whether field is required
    
    def applies_to(self, field_name: str) -> bool:
        """True if this rule applies to the given field"""
        import re
        return bool(re.match(self.field_pattern, field_name, re.IGNORECASE))
    
    def validate_value(self, value: str) -> bool:
        """Validate a value using this rule"""
        try:
            return self.value_validator(value)
        except Exception:
            return False

# Predefined validation rules
STANDARD_VALIDATION_RULES = [
    ValidationRule(
        field_pattern=r".*email.*",
        value_validator=lambda v: "@" in v and "." in v,
        error_message="Invalid email format"
    ),
    ValidationRule(
        field_pattern=r".*phone.*",
        value_validator=lambda v: any(c.isdigit() for c in v),
        error_message="Phone number must contain digits"
    ),
    ValidationRule(
        field_pattern=r".*date.*",
        value_validator=lambda v: len(v) >= 6,  # Basic date length check
        error_message="Date format appears invalid"
    )
]
```

## Data Transformation Pipeline

### Pipeline Stages
```
Constants File → ConstantsData → Field Mappings
Target File → Field Discovery → TargetField Collection
Field Mappings + TargetFields → Matching Algorithm → FieldMatch Collection
FieldMatch Collection → Population Operations → PopulationResult
```

### Data Flow Architecture
```python
@dataclass
class PopulationPipeline:
    """Orchestrates the complete data population pipeline"""
    config: PopulationConfig
    matching_strategy: MatchingStrategy
    validation_rules: List[ValidationRule]
    
    def execute(self, target_file_path: Path) -> PopulationResult:
        """Execute complete population pipeline"""
        # Stage 1: Load constants
        constants_data = ConstantsData.from_file(self.config.constants_file_path)
        
        # Stage 2: Discover target fields
        target_fields = self._discover_target_fields(target_file_path)
        
        # Stage 3: Match fields
        field_matches = self._match_fields(constants_data, target_fields)
        
        # Stage 4: Validate and populate
        operations = self._populate_fields(field_matches, target_file_path)
        
        # Stage 5: Generate result
        return PopulationResult(
            constants_data=constants_data,
            target_file_path=target_file_path,
            operations=operations,
            started_at=datetime.now(),
            completed_at=datetime.now(),
            overall_success=all(op.success for op in operations)
        )
```

## Performance Data Models

### PerformanceMetrics
**Purpose**: Track performance characteristics of population operations

```python
@dataclass
class PerformanceMetrics:
    """Performance tracking for population operations"""
    file_open_time: float          # Time to open Excel files
    field_discovery_time: float    # Time to scan for fields
    matching_time: float           # Time for field matching
    population_time: float         # Time to write data
    total_time: float              # Total operation time
    memory_peak: int               # Peak memory usage in MB
    fields_processed: int          # Number of fields processed
    
    @property
    def fields_per_second(self) -> float:
        """Processing rate in fields per second"""
        if self.total_time <= 0:
            return 0.0
        return self.fields_processed / self.total_time
    
    @property
    def is_performant(self) -> bool:
        """True if performance meets requirements"""
        return (self.total_time < 5.0 and       # Under 5 seconds
                self.memory_peak < 100 and       # Under 100MB
                self.fields_per_second > 2)      # At least 2 fields/sec
```

This data model provides a comprehensive foundation for implementing robust, performant Excel data population functionality with clear error handling and extensive configuration options.