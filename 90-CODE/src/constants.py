"""
Global constants for column mappings in Pricing Tool Accelerator
"""

# ============================================================================
# DIRECTORY CONFIGURATION  
# ============================================================================
# All directory paths - OneDrive shared library for team collaboration
# Updated: 2025-10-26 - Centralized all directory paths for consistency
# Uses ~ for cross-teammate compatibility (automatic home directory expansion)

# Constants directory - contains Excel files with field mappings and values
CONSTANTS_DIRECTORY = '~/Library/CloudStorage/OneDrive-SharedLibraries-Deloitte(O365D)/AU CBO Practice - MO - Cloud Network & Security/_PRESALES/_PROPOSALS/_PricingToolAccel/00-CONSTANTS/'

# Source pricing tools directory - contains template Excel files
PRICING_TOOL_SOURCE_DIRECTORY = '~/Library/CloudStorage/OneDrive-SharedLibraries-Deloitte(O365D)/AU CBO Practice - MO - Cloud Network & Security/_PRESALES/_PROPOSALS/_PricingToolAccel/10-LATEST-PRICING-TOOLS/'

# Output directory - where completed pricing tools are saved
OUTPUT_DIRECTORY = '~/Library/CloudStorage/OneDrive-SharedLibraries-Deloitte(O365D)/AU CBO Practice - MO - Cloud Network & Security/_PRESALES/_PROPOSALS/_PricingToolAccel/20-OUTPUT/'

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
