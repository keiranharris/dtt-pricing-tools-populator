"""
CLI interface utilities for the DTT Pricing Tool Accelerator.

This module provides atomic functions for user input collection and validation,
following the project constitution principles and SpecKit data models.

Feature 003: Implements extensible CLI field collection using configuration-driven approach.
Feature 004: Adds start date and duration field collection with flexible input parsing.
"""

from datetime import datetime, timedelta
import re
from typing import Optional, Union, Dict

from naming_utils import sanitize_user_input
from margin_validator import validate_margin_input, get_margin_prompt_text, get_margin_error_help
from data_models import (
    CLIFieldConfig, 
    CLIFieldValue, 
    CLICollectionResult, 
    UserInput,
    OperationError,
    ErrorType
)

# Feature 004: Date calculation functions
def calculate_default_start_date() -> str:
    """
    Calculate default start date as next business day after 4 weeks from current date.
    
    Returns:
        Formatted date string in DD/MM/YY format with day name for clarity
        
    Example:
        Current date: 12/10/25 (Sunday)
        4 weeks later: 09/11/25 (Sunday) 
        Next business day: 10/11/25 (Monday)
        Returns: "10/11/25 (Monday - next business day after 4 weeks)"
    """
    current_date = datetime.now().date()
    future_date = current_date + timedelta(weeks=4)
    
    # Find next business day (Monday=0, Sunday=6)
    days_to_add = 0
    while (future_date + timedelta(days=days_to_add)).weekday() > 4:  # 5=Saturday, 6=Sunday
        days_to_add += 1
    
    business_date = future_date + timedelta(days=days_to_add)
    day_name = business_date.strftime("%A")
    
    return f"{business_date.strftime('%d/%m/%y')} ({day_name} - next business day after 4 weeks)"


def parse_date_input(date_string: str) -> Optional[datetime]:
    """
    Parse date string with flexible format support.
    
    Supports formats: DD/MM/YY, DD-MM-YY, DD.MM.YY
    
    Args:
        date_string: User input date string
        
    Returns:
        Parsed datetime object or None if parsing fails
        
    Example:
        >>> parse_date_input("15/11/25")
        datetime(2025, 11, 15)
        >>> parse_date_input("15-11-25")  
        datetime(2025, 11, 15)
        >>> parse_date_input("invalid")
        None
    """
    if not date_string or not date_string.strip():
        return None
    
    # Clean input and try different separators
    cleaned = date_string.strip()
    
    # Try different date formats
    formats = ['%d/%m/%y', '%d-%m-%y', '%d.%m.%y']
    
    for date_format in formats:
        try:
            parsed_date = datetime.strptime(cleaned, date_format)
            # Ensure year is in 2000s (strptime uses 1900s for 2-digit years < 69)
            if parsed_date.year < 2000:
                parsed_date = parsed_date.replace(year=parsed_date.year + 100)
            return parsed_date
        except ValueError:
            continue
    
    return None


def validate_duration_input(duration_string: str) -> bool:
    """
    Validate duration input as integer between 1-52 weeks.
    
    Args:
        duration_string: User input duration string
        
    Returns:
        True if valid integer between 1-52, False otherwise
        
    Example:
        >>> validate_duration_input("12")
        True
        >>> validate_duration_input("53")
        False
        >>> validate_duration_input("abc")
        False
    """
    if not duration_string or not duration_string.strip():
        return False
    
    try:
        duration = int(duration_string.strip())
        return 1 <= duration <= 52
    except ValueError:
        return False


