#!/usr/bin/env python3
"""
OneDrive Path Configuration Module

Handles dynamic OneDrive path detection, configuration, and validation
for the DTT Pricing Tools Populator.

This module eliminates hardcoded OneDrive paths by providing:
- Interactive setup wizard for first-time configuration
- Persistent configuration storage in user home directory  
- Path validation and error recovery
- Integration with existing codebase modules

Author: DTT Pricing Tools Team
Created: 2025-10-28
Feature: 009-dynamic-onedrive-path
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, Any, List
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Module version for configuration compatibility
__version__ = "1.0.0"


class ValidationStatus(Enum):
    """Configuration validation status enumeration."""
    UNCONFIGURED = "unconfigured"
    VALID = "valid" 
    INVALID = "invalid"
    INACCESSIBLE = "inaccessible"
    MISSING_SUBDIRS = "missing_subdirectories"


class ConfigurationError(Exception):
    """Base exception for configuration-related errors."""
    pass


class SetupCancelledError(ConfigurationError):
    """Raised when user cancels the setup wizard."""
    pass


class SetupError(ConfigurationError):
    """Raised when setup wizard encounters an error."""
    pass


# Configuration file schema constants
CONFIG_FILE_NAME = ".dtt-pricing-tool-populator-config"
CONFIG_SCHEMA_VERSION = "1.0"
REQUIRED_SUBDIRECTORIES = [
    "00-CONSTANTS",
    "10-LATEST-PRICING-TOOLS", 
    "20-OUTPUT"
]

# Default configuration file location
DEFAULT_CONFIG_PATH = Path.home() / CONFIG_FILE_NAME


@dataclass
class ValidationResult:
    """Result of path configuration validation."""
    is_valid: bool
    status: ValidationStatus
    error_message: str = ""
    missing_directories: Optional[List[str]] = None
    inaccessible_paths: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.missing_directories is None:
            self.missing_directories = []
        if self.inaccessible_paths is None:
            self.inaccessible_paths = []


@dataclass
class DirectoryPaths:
    """Container for all required OneDrive directory paths."""
    base_path: Path
    constants_directory: Path
    source_directory: Path
    output_directory: Path
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary with string paths."""
        return {
            "base_path": str(self.base_path),
            "constants_directory": str(self.constants_directory),
            "source_directory": str(self.source_directory),
            "output_directory": str(self.output_directory)
        }
    
    @classmethod
    def from_base_path(cls, base_path: Path) -> 'DirectoryPaths':
        """Create DirectoryPaths from base OneDrive path."""
        return cls(
            base_path=base_path,
            constants_directory=base_path / "00-CONSTANTS",
            source_directory=base_path / "10-LATEST-PRICING-TOOLS", 
            output_directory=base_path / "20-OUTPUT"
        )


