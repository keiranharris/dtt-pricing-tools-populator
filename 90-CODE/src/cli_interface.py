"""
CLI interface utilities for the DTT Pricing Tool Accelerator.

This module provides atomic functions for user input collection and validation,
following the project constitution principles.

Feature 003: Implements extensible CLI field collection using configuration-driven approach.
Feature 004: Adds start date and duration field collection with flexible input parsing.
"""

from datetime import datetime, timedelta
import re
from typing import Optional, Union

from naming_utils import sanitize_user_input

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


# CLI Fields Configuration - Extensible design for easy addition of new fields
CLI_FIELDS_CONFIG = {
    "Client Name": {
        "prompt": "Enter Client Name:",
        "field_key": "client_name",
        "error_empty": "❌ Client name cannot be empty. Please try again.",
        "error_invalid": "❌ Client name contains only invalid characters. Please try again."
    },
    "Opportunity Name": {
        "prompt": "Enter Opportunity Name:",
        "field_key": "opportunity_name", 
        "error_empty": "❌ Opportunity name cannot be empty. Please try again.",
        "error_invalid": "❌ Opportunity name contains only invalid characters. Please try again."
    },
    "Start Date (DD/MM/YY)": {
        "prompt_template": "Enter Start Date (DD/MM/YY) [default: {default}]:",
        "field_key": "start_date",
        "default_generator": calculate_default_start_date,
        "validator": lambda x: parse_date_input(x) is not None,
        "error_empty": "❌ Using default start date.",
        "error_invalid": "❌ Invalid date format. Please use DD/MM/YY, DD-MM-YY, or DD.MM.YY (e.g., 15/11/25, 15-11-25, 15.11.25)"
    },
    "No of Periods (in Weeks)": {
        "prompt": "Enter No of Periods (in Weeks):",
        "field_key": "duration_weeks",
        "validator": validate_duration_input,
        "error_empty": "❌ Duration is required. Please enter a number between 1-52.",
        "error_invalid": "❌ Duration must be a whole number between 1-52 weeks (e.g., 12, 26, 52)"
    }
    # Future fields can be easily added here:
    # "Project Manager": {"prompt": "Enter Project Manager:", "field_key": "project_manager", ...}
}


def prompt_for_field(field_name: str) -> str:
    """
    Prompt the user for any configured field with validation and sanitization.
    
    Args:
        field_name: Name of field from CLI_FIELDS_CONFIG to prompt for
        
    Returns:
        Sanitized field value string (guaranteed to be non-empty)
        
    Example:
        >>> prompt_for_field("Client Name")
        Enter Client Name: Acme Corp & Co.
        -> Returns: "Acme Corp  Co"
    """
    if field_name not in CLI_FIELDS_CONFIG:
        raise ValueError(f"Unknown field name: {field_name}")
    
    config = CLI_FIELDS_CONFIG[field_name]
    
    # Generate dynamic prompt for fields with templates
    if "prompt_template" in config and "default_generator" in config:
        default_value = config["default_generator"]()
        prompt_text = config["prompt_template"].format(default=default_value)
    else:
        prompt_text = config.get("prompt", f"Enter {field_name}:")
    
    while True:
        user_input = input(f"{prompt_text} ").strip()
        
        # Handle empty input - check for default generator
        if not user_input:
            if "default_generator" in config:
                # Use default value for fields with generators (like dates)
                default_value = config["default_generator"]()
                print(config["error_empty"])
                return default_value.split(" (")[0]  # Extract just the date part
            else:
                # Required field with no default
                print(config["error_empty"])
                continue
        
        # Apply custom validator if configured
        if "validator" in config:
            if not config["validator"](user_input):
                print(config["error_invalid"])
                continue
            # For date fields, return formatted value
            if field_name == "Start Date (DD/MM/YY)":
                parsed_date = parse_date_input(user_input)
                return parsed_date.strftime("%d/%m/%y")
            # For duration, return as-is (already validated as integer)
            return user_input
        
        # Legacy path: sanitization for text fields
        sanitized = sanitize_user_input(user_input)
        
        if not sanitized:
            print(config["error_invalid"])
            continue
        
        return sanitized


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


def collect_cli_fields() -> dict[str, str]:
    """
    Collect all configured CLI fields from user using extensible design.
    
    Returns:
        Dictionary mapping field names to sanitized user inputs
        
    Example:
        >>> cli_data = collect_cli_fields()
        Enter Client Name: Acme Corp
        Enter Opportunity Name: Digital Transform
        >>> print(cli_data)
        {"Client Name": "Acme Corp", "Opportunity Name": "Digital Transform"}
    """
    print("\n📋 Please provide the following information:")
    print("   (Special characters will be automatically removed)")
    
    cli_data = {}
    for field_name in CLI_FIELDS_CONFIG.keys():
        cli_data[field_name] = prompt_for_field(field_name)
    
    return cli_data


def collect_user_inputs() -> tuple[str, str]:
    """
    Legacy function - collect both client name and opportunity name from user.
    
    Returns:
        Tuple of (client_name, opportunity_name) both sanitized and validated
        
    Example:
        >>> client, opportunity = collect_user_inputs()
        Enter Client Name: Acme Corp
        Enter Opportunity Name: Digital Transform
        >>> print(client, opportunity)
        "Acme Corp" "Digital Transform"
    """
    cli_data = collect_cli_fields()
    return cli_data["Client Name"], cli_data["Opportunity Name"]