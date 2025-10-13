"""
System integration utilities for the DTT Pricing Tool Accelerator.

This module provides atomic functions for Finder integration and OS operations,
following the project constitution principles.
"""

import subprocess
import logging
from pathlib import Path
from typing import Optional


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def open_file_in_finder(file_path: Path) -> bool:
    """
    Open Finder and select the specified file.
    
    Args:
        file_path: Path to file to select in Finder
        
    Returns:
        True if operation was successful, False otherwise
        
    Example:
        >>> success = open_file_in_finder(Path("output.xlsb"))
        >>> print(success)
        True
    """
    if not file_path.exists():
        logger.error(f"Cannot open file in Finder: file does not exist: {file_path}")
        return False
    
    try:
        # Use 'open -R' to open Finder and select the file
        result = subprocess.run(
            ['open', '-R', str(file_path)], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        
        if result.returncode == 0:
            logger.info(f"Successfully opened file in Finder: {file_path.name}")
            return True
        else:
            logger.error(f"Failed to open file in Finder: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.warning("Finder command timed out, but may have succeeded")
        return True  # Timeout often means the UI command launched successfully
        
    except FileNotFoundError:
        logger.error("'open' command not found - are you running on macOS?")
        return False
        
    except Exception as e:
        logger.error(f"Unexpected error opening file in Finder: {e}")
        return False


def open_folder_in_finder(folder_path: Path) -> bool:
    """
    Open the specified folder in Finder (without selecting a specific file).
    
    Args:
        folder_path: Path to folder to open in Finder
        
    Returns:
        True if operation was successful, False otherwise
        
    Example:
        >>> success = open_folder_in_finder(Path("output"))
        >>> print(success)
        True
    """
    if not folder_path.exists():
        logger.error(f"Cannot open folder in Finder: folder does not exist: {folder_path}")
        return False
        
    if not folder_path.is_dir():
        logger.error(f"Cannot open folder in Finder: path is not a directory: {folder_path}")
        return False
    
    try:
        # Use 'open' to open the folder in Finder
        result = subprocess.run(
            ['open', str(folder_path)], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        
        if result.returncode == 0:
            logger.info(f"Successfully opened folder in Finder: {folder_path}")
            return True
        else:
            logger.error(f"Failed to open folder in Finder: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.warning("Finder command timed out, but may have succeeded")
        return True
        
    except FileNotFoundError:
        logger.error("'open' command not found - are you running on macOS?")
        return False
        
    except Exception as e:
        logger.error(f"Unexpected error opening folder in Finder: {e}")
        return False


def show_success_message(file_path: Path, finder_success: bool) -> None:
    """
    Display success message with appropriate formatting.
    
    Args:
        file_path: Path to the created file
        finder_success: Whether Finder integration succeeded
        
    Example:
        >>> show_success_message(Path("output.xlsb"), True)
        ✓ Successfully created: output.xlsb
        ✓ Opening folder with file selected...
    """
    print(f"✅ Successfully created: {file_path.name}")
    
    if finder_success:
        print("✅ Opening folder with file selected...")
    else:
        print("⚠️  File created successfully, but could not open Finder automatically.")
        print(f"   File location: {file_path.parent.absolute()}")


def show_error_message(error_type: str, details: str, suggestion: Optional[str] = None) -> None:
    """
    Display error message with appropriate formatting and guidance.
    
    Args:
        error_type: Type of error (e.g., "File Not Found", "Permission Error")
        details: Detailed error information
        suggestion: Optional suggestion for resolution
        
    Example:
        >>> show_error_message("File Not Found", "template.xlsb not found", "Check source directory")
        ❌ File Not Found: template.xlsb not found
           💡 Suggestion: Check source directory
    """
    print(f"❌ {error_type}: {details}")
    
    if suggestion:
        print(f"   💡 Suggestion: {suggestion}")


def validate_system_requirements() -> bool:
    """
    Validate that system meets requirements for the application.
    
    Returns:
        True if system requirements are met, False otherwise
        
    Example:
        >>> valid = validate_system_requirements()
        >>> print(valid)
        True
    """
    try:
        # Check if 'open' command is available (macOS)
        result = subprocess.run(
            ['which', 'open'], 
            capture_output=True, 
            text=True, 
            timeout=5
        )
        
        if result.returncode != 0:
            logger.error("'open' command not found - macOS required for Finder integration")
            return False
            
        return True
        
    except Exception as e:
        logger.error(f"Error validating system requirements: {e}")
        return False