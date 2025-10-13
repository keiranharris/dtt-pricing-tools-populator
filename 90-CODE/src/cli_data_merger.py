"""
CLI Data Merging Module

This module provides functions to merge CLI-collected user inputs with constants
file data, implementing precedence rules and extensible field support.

Feature 003: CLI Field Population Integration
"""

from typing import Dict
import logging

logger = logging.getLogger(__name__)


def merge_cli_with_constants(cli_data: Dict[str, str], constants_data: Dict[str, str]) -> Dict[str, str]:
    """
    Merge CLI data with constants data, with CLI taking precedence.
    
    Args:
        cli_data: Dictionary of field names to values collected from CLI
        constants_data: Dictionary of field names to values from constants file
        
    Returns:
        Merged dictionary with CLI values taking precedence over constants
        
    Example:
        >>> cli = {"Client Name": "Acme Corp", "Opportunity Name": "Project X"}
        >>> constants = {"Client Name": "Default Client", "Cost Centre": "12345"}
        >>> merged = merge_cli_with_constants(cli, constants)
        >>> print(merged)
        {"Client Name": "Acme Corp", "Opportunity Name": "Project X", "Cost Centre": "12345"}
    """
    if not cli_data:
        logger.info("No CLI data provided, using constants data only")
        return constants_data.copy()
    
    if not constants_data:
        logger.info("No constants data found, using CLI data only")
        return cli_data.copy()
    
    # Start with constants data as base
    merged_data = constants_data.copy()
    
    # Track overrides for logging
    overrides = []
    additions = []
    
    # Apply CLI data with precedence
    for field_name, cli_value in cli_data.items():
        if field_name in merged_data:
            if merged_data[field_name] != cli_value:
                overrides.append(field_name)
                logger.info(f"CLI override: '{field_name}' = '{cli_value}' (was: '{merged_data[field_name]}')")
        else:
            additions.append(field_name)
            logger.info(f"CLI addition: '{field_name}' = '{cli_value}'")
        
        merged_data[field_name] = cli_value
    
    # Log summary
    total_fields = len(merged_data)
    cli_fields = len(cli_data)
    constants_fields = len(constants_data)
    
    logger.info(f"Data merge complete: {total_fields} total fields "
                f"({cli_fields} CLI + {constants_fields} constants, {len(overrides)} overrides)")
    
    return merged_data


def validate_cli_data(cli_data: Dict[str, str]) -> bool:
    """
    Validate CLI data structure and content.
    
    Args:
        cli_data: Dictionary of CLI field names to values
        
    Returns:
        True if CLI data is valid, False otherwise
        
    Example:
        >>> valid = validate_cli_data({"Client Name": "Acme", "Opportunity Name": "Project"})
        >>> print(valid)
        True
    """
    if not isinstance(cli_data, dict):
        logger.error("CLI data must be a dictionary")
        return False
    
    if not cli_data:
        logger.warning("CLI data is empty")
        return True  # Empty CLI data is valid
    
    # Check all keys and values are strings
    for field_name, value in cli_data.items():
        if not isinstance(field_name, str):
            logger.error(f"CLI field name must be string, got: {type(field_name)}")
            return False
        
        if not isinstance(value, str):
            logger.error(f"CLI field value must be string for '{field_name}', got: {type(value)}")
            return False
        
        if not field_name.strip():
            logger.error("CLI field names cannot be empty")
            return False
        
        if not value.strip():
            logger.warning(f"CLI field '{field_name}' has empty value")
    
    logger.info(f"CLI data validation passed: {len(cli_data)} fields")
    return True


def get_cli_field_summary(cli_data: Dict[str, str]) -> str:
    """
    Generate a human-readable summary of CLI field data.
    
    Args:
        cli_data: Dictionary of CLI field names to values
        
    Returns:
        Formatted string summarizing the CLI data
        
    Example:
        >>> cli = {"Client Name": "Acme Corp", "Opportunity Name": "Project X"}
        >>> summary = get_cli_field_summary(cli)
        >>> print(summary)
        "CLI Data: Client Name='Acme Corp', Opportunity Name='Project X'"
    """
    if not cli_data:
        return "CLI Data: None"
    
    field_summaries = [f"{field}='{value}'" for field, value in cli_data.items()]
    return f"CLI Data: {', '.join(field_summaries)}"