# CLI Fields Configuration - Using SpecKit data models
CLI_FIELDS_CONFIG: Dict[str, CLIFieldConfig] = {
    "Client Name": CLIFieldConfig(
        prompt="Enter Client Name:",
        field_key="client_name",
        required=True,
        max_length=50,
        error_empty="❌ Client name cannot be empty. Please try again.",
        error_invalid="❌ Client name contains only invalid characters. Please try again."
    ),
    "Opportunity Name": CLIFieldConfig(
        prompt="Enter Opportunity Name:",
        field_key="opportunity_name",
        required=True,
        max_length=50,
        error_empty="❌ Opportunity name cannot be empty. Please try again.",
        error_invalid="❌ Opportunity name contains only invalid characters. Please try again."
    ),
    "Start Date (DD/MM/YY)": CLIFieldConfig(
        prompt="Enter Start Date (DD/MM/YY) [default: {default}]:",
        field_key="start_date",
        required=True,
        default_generator=calculate_default_start_date,
        validator=lambda x: parse_date_input(x) is not None,
        error_empty="❌ Using default start date.",
        error_invalid="❌ Invalid date format. Please use DD/MM/YY, DD-MM-YY, or DD.MM.YY (e.g., 15/11/25, 15-11-25, 15.11.25)"
    ),
    "No of Periods (in Weeks)": CLIFieldConfig(
        prompt="Enter No of Periods (in Weeks):",
        field_key="duration_weeks",
        required=True,
        validator=validate_duration_input,
        error_empty="❌ Duration is required. Please enter a number between 1-52.",
        error_invalid="❌ Duration must be a whole number between 1-52 weeks (e.g., 12, 26, 52)"
    )
    # Future fields can be easily added here:
    # "Project Manager": CLIFieldConfig(prompt="Enter Project Manager:", field_key="project_manager", ...)
}


def prompt_for_field(field_name: str) -> CLIFieldValue:
    """
    Prompt the user for any configured field with validation and sanitization.
    
    Args:
        field_name: Name of field from CLI_FIELDS_CONFIG to prompt for
        
    Returns:
        CLIFieldValue with collected and sanitized value
        
    Raises:
        OperationError: If field configuration is invalid
    """
    if field_name not in CLI_FIELDS_CONFIG:
        raise OperationError.invalid_input(field_name, f"Unknown field configuration: {field_name}")
    
    config = CLI_FIELDS_CONFIG[field_name]
    
    # Generate dynamic prompt for fields with default generators
    if config.default_generator:
        default_value = config.default_generator()
        prompt_text = config.prompt.format(default=default_value)
    else:
        prompt_text = config.prompt
    
    while True:
        user_input = input(f"{prompt_text} ").strip()
        
        # Handle empty input - check for default generator
        if not user_input:
            if config.default_generator:
                # Use default value for fields with generators (like dates)
                default_raw = config.default_generator()
                default_value = default_raw.split(" (")[0]  # Extract just the date part
                # Don't print error_empty for date fields - accepting default is normal
                return CLIFieldValue(
                    field_name=field_name,
                    value=default_value,
                    sanitized_value=default_value,
                    collected_at=datetime.now(),
                    used_default=True
                )
            else:
                print(config.error_empty)
                continue
        
        # Validate input if validator provided
        if config.validator and not config.validator(user_input):
            print(config.error_invalid)
            continue
        
        # Sanitize input
        sanitized = sanitize_user_input(user_input)
        
        # Check if sanitized input is still valid
        if not sanitized or not sanitized.strip():
            print(config.error_invalid)
            continue
        
        return CLIFieldValue(
            field_name=field_name,
            value=user_input,
            sanitized_value=sanitized,
            collected_at=datetime.now(),
            used_default=False
        )


def prompt_for_client_name() -> str:
    """
    Prompt the user for client name with validation and sanitization.
    
    Returns:
        Sanitized client name string (guaranteed to be non-empty)
        
    Example:
        Enter Client Name: Acme Corp & Co.
        -> Returns: "Acme Corp  Co"
    """
    return prompt_for_field("Client Name")


def prompt_for_opportunity_name() -> str:
    """
    Prompt the user for opportunity/project name with validation and sanitization.
    
    Returns:
        Sanitized opportunity name string (guaranteed to be non-empty)
        
    Example:
        Enter Opportunity Name: Digital Transformation!
        -> Returns: "Digital Transformation"
    """
    return prompt_for_field("Opportunity Name")


