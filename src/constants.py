"""
Global constants for column mappings in Pricing Tool Accelerator
"""

import logging

# Configure logging
logger = logging.getLogger(__name__)

# ============================================================================
# DIRECTORY CONFIGURATION  
# ============================================================================
# Dynamic OneDrive path resolution - requires configuration
# Feature 009: OneDrive Path Configuration - Secure, configuration-only paths

def _get_dynamic_paths():
    """
    Get directory paths from OneDrive configuration.
    
    Returns:
        tuple: (constants_dir, source_dir, output_dir) as strings
        
    Raises:
        ConfigurationError: If no valid configuration exists
    """
    from src.path_configuration import ConfigurationManager
    
    config_manager = ConfigurationManager()
    directory_paths = config_manager.get_configured_paths()
    
    logger.debug("Using configured OneDrive paths")
    return (
        str(directory_paths.constants_directory),
        str(directory_paths.source_directory), 
        str(directory_paths.output_directory)
    )

# Lazy-loaded constants - evaluated when first accessed, not at import time
_cached_paths = None

def _get_paths():
    """Get paths with caching to avoid repeated configuration lookups."""
    global _cached_paths
    if _cached_paths is None:
        _cached_paths = _get_dynamic_paths()
    return _cached_paths

def get_constants_directory():
    """Get the constants directory path."""
    return _get_paths()[0]

def get_pricing_tool_source_directory():
    """Get the pricing tool source directory path."""
    return _get_paths()[1]

def get_output_directory():
    """Get the output directory path."""
    return _get_paths()[2]

# For backwards compatibility - these will be set after OneDrive setup
CONSTANTS_DIRECTORY = None
PRICING_TOOL_SOURCE_DIRECTORY = None
OUTPUT_DIRECTORY = None

def initialize_paths():
    """Initialize path constants - called after OneDrive setup is complete."""
    global CONSTANTS_DIRECTORY, PRICING_TOOL_SOURCE_DIRECTORY, OUTPUT_DIRECTORY
    paths = _get_paths()
    CONSTANTS_DIRECTORY = paths[0]
    PRICING_TOOL_SOURCE_DIRECTORY = paths[1] 
    OUTPUT_DIRECTORY = paths[2]

# ============================================================================
# EXCEL COLUMN MAPPINGS
# ============================================================================

# Pricing Setup sheet column mappings
PRICING_SETUP_CONSTANTS_FIELD_COL = 'C'  # Field names in constants file
PRICING_SETUP_CONSTANTS_VALUE_COL = 'D'  # Values in constants file
PRICING_SETUP_OUTPUT_FIELD_COL = 'E'     # Field names in output file
PRICING_SETUP_OUTPUT_VALUE_COL = 'F'     # Values in output file

# For xlwings, also provide numeric indices (1-based)
PRICING_SETUP_CONSTANTS_FIELD_COL_IDX = 3
PRICING_SETUP_CONSTANTS_VALUE_COL_IDX = 4
PRICING_SETUP_OUTPUT_FIELD_COL_IDX = 5
PRICING_SETUP_OUTPUT_VALUE_COL_IDX = 6
