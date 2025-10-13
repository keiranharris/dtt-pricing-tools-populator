"""
CLI Population Feedback Module

This module provides functions to display user-friendly feedback about CLI field
population results, showing which fields were successfully populated and which
encountered issues.

Feature 003: CLI Field Population - User Feedback
"""

from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


def display_cli_population_summary(cli_data: Dict[str, str], population_results: Dict[str, bool], 
                                 constants_summary: str = "") -> None:
    """
    Display a user-friendly summary of CLI field population results.
    
    Args:
        cli_data: Dictionary of CLI field names to values that were attempted
        population_results: Dictionary mapping field names to success status (True/False)
        constants_summary: Optional summary of constants population (e.g., "7 of 9 fields populated")
        
    Example:
        >>> cli_data = {"Client Name": "Acme Corp", "Opportunity Name": "Project X"}
        >>> results = {"Client Name": True, "Opportunity Name": False}
        >>> display_cli_population_summary(cli_data, results, "5 of 7 fields populated")
        
        CLI Field Population Results:
        ✅ Client Name: Successfully populated
        ⚠️  Opportunity Name: Field not found in Excel template
        Constants: 5 of 7 fields populated
    """
    if not cli_data:
        logger.info("No CLI data provided - skipping CLI population summary")
        return
    
    print("\n📋 CLI Field Population Results:")
    
    success_count = 0
    
    for field_name, field_value in cli_data.items():
        success = population_results.get(field_name, False)
        
        if success:
            print(f"✅ {field_name}: Successfully populated")
            success_count += 1
        else:
            print(f"⚠️  {field_name}: Field not found in Excel template")
    
    # Add constants summary if provided
    if constants_summary:
        print(f"📊 Constants: {constants_summary}")
    
    # Overall summary
    total_cli_fields = len(cli_data)
    if success_count == total_cli_fields:
        print(f"🎉 All {total_cli_fields} CLI fields populated successfully!")
    else:
        failed_count = total_cli_fields - success_count
        print(f"📈 CLI Summary: {success_count} of {total_cli_fields} fields populated "
              f"({failed_count} not found in template)")
    
    print()  # Add spacing


def generate_population_results_dict(cli_data: Dict[str, str], successful_matches: List[str]) -> Dict[str, bool]:
    """
    Generate a results dictionary showing which CLI fields were successfully populated.
    
    Args:
        cli_data: Dictionary of CLI field names to values
        successful_matches: List of field names that were successfully matched and populated
        
    Returns:
        Dictionary mapping CLI field names to success status
        
    Example:
        >>> cli_data = {"Client Name": "Acme", "Opportunity Name": "Project"}
        >>> successful = ["Client Name"]  # Only client name was found in Excel
        >>> results = generate_population_results_dict(cli_data, successful)
        >>> print(results)
        {"Client Name": True, "Opportunity Name": False}
    """
    results = {}
    
    for field_name in cli_data.keys():
        # Check if this CLI field was in the successful matches
        results[field_name] = field_name in successful_matches
    
    return results


def log_cli_integration_summary(cli_data: Dict[str, str], merged_data_size: int, 
                               constants_data_size: int) -> None:
    """
    Log detailed information about CLI integration for debugging and monitoring.
    
    Args:
        cli_data: Dictionary of CLI field names to values
        merged_data_size: Total number of fields after merging
        constants_data_size: Number of fields from constants file
        
    Example:
        >>> log_cli_integration_summary({"Client": "Acme"}, 15, 14)  
        # Logs: "CLI Integration: 1 CLI fields + 14 constants = 15 total fields"
    """
    if not cli_data:
        logger.info("CLI Integration: No CLI data provided, using constants only")
        return
    
    cli_field_count = len(cli_data)
    
    logger.info(f"CLI Integration: {cli_field_count} CLI fields + {constants_data_size} constants "
                f"= {merged_data_size} total fields for population")
    
    # Log individual CLI fields for debugging
    for field_name, field_value in cli_data.items():
        # Don't log the actual values for privacy, just the field names
        logger.debug(f"CLI field prepared for population: '{field_name}' (value provided)")


def create_enhancement_suggestions(failed_cli_fields: List[str]) -> None:
    """
    Provide helpful suggestions when CLI fields can't be populated.
    
    Args:
        failed_cli_fields: List of CLI field names that couldn't be populated
        
    Example:
        >>> create_enhancement_suggestions(["Project Manager", "Budget Code"])
        💡 Tips for missing fields:
           • Check if 'Project Manager' exists in the Excel 'Pricing Setup' worksheet
           • Verify field names match exactly (case-sensitive)
    """
    if not failed_cli_fields:
        return
    
    print("💡 Tips for missing CLI fields:")
    for field_name in failed_cli_fields:
        print(f"   • Check if '{field_name}' exists in the Excel 'Pricing Setup' worksheet")
        print(f"   • Verify the field name matches exactly (fuzzy matching with 80% threshold)")
    
    print("   • Field names are matched by removing first/last characters (e.g., 'Client Name:' matches 'Client Name')")
    print()