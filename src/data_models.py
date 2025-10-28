"""
Core Data Models for DTT Pricing Tools Populator

This module defines the fundamental data structures used across all features,
following the SpecKit specifications and constitution principles.

Features:
- 001: Spreadsheet copy data models (UserInput, SourceFile, OutputFile)
- 002: Excel data population models (ConstantsData, FieldMatch, PopulationResult)
- 003-004: CLI field models and configuration
- 005-006: Resource and rate card models

Author: DTT Pricing Tool Accelerator
Constitution Compliance: Atomic data structures with comprehensive type hints
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Protocol
from enum import Enum

# =============================================================================
# FEATURE 001: SPREADSHEET COPY DATA MODELS
# =============================================================================

@dataclass
class UserInput:
    """User-provided information for spreadsheet customization"""
    client_name: str
    gig_name: str
    
    def __post_init__(self) -> None:
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


@dataclass
class OutputFile:
    """Created spreadsheet file and operation result"""
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


@dataclass
class FileOperation:
    """Complete file copy operation with context"""
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


# =============================================================================
# FEATURE 002: EXCEL DATA POPULATION DATA MODELS
# =============================================================================

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
        
        # Import here to avoid circular dependencies
        from excel_constants_reader import read_field_mappings
        mappings = read_field_mappings(file_path)
        
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


@dataclass
class CellLocation:
    """Represents a cell location in an Excel worksheet"""
    row: int
    column: int
    cell_reference: str  # e.g., "B15"
    content: str = ""  # The actual text content of the cell
    
    def __str__(self) -> str:
        return f"Cell {self.cell_reference} (Row {self.row}, Col {self.column}): '{self.content}'"


@dataclass
class FieldMatch:
    """Represents a matched field between source constants and target spreadsheet"""
    source_field: str           # Field name from constants file
    target_location: CellLocation  # Target cell location
    confidence: float           # Confidence score 0.0-1.0
    source_value: str           # Value from constants file
    match_method: str           # Algorithm used ("core_content", "sequence_match", etc.)
    
    def __str__(self) -> str:
        return f"Match: '{self.source_field}' -> {self.target_location} (confidence: {self.confidence:.1%})"
    
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
    
    @property
    def can_populate(self) -> bool:
        """True if field can be populated with data"""
        return (self.is_writable and 
                self.field_type in [FieldType.TEXT, FieldType.DROPDOWN])


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


@dataclass
class FieldPopulationResult:
    """Simple result of field population operations (used by excel_data_populator)"""
    successful_fields: int = 0
    failed_fields: int = 0
    total_fields: int = 0
    error_messages: List[str] = field(default_factory=list)
    populated_fields: List[str] = field(default_factory=list)
    
    def __str__(self) -> str:
        """Human-readable summary"""
        return f"Populated {self.successful_fields}/{self.total_fields} fields ({self.successful_fields/self.total_fields*100:.1f}% success)" if self.total_fields > 0 else "No fields to populate"


@dataclass 
class PopulationResult:
    """Complete result of data population session"""
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


@dataclass
class PopulationSummary:
    """Comprehensive summary of data population operation"""
    constants_file_found: bool
    constants_loaded: int
    fields_matched: int
    fields_populated: int
    execution_time_seconds: float
    errors: List[str]
    warnings: List[str]
    
    def __str__(self) -> str:
        status = "SUCCESS" if self.fields_populated > 0 else "PARTIAL" if self.fields_matched > 0 else "FAILED"
        return f"Population Summary [{status}]: {self.fields_populated} fields populated in {self.execution_time_seconds:.1f}s"


# =============================================================================
# FEATURES 003-004: CLI FIELD DATA MODELS
# =============================================================================

@dataclass
class CLIFieldConfig:
    """Configuration for a single CLI field"""
    prompt: str
    field_key: str
    required: bool = True
    max_length: int = 50
    validator: Optional[callable] = None
    default_generator: Optional[callable] = None
    error_empty: str = "This field is required"
    error_invalid: str = "Invalid input format"


@dataclass
class CLIFieldValue:
    """Value collected from CLI with metadata"""
    field_name: str
    value: str
    sanitized_value: str
    collected_at: datetime
    used_default: bool = False
    
    @property
    def is_valid(self) -> bool:
        """True if value is valid and usable"""
        return bool(self.sanitized_value.strip())


@dataclass 
class CLICollectionResult:
    """Result of CLI field collection process"""
    fields: Dict[str, CLIFieldValue]
    collection_started: datetime
    collection_completed: datetime
    success: bool = True
    
    @property
    def as_dict(self) -> Dict[str, str]:
        """Convert to simple dictionary for backward compatibility"""
        return {name: field.sanitized_value for name, field in self.fields.items()}


# =============================================================================
# ERROR HANDLING DATA MODELS
# =============================================================================

class ErrorType(Enum):
    FILE_NOT_FOUND = "file_not_found"
    SOURCE_FILE_NOT_FOUND = "source_not_found"
    DESTINATION_NOT_WRITABLE = "destination_not_writable"
    VERSION_EXTRACTION_FAILED = "version_extraction_failed"
    INVALID_USER_INPUT = "invalid_input"
    FILE_COPY_FAILED = "copy_failed"
    SYSTEM_INTEGRATION_FAILED = "system_failed"
    CONSTANTS_FILE_NOT_FOUND = "constants_not_found"
    TARGET_FILE_ACCESS_ERROR = "target_access_error"
    SHEET_NOT_FOUND = "sheet_not_found"
    FIELD_WRITE_ERROR = "field_write_error"
    MATCH_CONFIDENCE_LOW = "match_confidence_low"
    PERMISSION_DENIED = "permission_denied"
    FILE_CORRUPTION = "file_corruption"


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
    
    @classmethod
    def file_not_found(cls, file_path: str, reason: str) -> 'OperationError':
        return cls(
            error_type=ErrorType.FILE_NOT_FOUND,
            message="File not found",
            technical_details=f"File: {file_path}. {reason}",
            user_guidance="Please check the file path and ensure the file exists"
        )
    
    @classmethod
    def permission_denied(cls, file_path: str, reason: str) -> 'OperationError':
        return cls(
            error_type=ErrorType.PERMISSION_DENIED,
            message="Permission denied",
            technical_details=f"File: {file_path}. {reason}",
            user_guidance="Please check file permissions and try again"
        )


# =============================================================================
# FEATURE 005: RESOURCE SETUP DATA MODELS
# =============================================================================

@dataclass
class ResourceCopyResult:
    """Results from resource setup range copying"""
    cells_copied: int
    source_range: str
    target_range: str
    success: bool
    error_messages: List[str]
    execution_time: float
    
    def __str__(self) -> str:
        status = "SUCCESS" if self.success else "FAILED"
        return f"Resource Copy [{status}]: {self.cells_copied} cells copied in {self.execution_time:.1f}s"


@dataclass  
class ValidationResult:
    """Validation results for resource setup prerequisites"""
    constants_file_exists: bool
    target_file_writeable: bool
    source_worksheet_exists: bool
    target_worksheet_exists: bool
    error_messages: List[str]
    
    @property
    def is_valid(self) -> bool:
        """True if all validations passed"""
        return (self.constants_file_exists and 
                self.target_file_writeable and 
                self.source_worksheet_exists and 
                self.target_worksheet_exists)
    
    def __str__(self) -> str:
        status = "VALID" if self.is_valid else "INVALID"
        return f"Validation [{status}]: {len(self.error_messages)} issues found"


# =============================================================================
# CONFIGURATION DATA MODELS
# =============================================================================

@dataclass
class PopulationConfig:
    """Configuration for data population operations"""
    constants_filename: str = "lowcomplexity_const_KHv1.xlsx"
    constants_directory: Path = None  # Will use centralized constant if None
    target_sheet_name: str = "Pricing Setup"
    match_threshold: float = 0.65
    enable_population: bool = True
    log_all_matches: bool = True
    backup_before_population: bool = False
    
    @property
    def constants_file_path(self) -> Path:
        """Full path to constants file"""
        # Use centralized constant if none specified
        if self.constants_directory is None:
            from constants import get_constants_directory
            constants_dir = Path(get_constants_directory()).expanduser()
        else:
            constants_dir = self.constants_directory
        return constants_dir / self.constants_filename
    
    def validate(self) -> List[str]:
        """Validate configuration and return any issues"""
        issues = []
        
        # Get the actual constants directory (with default handling)
        if self.constants_directory is None:
            from constants import get_constants_directory
            constants_dir = Path(get_constants_directory()).expanduser()
        else:
            constants_dir = self.constants_directory
        
        if not constants_dir.exists():
            issues.append(f"Constants directory not found: {constants_dir}")
        
        if not self.constants_file_path.exists():
            issues.append(f"Constants file not found: {self.constants_file_path}")
        
        if not 0.0 <= self.match_threshold <= 1.0:
            issues.append(f"Match threshold must be 0.0-1.0, got: {self.match_threshold}")
        
        return issues


# =============================================================================
# PROTOCOL DEFINITIONS
# =============================================================================

class FileOperationProtocol(Protocol):
    """Protocol for file operation implementations"""
    def copy_file(self, source: SourceFile, destination: Path) -> OutputFile:
        ...
    
    def discover_template(self, source_dir: Path) -> SourceFile:
        ...


class FieldMatcherProtocol(Protocol):
    """Protocol for field matching implementations"""
    def match_fields(self, constants_data: ConstantsData, target_fields: List[TargetField]) -> List[FieldMatch]:
        ...
    
    def calculate_match_score(self, source: str, target: str) -> float:
        ...


class DataPopulatorProtocol(Protocol):
    """Protocol for data population implementations"""
    def populate_fields(self, field_matches: List[FieldMatch], target_file: Path) -> List[PopulationOperation]:
        ...


class CLIInputProtocol(Protocol):
    """Protocol for CLI input collection implementations"""
    def collect_user_inputs(self) -> UserInput:
        ...
    
    def validate_input(self, input_text: str) -> bool:
        ...


class ValidationProtocol(Protocol):
    """Protocol for validation implementations"""
    def validate(self, data: Any) -> bool:
        ...
    
    def get_error_message(self) -> Optional[str]:
        ...


# =============================================================================
# FEATURE 006: MARGIN VALIDATION DATA MODELS
# =============================================================================

@dataclass
class MarginValidationResult:
    """Result of margin validation operation"""
    is_valid: bool
    decimal_value: Optional[float] = None
    error_message: Optional[str] = None
    
    def __str__(self) -> str:
        if self.is_valid:
            return f"Valid margin: {self.decimal_value:.3f} ({self.decimal_value * 100:.1f}%)"
        return f"Invalid margin: {self.error_message}"


@dataclass
class StandardCostRate:
    """Represents a standard cost rate for a staff level"""
    staff_level: str
    cost_rate: Optional[float] = None
    row_index: Optional[int] = None
    is_valid: bool = False
    error_message: Optional[str] = None
    cell_reference: Optional[str] = None
    
    def __str__(self) -> str:
        if self.is_valid and self.cost_rate is not None:
            return f"{self.staff_level}: ${self.cost_rate:.2f}"
        return f"{self.staff_level}: {self.error_message or 'Invalid'}"


@dataclass  
class EngineeringRate:
    """Represents a calculated engineering rate for a staff level"""
    staff_level: str
    standard_cost_rate: Optional[float] = None
    client_margin: Optional[float] = None
    engineering_rate: Optional[float] = None
    row_index: Optional[int] = None
    is_valid: bool = False
    error_message: Optional[str] = None
    cell_reference: Optional[str] = None
    
    def __str__(self) -> str:
        if self.is_valid and self.engineering_rate is not None:
            margin_pct = self.client_margin * 100 if self.client_margin else 0
            return f"{self.staff_level}: ${self.engineering_rate:.2f} (margin {margin_pct:.1f}%)"
        return f"{self.staff_level}: {self.error_message or 'Invalid'}"


@dataclass
class RateCalculationResult:
    """Result of rate calculation operation"""
    calculated_rates: List[EngineeringRate]
    total_processed: int
    successful_calculations: int
    skipped_invalid: int
    errors: List[str]
    
    def __str__(self) -> str:
        success_rate = (self.successful_calculations / self.total_processed * 100) if self.total_processed > 0 else 0
        return f"Rate Calculation: {self.successful_calculations}/{self.total_processed} successful ({success_rate:.1f}%)"


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def _sanitize_filename_component(text: str) -> str:
    """Remove illegal filename characters while preserving readability"""
    import re
    # Remove illegal filename characters
    cleaned = re.sub(r'[<>:"|?*\\/]', '', text)
    # Replace multiple spaces with single space
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned.strip()


def _extract_version(filename: str) -> str:
    """Extract version number from filename using regex pattern"""
    import re
    match = re.search(r'v(\d+\.\d+)', filename.lower())
    if match:
        return match.group(1)
    raise ValueError(f"Could not extract version from filename: {filename}")