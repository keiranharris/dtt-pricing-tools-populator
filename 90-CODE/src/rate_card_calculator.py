"""
Rate Card Calculator Module

This module provides atomic functions for calculating engineering rates using
client margin percentage and standard cost rates, following the project 
constitution principles.

Feature 006: Implements rate calculation using the formula:
Engineering Rate = Standard Cost Rate / (1 - Client Margin %)

Dependencies:
- typing: Type hints
- dataclasses: Data structures
- xlwings: Excel integration

Author: DTT Pricing Tool Accelerator
Feature: 006-populate-rate  
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import logging

# Excel integration (will be imported when xlwings is available)
try:
    import xlwings as xw
    XLWINGS_AVAILABLE = True
except ImportError:
    XLWINGS_AVAILABLE = False
    xw = None

logger = logging.getLogger(__name__)


# Import SpecKit data models
from data_models import StandardCostRate, EngineeringRate, RateCalculationResult


def calculate_engineering_rate(standard_cost_rate: float, client_margin_decimal: float) -> float:
    """
    Calculate engineering rate using the formula: Standard Cost Rate / (1 - Client Margin %)
    
    Rate is rounded to the nearest whole integer (no cents) for easier handling.
    
    Args:
        standard_cost_rate: Standard cost rate value
        client_margin_decimal: Client margin as decimal (e.g., 0.45 for 45%)
        
    Returns:
        Calculated engineering rate rounded to nearest whole number
        
    Raises:
        ValueError: If inputs are invalid or margin is >= 1.0
        
    Example:
        >>> rate = calculate_engineering_rate(100.0, 0.45)
        >>> print(f"${rate:.0f}")  # $182
    """
    if not isinstance(standard_cost_rate, (int, float)) or standard_cost_rate <= 0:
        raise ValueError(f"Standard cost rate must be a positive number, got {standard_cost_rate}")
    
    if not isinstance(client_margin_decimal, (int, float)) or client_margin_decimal < 0 or client_margin_decimal >= 1:
        raise ValueError(f"Client margin must be between 0 and 1 (exclusive), got {client_margin_decimal}")
    
    # Formula: Engineering Rate = Standard Cost Rate / (1 - Client Margin %)
    denominator = 1 - client_margin_decimal
    
    if denominator <= 0:
        raise ValueError(f"Invalid margin results in zero or negative denominator: {denominator}")
    
    raw_rate = standard_cost_rate / denominator
    
    # Round to nearest whole integer (no cents)
    return round(raw_rate)


def read_standard_cost_rates(worksheet: Any, column: str = "Q", 
                           start_row: int = 28, row_count: int = 7) -> List[StandardCostRate]:
    """
    Read standard cost rates from Excel column Q.
    
    Args:
        worksheet: xlwings worksheet object
        column: Column letter to read from (default "Q")  
        start_row: Starting row number (default 28)
        row_count: Number of rows to read (default 7)
        
    Returns:
        List of StandardCostRate objects with validation results
        
    Example:
        >>> rates = read_standard_cost_rates(worksheet, "Q", 28, 7)
        >>> valid_rates = [r for r in rates if r.is_valid]
    """
    if not XLWINGS_AVAILABLE:
        logger.error("xlwings is not available for Excel operations")
        return []
    
    rates = []
    
    for i in range(row_count):
        row_num = start_row + i
        staff_level = f"Level {i + 1}"
        
        try:
            cell_reference = f"{column}{row_num}"
            cell_value = worksheet.range(cell_reference).value
            
            if cell_value is None or cell_value == "":
                rates.append(StandardCostRate(
                    staff_level=staff_level,
                    row_index=row_num,
                    is_valid=False,
                    error_message="Empty cell",
                    cell_reference=cell_reference
                ))
                continue
            
            # Try to convert to float
            try:
                cost_rate = float(cell_value)
                if cost_rate <= 0:
                    rates.append(StandardCostRate(
                        staff_level=staff_level,
                        row_index=row_num,
                        is_valid=False,
                        error_message=f"Invalid rate: {cost_rate} (must be positive)",
                        cell_reference=cell_reference
                    ))
                else:
                    rates.append(StandardCostRate(
                        staff_level=staff_level,
                        cost_rate=cost_rate,
                        row_index=row_num,
                        is_valid=True,
                        cell_reference=cell_reference
                    ))
            except (ValueError, TypeError):
                rates.append(StandardCostRate(
                    staff_level=staff_level,
                    row_index=row_num,
                    is_valid=False,
                    error_message=f"Non-numeric value: {cell_value}",
                    cell_reference=cell_reference
                ))
                
        except Exception as e:
            rates.append(StandardCostRate(
                staff_level=staff_level,
                row_index=row_num,
                is_valid=False,
                error_message=f"Excel error: {str(e)}",
                cell_reference=f"{column}{row_num}"
            ))
    
    return rates


def calculate_engineering_rates(standard_rates: List[StandardCostRate], 
                              client_margin_decimal: float) -> RateCalculationResult:
    """
    Calculate engineering rates for all valid standard cost rates.
    
    Args:
        standard_rates: List of standard cost rates
        client_margin_decimal: Client margin as decimal (e.g., 0.45 for 45%)
        
    Returns:
        RateCalculationResult with calculated rates and statistics
        
    Example:
        >>> rates = calculate_engineering_rates(standard_rates, 0.45)
        >>> print(f"Calculated {rates.successful_calculations} rates")
    """
    calculated_rates = []
    errors = []
    successful = 0
    skipped = 0
    
    for standard_rate in standard_rates:
        if not standard_rate.is_valid or standard_rate.cost_rate is None:
            skipped += 1
            calculated_rates.append(EngineeringRate(
                staff_level=standard_rate.staff_level,
                row_index=standard_rate.row_index,
                is_valid=False,
                error_message=standard_rate.error_message or "Invalid standard rate",
                cell_reference=f"O{standard_rate.row_index}" if standard_rate.row_index else None
            ))
            continue
        
        try:
            engineering_rate_value = calculate_engineering_rate(
                standard_rate.cost_rate, 
                client_margin_decimal
            )
            
            calculated_rates.append(EngineeringRate(
                staff_level=standard_rate.staff_level,
                standard_cost_rate=standard_rate.cost_rate,
                client_margin=client_margin_decimal,
                engineering_rate=engineering_rate_value,
                row_index=standard_rate.row_index,
                is_valid=True,
                cell_reference=f"O{standard_rate.row_index}" if standard_rate.row_index else None
            ))
            successful += 1
            
        except Exception as e:
            error_msg = f"Calculation failed for {standard_rate.staff_level}: {str(e)}"
            errors.append(error_msg)
            calculated_rates.append(EngineeringRate(
                staff_level=standard_rate.staff_level,
                standard_cost_rate=standard_rate.cost_rate,
                client_margin=client_margin_decimal,
                row_index=standard_rate.row_index,
                is_valid=False,
                error_message=str(e),
                cell_reference=f"O{standard_rate.row_index}" if standard_rate.row_index else None
            ))
    
    return RateCalculationResult(
        calculated_rates=calculated_rates,
        total_processed=len(standard_rates),
        successful_calculations=successful,
        skipped_invalid=skipped,
        errors=errors
    )


def write_engineering_rates(worksheet: Any, engineering_rates: List[EngineeringRate],
                          column: str = "O", start_row: int = 28) -> Dict[str, Any]:
    """
    Write calculated engineering rates to Excel column O.
    
    Args:
        worksheet: xlwings worksheet object
        engineering_rates: List of calculated engineering rates
        column: Column letter to write to (default "O")
        start_row: Starting row number (default 28)
        
    Returns:
        Dictionary with write operation results
        
    Example:
        >>> result = write_engineering_rates(worksheet, rates, "O", 28)
        >>> print(f"Wrote {result['written_count']} values")
    """
    if not XLWINGS_AVAILABLE:
        logger.error("xlwings is not available for Excel operations")
        return {"success": False, "error": "xlwings not available"}
    
    written_count = 0
    skipped_count = 0
    errors = []
    
    for i, rate in enumerate(engineering_rates):
        row_num = start_row + i
        cell_reference = f"{column}{row_num}"
        
        try:
            if rate.is_valid and rate.engineering_rate is not None:
                # Format as whole currency (no cents)
                formatted_value = f"${int(rate.engineering_rate)}"
                worksheet.range(cell_reference).value = formatted_value
                written_count += 1
            else:
                # Skip invalid rates (leave cell unchanged)
                skipped_count += 1
                logger.warning(f"Skipped {rate.staff_level}: {rate.error_message}")
                
        except Exception as e:
            error_msg = f"Failed to write {rate.staff_level} to {cell_reference}: {str(e)}"
            errors.append(error_msg)
            logger.error(error_msg)
    
    return {
        "success": len(errors) == 0,
        "written_count": written_count,
        "skipped_count": skipped_count,
        "total_processed": len(engineering_rates),
        "errors": errors
    }