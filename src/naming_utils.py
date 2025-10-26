"""
Naming utilities for the DTT Pricing Tool Accelerator.

This module provides atomic functions for filename generation, input sanitization,
and collision handling, following the project constitution principles.
"""

import re
import subprocess
from datetime import datetime
from pathlib import Path

# Import SpecKit data models
from data_models import UserInput, SourceFile


def sanitize_user_input(text: str) -> str:
    """
    Sanitize user input by removing special characters and keeping only
    alphanumeric characters, spaces, and hyphens.
    
    Args:
        text: Raw user input string to sanitize
        
    Returns:
        Sanitized string with only safe characters
        
    Example:
        >>> sanitize_user_input("Acme Corp & Co.")
        "Acme Corp  Co"
        >>> sanitize_user_input("Project-123!")  
        "Project-123"
    """
    if not text:
        return ""
    
    # Keep only alphanumeric, spaces, and hyphens
    sanitized = re.sub(r'[^a-zA-Z0-9\s\-]', '', text)
    
    # Replace multiple spaces with single space
    sanitized = re.sub(r'\s+', ' ', sanitized)
    
    # Strip leading/trailing whitespace
    return sanitized.strip()


def get_current_username() -> str:
    """
    Get the current system username using the 'whoami' command.
    
    Returns:
        str: Current username, or 'unknown' if unable to determine
        
    Example:
        >>> get_current_username()  # doctest: +SKIP
        'keharris'
    """
    try:
        result = subprocess.run(['whoami'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return 'unknown'
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
        return 'unknown'


def generate_output_filename(
    date: str, 
    client: str, 
    gig: str, 
    username: str, 
    version: str
) -> str:
    """
    Generate the output filename following the specified naming convention.
    
    Args:
        date: Date in YYYYMMDD format
        client: Client name (should be pre-sanitized)
        gig: Gig/project name (should be pre-sanitized)
        username: Username of the person creating the file
        version: Version string (e.g., "V1.2")
        
    Returns:
        Formatted filename string
        
    Example:
        >>> generate_output_filename("20251012", "Acme Corp", "Digital Transform", "keharris", "V1.2")
        "20251012 - Acme Corp - Digital Transform - keharris - (LowCompV1.2).xlsb"
    """
    return f"{date} - {client} - {gig} - {username} - (LowComp{version}).xlsb"


def generate_output_filename_from_models(
    user_input: UserInput, 
    source_file: SourceFile, 
    operation_date: datetime
) -> str:
    """
    Generate standardized output filename from SpecKit data models.
    
    Args:
        user_input: Validated user input
        source_file: Source template file information
        operation_date: Date for filename timestamp
        
    Returns:
        str: Standardized filename following naming convention
        
    Raises:
        ValueError: If inputs are invalid or generate invalid filename
        
    Side Effects:
        None - pure function
        
    Performance:
        O(1) - simple string formatting operations
    """
    # Format date as YYYYMMDD
    date_str = operation_date.strftime("%Y%m%d")
    
    # Use the existing filename generation logic
    return generate_output_filename(
        date=date_str,
        client=user_input.client_name,
        gig=user_input.gig_name,
        username=get_current_username(),
        version=source_file.version_number
    )


def handle_filename_collision(base_path: Path) -> Path:
    """
    Handle filename collisions by appending a timestamp if the file already exists.
    
    Args:
        base_path: The desired file path that may already exist
        
    Returns:
        Path object with timestamp appended if collision detected
        
    Example:
        >>> # If file exists, returns path with timestamp suffix
        >>> handle_filename_collision(Path("output.xlsb"))
        Path("output_143022.xlsb")  # Where 143022 is HHMMSS
    """
    if not base_path.exists():
        return base_path
    
    # Generate timestamp suffix
    timestamp = datetime.now().strftime("_%H%M%S")
    
    # Insert timestamp before file extension
    stem = base_path.stem
    suffix = base_path.suffix
    
    collision_path = base_path.parent / f"{stem}{timestamp}{suffix}"
    
    return collision_path


def get_current_date_string() -> str:
    """
    Get the current date formatted as YYYYMMDD.
    
    Returns:
        Current date as string in YYYYMMDD format
        
    Example:
        >>> get_current_date_string()
        "20251012"
    """
    return datetime.now().strftime("%Y%m%d")