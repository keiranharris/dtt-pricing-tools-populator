"""
Excel Integration Utilities for Rate Card Operations.

This module provides comprehensive Excel integration utilities specifically
for rate card reading and writing operations, with robust error handling
and worksheet validation.

Dependencies:
- xlwings: Excel automation
- rate_card_calculator: Core calculation functions

Author: DTT Pricing Tool Accelerator
Feature: 006-populate-rate
"""

import logging
from typing import Optional, Dict, List, Any, Tuple
from pathlib import Path

try:
    import xlwings as xw
    XLWINGS_AVAILABLE = True
except ImportError:
    XLWINGS_AVAILABLE = False
    xw = None

from rate_card_calculator import (
    StandardCostRate, 
    EngineeringRate,
    read_standard_cost_rates,
    calculate_engineering_rates,
    write_engineering_rates
)

logger = logging.getLogger(__name__)


class ExcelAccessError(Exception):
    """Raised when Excel file access fails."""
    pass


class WorksheetNotFoundError(Exception):
    """Raised when expected worksheet is not found."""
    pass


def validate_excel_environment() -> bool:
    """
    Validate Excel integration environment.
    
    Returns:
        True if Excel environment is ready, False otherwise
    """
    if not XLWINGS_AVAILABLE:
        logger.error("xlwings is not available - Excel operations will fail")
        return False
    
    try:
        # Test Excel availability (this will fail gracefully if Excel not installed)
        app = xw.App(visible=False, add_book=False)
        app.quit()
        return True
    except Exception as e:
        logger.error(f"Excel not available: {e}")
        return False


def open_excel_file_safely(file_path: Path, reuse_app: Optional[Any] = None) -> Optional[Any]:
    """
    Open Excel file with comprehensive error handling and optional app reuse.
    
    Args:
        file_path: Path to Excel file to open
        reuse_app: Optional xlwings app instance to reuse for performance
        
    Returns:
        xlwings workbook object or None if failed
        
    Raises:
        ExcelAccessError: If file cannot be opened
    """
    if not XLWINGS_AVAILABLE:
        raise ExcelAccessError("xlwings is not available for Excel operations")
    
    if not file_path.exists():
        raise ExcelAccessError(f"Excel file not found: {file_path}")
    
    try:
        # Reuse existing app if provided, otherwise create new one
        if reuse_app:
            app = reuse_app
        else:
            app = xw.App(visible=False, add_book=False)
        
        workbook = app.books.open(file_path)
        return workbook
    except PermissionError:
        raise ExcelAccessError(f"Permission denied accessing Excel file: {file_path}")
    except Exception as e:
        raise ExcelAccessError(f"Failed to open Excel file {file_path}: {str(e)}")


def get_worksheet_safely(workbook: Any, worksheet_name: str) -> Optional[Any]:
    """
    Get worksheet from workbook with error handling.
    
    Args:
        workbook: xlwings workbook object
        worksheet_name: Name of worksheet to retrieve
        
    Returns:
        xlwings worksheet object or None if not found
        
    Raises:
        WorksheetNotFoundError: If worksheet cannot be found
    """
    try:
        worksheet = workbook.sheets[worksheet_name]
        return worksheet
    except KeyError:
        available_sheets = [sheet.name for sheet in workbook.sheets]
        raise WorksheetNotFoundError(
            f"Worksheet '{worksheet_name}' not found. "
            f"Available sheets: {', '.join(available_sheets)}"
        )
    except Exception as e:
        raise WorksheetNotFoundError(f"Error accessing worksheet '{worksheet_name}': {str(e)}")


