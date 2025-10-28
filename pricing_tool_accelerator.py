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
# CONSTANTS_DIR_NAME removed - now using CONSTANTS_DIRECTORY from src.constants

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
# FEATURE 007: CLI OUTPUT CONFIGURATION
# ============================================================================
# Controls production vs verbose CLI output mode

VERBOSE_LOGGING_ENABLED = False                       # Production mode by default

# ============================================================================

from src.cli_interface import collect_user_inputs, collect_cli_fields, collect_margin_percentage
from src.file_operations import get_source_file_info, copy_file_with_rename
from src.naming_utils import generate_output_filename, get_current_date_string, get_current_username, handle_filename_collision
from src.system_integration import (
    open_file_in_finder, 
    show_success_message, 
    show_error_message, 
    validate_system_requirements
)

# Import SpecKit data models
from src.data_models import UserInput, SourceFile, OutputFile, OperationError

# Feature 002: Data Population imports (backward compatible)
from src.data_population_orchestrator import populate_spreadsheet_data, show_population_feedback
# Feature 003: Enhanced CLI Population imports
from src.data_population_orchestrator import populate_spreadsheet_data_with_cli
# Feature 005: Resource Setup Population imports
from src.data_population_orchestrator import populate_spreadsheet_data_with_cli_and_resources
# Feature 006: Rate Card Population imports
from src.data_population_orchestrator import populate_spreadsheet_data_with_cli_resources_and_rates, populate_spreadsheet_data_consolidated_session


def setup_shell_alias_if_needed() -> bool:
    """
    Set up shell alias for easy access if needed.
    
    This function attempts to set up a shell alias ('priceup') that allows
    users to run this tool from anywhere. It operates silently and never
    raises exceptions that would interrupt the main application.
    
    Returns:
        bool: True to continue main app execution (always returns True)
    """
    try:
        # Only attempt if we're in an interactive shell environment
        import os
        if not os.environ.get('SHELL'):
            return True  # Not in a shell, skip silently
        
        # Import shell alias functionality
        from src.shell_alias_manager import ShellAliasManager, AliasSetupRequest
        from src.shell_alias_constants import DEFAULT_ALIAS_NAME
        
        # Create manager and setup request
        manager = ShellAliasManager()
        request = AliasSetupRequest(alias_name=DEFAULT_ALIAS_NAME)
        
        # Attempt alias setup
        result = manager.setup_alias(request)
        
        # Handle results with appropriate messaging
        if result.success:
            print(f"✅ Shell alias '{result.alias_name}' set up successfully!")
            print("   You can now run 'priceup' from anywhere to access this tool.")
            print("   Restart your terminal or run 'source ~/.zshrc' to activate.\n")
        elif result.already_exists:
            # Alias exists - silent operation (no message needed)
            pass
        else:
            # Setup failed - show manual instructions in verbose mode only
            if VERBOSE_LOGGING_ENABLED:
                print(f"⚠️  Could not auto-setup shell alias: {result.message}")
                print("   You can manually add this alias to your ~/.zshrc:")
                print(f"   alias {request.alias_name}='python3 {request.target_script_path}'")
                print("   Then run 'source ~/.zshrc' to activate.\n")
        
        return True
        
    except Exception as e:
        # Never let alias setup interrupt the main application
        if VERBOSE_LOGGING_ENABLED:
            print(f"⚠️  Shell alias setup failed: {str(e)}")
            print("   Continuing with main application...\n")
        return True


