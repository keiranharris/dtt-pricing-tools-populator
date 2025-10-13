"""
Data Population Orchestrator Module

This module coordinates the entire data population process, integrating constants
reading, field matching, and data writing into a cohesive workflow. Handles
integration with Feature 001 and provides comprehensive error handling.

Dependencies:
- dataclasses: Data structures  
- pathlib: Path handling
- typing: Type hints
- All other Feature 002 modules

Author: DTT Pricing Tool Accelerator
Feature: 002-excel-data-population
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional
import logging
import time

# Import other module types
from excel_constants_reader import read_constants_data, validate_constants_file
from field_matcher import find_matching_fields, find_matching_fields_xlwings, FieldMatch
from excel_data_populator import populate_matched_fields, populate_matched_fields_xlwings, PopulationResult
from cli_data_merger import merge_cli_with_constants, validate_cli_data, get_cli_field_summary
from cli_population_feedback import display_cli_population_summary, generate_population_results_dict, log_cli_integration_summary

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class PopulationSummary:
    """Comprehensive summary of data population operation."""
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


def populate_spreadsheet_data(target_file: Path, constants_filename: str, 
                            constants_dir_name: str = "00-CONSTANTS",
                            threshold: float = 0.8) -> PopulationSummary:
    """
    Main orchestration function for complete data population process.
    
    Args:
        target_file: Path to target Excel spreadsheet file
        constants_filename: Name of constants file to read from
        constants_dir_name: Name of constants directory
        threshold: Similarity threshold for field matching
        
    Returns:
        Comprehensive summary of population operation
        
    Example:
        >>> summary = populate_spreadsheet_data(Path("output.xlsx"), "constants.xlsx")
        >>> print(f"Populated {summary.fields_populated} fields")
    """
    start_time = time.time()
    errors = []
    warnings = []
    
    logger.info("🚀 Starting spreadsheet data population...")
    
    try:
        # Determine constants directory path
        constants_dir = target_file.parent.parent / constants_dir_name
        
        logger.info(f"📁 Constants directory: {constants_dir}")
        logger.info(f"📄 Target file: {target_file}")
        
        # Step 1: Read constants data
        logger.info("📋 Step 1: Reading constants data...")
        constants_data = read_constants_data(constants_dir, constants_filename)
        
        if not constants_data:
            logger.warning("⚠️  No constants data found - skipping population")
            return PopulationSummary(
                constants_file_found=False,
                constants_loaded=0,
                fields_matched=0,
                fields_populated=0,
                execution_time_seconds=time.time() - start_time,
                errors=[],
                warnings=["Constants file not found or empty"]
            )
        
        logger.info(f"✅ Loaded {len(constants_data)} constants")
        
        # Step 2: Open target file and find matching fields
        logger.info("🔍 Step 2: Finding field matches...")
        
        try:
            # Handle both .xlsb and .xlsx files appropriately
            if target_file.suffix.lower() == '.xlsb':
                # Hybrid approach: Convert .xlsb to temporary .xlsx for field matching
                # This gives us accurate openpyxl field detection while preserving .xlsb format
                temp_xlsx = target_file.with_suffix('.temp.xlsx')
                
                logger.info("🔄 Creating temporary .xlsx for field matching...")
                import xlwings as xw
                with xw.App(visible=False) as app:
                    wb = app.books.open(target_file)
                    wb.save(temp_xlsx)
                    wb.close()
                
                # Use openpyxl on the temporary file for accurate field detection
                import openpyxl
                workbook = openpyxl.load_workbook(temp_xlsx, data_only=True)
                
                if "Pricing Setup" not in workbook.sheetnames:
                    error_msg = "Target worksheet 'Pricing Setup' not found"
                    errors.append(error_msg)
                    logger.error(f"❌ {error_msg}")
                    workbook.close()
                    temp_xlsx.unlink(missing_ok=True)  # Clean up temp file
                    return PopulationSummary(
                        constants_file_found=True,
                        constants_loaded=len(constants_data),
                        fields_matched=0,
                        fields_populated=0,
                        execution_time_seconds=time.time() - start_time,
                        errors=errors,
                        warnings=warnings
                    )
                
                worksheet = workbook["Pricing Setup"]
                matches = find_matching_fields(constants_data, worksheet, threshold)
                workbook.close()
                temp_xlsx.unlink(missing_ok=True)  # Clean up temp file
            else:
                # Use openpyxl for .xlsx files
                import openpyxl
                workbook = openpyxl.load_workbook(target_file, data_only=True)
                
                if "Pricing Setup" not in workbook.sheetnames:
                    error_msg = "Target worksheet 'Pricing Setup' not found"
                    errors.append(error_msg)
                    logger.error(f"❌ {error_msg}")
                    workbook.close()
                    return PopulationSummary(
                        constants_file_found=True,
                        constants_loaded=len(constants_data),
                        fields_matched=0,
                        fields_populated=0,
                        execution_time_seconds=time.time() - start_time,
                        errors=errors,
                        warnings=warnings
                    )
                
                worksheet = workbook["Pricing Setup"]
                matches = find_matching_fields(constants_data, worksheet, threshold)
                workbook.close()
            
            logger.info(f"✅ Found {len(matches)} field matches")
            
            # Step 3: Populate matched fields
            logger.info("✏️  Step 3: Populating matched fields...")
            
            # Choose appropriate population method based on file format
            if target_file.suffix.lower() == '.xlsb':
                population_result = populate_matched_fields_xlwings(target_file, matches)
            else:
                population_result = populate_matched_fields(target_file, matches)
            
            # Compile final summary
            execution_time = time.time() - start_time
            
            summary = PopulationSummary(
                constants_file_found=True,
                constants_loaded=len(constants_data),
                fields_matched=len(matches),
                fields_populated=population_result.successful_fields,
                execution_time_seconds=execution_time,
                errors=errors + population_result.error_messages,
                warnings=warnings
            )
            
            logger.info(f"🎉 Population complete: {summary}")
            return summary
            
        except ImportError:
            error_msg = "openpyxl library not available"
            errors.append(error_msg)
            logger.error(f"❌ {error_msg}")
            return PopulationSummary(
                constants_file_found=True,
                constants_loaded=len(constants_data),
                fields_matched=0,
                fields_populated=0,
                execution_time_seconds=time.time() - start_time,
                errors=errors,
                warnings=warnings
            )
            
    except Exception as e:
        error_msg = f"Unexpected error during population: {e}"
        errors.append(error_msg)
        logger.error(f"❌ {error_msg}")
        
        return PopulationSummary(
            constants_file_found=False,
            constants_loaded=0,
            fields_matched=0,
            fields_populated=0,
            execution_time_seconds=time.time() - start_time,
            errors=errors,
            warnings=warnings
        )


def integrate_with_feature_001(output_file: Path) -> bool:
    """
    Integration point with Feature 001 (spreadsheet copy).
    
    Args:
        output_file: Path to newly created spreadsheet from Feature 001
        
    Returns:
        True if data population was successful or gracefully skipped
        
    Example:
        >>> success = integrate_with_feature_001(Path("new_spreadsheet.xlsx"))
        >>> if success: print("Integration successful")
    """
    # Implementation will be added in Phase 4
    pass


def show_population_feedback(summary: PopulationSummary) -> None:
    """
    Display user-friendly feedback about population results.
    
    Args:
        summary: Results summary to display
        
    Example:
        >>> show_population_feedback(population_summary)
        # Prints user-friendly status messages
    """
    if not summary.constants_file_found:
        print("📋 Skipping data population - constants file not found")
        return
    
    if summary.constants_loaded == 0:
        print("📋 Skipping data population - no constants data loaded")
        return
    
    # Show population results
    if summary.fields_populated > 0:
        print(f"✅ Populated {summary.fields_populated}/{summary.fields_matched} matched fields "
              f"from {summary.constants_loaded} constants")
        
        if summary.fields_populated == summary.fields_matched:
            print("🎉 All matched fields populated successfully!")
        else:
            failed_count = summary.fields_matched - summary.fields_populated
            print(f"⚠️  {failed_count} fields failed to populate")
            
    elif summary.fields_matched > 0:
        print(f"❌ Found {summary.fields_matched} field matches but none were populated successfully")
        
    else:
        print(f"🔍 No field matches found from {summary.constants_loaded} constants")
        print("💡 Try adjusting field names in constants file or target spreadsheet")
    
    # Show timing
    print(f"⏱️  Population completed in {summary.execution_time_seconds:.1f} seconds")
    
    # Show any warnings or errors (first few only)
    if summary.warnings:
        for warning in summary.warnings[:2]:
            print(f"⚠️  {warning}")
    
    if summary.errors:
        for error in summary.errors[:2]:
            print(f"❌ {error}")


def populate_spreadsheet_data_with_cli(target_file: Path, constants_filename: str,
                                     cli_data: Optional[Dict[str, str]] = None,
                                     constants_dir_name: str = "00-CONSTANTS",
                                     threshold: float = 0.8) -> PopulationSummary:
    """
    Enhanced orchestration function supporting CLI field population alongside constants.
    
    Args:
        target_file: Path to target Excel spreadsheet file
        constants_filename: Name of constants file to read from
        cli_data: Optional dictionary of CLI field names to values
        constants_dir_name: Name of constants directory
        threshold: Similarity threshold for field matching
        
    Returns:
        Comprehensive summary of population operation including CLI fields
        
    Example:
        >>> cli_data = {"Client Name": "Acme Corp", "Opportunity Name": "Project X"}
        >>> summary = populate_spreadsheet_data_with_cli(Path("output.xlsx"), 
        ...                                             "constants.xlsx", cli_data)
        >>> print(f"Populated {summary.fields_populated} fields total")
    """
    start_time = time.time()
    errors = []
    warnings = []
    
    logger.info("🚀 Starting enhanced spreadsheet data population with CLI integration...")
    
    # Validate CLI data if provided
    if cli_data and not validate_cli_data(cli_data):
        errors.append("Invalid CLI data structure")
        cli_data = {}  # Reset to empty if invalid
    
    if cli_data:
        logger.info(f"📋 CLI data: {get_cli_field_summary(cli_data)}")
    
    try:
        # Determine constants directory path
        constants_dir = target_file.parent.parent / constants_dir_name
        
        logger.info(f"📁 Constants directory: {constants_dir}")
        logger.info(f"📄 Target file: {target_file}")
        
        # Step 1: Read constants data
        logger.info("📋 Step 1: Reading constants data...")
        constants_data = read_constants_data(constants_dir, constants_filename)
        
        # Step 2: Merge CLI data with constants data
        if cli_data:
            logger.info("🔗 Step 2: Merging CLI data with constants...")
            merged_data = merge_cli_with_constants(cli_data, constants_data)
            log_cli_integration_summary(cli_data, len(merged_data), len(constants_data))
        else:
            logger.info("📋 No CLI data provided, using constants only")
            merged_data = constants_data
        
        if not merged_data:
            logger.warning("⚠️  No data available for population (neither CLI nor constants)")
            return PopulationSummary(
                constants_file_found=len(constants_data) > 0,
                constants_loaded=len(constants_data),
                fields_matched=0,
                fields_populated=0,
                execution_time_seconds=time.time() - start_time,
                errors=[],
                warnings=["No data available for population"]
            )
        
        logger.info(f"✅ Total data for population: {len(merged_data)} fields")
        
        # Step 3: Open target file and find matching fields
        logger.info("🔍 Step 3: Finding field matches...")
        
        try:
            # Handle both .xlsb and .xlsx files appropriately (same logic as original function)
            if target_file.suffix.lower() == '.xlsb':
                # Hybrid approach: Convert .xlsb to temporary .xlsx for field matching
                temp_xlsx = target_file.with_suffix('.temp.xlsx')
                
                logger.info("🔄 Creating temporary .xlsx for field matching...")
                import xlwings as xw
                with xw.App(visible=False) as app:
                    wb = app.books.open(target_file)
                    wb.save(temp_xlsx)
                    wb.close()
                
                # Use openpyxl on the temporary file for accurate field detection
                import openpyxl
                workbook = openpyxl.load_workbook(temp_xlsx, data_only=True)
                
                if "Pricing Setup" not in workbook.sheetnames:
                    error_msg = "Target worksheet 'Pricing Setup' not found"
                    errors.append(error_msg)
                    logger.error(f"❌ {error_msg}")
                    workbook.close()
                    temp_xlsx.unlink(missing_ok=True)
                    return PopulationSummary(
                        constants_file_found=len(constants_data) > 0,
                        constants_loaded=len(constants_data),
                        fields_matched=0,
                        fields_populated=0,
                        execution_time_seconds=time.time() - start_time,
                        errors=errors,
                        warnings=warnings
                    )
                
                worksheet = workbook["Pricing Setup"]
                matches = find_matching_fields(merged_data, worksheet, threshold)
                workbook.close()
                temp_xlsx.unlink(missing_ok=True)
            else:
                # Use openpyxl for .xlsx files
                import openpyxl
                workbook = openpyxl.load_workbook(target_file, data_only=True)
                
                if "Pricing Setup" not in workbook.sheetnames:
                    error_msg = "Target worksheet 'Pricing Setup' not found"
                    errors.append(error_msg)
                    logger.error(f"❌ {error_msg}")
                    workbook.close()
                    return PopulationSummary(
                        constants_file_found=len(constants_data) > 0,
                        constants_loaded=len(constants_data),
                        fields_matched=0,
                        fields_populated=0,
                        execution_time_seconds=time.time() - start_time,
                        errors=errors,
                        warnings=warnings
                    )
                
                worksheet = workbook["Pricing Setup"]
                matches = find_matching_fields(merged_data, worksheet, threshold)
                workbook.close()
            
            logger.info(f"✅ Found {len(matches)} field matches")
            
            # Step 4: Populate matched fields
            logger.info("✏️  Step 4: Populating matched fields...")
            
            # Choose appropriate population method based on file format
            if target_file.suffix.lower() == '.xlsb':
                population_result = populate_matched_fields_xlwings(target_file, matches)
            else:
                population_result = populate_matched_fields(target_file, matches)
            
            # Step 5: Display CLI population feedback if CLI data was provided
            if cli_data:
                logger.info("📊 Step 5: Generating CLI population feedback...")
                
                # Determine which CLI fields were successfully populated
                successful_field_names = [match.field_name for match in matches 
                                        if match.field_name in cli_data and 
                                        match.field_name in [m.field_name for m in matches]]
                
                # Generate and display results
                cli_results = generate_population_results_dict(cli_data, successful_field_names)
                constants_summary = f"{len(constants_data)} constants loaded"
                display_cli_population_summary(cli_data, cli_results, constants_summary)
            
            # Compile final summary
            execution_time = time.time() - start_time
            
            summary = PopulationSummary(
                constants_file_found=len(constants_data) > 0,
                constants_loaded=len(constants_data),
                fields_matched=len(matches),
                fields_populated=population_result.successful_fields,
                execution_time_seconds=execution_time,
                errors=errors + population_result.error_messages,
                warnings=warnings
            )
            
            logger.info(f"🎉 Enhanced population complete: {summary}")
            return summary
            
        except ImportError as e:
            error_msg = f"Required library not available: {e}"
            errors.append(error_msg)
            logger.error(f"❌ {error_msg}")
            return PopulationSummary(
                constants_file_found=len(constants_data) > 0,
                constants_loaded=len(constants_data),
                fields_matched=0,
                fields_populated=0,
                execution_time_seconds=time.time() - start_time,
                errors=errors,
                warnings=warnings
            )
            
    except Exception as e:
        error_msg = f"Unexpected error during population: {e}"
        errors.append(error_msg)
        logger.error(f"❌ {error_msg}")
        return PopulationSummary(
            constants_file_found=False,
            constants_loaded=0,
            fields_matched=0,
            fields_populated=0,
            execution_time_seconds=time.time() - start_time,
            errors=errors,
            warnings=warnings
        )


# ============================================================================
# FEATURE 005: RESOURCE SETUP INTEGRATION
# ============================================================================

def populate_resource_setup_data(
    target_file: Path,
    constants_filename: str,
    constants_dir_name: str = "00-CONSTANTS",
    resource_row_count: int = 7,
    worksheet_name: str = "Resource Setup"
) -> Optional['ResourceCopyResult']:
    """
    Populate Resource Setup worksheet with data from constants file.
    
    This function integrates Resource Setup population into the existing workflow,
    copying structured resource data from the constants file to the target file's
    Resource Setup worksheet.
    
    Args:
        target_file: Path to target Excel spreadsheet file
        constants_filename: Name of constants file containing resource data
        constants_dir_name: Name of constants directory
        resource_row_count: Number of resource rows to copy (default 7)
        worksheet_name: Name of Resource Setup worksheet
        
    Returns:
        ResourceCopyResult if successful, None if skipped or failed
        
    Example:
        >>> result = populate_resource_setup_data(
        ...     Path("pricing_tool.xlsb"),
        ...     "lowcomplexity_const_KHv1.xlsx"
        ... )
        >>> if result and result.success:
        ...     print(f"Copied {result.cells_copied} resource cells")
    """
    try:
        from resource_setup_populator import copy_resource_setup_range, get_resource_setup_summary
        
        # Determine constants file path
        constants_dir = target_file.parent.parent / constants_dir_name
        constants_file = constants_dir / constants_filename
        
        if not constants_file.exists():
            logger.warning(f"Constants file not found: {constants_file}")
            return None
        
        logger.info(f"📋 Starting Resource Setup population...")
        logger.info(f"   Source: {constants_file}")
        logger.info(f"   Target: {target_file}")
        logger.info(f"   Worksheet: {worksheet_name}")
        
        # Perform the resource setup copy
        result = copy_resource_setup_range(
            source_file=constants_file,
            target_file=target_file,
            resource_row_count=resource_row_count,
            worksheet_name=worksheet_name
        )
        
        # Log the result
        if result.success:
            logger.info(f"✅ Resource Setup completed: {get_resource_setup_summary(result)}")
        else:
            logger.warning(f"⚠️ Resource Setup failed: {get_resource_setup_summary(result)}")
        
        return result
        
    except ImportError as e:
        logger.warning(f"Resource Setup module not available: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in Resource Setup population: {e}")
        return None


def populate_spreadsheet_data_with_cli_and_resources(
    target_file: Path, 
    constants_filename: str,
    cli_data: Optional[Dict[str, str]] = None,
    constants_dir_name: str = "00-CONSTANTS",
    field_match_threshold: float = 0.8,
    enable_resource_setup: bool = True,
    resource_row_count: int = 7
) -> PopulationSummary:
    """
    Enhanced orchestration including Resource Setup population.
    
    This function extends the existing CLI population workflow to include
    Resource Setup data copying, providing a complete data population solution.
    
    Args:
        target_file: Path to target Excel spreadsheet file
        constants_filename: Name of constants file
        cli_data: Optional dictionary of CLI field names to values
        constants_dir_name: Name of constants directory
        field_match_threshold: Similarity threshold for field matching
        enable_resource_setup: Whether to include Resource Setup population
        resource_row_count: Number of resource rows to copy
        
    Returns:
        Enhanced PopulationSummary including Resource Setup results
        
    Example:
        >>> cli_data = {"Client Name": "Acme Corp"}
        >>> summary = populate_spreadsheet_data_with_cli_and_resources(
        ...     Path("output.xlsb"), "constants.xlsx", cli_data
        ... )
        >>> print(f"Total operation took {summary.execution_time_seconds:.1f}s")
    """
    logger.info("🚀 Starting comprehensive data population (CLI + Resources)...")
    
    # Step 1: Perform existing CLI and constants population
    base_summary = populate_spreadsheet_data_with_cli(
        target_file=target_file,
        constants_filename=constants_filename,
        cli_data=cli_data,
        constants_dir_name=constants_dir_name,
        threshold=field_match_threshold
    )
    
    # Step 2: Add Resource Setup population if enabled
    resource_result = None
    if enable_resource_setup:
        logger.info("📋 Step 6: Populating Resource Setup...")
        resource_result = populate_resource_setup_data(
            target_file=target_file,
            constants_filename=constants_filename,
            constants_dir_name=constants_dir_name,
            resource_row_count=resource_row_count
        )
        
        if resource_result and resource_result.success:
            logger.info(f"✅ Resource Setup: {resource_result.cells_copied} cells copied")
        elif resource_result and not resource_result.success:
            logger.warning(f"⚠️ Resource Setup failed but continuing: {resource_result.error_messages}")
        else:
            logger.info("ℹ️ Resource Setup skipped (module not available or disabled)")
    
    # Return enhanced summary (for now, return base summary - could be extended)
    logger.info("🎉 Comprehensive population complete!")
    return base_summary


def show_population_feedback_with_resources(
    base_summary: PopulationSummary, 
    resource_result: Optional['ResourceCopyResult'] = None
) -> None:
    """
    Enhanced feedback display including Resource Setup results.
    
    Args:
        base_summary: Results from CLI and constants population
        resource_result: Optional results from Resource Setup population
    """
    # Show base population feedback
    show_population_feedback(base_summary)
    
    # Add Resource Setup feedback
    if resource_result:
        from resource_setup_populator import get_resource_setup_summary
        print(get_resource_setup_summary(resource_result))
    else:
        print("ℹ️ Resource Setup: Skipped or not available")