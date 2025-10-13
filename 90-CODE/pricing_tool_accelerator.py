#!/usr/bin/env python3
"""
DTT Pricing Tool Accelerator

Main entry point for automating pricing tool administrative tasks.
Copies and renames Excel templates based on user input.
"""

import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

# ============================================================================
# FEATURE 002: EXCEL DATA POPULATION CONFIGURATION
# ============================================================================
# These constants control data population from the constants file.
# Update these values to change behavior without modifying code.

# Constants file configuration
CONSTANTS_FILENAME = "lowcomplexity_const_KHv1.xlsx"  # Easy to update when constants file changes
CONSTANTS_DIR_NAME = "00-CONSTANTS"                   # Directory containing constants files

# Target worksheet configuration  
TARGET_WORKSHEET_NAME = "Pricing Setup"               # Worksheet to populate in target file

# Field matching configuration
FIELD_MATCH_THRESHOLD = 0.8                          # Minimum similarity score for field matches (0.0-1.0)
CHAR_STRIP_COUNT = 2                                 # Characters to strip from start/end for core matching

# ============================================================================
# FEATURE 005: RESOURCE SETUP CONFIGURATION
# ============================================================================
# These constants control Resource Setup data copying from the constants file.

# Resource Setup configuration
RESOURCE_SETUP_ROW_COUNT = 7                         # Number of resource rows to copy
RESOURCE_SETUP_WORKSHEET_NAME = "Resource Setup"     # Worksheet name in both files
RESOURCE_SETUP_ENABLED = True                        # Feature toggle

# ============================================================================

from cli_interface import collect_user_inputs, collect_cli_fields, collect_margin_percentage
from file_operations import get_source_file_info, copy_file_with_rename
from naming_utils import generate_output_filename, get_current_date_string, handle_filename_collision
from system_integration import (
    open_file_in_finder, 
    show_success_message, 
    show_error_message, 
    validate_system_requirements
)

# Feature 002: Data Population imports (backward compatible)
from data_population_orchestrator import populate_spreadsheet_data, show_population_feedback
# Feature 003: Enhanced CLI Population imports
from data_population_orchestrator import populate_spreadsheet_data_with_cli
# Feature 005: Resource Setup Population imports
from data_population_orchestrator import populate_spreadsheet_data_with_cli_and_resources
# Feature 006: Rate Card Population imports
from data_population_orchestrator import populate_spreadsheet_data_with_cli_resources_and_rates, populate_spreadsheet_data_consolidated_session


def main() -> None:
    """Main entry point for the pricing tool accelerator."""
    print("🚀 DTT Pricing Tool Accelerator v1.0.0")
    print("   Automating pricing tool spreadsheet setup...")
    print("   Features: File Copy + Data Population + Resource Setup + Rate Card Calculation\n")
    
    # Validate system requirements
    if not validate_system_requirements():
        show_error_message(
            "System Requirements", 
            "macOS required for full functionality",
            "Finder integration may not work on other platforms"
        )
        return
    
    try:
        # Configuration
        source_dir = Path(__file__).parent.parent / "10-LATEST-PRICING-TOOLS"
        output_dir = Path(__file__).parent.parent / "20-OUTPUT"
        search_pattern = "Low Complexity"
        
        print(f"📁 Source directory: {source_dir}")
        print(f"📁 Output directory: {output_dir}")
        print(f"🔍 Searching for: {search_pattern}\n")
        
        # Step 1: Find source file and extract version
        print("🔍 Finding source template...")
        source_file, version = get_source_file_info(source_dir, search_pattern)
        print(f"✅ Found: {source_file.name}")
        print(f"✅ Version: {version}\n")
        
        # Step 2: Collect user inputs (Feature 003: Enhanced CLI collection)
        cli_data = collect_cli_fields()
        
        # Extract individual values for backward compatibility with filename generation
        client_name = cli_data.get("Client Name", "Unknown Client")
        gig_name = cli_data.get("Opportunity Name", "Unknown Opportunity")  # Updated terminology
        
        print(f"\n📝 Client: {client_name}")
        print(f"📝 Opportunity: {gig_name}")  # Updated display name
        
        # Step 2.5: Feature 006 - Collect client margin percentage
        margin_decimal = collect_margin_percentage()
        
        # Step 3: Generate output filename  
        current_date = get_current_date_string()
        base_filename = generate_output_filename(current_date, client_name, gig_name, version)
        base_output_path = output_dir / base_filename
        
        # Step 4: Handle filename collisions
        final_output_path = handle_filename_collision(base_output_path)
        
        if final_output_path != base_output_path:
            print(f"\n⚠️  File collision detected, using: {final_output_path.name}")
        
        print(f"\n📋 Final filename: {final_output_path.name}")
        
        # Step 5: Copy the file (no conversion needed)
        print("\n📄 Copying template...")
        copy_success = copy_file_with_rename(source_file, final_output_path)
        
        if not copy_success:
            show_error_message("Copy Failed", "Unable to copy template file")
            return
        
        # Step 6: FEATURE 005 - Enhanced data population (CLI + constants + Resource Setup)
        print("📋 Populating data from CLI inputs, constants, and Resource Setup...")
        
        # If .xlsb file, warn user about Excel launch
        if final_output_path.suffix.lower() == '.xlsb':
            print("⏳ Opening Excel in background to modify .xlsb file...")
            print("   (This may trigger permission dialogs - please allow access)")
        
        try:
            # Try consolidated Excel session approach first (single open/close)
            print("⚡ Using optimized single-session Excel workflow...")
            print("   (This eliminates multiple permission dialogs!)")
            
            population_summary = populate_spreadsheet_data_consolidated_session(
                final_output_path, 
                CONSTANTS_FILENAME,
                cli_data,  # Feature 003: Include CLI data
                margin_decimal,  # Feature 006: Include client margin
                CONSTANTS_DIR_NAME,
                FIELD_MATCH_THRESHOLD,
                RESOURCE_SETUP_ENABLED,  # Feature 005: Include Resource Setup
                True,  # Feature 006: Enable rate card calculation
                7  # Resource row count
            )
            show_population_feedback(population_summary)
            
        except Exception as e:
            print(f"📋 Skipping data population: {e}")
            print("📄 Spreadsheet copy successful, continuing with remaining steps...")
        
        # Step 7: Open in Finder
        print("🔍 Opening in Finder...")
        finder_success = open_file_in_finder(final_output_path)
        
        # Step 8: Show final success message
        print()
        show_success_message(final_output_path, finder_success)
        print(f"\n🎉 Task completed! Your pricing tool is ready to use.")
        
    except FileNotFoundError as e:
        show_error_message(
            "File Not Found", 
            str(e),
            "Verify source directory exists and contains the expected template"
        )
    
    except ValueError as e:
        show_error_message(
            "Invalid Data", 
            str(e),
            "Check filename format and version numbering"
        )
    
    except PermissionError as e:
        show_error_message(
            "Permission Error", 
            str(e),
            "Check file permissions and available disk space"
        )
    
    except Exception as e:
        show_error_message(
            "Unexpected Error", 
            str(e),
            "Please report this issue if it persists"
        )


if __name__ == "__main__":
    main()