"""
Margin Validator Module

This module provides atomic functions for client margin percentage validation
and conversion, following the project constitution principles.

Feature 006: Implements margin input validation and decimal conversion for
rate card calculation using the formula: Standard Cost Rate / (1 - Client Margin %)

Dependencies:
- typing: Type hints
- re: Regular expression validation

Author: DTT Pricing Tool Accelerator  
Feature: 006-populate-rate
"""

import re
from typing import Optional, Union
# Import SpecKit data models
from data_models import MarginValidationResult, OperationError


def validate_margin_input(margin_input: str) -> MarginValidationResult:
    """
    Validate client margin percentage input.
    
    Accepts percentage values as positive numbers.
    Supports formats: "35", "35%", "35.5", "35.5%"
    
    Args:
        margin_input: Raw user input string
        
    Returns:
        MarginValidationResult with validation status and parsed value
        
    Example:
        >>> result = validate_margin_input("45%")
        >>> print(result.is_valid)  # True
        >>> print(result.decimal_value)  # 0.45
    """
    if not isinstance(margin_input, str):
        return MarginValidationResult(
            is_valid=False,
            error_message="Input must be a string"
        )
    
    # Clean input: strip whitespace and normalize
    cleaned = margin_input.strip()
    
    if not cleaned:
        return MarginValidationResult(
            is_valid=False,
            error_message="Input cannot be empty"
        )
    
    # Remove % symbol if present
    if cleaned.endswith('%'):
        cleaned = cleaned[:-1]
    
    # Validate numeric format
    try:
        percentage_value = float(cleaned)
    except ValueError:
        return MarginValidationResult(
            is_valid=False,
            error_message=f"Invalid number format: '{margin_input}'"
        )
    
    # Validate range: must be positive
    if percentage_value <= 0:
        return MarginValidationResult(
            is_valid=False,
            error_message=f"Margin must be a positive percentage, got {percentage_value}%"
        )
    
    # Convert to decimal
    decimal_value = percentage_value / 100
    
    return MarginValidationResult(
        is_valid=True,
        decimal_value=decimal_value
    )


def convert_margin_to_decimal(margin_percentage: Union[str, float]) -> float:
    """
    Convert validated margin percentage to decimal format.
    
    Args:
        margin_percentage: Percentage value (e.g., 45 or "45%")
        
    Returns:
        Decimal representation (e.g., 0.45)
        
    Raises:
        ValueError: If input is invalid or out of range
        
    Example:
        >>> decimal = convert_margin_to_decimal("45%")
        >>> print(decimal)  # 0.45
    """
    if isinstance(margin_percentage, (int, float)):
        percentage_value = float(margin_percentage)
    else:
        result = validate_margin_input(str(margin_percentage))
        if not result.is_valid:
            raise OperationError.invalid_input("margin_percentage", result.error_message)
        percentage_value = result.decimal_value * 100
    
    # Validate range
    if percentage_value <= 0:
        raise OperationError.invalid_input("margin_percentage", f"Margin must be a positive percentage, got {percentage_value}%")
    
    return percentage_value / 100


def get_margin_prompt_text() -> str:
    """
    Get standardized prompt text for margin input collection.
    
    Returns:
        User-friendly prompt string
    """
    return (
        "Enter client margin percentage:\n"
        "  Examples: 45, 45%, 42.5, 42.5%\n"
        "  Must be a positive percentage\n"
        "Margin: "
    )


def get_margin_error_help() -> str:
    """
    Get help text for margin input errors.
    
    Returns:
        Helpful error guidance string
    """
    return (
        "\n❌ Invalid margin input. Please enter:\n"
        "  • A positive percentage number\n"
        "  • With or without % symbol\n"
        "  • Decimals are allowed (e.g., 42.5%)\n"
        "  • Examples: 45, 45%, 42.5, 42.5%\n"
    )