# Feature Specification: Spreadsheet Copy and Instantiation

**Feature Branch**: `001-spreadsheet-copy`  
**Created**: 2025-10-12  
**Status**: Implemented  
**Input**: User description: "Automate the weekly task of copying and renaming Excel templates from source directory to output directory with proper naming conventions"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Basic Template Copy (Priority: P1)

A consultant needs to quickly create a new pricing spreadsheet for a client project by copying the standard Low Complexity template with proper naming conventions.

**Why this priority**: This is the core functionality that eliminates the manual file copying process and provides immediate value to users.

**Independent Test**: Can be fully tested by running the CLI command, providing client and gig names, and verifying a properly named file is created in the output directory with Finder integration.

**Acceptance Scenarios**:

1. **Given** the Low Complexity template exists in `/10-LATEST-PRICING-TOOLS/`, **When** user runs the command and provides "Acme Corp" and "Digital Transformation", **Then** a file named "YYYYMMDD - Acme Corp - Digital Transformation (LowCompV1.2).xlsb" is created in the OneDrive shared output directory
2. **Given** a file already exists with the same name, **When** user creates another file with identical inputs, **Then** the system appends a timestamp to prevent overwriting
3. **Given** user provides input with special characters, **When** the system processes the input, **Then** special characters are sanitized while preserving readable text

---

### User Story 2 - Error Handling and Edge Cases (Priority: P2)

Users encounter various error conditions gracefully with clear guidance on how to resolve issues.

**Why this priority**: Robust error handling ensures the tool is reliable and user-friendly even when things go wrong.

**Independent Test**: Can be tested by creating scenarios with missing files, invalid permissions, or empty inputs and verifying appropriate error messages.

**Acceptance Scenarios**:

1. **Given** the source template file is missing, **When** user runs the command, **Then** system displays clear error explaining which file was expected and where
2. **Given** the output directory is not writable, **When** user attempts to create a file, **Then** system provides permission error with guidance
3. **Given** user provides empty input for client name, **When** prompted, **Then** system re-prompts for valid input

---

### User Story 3 - Version Extraction and File Integration (Priority: P3)

The system automatically extracts version information from the source template and integrates with the operating system for improved user experience.

**Why this priority**: These features enhance usability but are not critical for core functionality.

**Independent Test**: Can be tested by verifying version numbers are correctly extracted from filenames and Finder opens with the new file selected.

**Acceptance Scenarios**:

1. **Given** source file contains version "v1.2", **When** file is copied, **Then** output filename includes "LowCompV1.2"
2. **Given** file copy is successful, **When** operation completes, **Then** Finder opens with the new file selected for immediate access

## Technical Requirements *(mandatory)*

### File Operations & Data Processing
- **Source File Discovery**: Automatically locate Excel file containing "Low Complexity" in filename from `/10-LATEST-PRICING-TOOLS/`
- **File Format Preservation**: Maintain original `.xlsb` format for programmatic compatibility
- **Version Extraction**: Use regex pattern to extract version numbers (e.g., "v1.2" → "V1.2") from source filenames
- **Copy Operations**: Use Python's `shutil.copy2` for metadata preservation without modifying original files

### User Interface & Input Processing
- **CLI Interface**: Prompt for client name and gig name with clear instructions
- **Input Sanitization**: Strip special characters while preserving alphanumeric, spaces, and hyphens
- **Date Handling**: Automatically generate current date in YYYYMMDD format
- **Naming Convention**: Generate filenames as "YYYYMMDD - <ClientName> - <GigName> (LowComp<Version>).xlsb"

### System Integration & Error Handling
- **File Collision Resolution**: Auto-append timestamp (HHMMSS) if destination file already exists
- **Directory Management**: Ensure output directory exists, create if necessary
- **Finder Integration**: Open destination folder with new file selected (macOS-specific)
- **Validation**: Verify source file existence, output directory writability, and input completeness

