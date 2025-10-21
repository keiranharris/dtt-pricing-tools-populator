"""
CLI Data Merging Module

This module provides functions to merge CLI-collected user inputs with constants
file data, implementing precedence rules and extensible field support.

Feature 003: CLI Field Population Integration
"""

from typing import Dict, Union
import logging

# Import SpecKit data models
from data_models import CLICollectionResult, ConstantsData

logger = logging.getLogger(__name__)


def merge_cli_with_constants(
    cli_data: Union[Dict[str, str], CLICollectionResult, None], 
    constants_data: Union[Dict[str, str], ConstantsData, None]
) -> Dict[str, str]:
    """
    Merge CLI data with constants data, with CLI taking precedence.
    
    Args:
        cli_data: CLI field data (dictionary, CLICollectionResult, or None)
        constants_data: Constants data (dictionary, ConstantsData, or None)
        
    Returns:
        Merged dictionary with CLI values taking precedence over constants
        
    Example:
        >>> cli = {"Client Name": "Acme Corp", "Opportunity Name": "Project X"}
        >>> constants = {"Client Name": "Default Client", "Cost Centre": "12345"}
        >>> merged = merge_cli_with_constants(cli, constants)
        >>> print(merged)
        {"Client Name": "Acme Corp", "Opportunity Name": "Project X", "Cost Centre": "12345"}
    """
    # Convert inputs to dictionaries for processing
    cli_dict = _convert_to_dict(cli_data) if cli_data else {}
    constants_dict = _convert_to_dict(constants_data) if constants_data else {}
    
    if not cli_dict:
        logger.info("No CLI data provided, using constants data only")
        return constants_dict.copy()
    
    if not constants_dict:
        logger.info("No constants data found, using CLI data only")
        return cli_dict.copy()
    
    # Start with constants data as base
    merged_data = constants_dict.copy()
    
    # Track overrides for logging
    overrides = []
    additions = []
    
    # Apply CLI data with precedence
    for field_name, cli_value in cli_dict.items():
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


def validate_cli_data(cli_data: Union[Dict[str, str], CLICollectionResult, None]) -> bool:
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
    # Convert to dictionary for validation
    cli_dict = _convert_to_dict(cli_data)
    
    if not cli_dict:
        logger.warning("CLI data is empty")
        return True  # Empty CLI data is valid
    
    # Check all keys and values are strings
    for field_name, value in cli_dict.items():
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


def get_cli_field_summary(cli_data: Union[Dict[str, str], CLICollectionResult, None]) -> str:
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
    # Convert to dictionary for processing
    cli_dict = _convert_to_dict(cli_data)
    
    if not cli_dict:
        return "CLI Data: None"
    
    field_summaries = [f"{field}='{value}'" for field, value in cli_dict.items()]
    return f"CLI Data: {', '.join(field_summaries)}"


def _convert_to_dict(data: Union[Dict[str, str], CLICollectionResult, ConstantsData, None]) -> Dict[str, str]:
    """
    Convert various data types to dictionary format for processing.
    
    Args:
        data: Data to convert (dictionary, CLICollectionResult, ConstantsData, or None)
        
    Returns:
        Dictionary representation of the data
    """
    if data is None:
        return {}
    elif isinstance(data, dict):
        return data
    elif isinstance(data, CLICollectionResult):
        return data.as_dict
    elif isinstance(data, ConstantsData):
        return data.constants_fields
    else:
        logger.warning(f"Unknown data type for conversion: {type(data)}")
        return {}