def setup_onedrive_paths_if_needed(force_reconfigure: bool = False) -> bool:
    """
    Set up OneDrive path configuration if needed.
    
    This function checks if OneDrive paths are configured and runs the
    setup wizard if not. It handles first-time setup gracefully and
    provides helpful error messages for configuration issues.
    
    Returns:
        bool: True to continue main app execution
        
    Raises:
        SystemExit: If configuration setup fails or is cancelled
    """
    try:
        from src.path_configuration import ConfigurationManager, SetupWizard, ConfigurationError, SetupCancelledError, SetupError
        
        # Initialize configuration manager
        config_manager = ConfigurationManager()
        
        # Try to load existing configuration
        config = config_manager.load_configuration()
        
        if config is None or force_reconfigure:
            # No configuration exists or forced reconfiguration - run setup wizard
            if force_reconfigure and config is not None:
                print("🔧 OneDrive Path Reconfiguration")
                print("   Reconfiguring OneDrive folder paths as requested.\n")
            else:
                print("🔧 OneDrive Path Configuration Setup Required")
                print("   This appears to be your first time running the tool.")
                print("   We need to configure your OneDrive folder paths.\n")
            
            try:
                setup_wizard = SetupWizard(config_manager)
                config = setup_wizard.start_setup()
                print("✅ OneDrive paths configured successfully!\n")
                return True
                
            except SetupCancelledError:
                print("\n❌ Setup cancelled by user. Cannot proceed without OneDrive configuration.")
                print("   Run the tool again when ready to configure paths.")
                sys.exit(1)
                
            except SetupError as e:
                print(f"\n❌ Setup failed: {e}")
                print("   Please check your OneDrive folder structure and try again.")
                sys.exit(1)
        
        else:
            # Configuration exists - validate it
            validation_result = config_manager.validate_configuration(config)
            
            if validation_result.is_valid:
                # Configuration is valid - continue silently
                return True
            else:
                # Configuration is invalid - offer reconfiguration
                print(f"⚠️  OneDrive Path Validation Failed: {validation_result.error_message}")
                
                if validation_result.missing_directories:
                    print("   Missing directories:")
                    for missing_dir in validation_result.missing_directories:
                        print(f"     - {missing_dir}")
                
                if validation_result.inaccessible_paths:
                    print("   Inaccessible paths:")
                    for inaccessible_path in validation_result.inaccessible_paths:
                        print(f"     - {inaccessible_path}")
                
                # Check OneDrive sync status and provide guidance
                from src.path_configuration import check_onedrive_sync_status
                sync_info = check_onedrive_sync_status(config.onedrive_base_path)
                
                if sync_info["guidance_messages"]:
                    print("\n" + "\n".join(sync_info["guidance_messages"]))
                
                print("\nWould you like to reconfigure your OneDrive paths now? (y/n): ", end="")
                response = input().strip().lower()
                
                if response in ['y', 'yes', '1', 'true']:
                    try:
                        setup_wizard = SetupWizard(config_manager)
                        config = setup_wizard.start_setup()
                        print("✅ OneDrive paths reconfigured successfully!\n")
                        return True
                        
                    except (SetupCancelledError, SetupError) as e:
                        print(f"\n❌ Reconfiguration failed: {e}")
                        print("   Cannot proceed without valid OneDrive configuration.")
                        sys.exit(1)
                else:
                    print("❌ Cannot proceed without valid OneDrive configuration.")
                    print("   Please fix the OneDrive paths and run the tool again.")
                    sys.exit(1)
        
    except ConfigurationError as e:
        print(f"❌ OneDrive Configuration Error: {e}")
        print("   Please check your OneDrive setup and try again.")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Unexpected error during OneDrive setup: {e}")
        print("   Please report this issue if it persists.")
        sys.exit(1)