### Code Architecture (Constitution Compliance)
- **Atomic Functions**: Separate functions for file discovery, copying, naming, and CLI input
- **Type Hints**: Comprehensive type annotations for all function parameters and returns
- **Documentation**: Detailed docstrings following Python standards
- **Error Messages**: Clear, actionable feedback for users in all error scenarios

## Data Model *(mandatory)*

### Input Data Structure
```python
@dataclass
class UserInput:
    client_name: str        # User-provided client name
    gig_name: str          # User-provided project/engagement name
    
@dataclass
class SourceFile:
    path: Path             # Full path to source template file
    version: str           # Extracted version (e.g., "V1.2")
    original_name: str     # Original filename
```

### Output Data Structure
```python
@dataclass
class OutputFile:
    path: Path             # Full path to created file
    filename: str          # Generated filename
    timestamp: str         # Creation timestamp (if collision occurred)
    success: bool          # Operation success status
```

### File System Paths
- **Source Directory**: `/10-LATEST-PRICING-TOOLS/`
- **Destination Directory**: `~/Library/CloudStorage/OneDrive-SharedLibraries-Deloitte(O365D)/AU CBO Practice - MO - Cloud Network & Security/_PRESALES/_PROPOSALS/_PricingToolAccel/20-OUTPUT/`
  - **Configuration**: Defined in `src/constants.py` as `OUTPUT_DIRECTORY` constant
  - **Cross-team compatibility**: Uses `~` for user home directory expansion
  - **Path handling**: Automatically created if it doesn't exist
- **Template Pattern**: Files containing "Low Complexity" in name
- **Output Pattern**: "YYYYMMDD - <Client> - <Gig> (LowComp<Version>).xlsb"

## Implementation Notes *(mandatory)*

### Architecture Overview
The implementation follows a modular design with atomic functions organized across specialized modules:

- **`file_operations.py`**: Source discovery, version parsing, file copying operations
- **`cli_interface.py`**: User input collection, validation, and sanitization
- **`naming_utils.py`**: Filename generation, collision resolution, character sanitization
- **`system_integration.py`**: Finder integration and OS-specific operations

### Key Implementation Details
1. **Version Extraction**: Uses regex pattern `r'v(\d+\.\d+)'` to extract version numbers
2. **Input Sanitization**: Removes special characters while preserving readability
3. **Collision Handling**: Appends timestamp in format `_HHMMSS` when files already exist
4. **Error Recovery**: Comprehensive error handling with user-friendly messages

### Dependencies
- **Python Standard Library Only**: No external dependencies required
- **macOS Integration**: Uses `subprocess` with `open -R` command for Finder integration
- **File Operations**: `shutil.copy2`, `pathlib.Path`, `re` for core functionality

### Testing Strategy
- **Unit Tests**: Individual function testing with mock file operations
- **Integration Tests**: End-to-end workflow testing with temporary directories
- **Error Scenario Testing**: Validation of error handling for missing files, permissions, invalid input
---

## Research & External Dependencies *(if applicable)*

### Technical Research Areas
- **File Operations**: Investigation of Python's `shutil.copy2` vs `shutil.copy` for metadata preservation
- **Regex Patterns**: Development of version extraction patterns for various filename formats
- **macOS Integration**: Validation of `open -R` command for Finder integration
- **File Format Support**: Verification of .xlsb file integrity after copy operations

### External Dependencies
None - Uses Python standard library only for maximum compatibility and simplicity.

### Platform Considerations
- **Primary Target**: macOS (for Finder integration)
- **Future Compatibility**: Code structure allows for cross-platform adaptation

## Success Metrics

- **Time Savings**: Reduce 2-3 minute manual process to 30 seconds
- **Error Reduction**: Eliminate filename typos and formatting inconsistencies  
- **Usability**: Single command execution with clear prompts
- **Reliability**: 100% success rate when source file and permissions are available

## Future Considerations

- Support for multiple template types (beyond Low Complexity)
- Batch processing for multiple clients
- Integration with calendar systems for automatic date handling
- Configuration file for customizable naming patterns

---

*This specification defines the foundational spreadsheet copying functionality that will serve as the base for more complex data population features.*