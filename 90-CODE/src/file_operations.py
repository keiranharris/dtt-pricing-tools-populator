"""
File operations for the DTT Pricing Tool Accelerator.

This module provides atomic functions for file discovery, version extraction,
copy operations, and Excel format conversion, following the project constitution principles.
"""

import re
import shutil
from pathlib import Path
from typing import Optional


def find_source_file(source_dir: Path, pattern: str) -> Path:
    """
    Find the source file containing the specified pattern in the source directory.
    
    Args:
        source_dir: Directory to search for the source file
        pattern: Pattern to match in filenames (e.g., "Low Complexity")
        
    Returns:
        Path to the found source file
        
    Raises:
        FileNotFoundError: If no file matching pattern is found
        RuntimeError: If multiple files match the pattern
        
    Example:
        >>> source_dir = Path("10-LATEST-PRICING-TOOLS")
        >>> file_path = find_source_file(source_dir, "Low Complexity")
        >>> print(file_path.name)
        "FY26 Low Complexity Pricing Tool v1.2.xlsb"
    """
    if not source_dir.exists():
        raise FileNotFoundError(f"Source directory not found: {source_dir}")
    
    if not source_dir.is_dir():
        raise FileNotFoundError(f"Source path is not a directory: {source_dir}")
    
    # Find files matching the pattern (exclude temporary Excel files starting with ~$)
    matching_files = []
    for file_path in source_dir.iterdir():
        if (file_path.is_file() and 
            pattern.lower() in file_path.name.lower() and 
            not file_path.name.startswith('~$')):
            matching_files.append(file_path)
    
    if not matching_files:
        raise FileNotFoundError(
            f"No files containing '{pattern}' found in {source_dir}. "
            f"Available files: {[f.name for f in source_dir.iterdir() if f.is_file()]}"
        )
    
    if len(matching_files) > 1:
        raise RuntimeError(
            f"Multiple files containing '{pattern}' found in {source_dir}: "
            f"{[f.name for f in matching_files]}. Please ensure only one template exists."
        )
    
    return matching_files[0]


def extract_version_from_filename(filename: str) -> str:
    """
    Extract version number from filename using regex pattern.
    
    Args:
        filename: Filename to extract version from
        
    Returns:
        Version string in format "V{major}.{minor}" (e.g., "V1.2")
        
    Raises:
        ValueError: If no version pattern is found in filename
        
    Example:
        >>> extract_version_from_filename("FY26 Low Complexity Pricing Tool v1.2.xlsb")
        "V1.2"
        >>> extract_version_from_filename("Tool v2.5.xlsb")
        "V2.5"
    """
    version_pattern = r'v(\d+\.\d+)'
    match = re.search(version_pattern, filename, re.IGNORECASE)
    
    if not match:
        raise ValueError(
            f"No version pattern found in filename: '{filename}'. "
            "Expected format: 'v{major}.{minor}' (e.g., 'v1.2')"
        )
    
    version = match.group(1)
    return f"V{version}"


def copy_file_with_rename(source: Path, destination: Path) -> bool:
    """
    Copy source file to destination with metadata preservation and writable permissions.
    
    Args:
        source: Source file path
        destination: Destination file path
        
    Returns:
        True if copy was successful
        
    Raises:
        FileNotFoundError: If source file doesn't exist
        PermissionError: If insufficient permissions for copy operation
        OSError: If copy operation fails for other reasons
        
    Example:
        >>> source = Path("template.xlsb")
        >>> dest = Path("output/new_file.xlsb")
        >>> success = copy_file_with_rename(source, dest)
        >>> print(success)
        True
    """
    import stat
    
    if not source.exists():
        raise FileNotFoundError(f"Source file not found: {source}")
    
    if not source.is_file():
        raise FileNotFoundError(f"Source path is not a file: {source}")
    
    # Ensure destination directory exists
    destination.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Use shutil.copy2 to preserve metadata (timestamps, permissions)
        shutil.copy2(source, destination)
        
        # Remove read-only flag by adding write permissions for user
        current_mode = destination.stat().st_mode
        writable_mode = current_mode | stat.S_IWUSR | stat.S_IWGRP
        destination.chmod(writable_mode)
        
        # Remove ALL extended attributes that can cause read-only warnings
        try:
            import subprocess
            
            # Remove all extended attributes at once (most reliable method)
            result = subprocess.run(['xattr', '-c', str(destination)], 
                                  capture_output=True, text=True, check=False)
            
            # Verify removal was successful
            verify_result = subprocess.run(['xattr', str(destination)], 
                                         capture_output=True, text=True, check=False)
            
            if verify_result.returncode == 0 and not verify_result.stdout.strip():
                # Success: no attributes remaining
                pass
            else:
                # Fallback: try removing each attribute individually
                if verify_result.stdout.strip():
                    attributes = verify_result.stdout.strip().split('\n')
                    for attr in attributes:
                        if attr.strip():
                            subprocess.run(['xattr', '-d', attr.strip(), str(destination)], 
                                         capture_output=True, check=False)
                         
        except Exception as e:
            # Log the error but continue - file is still usable
            # In a production version, this could use proper logging
            import sys
            print(f"Warning: Failed to remove extended attributes: {e}", file=sys.stderr)
        
        # Verify the copy was successful by comparing file sizes
        if source.stat().st_size != destination.stat().st_size:
            raise OSError(f"File copy verification failed: size mismatch")
        
        return True
        
    except PermissionError as e:
        raise PermissionError(
            f"Permission denied copying file. Check read access to {source} "
            f"and write access to {destination.parent}. Error: {e}"
        )
    except OSError as e:
        raise OSError(f"File copy operation failed: {e}")