def show_configuration() -> None:
    """Display current OneDrive path configuration."""
    try:
        from src.path_configuration import ConfigurationManager, ConfigurationError
        
        print("🔧 DTT Pricing Tool - OneDrive Path Configuration")
        print("=" * 50)
        
        config_manager = ConfigurationManager()
        config = config_manager.load_configuration()
        
        if config is None:
            print("❌ No configuration found.")
            print("   Run the tool without arguments to set up OneDrive paths.")
            return
        
        print(f"📅 Configuration Version: {config.version}")
        print(f"🕒 Last Validated: {config.last_validated.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📊 Status: {config.validation_status.value}")
        print()
        print("📁 Configured Paths:")
        print(f"   Base Path: {config.onedrive_base_path}")
        print(f"   Constants: {config.constants_directory}")
        print(f"   Source:    {config.source_directory}")
        print(f"   Output:    {config.output_directory}")
        print()
        
        # Validate current configuration
        validation_result = config_manager.validate_configuration(config)
        
        if validation_result.is_valid:
            print("✅ Configuration is valid and accessible")
        else:
            print(f"❌ Configuration validation failed: {validation_result.error_message}")
            
            if validation_result.missing_directories:
                print("   Missing directories:")
                for missing_dir in validation_result.missing_directories:
                    print(f"     - {missing_dir}")
            
            if validation_result.inaccessible_paths:
                print("   Inaccessible paths:")
                for inaccessible_path in validation_result.inaccessible_paths:
                    print(f"     - {inaccessible_path}")
            
            print("\n💡 Run with --configure-paths to reconfigure")
        
        print(f"\n📄 Configuration file: {config_manager.file_manager.config_path}")
        
    except ConfigurationError as e:
        print(f"❌ Configuration Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


def main() -> None:
    """Main entry point for the pricing tool accelerator."""
    
    # Check for command line arguments
    import argparse
    
    parser = argparse.ArgumentParser(
        description="DTT Pricing Tool Accelerator - Automate pricing tool spreadsheet setup",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--configure-paths", 
        action="store_true", 
        help="Force reconfiguration of OneDrive paths"
    )
    parser.add_argument(
        "--show-config", 
        action="store_true", 
        help="Display current OneDrive path configuration and exit"
    )
    
    args = parser.parse_args()
    
    # Handle --show-config option
    if args.show_config:
        show_configuration()
        return
    
    # Feature 007: Initialize production logging system
    from src.system_integration import setup_production_logging
    setup_production_logging(verbose_enabled=VERBOSE_LOGGING_ENABLED)
    
    # Feature 008: Shell alias auto-setup for easy access
    setup_shell_alias_if_needed()
    
    # Feature 009: OneDrive path configuration setup
    setup_onedrive_paths_if_needed(force_reconfigure=args.configure_paths)
    
    # Initialize path constants after OneDrive setup
    from src.constants import initialize_paths
    initialize_paths()
    
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
        from src.constants import OUTPUT_DIRECTORY, PRICING_TOOL_SOURCE_DIRECTORY
        source_dir = Path(PRICING_TOOL_SOURCE_DIRECTORY).expanduser()  # Use centralized constant
        output_dir = Path(OUTPUT_DIRECTORY).expanduser()  # expanduser() handles ~ properly
        search_pattern = "Low Complexity"
        
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"📁 Source directory: {source_dir}")
        print(f"📁 Output directory: {output_dir}")
        print(f"🔍 Searching for: {search_pattern}\n")
        
        # Step 1: Find source file and extract version (using centralized constants)
        print("🔍 Finding source template...")
        source_file, version = get_source_file_info()  # Use defaults from centralized constants
        print(f"✅ Found: {source_file.name}")
        print(f"✅ Version: {version}\n")
        
        # Step 2: Collect user inputs (Feature 003: Enhanced CLI collection)
        cli_result = collect_cli_fields()
        
        # Step 2.5: Feature 006 - Collect client margin percentage
        margin_decimal = collect_margin_percentage()
        
        # Extract individual values for backward compatibility with filename generation  
        client_name = cli_result.fields["Client Name"].sanitized_value
        gig_name = cli_result.fields["Opportunity Name"].sanitized_value
        
        # Step 3: Generate output filename  
        current_date = get_current_date_string()
        current_username = get_current_username()
        base_filename = generate_output_filename(current_date, client_name, gig_name, current_username, version)
        base_output_path = output_dir / base_filename
        
        # Step 4: Handle filename collisions
        final_output_path = handle_filename_collision(base_output_path)
        
        if final_output_path != base_output_path:
            print(f"\n⚠️  File collision detected, using: {final_output_path.name}")
        
        print(f"\n📋 Final filename: {final_output_path.name}")
        
        # Step 5: Copy the file to /tmp directory for processing (avoids OneDrive sync issues)
        print("\n📄 Copying template to temporary workspace...")
        
        # Create temp path in /tmp directory - much faster and no sync conflicts
        import tempfile
        temp_dir = Path(tempfile.gettempdir())
        temp_output_path = temp_dir / final_output_path.name
        copy_success = copy_file_with_rename(source_file, temp_output_path)
        
        if not copy_success:
            show_error_message("Copy Failed", "Unable to copy template file to temporary workspace")
            return
        
        # Step 6: FEATURE 005 - Enhanced data population (CLI + constants + Resource Setup)
        print("📋 Populating data from CLI inputs, constants, and Resource Setup...")
        
        # If .xlsb file, warn user about Excel launch
        if temp_output_path.suffix.lower() == '.xlsb':
            print("⏳ Opening Excel in background to modify .xlsb file...")
            print("   (This may trigger permission dialogs - please allow access)")
        
        try:
            # Use centralized constants directory path
            from src.constants import get_constants_directory
            absolute_constants_dir = Path(get_constants_directory()).expanduser()
            
            # Try consolidated Excel session approach first with automatic fallback
            population_summary = populate_spreadsheet_data_consolidated_session(
                temp_output_path,  # Work on temporary file
                CONSTANTS_FILENAME,
                cli_result.as_dict,  # Feature 003: Include CLI data (backward compatibility)
                margin_decimal,  # Feature 006: Include client margin
                str(absolute_constants_dir),  # Pass absolute path from centralized constant
                FIELD_MATCH_THRESHOLD,
                RESOURCE_SETUP_ENABLED,  # Feature 005: Include Resource Setup
                True,  # Feature 006: Enable rate card calculation
                7  # Resource row count
            )
            show_population_feedback(population_summary)
            
            # Step 6.5: Move completed file from /tmp to OneDrive (Excel is closed, safe to move)
            print("📝 Moving completed file to OneDrive...")
            try:
                # Ensure OneDrive directory exists
                final_output_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Move file from /tmp to OneDrive (atomic operation)
                import shutil
                shutil.move(str(temp_output_path), str(final_output_path))
                print(f"✅ File moved to OneDrive: {final_output_path.name}")
                
                # Step 6.6: Open the final file in Excel for user access
                print("📊 Opening completed file in Excel...")
                try:
                    import xlwings as xw
                    app = xw.App(visible=True, add_book=False)
                    workbook = app.books.open(final_output_path)
                    print("✅ Excel opened with populated data")
                except Exception as e:
                    print(f"⚠️  File ready but could not auto-open in Excel: {e}")
                    
            except Exception as e:
                print(f"⚠️  Warning: Could not move to OneDrive location: {e}")
                print(f"   File is available in temp directory: {temp_output_path}")
                # Don't update final_output_path - let user know where to find it
            
        except Exception as e:
            print(f"📋 Skipping data population: {e}")
            print("📄 Spreadsheet copy successful, continuing with remaining steps...")
            
            # If population failed, still try to move the file to OneDrive
            try:
                final_output_path.parent.mkdir(parents=True, exist_ok=True)
                import shutil
                shutil.move(str(temp_output_path), str(final_output_path))
                print(f"✅ Template file moved to OneDrive: {final_output_path.name}")
            except Exception as move_error:
                print(f"⚠️  Could not move to OneDrive: {move_error}")
                final_output_path = temp_output_path  # Use temp path for Finder
        
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