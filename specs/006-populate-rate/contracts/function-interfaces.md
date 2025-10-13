# Function Contracts: Rate Card Calculator

**Feature**: 006-populate-rate  
**Date**: 2025-10-13  
**Purpose**: Define function interfaces for rate card calculation components

## CLI Interface Extensions

### collect_margin_percentage()
```python
def collect_margin_percentage() -> int:
    """
    Collect client margin percentage from user via CLI prompt.
    
    Returns:
        int: Validated margin percentage between 35-65 inclusive
        
    Raises:
        KeyboardInterrupt: If user cancels input (Ctrl+C)
        
    Behavior:
        - Prompts with "Client Margin %:"  
        - Validates input is whole number 35-65
        - Re-prompts on invalid input with clear error message
        - Loops until valid input received
    """
```

## Margin Validation

### validate_margin_input()
```python
def validate_margin_input(user_input: str) -> tuple[bool, int | None, str]:
    """
    Validate user-provided margin percentage string.
    
    Args:
        user_input: Raw string input from CLI
        
    Returns:
        tuple containing:
        - bool: True if valid, False otherwise
        - int | None: Parsed integer value if valid, None if invalid
        - str: Error message if invalid, empty string if valid
        
    Validation Rules:
        - Must be convertible to integer
        - Must be between 35 and 65 inclusive
        - No decimal places allowed
    """
```

### convert_margin_to_decimal()
```python
def convert_margin_to_decimal(percentage: int) -> float:
    """
    Convert margin percentage to decimal for calculation.
    
    Args:
        percentage: Validated margin percentage (35-65)
        
    Returns:
        float: Decimal representation (0.35-0.65)
        
    Example:
        convert_margin_to_decimal(44) -> 0.44
    """
```

## Rate Calculation Core

### calculate_engineering_rate()
```python
def calculate_engineering_rate(cost_rate: float, margin_decimal: float) -> float:
    """
    Calculate engineering rate using standard formula.
    
    Args:
        cost_rate: Standard cost rate from source data
        margin_decimal: Client margin as decimal (0.35-0.65)
        
    Returns:
        float: Calculated engineering rate rounded to 2 decimal places
        
    Formula:
        rate = cost_rate / (1 - margin_decimal)
        
    Example:
        calculate_engineering_rate(100.00, 0.40) -> 166.67
    """
```

### process_rate_card_batch()
```python
def process_rate_card_batch(
    cost_rates: dict[str, float], 
    margin_decimal: float
) -> dict[str, float | None]:
    """
    Process entire rate card calculation for all staff levels.
    
    Args:
        cost_rates: Dict mapping cell references to cost values
                   e.g., {"Q28": 100.0, "Q29": 120.0, ...}
        margin_decimal: Client margin as decimal (0.35-0.65)
        
    Returns:
        dict: Mapping cell references to calculated rates or None for invalid
             e.g., {"O28": 166.67, "O29": 200.0, "O30": None, ...}
             
    Behavior:
        - Processes each cost rate individually
        - Skips invalid/None cost rates  
        - Returns None for skipped calculations
        - Logs skipped cells for user feedback
    """
```

## Excel Integration

### read_cost_rates_from_excel()
```python
def read_cost_rates_from_excel(
    workbook_path: str, 
    worksheet_name: str = "Resource Setup"
) -> dict[str, float | None]:
    """
    Read standard cost rates from Excel worksheet column Q.
    
    Args:
        workbook_path: Absolute path to Excel workbook
        worksheet_name: Name of worksheet containing cost data
        
    Returns:
        dict: Mapping cell references to cost values or None if invalid
             e.g., {"Q28": 100.0, "Q29": None, "Q30": 150.0, ...}
             
    Raises:
        FileNotFoundError: If workbook doesn't exist
        WorksheetNotFoundError: If worksheet doesn't exist
        ExcelAccessError: If Excel automation fails
        
    Behavior:
        - Reads cells Q28 through Q34
        - Validates each cell contains numeric data
        - Returns None for invalid/empty cells
        - Uses existing Excel application instance
    """
```

### write_rates_to_excel()
```python
def write_rates_to_excel(
    workbook_path: str,
    calculated_rates: dict[str, float],
    worksheet_name: str = "Resource Setup"
) -> int:
    """
    Write calculated engineering rates to Excel worksheet column O.
    
    Args:
        workbook_path: Absolute path to Excel workbook
        calculated_rates: Dict mapping target cells to calculated values
                         e.g., {"O28": 166.67, "O29": 200.0, ...}
        worksheet_name: Name of worksheet to write to
        
    Returns:
        int: Number of cells successfully written
        
    Raises:
        FileNotFoundError: If workbook doesn't exist
        WorksheetNotFoundError: If worksheet doesn't exist
        ExcelAccessError: If Excel automation fails
        
    Behavior:
        - Writes to cells O28 through O34
        - Overwrites existing data without warning
        - Skips None values (doesn't write anything)
        - Uses existing Excel application instance
        - Formats values as currency with 2 decimal places
    """
```

## Orchestration Integration

### populate_rate_card_with_margin()
```python
def populate_rate_card_with_margin(
    workbook_path: str,
    margin_percentage: int
) -> ProcessingResult:
    """
    Main orchestration function for rate card population.
    
    Args:
        workbook_path: Absolute path to Excel workbook
        margin_percentage: Validated margin percentage (35-65)
        
    Returns:
        ProcessingResult: Detailed results of operation including:
                         - successful_calculations: int
                         - skipped_cells: List[str] 
                         - error_details: List[ValidationError]
                         - execution_time_seconds: float
                         - overall_status: str
                         
    Raises:
        DependencyError: If Feature 005 Resource Setup not completed
        
    Behavior:
        - Converts margin to decimal
        - Reads cost rates from Excel
        - Calculates engineering rates  
        - Writes results back to Excel
        - Provides comprehensive feedback
        - Times operation for performance metrics
    """
```

## Error Contracts

### ProcessingResult
```python
@dataclass
class ProcessingResult:
    """Result container for rate card processing operations."""
    successful_calculations: int
    skipped_cells: list[str]
    error_details: list[ValidationError] 
    execution_time_seconds: float
    overall_status: str  # "success", "partial_success", "failed"
```

### ValidationError  
```python
@dataclass
class ValidationError:
    """Container for validation failure information."""
    entity_type: str
    field_name: str
    provided_value: Any
    error_message: str
    recovery_suggestion: str
```

These contracts define the complete interface for the rate card calculation feature, ensuring atomic functions with clear responsibilities, comprehensive error handling, and integration with the existing Excel automation infrastructure.