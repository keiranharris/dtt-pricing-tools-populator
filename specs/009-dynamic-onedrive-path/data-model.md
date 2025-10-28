# Data Model: Dynamic OneDrive Path Configuration

**Created**: 2025-10-28  
**Purpose**: Define data structures and relationships for OneDrive path management

## Core Entities

### PathConfiguration

Represents the user's OneDrive path configuration stored in local file system.

**Attributes:**
- `version: str` - Configuration schema version for future compatibility
- `onedrive_base_path: Path` - User-provided path to PricingToolAccel folder
- `constants_directory: Path` - Derived path to 00-CONSTANTS subfolder
- `source_directory: Path` - Derived path to 10-LATEST-PRICING-TOOLS subfolder  
- `output_directory: Path` - Derived path to 20-OUTPUT subfolder
- `last_validated: datetime` - Timestamp of last successful path validation
- `validation_status: ValidationStatus` - Current accessibility status

**Relationships:**
- Has one-to-many derived paths from base path
- Persisted to local configuration file
- Used by ConfigurationManager for path operations

**Validation Rules:**
- `onedrive_base_path` must exist and be accessible
- Required subdirectories (00-CONSTANTS, 10-LATEST-PRICING-TOOLS, 20-OUTPUT) must exist within base path
- `version` must match supported schema versions
- `last_validated` updated on successful validation

**State Transitions:**
- `UNCONFIGURED` → `VALID` (successful first-time setup)
- `VALID` → `INVALID` (path becomes inaccessible)
- `INVALID` → `VALID` (successful reconfiguration)
- `VALID` → `VALID` (successful revalidation)

### ConfigurationManager

Handles configuration file operations and path validation logic.

**Attributes:**
- `config_file_path: Path` - Location of configuration file in user home directory
- `current_config: Optional[PathConfiguration]` - Loaded configuration instance

**Methods:**
- `load_configuration() -> Optional[PathConfiguration]` - Load from file or return None if not configured
- `save_configuration(config: PathConfiguration) -> None` - Persist configuration to file
- `validate_configuration(config: PathConfiguration) -> ValidationResult` - Check path accessibility
- `get_configured_paths() -> DirectoryPaths` - Return current directory paths for use by application

**Relationships:**
- Manages PathConfiguration lifecycle
- Interfaces with SetupWizard for initial configuration
- Used by existing modules to resolve directory paths

### SetupWizard

Manages interactive setup process for first-time users or reconfiguration.

**Attributes:**
- `current_step: SetupStep` - Current position in setup workflow
- `user_input: str` - Path provided by user during setup
- `validation_attempts: int` - Number of validation attempts for current session

**Methods:**
- `start_setup() -> PathConfiguration` - Begin interactive setup process
- `prompt_for_path() -> str` - Request user input for OneDrive base path
- `validate_user_path(path: str) -> ValidationResult` - Check provided path structure
- `handle_validation_error(error: ValidationError) -> None` - Display error and recovery options

**Relationships:**
- Creates PathConfiguration instances from user input
- Uses ConfigurationManager to persist results
- Interfaces with CLI for user interaction

## Supporting Types

### ValidationStatus (Enum)
- `VALID` - Configuration is accessible and validated
- `INVALID` - Configuration exists but paths are not accessible  
- `UNCONFIGURED` - No configuration exists

### ValidationResult
- `is_valid: bool` - Whether validation succeeded
- `error_message: Optional[str]` - User-friendly error description if validation failed
- `missing_directories: List[str]` - Specific subdirectories that could not be found

### DirectoryPaths (Dataclass)
- `constants: Path` - Path to 00-CONSTANTS directory
- `source: Path` - Path to 10-LATEST-PRICING-TOOLS directory
- `output: Path` - Path to 20-OUTPUT directory

### SetupStep (Enum)
- `WELCOME` - Initial setup greeting
- `PATH_INPUT` - Requesting base path from user
- `VALIDATION` - Validating provided path
- `CONFIRMATION` - Confirming successful configuration
- `COMPLETE` - Setup finished successfully

## Configuration File Schema

**Location**: `~/.dtt-pricing-tool-populator-config`
**Format**: JSON

```json
{
  "version": "1.0",
  "onedrive_base_path": "/Users/username/Library/CloudStorage/OneDrive-SharedLibraries-Deloitte(O365D)/AU CBO Practice - MO - Cloud Network & Security/_PRESALES/_PROPOSALS/_PricingToolAccel",
  "last_validated": "2025-10-28T10:30:00Z",
  "validation_status": "valid"
}
```

**Version Evolution**: Future schema versions will maintain backwards compatibility by supporting multiple version parsers and automatic migration.