def perform_rate_card_calculation(
    excel_file_path: Path, 
    client_margin_decimal: float,
    worksheet_name: str = "Resource Setup"
) -> Dict[str, Any]:
    """
    Perform complete rate card calculation on Excel file.
    
    This function opens the Excel file, reads standard cost rates,
    calculates engineering rates, and writes results back to the file.
    
    Args:
        excel_file_path: Path to Excel file to process
        client_margin_decimal: Client margin as decimal (e.g., 0.45)
        worksheet_name: Name of worksheet containing rate data
        
    Returns:
        Dictionary containing operation results and statistics
        
    Example:
        >>> result = perform_rate_card_calculation(Path("pricing.xlsb"), 0.45)
        >>> print(f"Success: {result['success']}")
        >>> print(f"Rates calculated: {result['successful_calculations']}")
    """
    results = {
        "success": False,
        "excel_file": str(excel_file_path),
        "worksheet_name": worksheet_name,
        "client_margin_percent": client_margin_decimal * 100,
        "standard_rates_found": 0,
        "successful_calculations": 0,
        "rates_written": 0,
        "errors": [],
        "warnings": []
    }
    
    workbook = None
    
    try:
        # Validate environment
        if not validate_excel_environment():
            results["errors"].append("Excel environment validation failed")
            return results
        
        # Open Excel file
        logger.info(f"Opening Excel file: {excel_file_path}")
        workbook = open_excel_file_safely(excel_file_path)
        
        # Get target worksheet
        logger.info(f"Accessing worksheet: {worksheet_name}")
        worksheet = get_worksheet_safely(workbook, worksheet_name)
        
        # Read standard cost rates from column Q
        logger.info("Reading standard cost rates from column Q")
        standard_rates = read_standard_cost_rates(worksheet, column="Q", start_row=28, row_count=7)
        results["standard_rates_found"] = len([r for r in standard_rates if r.is_valid])
        
        if results["standard_rates_found"] == 0:
            results["warnings"].append("No valid standard cost rates found in column Q (rows 28-34)")
        
        # Calculate engineering rates
        logger.info("Calculating engineering rates")
        calculation_result = calculate_engineering_rates(standard_rates, client_margin_decimal)
        results["successful_calculations"] = calculation_result.successful_calculations
        
        if calculation_result.errors:
            results["errors"].extend(calculation_result.errors)
        
        # Write engineering rates to column O
        logger.info("Writing engineering rates to column O")
        write_result = write_engineering_rates(worksheet, calculation_result.calculated_rates, column="O", start_row=28)
        
        if write_result["success"]:
            results["rates_written"] = write_result["written_count"]
            results["success"] = True
        else:
            results["errors"].extend(write_result["errors"])
        
        # Save workbook
        workbook.save()
        logger.info("Rate card calculation completed successfully")
        
    except ExcelAccessError as e:
        results["errors"].append(f"Excel access error: {str(e)}")
        logger.error(f"Rate Card Excel Access Error: {e}")
        logger.error(f"  File: {excel_file_path}")
        logger.error(f"  Margin: {client_margin_decimal * 100:.1f}%")
        
    except WorksheetNotFoundError as e:
        results["errors"].append(f"Worksheet error: {str(e)}")
        logger.error(f"Rate Card Worksheet Error: {e}")
        logger.error(f"  File: {excel_file_path}")
        logger.error(f"  Expected worksheet: {worksheet_name}")
        
    except Exception as e:
        results["errors"].append(f"Unexpected error: {str(e)}")
        logger.error(f"Rate Card Unexpected Error: {e}")
        logger.error(f"  File: {excel_file_path}")
        logger.error(f"  Margin: {client_margin_decimal * 100:.1f}%")
        logger.exception("Full traceback:")
        
    finally:
        # Clean up Excel resources
        if workbook:
            try:
                workbook.close()
                if hasattr(workbook, 'app'):
                    workbook.app.quit()
            except Exception as cleanup_error:
                logger.warning(f"Error during Excel cleanup: {cleanup_error}")
    
    return results