@dataclass
class PathConfiguration:
    """OneDrive path configuration with validation."""
    version: str
    onedrive_base_path: Path
    constants_directory: Path
    source_directory: Path
    output_directory: Path
    last_validated: datetime
    validation_status: ValidationStatus = ValidationStatus.UNCONFIGURED
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        # Convert string paths to Path objects if needed
        if isinstance(self.onedrive_base_path, str):
            self.onedrive_base_path = Path(self.onedrive_base_path)
        if isinstance(self.constants_directory, str):
            self.constants_directory = Path(self.constants_directory)
        if isinstance(self.source_directory, str):
            self.source_directory = Path(self.source_directory)
        if isinstance(self.output_directory, str):
            self.output_directory = Path(self.output_directory)
        if isinstance(self.last_validated, str):
            self.last_validated = datetime.fromisoformat(self.last_validated)
    
    @classmethod
    def create_new(cls, base_path: Path) -> 'PathConfiguration':
        """Create new configuration from OneDrive base path."""
        directory_paths = DirectoryPaths.from_base_path(base_path)
        return cls(
            version=CONFIG_SCHEMA_VERSION,
            onedrive_base_path=directory_paths.base_path,
            constants_directory=directory_paths.constants_directory,
            source_directory=directory_paths.source_directory,
            output_directory=directory_paths.output_directory,
            last_validated=datetime.now(),
            validation_status=ValidationStatus.UNCONFIGURED
        )
    
    def get_directory_paths(self) -> DirectoryPaths:
        """Get DirectoryPaths object for this configuration."""
        return DirectoryPaths(
            base_path=self.onedrive_base_path,
            constants_directory=self.constants_directory,
            source_directory=self.source_directory,
            output_directory=self.output_directory
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "version": self.version,
            "onedrive_base_path": str(self.onedrive_base_path),
            "constants_directory": str(self.constants_directory),
            "source_directory": str(self.source_directory),
            "output_directory": str(self.output_directory),
            "last_validated": self.last_validated.isoformat(),
            "validation_status": self.validation_status.value
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PathConfiguration':
        """Create configuration from dictionary (JSON deserialization)."""
        return cls(
            version=data["version"],
            onedrive_base_path=Path(data["onedrive_base_path"]),
            constants_directory=Path(data["constants_directory"]),
            source_directory=Path(data["source_directory"]),
            output_directory=Path(data["output_directory"]),
            last_validated=datetime.fromisoformat(data["last_validated"]),
            validation_status=ValidationStatus(data["validation_status"])
        )


class ConfigurationFileManager:
    """Handles configuration file I/O operations."""
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize with optional custom configuration path."""
        self.config_path = config_path or DEFAULT_CONFIG_PATH
    
    def save_configuration(self, config: PathConfiguration) -> None:
        """Save configuration to JSON file."""
        try:
            # Ensure parent directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Saving configuration to {self.config_path}")
            
            # Write configuration to JSON
            with open(self.config_path, 'w', encoding='utf-8') as file:
                json.dump(config.to_dict(), file, indent=2, ensure_ascii=False)
                
            logger.info(f"Configuration saved successfully: {config.onedrive_base_path}")
            
        except (OSError, IOError) as e:
            logger.error(f"I/O error saving configuration: {e}")
            raise ConfigurationError(f"Failed to save configuration: {e}")
        except Exception as e:
            logger.error(f"Unexpected error saving configuration: {e}")
            raise ConfigurationError(f"Unexpected error saving configuration: {e}")
    
    def load_configuration(self) -> Optional[PathConfiguration]:
        """Load configuration from JSON file."""
        try:
            if not self.config_path.exists():
                logger.debug(f"Configuration file not found: {self.config_path}")
                return None
            
            with open(self.config_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            # Validate schema version
            if data.get("version") != CONFIG_SCHEMA_VERSION:
                logger.warning(f"Configuration version mismatch: {data.get('version')} vs {CONFIG_SCHEMA_VERSION}")
                # For now, attempt to load anyway - future versions might need migration
            
            config = PathConfiguration.from_dict(data)
            logger.info(f"Configuration loaded successfully: {config.onedrive_base_path}")
            return config
            
        except (OSError, IOError) as e:
            logger.error(f"I/O error reading configuration: {e}")
            raise ConfigurationError(f"Failed to read configuration file: {e}")
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(f"Configuration file format error: {e}")
            raise ConfigurationError(f"Invalid configuration file format: {e}")
        except Exception as e:
            logger.error(f"Unexpected error loading configuration: {e}")
            raise ConfigurationError(f"Unexpected error loading configuration: {e}")
    
    def configuration_exists(self) -> bool:
        """Check if configuration file exists."""
        return self.config_path.exists()
    
    def delete_configuration(self) -> None:
        """Delete configuration file."""
        try:
            if self.config_path.exists():
                self.config_path.unlink()
                logger.info(f"Configuration file deleted: {self.config_path}")
        except (OSError, IOError) as e:
            raise ConfigurationError(f"Failed to delete configuration: {e}")


class ConfigurationManager:
    """High-level configuration management operations."""
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize configuration manager."""
        self.file_manager = ConfigurationFileManager(config_path)
        self.current_config: Optional[PathConfiguration] = None
    
    def load_configuration(self) -> Optional[PathConfiguration]:
        """Load existing path configuration from user's home directory."""
        try:
            self.current_config = self.file_manager.load_configuration()
            return self.current_config
        except ConfigurationError:
            # Log error but don't raise - caller handles None return
            logger.exception("Failed to load configuration")
            return None
    
    def save_configuration(self, config: PathConfiguration) -> None:
        """Persist path configuration to user's home directory."""
        self.file_manager.save_configuration(config)
        self.current_config = config
    
    def validate_configuration(self, config: PathConfiguration) -> ValidationResult:
        """Check if configured paths are currently accessible."""
        missing_dirs = []
        inaccessible_paths = []
        
        # Check base path accessibility
        if not config.onedrive_base_path.exists():
            return ValidationResult(
                is_valid=False,
                status=ValidationStatus.INACCESSIBLE,
                error_message=f"OneDrive base path not accessible: {config.onedrive_base_path}",
                inaccessible_paths=[str(config.onedrive_base_path)]
            )
        
        if not os.access(config.onedrive_base_path, os.R_OK):
            return ValidationResult(
                is_valid=False,
                status=ValidationStatus.INACCESSIBLE,
                error_message=f"OneDrive base path not readable: {config.onedrive_base_path}",
                inaccessible_paths=[str(config.onedrive_base_path)]
            )
        
        # Check required subdirectories
        required_paths = [
            config.constants_directory,
            config.source_directory,
            config.output_directory
        ]
        
        for path in required_paths:
            if not path.exists():
                missing_dirs.append(str(path))
            elif not os.access(path, os.R_OK | os.W_OK):
                inaccessible_paths.append(str(path))
        
        # Determine validation result
        if missing_dirs:
            return ValidationResult(
                is_valid=False,
                status=ValidationStatus.MISSING_SUBDIRS,
                error_message=f"Required directories missing: {', '.join(missing_dirs)}",
                missing_directories=missing_dirs
            )
        
        if inaccessible_paths:
            return ValidationResult(
                is_valid=False,
                status=ValidationStatus.INACCESSIBLE,
                error_message=f"Directories not accessible: {', '.join(inaccessible_paths)}",
                inaccessible_paths=inaccessible_paths
            )
        
        # All validation passed
        # Update config validation timestamp
        config.validation_status = ValidationStatus.VALID
        config.last_validated = datetime.now()
        
        return ValidationResult(
            is_valid=True,
            status=ValidationStatus.VALID,
            error_message="Configuration is valid"
        )
    
    def get_configured_paths(self) -> DirectoryPaths:
        """Get current directory paths for application use."""
        if self.current_config is None:
            self.current_config = self.load_configuration()
        
        if self.current_config is None:
            raise ConfigurationError("No valid configuration exists. Please run setup wizard.")
        
        # Validate current configuration
        validation_result = self.validate_configuration(self.current_config)
        if not validation_result.is_valid:
            raise ConfigurationError(f"Configuration validation failed: {validation_result.error_message}")
        
        return self.current_config.get_directory_paths()


class SetupWizard:
    """Interactive setup wizard for OneDrive path configuration."""
    
    def __init__(self, config_manager: Optional[ConfigurationManager] = None):
        """Initialize setup wizard."""
        self.config_manager = config_manager or ConfigurationManager()
    
    def start_setup(self) -> PathConfiguration:
        """Begin interactive setup process for OneDrive path configuration."""
        print("\n" + "="*60)
        print("DTT Pricing Tools - OneDrive Path Configuration Setup")
        print("="*60)
        print()
        print("This setup wizard will help you configure the OneDrive paths")
        print("for the DTT Pricing Tools Populator.")
        print()
        print("You need to provide the path to your 'PricingToolAccel' folder")
        print("which should contain these subdirectories:")
        for subdir in REQUIRED_SUBDIRECTORIES:
            print(f"  - {subdir}")
        print()
        print("💡 Tips:")
        print("   • Spaces in folder names are allowed")
        print("   • You can use quotes around the path if you prefer: '/path with spaces/'")
        print("   • Both single quotes 'path' and double quotes \"path\" are supported")
        print()
        
        max_attempts = 3
        attempt = 0
        
        while attempt < max_attempts:
            attempt += 1
            
            # Get user input
            if attempt == 1:
                prompt = "Please enter the full path to your PricingToolAccel folder (spaces allowed): "
            else:
                print(f"\nAttempt {attempt} of {max_attempts}")
                prompt = "Please try again. Enter the full path to your PricingToolAccel folder (spaces allowed): "
            
            try:
                user_input = input(prompt).strip()
                
                # Strip quotation marks if present (both single and double quotes)
                if len(user_input) >= 2:
                    if (user_input.startswith('"') and user_input.endswith('"')) or \
                       (user_input.startswith("'") and user_input.endswith("'")):
                        user_input = user_input[1:-1].strip()
                        print(f"   📝 Cleaned path: {user_input}")
                
                if not user_input:
                    print("❌ Error: Path cannot be empty.")
                    continue
                
                # Handle user cancellation
                if user_input.lower() in ['quit', 'exit', 'cancel', 'q']:
                    raise SetupCancelledError("Setup cancelled by user")
                
                # Validate the path
                validation_result = self.validate_user_path(user_input)
                
                if validation_result.is_valid:
                    # Create and save configuration
                    base_path = Path(user_input)
                    config = PathConfiguration.create_new(base_path)
                    
                    # Run full validation
                    final_validation = self.config_manager.validate_configuration(config)
                    if final_validation.is_valid:
                        self.config_manager.save_configuration(config)
                        
                        print("\n✅ Configuration successful!")
                        print(f"   Base path: {config.onedrive_base_path}")
                        print(f"   Configuration saved to: {self.config_manager.file_manager.config_path}")
                        print()
                        
                        return config
                    else:
                        print(f"❌ Final validation failed: {final_validation.error_message}")
                        continue
                else:
                    print(f"❌ {validation_result.error_message}")
                    if validation_result.missing_directories:
                        print("   Missing directories:")
                        for missing_dir in validation_result.missing_directories:
                            print(f"     - {missing_dir}")
                    continue
                    
            except KeyboardInterrupt:
                raise SetupCancelledError("Setup cancelled by user (Ctrl+C)")
            except EOFError:
                raise SetupCancelledError("Setup cancelled by user (EOF)")
        
        raise SetupError(f"Setup failed after {max_attempts} attempts")
    
    def validate_user_path(self, path_str: str) -> ValidationResult:
        """Validate user-provided OneDrive base path."""
        try:
            # Convert to Path object and resolve
            path = Path(path_str).expanduser().resolve()
            
            # Check if base path exists and is accessible
            if not path.exists():
                return ValidationResult(
                    is_valid=False,
                    status=ValidationStatus.INACCESSIBLE,
                    error_message=f"Path does not exist: {path}"
                )
            
            if not path.is_dir():
                return ValidationResult(
                    is_valid=False,
                    status=ValidationStatus.INACCESSIBLE,
                    error_message=f"Path is not a directory: {path}"
                )
            
            if not os.access(path, os.R_OK):
                return ValidationResult(
                    is_valid=False,
                    status=ValidationStatus.INACCESSIBLE,
                    error_message=f"Directory is not readable: {path}"
                )
            
            # Check for required subdirectories
            missing_dirs = []
            for subdir_name in REQUIRED_SUBDIRECTORIES:
                subdir_path = path / subdir_name
                if not subdir_path.exists():
                    missing_dirs.append(subdir_name)
                elif not subdir_path.is_dir():
                    missing_dirs.append(f"{subdir_name} (not a directory)")
            
            if missing_dirs:
                return ValidationResult(
                    is_valid=False,
                    status=ValidationStatus.MISSING_SUBDIRS,
                    error_message="Required subdirectories are missing or invalid",
                    missing_directories=missing_dirs
                )
            
            # All validation passed
            return ValidationResult(
                is_valid=True,
                status=ValidationStatus.VALID,
                error_message="Path validation successful"
            )
            
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                status=ValidationStatus.INACCESSIBLE,
                error_message=f"Error validating path: {e}"
            )