def get_source_file_info(source_dir: Path, pattern: str) -> tuple[Path, str]:
    """
    Get source file path and extract version information.
    
    Args:
        source_dir: Directory to search for source file
        pattern: Pattern to match in filenames
        
    Returns:
        Tuple of (source_file_path, version_string)
        
    Raises:
        FileNotFoundError: If source file not found
        ValueError: If version cannot be extracted
        
    Example:
        >>> source_dir = Path("10-LATEST-PRICING-TOOLS")
        >>> file_path, version = get_source_file_info(source_dir, "Low Complexity")
        >>> print(f"File: {file_path.name}, Version: {version}")
        "File: FY26 Low Complexity Pricing Tool v1.2.xlsb, Version: V1.2"
    """
    source_file = find_source_file(source_dir, pattern)
    version = extract_version_from_filename(source_file.name)
    
    return source_file, version


def convert_xlsb_to_xlsx(xlsb_path: Path, xlsx_path: Path) -> bool:
    """
    Convert Excel binary (.xlsb) file to standard Excel (.xlsx) format.
    
    This function uses xlwings to open the .xlsb file and openpyxl to save it
    as .xlsx format, preserving all worksheet data, formatting, and structure.
    
    Args:
        xlsb_path: Source .xlsb file path
        xlsx_path: Destination .xlsx file path
        
    Returns:
        True if conversion was successful
        
    Raises:
        FileNotFoundError: If source .xlsb file doesn't exist
        RuntimeError: If Excel conversion fails
        ImportError: If required libraries (xlwings/openpyxl) not available
        
    Example:
        >>> source = Path("template.xlsb")
        >>> dest = Path("converted.xlsx") 
        >>> success = convert_xlsb_to_xlsx(source, dest)
        >>> print(success)
        True
    """
    if not xlsb_path.exists():
        raise FileNotFoundError(f"Source .xlsb file not found: {xlsb_path}")
    
    if not xlsb_path.suffix.lower() == '.xlsb':
        raise ValueError(f"Source file must be .xlsb format, got: {xlsb_path.suffix}")
    
    try:
        import xlwings as xw
        import openpyxl
        
        # Ensure destination directory exists
        xlsx_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Use xlwings to open the .xlsb file (requires Excel to be installed)
        with xw.App(visible=False) as app:
            # Open the .xlsb file
            xlsb_book = app.books.open(xlsb_path)
            
            # Save as .xlsx format using Excel's native conversion
            xlsb_book.save(xlsx_path)
            xlsb_book.close()
            
        # Verify the conversion by trying to open with openpyxl
        try:
            test_workbook = openpyxl.load_workbook(xlsx_path, data_only=True)
            test_workbook.close()
        except Exception as e:
            raise RuntimeError(f"Conversion verification failed - openpyxl cannot read result: {e}")
            
        return True
        
    except ImportError as e:
        raise ImportError(f"Required libraries not available for .xlsb conversion: {e}")
    except Exception as e:
        raise RuntimeError(f"Excel conversion failed: {e}")


def copy_and_convert_file(source: Path, destination: Path) -> bool:
    """
    Copy file and convert .xlsb to .xlsx if needed to ensure compatibility.
    
    This function automatically detects .xlsb files and converts them to .xlsx
    format for better compatibility with openpyxl data population features.
    
    Args:
        source: Source file path
        destination: Destination file path (extension may be modified)
        
    Returns:
        True if copy/conversion was successful
        
    Raises:
        FileNotFoundError: If source file doesn't exist
        RuntimeError: If conversion fails for .xlsb files
        
    Example:
        >>> source = Path("template.xlsb")
        >>> dest = Path("output.xlsb")  # Will become output.xlsx automatically
        >>> success = copy_and_convert_file(source, dest)
        >>> print(dest.with_suffix('.xlsx').exists())  # True
        True
    """
    if not source.exists():
        raise FileNotFoundError(f"Source file not found: {source}")
    
    # If source is .xlsb, convert destination to .xlsx and perform conversion
    if source.suffix.lower() == '.xlsb':
        xlsx_destination = destination.with_suffix('.xlsx')
        return convert_xlsb_to_xlsx(source, xlsx_destination)
    else:
        # For non-.xlsb files, use regular copy
        return copy_file_with_rename(source, destination)