# Legacy function for backward compatibility
def prompt_for_gig_name() -> str:
    """
    Legacy function - redirects to opportunity name prompt.
    
    Returns:
        Sanitized opportunity name string (guaranteed to be non-empty)
    """
    return prompt_for_opportunity_name()


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
    while True:
        try:
            user_input = input(f"{prompt}: ").strip()
            
            if not user_input:
                print(f"❌ {field_name} cannot be empty. Please try again.")
                continue
            
            if len(user_input) > max_length:
                print(f"❌ {field_name} must be {max_length} characters or less. Please try again.")
                continue
            
            # Sanitize input
            sanitized = sanitize_user_input(user_input)
            
            if not sanitized.strip():
                print(f"❌ {field_name} contains only invalid characters. Please try again.")
                continue
            
            return sanitized.strip()
            
        except KeyboardInterrupt:
            print("\n❌ Operation cancelled by user.")
            raise
        except EOFError:
            raise OperationError.invalid_input(field_name, "No input provided")


def validate_user_input(input_text: str) -> bool:
    """
    Validate that user input is acceptable (non-empty after sanitization).
    
    Args:
        input_text: Raw user input to validate
        
    Returns:
        True if input is valid, False otherwise
        
    Example:
        >>> validate_user_input("Valid Input")
        True
        >>> validate_user_input("")
        False
        >>> validate_user_input("!@#$%")
        False
    """
    if not input_text or not input_text.strip():
        return False
    
    sanitized = sanitize_user_input(input_text)
    return bool(sanitized and sanitized.strip())


def collect_cli_fields() -> CLICollectionResult:
    """
    Collect all configured CLI fields from user using extensible design.
    
    Returns:
        CLICollectionResult with collected field values and metadata
        
    Example:
        >>> result = collect_cli_fields()
        Enter Client Name: Acme Corp
        Enter Opportunity Name: Digital Transform
        >>> print(result.as_dict())
        {"Client Name": "Acme Corp", "Opportunity Name": "Digital Transform"}
    """
    print("\n📋 Please provide the following information:")
    print("   (Special characters will be automatically removed)")
    
    collection_started = datetime.now()
    fields = {}
    
    for field_name in CLI_FIELDS_CONFIG.keys():
        field_value = prompt_for_field(field_name)
        fields[field_name] = field_value
    
    return CLICollectionResult(
        fields=fields,
        collection_started=collection_started,
        collection_completed=datetime.now(),
        success=True
    )


def collect_user_inputs() -> UserInput:
    """
    Collect user inputs and return as structured UserInput data model.
    
    Returns:
        UserInput with validated client name and gig name
        
    Example:
        >>> user_input = collect_user_inputs()
        Enter Client Name: Acme Corp
        Enter Opportunity Name: Digital Transform
        >>> print(user_input.client_name, user_input.gig_name)
        "Acme Corp" "Digital Transform"
    """
    result = collect_cli_fields()
    client_name = result.fields["Client Name"].sanitized_value
    gig_name = result.fields["Opportunity Name"].sanitized_value
    
    return UserInput(client_name=client_name, gig_name=gig_name)


def collect_margin_percentage() -> float:
    """
    Collect client margin percentage from user with validation and retry logic.
    
    Prompts user for margin percentage (35-65%) with validation loop.
    Continues prompting until valid input is provided.
    
    Returns:
        Validated margin percentage as decimal (e.g., 0.45 for 45%)
        
    Example:
        >>> margin = collect_margin_percentage()
        Enter client margin percentage (35-65%):
          Examples: 45, 45%, 42.5, 42.5%
          Range: 35% to 65% inclusive
        Margin: 45%
        >>> print(margin)  # 0.45
    """
    print("\n📊 Client Margin Configuration")
    print("=" * 40)
    
    while True:
        try:
            # Get user input
            user_input = input(get_margin_prompt_text()).strip()
            
            # Validate input
            result = validate_margin_input(user_input)
            
            if result.is_valid:
                # Success - show confirmation and return
                margin_pct = result.decimal_value * 100
                print(f"✅ Confirmed: {margin_pct:.1f}% client margin")
                return result.decimal_value
            else:
                # Invalid input - show error and retry
                print(get_margin_error_help())
                print(f"🔄 Please try again...")
                
        except KeyboardInterrupt:
            print("\n\n⚠️  Operation cancelled by user")
            raise
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            print("🔄 Please try again...")
            continue