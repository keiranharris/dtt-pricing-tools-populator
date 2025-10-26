#!/usr/bin/env python3
"""
Shell Alias CLI Interface - Command-line interface for shell alias management.

This module provides the command-line interface for setting up and managing
shell aliases for the DTT Pricing Tool.
"""

import sys
import argparse
from pathlib import Path
from typing import Optional
from .shell_alias_manager import ShellAliasManager, AliasSetupRequest
from .shell_detection import ShellDetector
from .path_resolution import PathResolver
from .shell_alias_constants import (
    DEFAULT_ALIAS_NAME,
    DEFAULT_TARGET_SCRIPT,
    INFO_MESSAGES,
    SUCCESS_MESSAGES,
    ERROR_MESSAGES
)


class ShellAliasCLI:
    """Command-line interface for shell alias management."""
    
    def __init__(self):
        """Initialize the CLI."""
        self.manager = ShellAliasManager()
    
    def create_parser(self) -> argparse.ArgumentParser:
        """Create and configure the argument parser."""
        parser = argparse.ArgumentParser(
            description="Set up shell aliases for DTT Pricing Tool",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  %(prog)s                          # Set up default 'priceup' alias
  %(prog)s --alias pricetool        # Set up custom alias name
  %(prog)s --force                  # Overwrite existing alias
  %(prog)s --script-path ./custom.py # Use custom script path
  %(prog)s --check                  # Check current shell environment
  %(prog)s --debug                  # Show detailed debug information
            """
        )
        
        # Main operation arguments
        parser.add_argument(
            '--alias', '-a',
            default=DEFAULT_ALIAS_NAME,
            help=f'Name of the alias to create (default: {DEFAULT_ALIAS_NAME})'
        )
        
        parser.add_argument(
            '--script-path', '-s',
            type=Path,
            help='Path to the target script (auto-detected if not provided)'
        )
        
        parser.add_argument(
            '--force', '-f',
            action='store_true',
            help='Overwrite existing alias if it exists'
        )
        
        # Information and debugging arguments
        parser.add_argument(
            '--check', '-c',
            action='store_true',
            help='Check shell environment and configuration'
        )
        
        parser.add_argument(
            '--debug', '-d',
            action='store_true',
            help='Show detailed debug information'
        )
        
        parser.add_argument(
            '--list-scripts', '-l',
            action='store_true',
            help='List all potential script locations'
        )
        
        parser.add_argument(
            '--quiet', '-q',
            action='store_true',
            help='Suppress informational messages'
        )
        
        return parser
    
    def run(self, args: Optional[list] = None) -> int:
        """
        Run the CLI with the provided arguments.
        
        Args:
            args: Command line arguments (uses sys.argv if None)
            
        Returns:
            Exit code (0 for success, 1 for error)
        """
        parser = self.create_parser()
        parsed_args = parser.parse_args(args)
        
        try:
            # Handle information commands first
            if parsed_args.check:
                return self._handle_check_command(parsed_args)
            
            if parsed_args.list_scripts:
                return self._handle_list_scripts_command(parsed_args)
            
            # Handle main alias setup command
            return self._handle_setup_command(parsed_args)
            
        except KeyboardInterrupt:
            if not parsed_args.quiet:
                print("\nOperation cancelled by user.", file=sys.stderr)
            return 1
        
        except Exception as e:
            if parsed_args.debug:
                import traceback
                traceback.print_exc()
            else:
                print(f"Error: {str(e)}", file=sys.stderr)
            return 1
    
    def _handle_setup_command(self, args: argparse.Namespace) -> int:
        """Handle the main alias setup command."""
        if not args.quiet:
            print(INFO_MESSAGES["checking_shell"])
        
        # Create setup request
        try:
            request = AliasSetupRequest(
                alias_name=args.alias,
                target_script_path=args.script_path,
                force_overwrite=args.force
            )
        except ValueError as e:
            print(f"Error: {str(e)}", file=sys.stderr)
            return 1
        
        if not args.quiet:
            print(INFO_MESSAGES["detecting_script"])
            if args.debug:
                print(f"Target script: {request.target_script_path}")
        
        # Perform setup
        result = self.manager.setup_alias(request)
        
        # Handle result
        if result.success:
            if not args.quiet:
                print(f"✅ {result.message}")
                
                if result.backup_created and result.config_file:
                    backup_path = result.config_file.with_suffix(result.config_file.suffix + ".backup")
                    print(f"📁 Backup created: {backup_path}")
                
                print(f"\n🚀 You can now use '{result.alias_name}' from anywhere!")
                print("   Run 'source ~/.zshrc' or restart your terminal to activate.")
            
            return 0
        
        else:
            # Handle specific error cases
            if result.already_exists and not args.force:
                print(f"⚠️  {result.message}", file=sys.stderr)
                print(f"   Use --force to overwrite the existing alias.", file=sys.stderr)
            else:
                print(f"❌ {result.message}", file=sys.stderr)
            
            return 1
    
    def _handle_check_command(self, args: argparse.Namespace) -> int:
        """Handle the shell environment check command."""
        print("🔍 Shell Environment Check")
        print("=" * 40)
        
        # Get shell information
        shell_info = ShellDetector.get_shell_info()
        
        print(f"Current Shell: {shell_info['shell_name']}")
        print(f"Supported: {shell_info['is_supported']}")
        print(f"SHELL Environment: {shell_info['shell_env']}")
        
        if 'config_file' in shell_info:
            print(f"Config File: {shell_info['config_file']}")
            print(f"Config Exists: {shell_info['config_exists']}")
            print(f"Config Accessible: {shell_info['config_accessible']}")
            
            if 'access_error' in shell_info:
                print(f"Access Error: {shell_info['access_error']}")
        
        # Check script resolution
        print("\n📂 Script Resolution")
        print("=" * 40)
        
        try:
            if args.script_path:
                script_path = args.script_path
                print(f"Using provided path: {script_path}")
            else:
                script_path = PathResolver.resolve_target_script_path()
                print(f"Auto-detected path: {script_path}")
            
            if script_path:
                is_valid, error_msg = PathResolver.validate_script_path(script_path)
                print(f"Script Valid: {is_valid}")
                if error_msg:
                    print(f"Validation Error: {error_msg}")
            else:
                print("Script Valid: False")
                print("Validation Error: Could not locate script")
                
        except Exception as e:
            print(f"Error during script resolution: {str(e)}")
        
        # Show debug information if requested
        if args.debug:
            self._show_debug_info()
        
        return 0
    
    def _handle_list_scripts_command(self, args: argparse.Namespace) -> int:
        """Handle the list scripts command."""
        print("📋 Potential Script Locations")
        print("=" * 40)
        
        try:
            scripts = PathResolver.find_all_potential_scripts()
            
            if scripts:
                for i, script_path in enumerate(scripts, 1):
                    print(f"{i}. {script_path}")
                    
                    # Validate each script
                    is_valid, error_msg = PathResolver.validate_script_path(script_path)
                    if is_valid:
                        print("   ✅ Valid")
                    else:
                        print(f"   ❌ {error_msg}")
                    print()
            else:
                print("No potential script locations found.")
                print("\nSearch locations checked:")
                from .shell_alias_constants import SCRIPT_SEARCH_PATHS
                for path in SCRIPT_SEARCH_PATHS:
                    print(f"  - {path}")
        
        except Exception as e:
            print(f"Error listing scripts: {str(e)}", file=sys.stderr)
            return 1
        
        return 0
    
    def _show_debug_info(self):
        """Show detailed debug information."""
        print("\n🐛 Debug Information")
        print("=" * 40)
        
        # Shell environment details
        import os
        print("Environment Variables:")
        env_vars = ['SHELL', 'ZSH_VERSION', 'BASH_VERSION', 'TERM', 'HOME']
        for var in env_vars:
            value = os.environ.get(var, 'not set')
            print(f"  {var}: {value}")
        
        print(f"\nCurrent Working Directory: {Path.cwd()}")
        
        # Repository information
        repo_root = PathResolver._find_repository_root(Path.cwd())
        print(f"Repository Root: {repo_root}")
        
        # File system information
        home_dir = Path.home()
        zshrc_path = home_dir / ".zshrc"
        
        print("\nFile System:")
        print(f"  Home Directory: {home_dir}")
        print(f"  .zshrc exists: {zshrc_path.exists()}")
        
        if zshrc_path.exists():
            try:
                stat = zshrc_path.stat()
                print(f"  .zshrc size: {stat.st_size} bytes")
                print(f"  .zshrc readable: {os.access(zshrc_path, os.R_OK)}")
                print(f"  .zshrc writable: {os.access(zshrc_path, os.W_OK)}")
            except Exception as e:
                print(f"  .zshrc stat error: {e}")


def main():
    """Main entry point for the CLI."""
    cli = ShellAliasCLI()
    exit_code = cli.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()