def check_onedrive_sync_status(path: Path) -> Dict[str, Any]:
    """
    Check OneDrive sync status and provide guidance.
    
    Returns:
        Dict containing sync status information and guidance messages
    """
    sync_info = {
        "is_syncing": False,
        "sync_issues": [],
        "guidance_messages": []
    }
    
    try:
        # Check for OneDrive sync indicators
        path_str = str(path).lower()
        
        # Common OneDrive sync issue patterns
        if "onedrive" not in path_str:
            sync_info["guidance_messages"].append(
                "💡 This path doesn't appear to be in OneDrive. Make sure you're pointing to your OneDrive folder."
            )
        
        # Check for OneDrive sync status files (Windows/Mac specific)
        onedrive_indicators = [
            ".tmp",      # Temporary sync files
            "~$",        # Excel lock files from OneDrive
            ".onedrive"  # OneDrive metadata
        ]
        
        if path.exists():
            # Look for sync conflict files
            conflict_files = list(path.glob("*-conflict-*"))
            if conflict_files:
                sync_info["sync_issues"].append("Sync conflict files detected")
                sync_info["guidance_messages"].append(
                    "⚠️ OneDrive sync conflicts detected. Resolve conflicts in OneDrive before proceeding."
                )
            
            # Check for OneDrive lock files
            lock_files = list(path.glob("~$*"))
            if lock_files:
                sync_info["sync_issues"].append("OneDrive lock files present")
                sync_info["guidance_messages"].append(
                    "⚠️ Files may be open in Excel via OneDrive. Close Excel files and wait for sync to complete."
                )
            
            # Check if folder is accessible but empty (potential sync issue)
            try:
                contents = list(path.iterdir())
                if not contents:
                    sync_info["guidance_messages"].append(
                        "💡 Folder appears empty. If you expect files here, check OneDrive sync status."
                    )
            except PermissionError:
                sync_info["sync_issues"].append("Permission denied")
                sync_info["guidance_messages"].append(
                    "⚠️ Permission denied. Check OneDrive sync permissions and folder access rights."
                )
        
        # General OneDrive guidance
        if sync_info["sync_issues"]:
            sync_info["guidance_messages"].append(
                "🔄 OneDrive Troubleshooting Tips:"
            )
            sync_info["guidance_messages"].append(
                "   • Check OneDrive sync status in system tray/menu bar"
            )
            sync_info["guidance_messages"].append(
                "   • Ensure you have internet connection for OneDrive sync"
            )
            sync_info["guidance_messages"].append(
                "   • Try pausing and resuming OneDrive sync"
            )
            sync_info["guidance_messages"].append(
                "   • Restart OneDrive application if sync is stuck"
            )
        
    except Exception as e:
        sync_info["sync_issues"].append(f"Error checking sync status: {e}")
        sync_info["guidance_messages"].append(
            "💡 Unable to check OneDrive sync status. Ensure path is accessible."
        )
    
    return sync_info