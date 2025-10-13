# Feature Specification: Spreadsheet Copy and Instantiation

**Feature ID**: `001-spreadsheet-copy`  
**Branch**: `001-spreadsheet-copy`  
**Date**: 2025-10-12  
**Status**: Specification  

## Problem Statement

Weekly administrative tasks require manual copying and renaming of Excel files from a template directory to an output directory. This repetitive process involves:

1. Locating the correct template file (Low Complexity pricing tool)
2. Copying it to the output directory
3. Renaming it with current date and client-specific information
4. Manual typing prone to errors and inconsistency

This manual process occurs multiple times per week and represents inefficient use of time.

## Feature Overview

Create an automated system that copies the Low Complexity Excel template from the source directory (`/10-LATEST-PRICING-TOOLS/`) to the output directory (`/20-OUTPUT/`) with proper naming convention based on user-provided client information.

## Functional Requirements

### Primary Function
- **Source File**: Locate and copy the Excel file containing "Low Complexity" in filename from `/10-LATEST-PRICING-TOOLS/`
- **Destination**: Copy to `/20-OUTPUT/` directory
- **Naming Convention**: `YYYYMMDD - <ClientName> - <GigName> (LowComp<VersionFromSource>).xlsb`

### User Interface Requirements
- **CLI Input**: Prompt user for two text inputs:
  1. `ClientName`: Name of the client (text input, special characters will be stripped)
  2. `GigName`: Name of the engagement/project (text input, special characters will be stripped)
- **Date Handling**: Automatically use current date in YYYYMMDD format
- **File Format**: Keep original `.xlsb` format (no conversion needed)
- **Version Extraction**: Extract version number from source filename (e.g., "v1.2" → "V1.2")

### Validation Requirements
- **Source File Existence**: Verify source file exists before attempting copy
- **Destination Directory**: Ensure `/20-OUTPUT/` directory exists (create if needed)
- **Input Validation**: Ensure ClientName and GigName are provided (non-empty strings)
- **Filename Safety**: Strip special characters from user input (keep only alphanumeric, spaces, hyphens)
- **File Collision**: Auto-append timestamp if destination file already exists
- **Version Parsing**: Extract version number from source filename using regex pattern

## Technical Requirements

### File Operations
- **Copy Operation**: Use Python's file copy functionality (not move - preserve original)
- **Format Preservation**: Keep original `.xlsb` format (supports programmatic data input)
- **Error Handling**: Graceful handling of file permission issues, disk space, etc.
- **File Opening**: Open destination folder in Finder with new file selected after successful copy

### Input Processing
- **CLI Interface**: Clean command-line prompts with clear instructions
- **Input Sanitization**: Strip special characters, keep only alphanumeric, spaces, and hyphens
- **Case Handling**: Preserve user input case for client/gig names
- **Version Parsing**: Use regex to extract version (e.g., "v1.2", "v1.3") from source filename
- **Collision Handling**: Append timestamp (HHMMSS) if destination file exists

### Code Structure (Per Constitution)
- **Atomic Functions**: Separate functions for file discovery, copying, renaming, and CLI input
- **Type Hints**: All functions must include proper type annotations
- **Documentation**: Comprehensive docstrings following Python standards
- **Error Messages**: Clear, actionable error messages for users

## Expected Behavior

### Success Case
```
$ python pricing_tool_accelerator.py
Enter Client Name: Acme Corp
Enter Gig Name: Digital Transformation
✓ Successfully created: 20251012 - Acme Corp - Digital Transformation (LowCompV1.2).xlsb
✓ Opening folder with file selected...
```

### Error Cases
- Source file not found → Clear error message explaining which file was expected
- Destination directory not writable → Permission error with guidance
- Empty input → Re-prompt for valid input
- File already exists → Auto-append timestamp (HHMMSS) to filename
- Version not parseable → Error with explanation of expected format

## File Mapping

### Input
- **Source**: `/10-LATEST-PRICING-TOOLS/FY26 Low Complexity Pricing Tool v1.2.xlsb`

### Output  
- **Destination**: `/20-OUTPUT/YYYYMMDD - <ClientName> - <GigName> (LowComp<VersionFromSource>).xlsb`
- **Example**: `/20-OUTPUT/20251012 - Acme Corp - Digital Transformation (LowCompV1.2).xlsb`
- **Collision Example**: `/20-OUTPUT/20251012 - Acme Corp - Digital Transformation (LowCompV1.2)_143022.xlsb`

## Acceptance Criteria

1. **Source File Discovery**: ✓ Automatically finds file with "Low Complexity" in name
2. **Version Extraction**: ✓ Extracts version number from source filename (e.g., "v1.2" → "V1.2")
3. **User Input Collection**: ✓ Prompts for and collects ClientName and GigName via CLI
4. **Input Sanitization**: ✓ Strips special characters from user input
5. **File Copy**: ✓ Successfully copies source file to destination with correct naming
6. **Date Formatting**: ✓ Uses current date in YYYYMMDD format
7. **Collision Handling**: ✓ Auto-appends timestamp if destination file exists
8. **Folder Opening**: ✓ Opens destination folder in Finder with new file selected
9. **Error Handling**: ✓ Handles missing source file, permission errors, invalid input
10. **Code Quality**: ✓ Follows constitution principles (atomic functions, type hints, documentation)

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