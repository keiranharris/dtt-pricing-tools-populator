"""
Resource Setup Populator Module

This module handles copying structured resource data from constants file to target
pricing tool spreadsheets. Implements dynamic positioning to place resource data
in the last available editable rows of the Resource Setup worksheet.

Dependencies:
- dataclasses: Data structures
- pathlib: Path handling
- typing: Type hints
- xlwings: Excel automation (.xlsb support)

Author: DTT Pricing Tool Accelerator
Feature: 005-populate-resource-setup
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple
import logging
import time

try:
    import xlwings as xw
except ImportError:
    xw = None

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class ResourceCopyResult:
    """Results from resource setup range copying."""
    cells_copied: int
    source_range: str
    target_range: str
    success: bool
    error_messages: List[str]
    execution_time: float
    
    def __str__(self) -> str:
        status = "SUCCESS" if self.success else "FAILED"
        return f"Resource Copy [{status}]: {self.cells_copied} cells copied in {self.execution_time:.1f}s"


@dataclass  
class ValidationResult:
    """Validation results for resource setup prerequisites."""
    source_worksheet_exists: bool
    target_worksheet_exists: bool
    source_data_found: bool
    target_area_accessible: bool
    validation_errors: List[str]
    
    @property
    def is_valid(self) -> bool:
        """Check if all validation criteria are met."""
        return (self.source_worksheet_exists and 
                self.target_worksheet_exists and 
                self.source_data_found and 
                self.target_area_accessible)


class ResourceSetupError(Exception):
    """Custom exception for resource setup operations."""
    pass


def find_source_resource_data(source_worksheet, expected_rows: int = 7) -> Optional[str]:
    """
    Find the source resource data range in the constants file.
    
    This function locates the resource data block in the source worksheet.
    Based on the user's screenshot, it appears the resource data is at the top
    of the Resource Setup sheet, not at rows 28-34.
    
    Args:
        source_worksheet: xlwings worksheet object for constants file
        expected_rows: Expected number of resource data rows
        
    Returns:
        Range string like "C1:H7" or None if not found
        
    Raises:
        ResourceSetupError: If worksheet access fails or data format unexpected
    """
    try:
        # Strategy: User confirmed the range should be C28:H34 (not B28:H34)
        # The pink highlighted cells in the screenshot are in C-H columns
        test_ranges = [
            f"C28:H{27 + expected_rows}",  # Correct expected location - C28:H34
            f"C25:H{24 + expected_rows}",  # A bit higher in C-H
            f"C30:H{29 + expected_rows}",  # A bit lower in C-H
            f"B28:H{27 + expected_rows}",  # Fallback: B-H columns (in case data shifted)
            f"D28:I{27 + expected_rows}",  # Fallback: D-I columns (in case data shifted right)
            f"A28:H{27 + expected_rows}",  # Fallback: Include A column
        ]
        
        for test_range in test_ranges:
            logger.debug(f"Testing range for resource data: {test_range}")
            
            try:
                data = source_worksheet.range(test_range).value
                # Check if we have substantial data (not just empty cells or "Group 1" repeats)
                if data and _has_meaningful_resource_data(data):
                    logger.info(f"Found meaningful resource data in range: {test_range}")
                    return test_range
            except Exception as e:
                logger.warning(f"Could not access range {test_range}: {e}")
        
        # If not found, try a more comprehensive search
        logger.info("Attempting comprehensive search for resource data...")
        return _comprehensive_resource_search(source_worksheet, expected_rows)
        
    except Exception as e:
        raise ResourceSetupError(f"Failed to search for source resource data: {e}")


def _has_meaningful_resource_data(data) -> bool:
    """
    Check if the data contains meaningful resource information.
    
    This helps distinguish between real resource data and empty/placeholder rows.
    """
    if not data:
        return False
        
    # Convert single row to list of lists for consistent processing
    if not isinstance(data[0], list):
        data = [data]
    
    meaningful_rows = 0
    for row in data:
        if not row:
            continue
            
        # Look for signs of real resource data
        row_str = ' '.join(str(cell) for cell in row if cell)
        
        # Skip rows that are just "Group 1" or similar placeholder text
        if row_str and not (row_str.strip() in ['Group 1', 'Group 2', 'Group 3', '']):
            # Look for resource-like content
            resource_indicators = ['deloitte', 'consultant', 'manager', 'director', 'tech', 'transformation']
            if any(indicator in row_str.lower() for indicator in resource_indicators):
                meaningful_rows += 1
    
    # We need at least 2-3 rows of meaningful data
    return meaningful_rows >= 2


def _comprehensive_resource_search(source_worksheet, expected_rows: int) -> Optional[str]:
    """
    Perform a more thorough search across the worksheet for resource data.
    """
    try:
        # Get the used range to limit our search
        used_range = source_worksheet.used_range
        if not used_range:
            return None
            
        max_row = min(used_range.last_cell.row, 50)  # Don't search too far down
        
        # Search through the first several rows for meaningful data
        for start_row in range(1, min(max_row - expected_rows + 2, 20)):
            for start_col in ['A', 'B', 'C']:
                end_col = chr(ord(start_col) + 5)  # 6 columns wide
                test_range = f"{start_col}{start_row}:{end_col}{start_row + expected_rows - 1}"
                
                try:
                    data = source_worksheet.range(test_range).value
                    if _has_meaningful_resource_data(data):
                        logger.info(f"Comprehensive search found data: {test_range}")
                        return test_range
                except:
                    continue
        
        logger.warning("Comprehensive search found no suitable resource data")
        return None
        
    except Exception as e:
        logger.error(f"Comprehensive search failed: {e}")
        return None


def find_target_editable_area(target_worksheet, required_rows: int = 7) -> Optional[str]:
    """
    Find available rows in target worksheet for resource data.
    
    Based on the user's screenshot, there are many empty rows with "Group 1" 
    placeholders. We'll look for a suitable empty area to place the actual resource data.
    
    Args:
        target_worksheet: xlwings worksheet object for target file
        required_rows: Number of rows needed for resource data
        
    Returns:
        Range string for target area like "B28:H34" or None if not found
        
    Raises:
        ResourceSetupError: If worksheet access fails or no suitable area found
    """
    try:
        # Strategy: Look for empty rows that we can populate
        # Based on screenshot, there are many rows with just "Group 1" that we can use
        
        # Try common locations where resource data should go
        search_locations = [
            28,  # Original expectation (C28:H34 area)
            25,  # A bit higher 
            30,  # A bit lower
            20,  # Higher up
            35,  # Lower down
        ]
        
        # Try both B-H and C-H column ranges (screenshot shows data in B column too)
        column_ranges = [
            ('B', 'H'),  # Broader range including B column
            ('C', 'H'),  # Original expected range
            ('A', 'H'),  # Even broader if needed
        ]
        
        for start_row in search_locations:
            for start_col, end_col in column_ranges:
                target_range = f"{start_col}{start_row}:{end_col}{start_row + required_rows - 1}"
                
                logger.debug(f"Testing target area: {target_range}")
                
                try:
                    # Test if this range is accessible (not protected)
                    test_data = target_worksheet.range(target_range).value
                    
                    # Check if this area is mostly empty or has placeholder text
                    if _is_suitable_target_area(test_data):
                        logger.info(f"Found suitable target area: {target_range}")
                        return target_range
                        
                except Exception as e:
                    logger.debug(f"Range {target_range} not accessible: {e}")
                    continue
        
        # If no suitable range found in expected areas, try a broader search
        logger.info("Searching more broadly for target area...")
        return _find_any_empty_area(target_worksheet, required_rows)
        
    except ResourceSetupError:
        raise
    except Exception as e:
        raise ResourceSetupError(f"Failed to find target editable area: {e}")


def _is_suitable_target_area(data) -> bool:
    """
    Check if a target area is suitable for placing resource data.
    
    Suitable areas are mostly empty or contain placeholder text like "Group 1".
    """
    if not data:
        return True  # Empty area is suitable
    
    # Convert single row to list format
    if not isinstance(data[0], list):
        data = [data]
    
    empty_or_placeholder_rows = 0
    total_rows = len(data)
    
    for row in data:
        if not row:
            empty_or_placeholder_rows += 1
            continue
            
        # Check if row contains only placeholder text
        row_content = ' '.join(str(cell) for cell in row if cell).strip()
        
        if (not row_content or 
            row_content in ['Group 1', 'Group 2', 'Group 3'] or
            all(not cell for cell in row)):
            empty_or_placeholder_rows += 1
    
    # Area is suitable if most rows are empty or placeholder
    suitability_threshold = 0.8  # 80% of rows should be empty/placeholder
    return (empty_or_placeholder_rows / total_rows) >= suitability_threshold


def _find_any_empty_area(target_worksheet, required_rows: int) -> Optional[str]:
    """
    Find any available empty area in the worksheet as fallback.
    """
    try:
        # Search through reasonable row ranges
        for start_row in range(20, 101, 5):  # Search rows 20-100 in steps of 5
            for start_col in ['B', 'C']:
                end_col = 'H'
                target_range = f"{start_col}{start_row}:{end_col}{start_row + required_rows - 1}"
                
                try:
                    test_data = target_worksheet.range(target_range).value
                    if _is_suitable_target_area(test_data):
                        logger.info(f"Fallback search found area: {target_range}")
                        return target_range
                except:
                    continue
        
        return None
        
    except Exception:
        return None


def copy_resource_setup_range(
    source_file: Path,
    target_file: Path,
    resource_row_count: int = 7,
    worksheet_name: str = "Resource Setup"
) -> ResourceCopyResult:
    """
    Copy resource setup data from source to target file using dynamic positioning.
    
    This is the main function that orchestrates the resource setup copying process.
    It finds the source resource data, identifies a suitable target location, and
    performs the copy operation.
    
    Args:
        source_file: Path to constants file containing resource data
        target_file: Path to target pricing tool file
        resource_row_count: Number of resource rows to copy (default 7)
        worksheet_name: Name of worksheet containing resource data
        
    Returns:
        ResourceCopyResult with details of the operation
        
    Raises:
        ResourceSetupError: For various failure scenarios
    """
    start_time = time.time()
    
    if not xw:
        raise ResourceSetupError("xlwings not available - required for Resource Setup population")
    
    errors = []
    
    try:
        # Open or get existing Excel application
        try:
            app = xw.apps.active
            if app is None:
                raise Exception("No active app")
        except:
            app = xw.App(visible=False)
        
        source_wb = None
        target_wb = None
        
        try:
            # Open source file (constants)
            source_wb = app.books.open(source_file)
            source_ws = source_wb.sheets[worksheet_name]
            
            # Open target file
            target_wb = app.books.open(target_file)
            target_ws = target_wb.sheets[worksheet_name]
            
            # Find source resource data
            source_range = find_source_resource_data(source_ws, resource_row_count)
            if not source_range:
                raise ResourceSetupError(f"No resource data found in source {worksheet_name} worksheet")
            
            # Find target editable area
            target_range = find_target_editable_area(target_ws, resource_row_count)
            if not target_range:
                raise ResourceSetupError(f"No suitable editable area found in target {worksheet_name} worksheet")
            
            # Perform the copy operation
            source_data = source_ws.range(source_range).value
            if not source_data:
                raise ResourceSetupError(f"Source range {source_range} contains no data")
            
            # Copy data to target
            target_ws.range(target_range).value = source_data
            
            # Calculate cells copied
            if isinstance(source_data[0], list):
                cells_copied = len(source_data) * len(source_data[0])
            else:
                cells_copied = len(source_data) if isinstance(source_data, list) else 1
            
            # Save target file
            target_wb.save()
            
            execution_time = time.time() - start_time
            
            logger.info(f"Successfully copied {cells_copied} cells from {source_range} to {target_range}")
            
            return ResourceCopyResult(
                cells_copied=cells_copied,
                source_range=source_range,
                target_range=target_range,
                success=True,
                error_messages=[],
                execution_time=execution_time
            )
            
        finally:
            # Clean up - close workbooks but leave app running for other operations
            if source_wb:
                try:
                    source_wb.close()
                except:
                    pass
            if target_wb:
                try:
                    target_wb.close()
                except:
                    pass
    
    except ResourceSetupError:
        raise
    except Exception as e:
        execution_time = time.time() - start_time
        error_msg = f"Unexpected error during resource setup copy: {e}"
        logger.error(error_msg)
        
        return ResourceCopyResult(
            cells_copied=0,
            source_range="",
            target_range="",
            success=False,
            error_messages=[error_msg],
            execution_time=execution_time
        )


def validate_resource_setup_requirements(
    source_file: Path,
    target_file: Path,
    worksheet_name: str = "Resource Setup"
) -> ValidationResult:
    """
    Validate that resource setup prerequisites are met.
    
    Checks that both files exist, contain the required worksheets, and that
    the source contains resource data while target has accessible area.
    
    Args:
        source_file: Path to constants file
        target_file: Path to target pricing tool file  
        worksheet_name: Name of Resource Setup worksheet
        
    Returns:
        ValidationResult with detailed validation status
    """
    errors = []
    source_ws_exists = False
    target_ws_exists = False
    source_data_found = False
    target_area_accessible = False
    
    if not xw:
        errors.append("xlwings not available - required for Resource Setup")
        return ValidationResult(False, False, False, False, errors)
    
    try:
        app = xw.apps.active if xw.apps.active else xw.App(visible=False)
        
        # Check source file and worksheet
        try:
            source_wb = app.books.open(source_file)
            try:
                source_ws = source_wb.sheets[worksheet_name]
                source_ws_exists = True
                
                # Check if source has resource data
                if find_source_resource_data(source_ws):
                    source_data_found = True
                else:
                    errors.append(f"No resource data found in source {worksheet_name}")
                    
            except Exception as e:
                errors.append(f"Source worksheet '{worksheet_name}' not accessible: {e}")
            finally:
                source_wb.close()
                
        except Exception as e:
            errors.append(f"Cannot open source file {source_file}: {e}")
        
        # Check target file and worksheet
        try:
            target_wb = app.books.open(target_file)
            try:
                target_ws = target_wb.sheets[worksheet_name]
                target_ws_exists = True
                
                # Check if target has accessible area
                if find_target_editable_area(target_ws):
                    target_area_accessible = True
                else:
                    errors.append(f"No editable area found in target {worksheet_name}")
                    
            except Exception as e:
                errors.append(f"Target worksheet '{worksheet_name}' not accessible: {e}")
            finally:
                target_wb.close()
                
        except Exception as e:
            errors.append(f"Cannot open target file {target_file}: {e}")
            
    except Exception as e:
        errors.append(f"Excel application error: {e}")
    
    return ValidationResult(
        source_worksheet_exists=source_ws_exists,
        target_worksheet_exists=target_ws_exists,
        source_data_found=source_data_found,
        target_area_accessible=target_area_accessible,
        validation_errors=errors
    )


def get_resource_setup_summary(copy_result: ResourceCopyResult) -> str:
    """
    Generate a user-friendly summary of resource setup operation.
    
    Args:
        copy_result: Result from copy_resource_setup_range operation
        
    Returns:
        Formatted summary string for user feedback
    """
    if copy_result.success:
        return (f"✅ Resource Setup: {copy_result.cells_copied} cells copied "
                f"({copy_result.source_range} → {copy_result.target_range}) "
                f"in {copy_result.execution_time:.1f}s")
    else:
        error_summary = "; ".join(copy_result.error_messages[:2])  # Limit to first 2 errors
        return f"❌ Resource Setup failed: {error_summary}"