def validate_rate_card_data(excel_file_path: Path, worksheet_name: str = "Resource Setup") -> Dict[str, Any]:
    """
    Validate rate card data without performing calculations.
    
    Args:
        excel_file_path: Path to Excel file to validate
        worksheet_name: Name of worksheet to check
        
    Returns:
        Dictionary containing validation results
    """
    validation_results = {
        "file_accessible": False,
        "worksheet_found": False,
        "standard_rates_valid": 0,
        "total_rate_positions": 7,
        "missing_rates": [],
        "invalid_rates": [],
        "validation_errors": []
    }
    
    workbook = None
    
    try:
        # Check file access
        workbook = open_excel_file_safely(excel_file_path)
        validation_results["file_accessible"] = True
        
        # Check worksheet
        worksheet = get_worksheet_safely(workbook, worksheet_name)
        validation_results["worksheet_found"] = True
        
        # Check standard cost rates
        standard_rates = read_standard_cost_rates(worksheet, column="Q", start_row=28, row_count=7)
        
        for rate in standard_rates:
            if rate.is_valid:
                validation_results["standard_rates_valid"] += 1
            else:
                if "Empty cell" in (rate.error_message or ""):
                    validation_results["missing_rates"].append(rate.staff_level)
                else:
                    validation_results["invalid_rates"].append(f"{rate.staff_level}: {rate.error_message}")
        
    except (ExcelAccessError, WorksheetNotFoundError) as e:
        validation_results["validation_errors"].append(str(e))
        
    except Exception as e:
        validation_results["validation_errors"].append(f"Unexpected validation error: {str(e)}")
        
    finally:
        if workbook:
            try:
                workbook.close()
                if hasattr(workbook, 'app'):
                    workbook.app.quit()
            except:
                pass
    
    return validation_results


def calculate_rate_card_in_worksheet(worksheet, client_margin_decimal: float) -> Dict[str, Any]:
    """
    Perform rate card calculation using an already-open xlwings worksheet.
    
    This function works with an existing xlwings worksheet object (part of an already-open workbook)
    instead of opening files. This enables consolidated Excel operations in a single session.
    
    Args:
        worksheet: xlwings worksheet object (already open)  
        client_margin_decimal: Client margin as decimal (e.g., 0.45 for 45%)
        
    Returns:
        Dictionary containing operation results and statistics
        
    Example:
        >>> with ExcelSessionManager(file_path) as session:
        ...     worksheet = session.get_worksheet("Resource Setup")
        ...     result = calculate_rate_card_in_worksheet(worksheet, 0.45)
        ...     print(f"Rates calculated: {result['successful_calculations']}")
    """
    results = {
        "success": False,
        "worksheet_name": worksheet.name,
        "client_margin_percent": client_margin_decimal * 100,
        "standard_rates_found": 0,
        "successful_calculations": 0,
        "rates_written": 0,
        "errors": [],
        "warnings": []
    }
    
    try:
        # Read standard cost rates from column Q
        logger.info("Reading standard cost rates from column Q in existing session")
        standard_rates = read_standard_cost_rates(worksheet, column="Q", start_row=28, row_count=7)
        results["standard_rates_found"] = len([r for r in standard_rates if r.is_valid])
        
        if results["standard_rates_found"] == 0:
            results["warnings"].append("No valid standard cost rates found in column Q (rows 28-34)")
            return results
        
        # Calculate engineering rates
        logger.info("Calculating engineering rates")
        calculation_result = calculate_engineering_rates(standard_rates, client_margin_decimal)
        results["successful_calculations"] = calculation_result.successful_calculations
        
        if calculation_result.errors:
            results["errors"].extend(calculation_result.errors)
        
        # Write engineering rates to column O
        logger.info("Writing engineering rates to column O")
        write_result = write_engineering_rates(worksheet, calculation_result.calculated_rates, column="O", start_row=28)
        
        if write_result["success"]:
            results["rates_written"] = write_result["written_count"]
            results["success"] = True
            logger.info("Rate card calculation completed successfully in existing session")
        else:
            results["errors"].extend(write_result["errors"])
        
    except Exception as e:
        results["errors"].append(f"Unexpected error in worksheet rate calculation: {str(e)}")
        logger.error(f"Rate Card Worksheet Error: {e}")
        logger.exception("Full traceback:")
    
    return results