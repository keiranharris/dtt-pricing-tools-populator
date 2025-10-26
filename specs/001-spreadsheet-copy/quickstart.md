# Quick Start: Spreadsheet Copy and Instantiation

**Feature**: 001-spreadsheet-copy  
**Status**: Implemented  
**Last Updated**: 2025-10-12

## Overview

This feature automates the weekly task of copying and renaming Excel pricing templates from the source directory to the output directory with proper naming conventions based on user input.

## Prerequisites

- Python 3.11 or higher
- macOS (for Finder integration)
- Template file in `/10-LATEST-PRICING-TOOLS/` directory
- Write access to `/20-OUTPUT/` directory

## Usage

### Basic Operation

```bash
cd /path/to/dtt-pricing-tools-populator
python pricing_tool_accelerator.py
```

The system will prompt you for:
1. **Client Name**: Name of the client organization
2. **Gig Name**: Name of the project/engagement

### Example Session

```
$ python pricing_tool_accelerator.py
Enter Client Name: Acme Corporation
Enter Gig Name: Digital Transformation

✓ Found template: FY26 Low Complexity Pricing Tool v1.2.xlsb
✓ Generated filename: 20251012 - Acme Corporation - Digital Transformation (LowCompV1.2).xlsb
✓ Successfully copied to: /20-OUTPUT/
✓ Opening in Finder...

Operation completed successfully!
```

## File Structure

### Input Requirements
```
10-LATEST-PRICING-TOOLS/
└── FY26 Low Complexity Pricing Tool v1.2.xlsb  # Template file
```

### Output Results
```
20-OUTPUT/
└── 20251012 - Acme Corporation - Digital Transformation (LowCompV1.2).xlsb
```

## Naming Convention

Generated files follow this pattern:
```
YYYYMMDD - <ClientName> - <GigName> (LowComp<Version>).xlsb
```

Where:
- **YYYYMMDD**: Current date (e.g., 20251012)
- **ClientName**: Sanitized client name from user input
- **GigName**: Sanitized gig name from user input  
- **Version**: Extracted from source template (e.g., V1.2)

## Error Handling

### Common Issues and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| "Template file not found" | No Low Complexity file in source directory | Verify template exists in `/10-LATEST-PRICING-TOOLS/` |
| "Cannot write to output directory" | Permission denied | Check write permissions for `/20-OUTPUT/` |
| "Version extraction failed" | Template filename format changed | Ensure template has version like "v1.2" in filename |
| "File already exists" | Duplicate filename | System auto-appends timestamp (e.g., `_143022`) |

### Input Validation

- **Client Name**: Required, max 50 characters, special characters removed
- **Gig Name**: Required, max 50 characters, special characters removed  
- **Illegal characters**: `< > : " | ? * \ /` are automatically removed

## Advanced Features

### Collision Handling

If a file with the same name already exists:
```
Original: 20251012 - Acme Corp - Project (LowCompV1.2).xlsb
Collision: 20251012 - Acme Corp - Project (LowCompV1.2)_143022.xlsb
```

The timestamp suffix (HHMMSS format) prevents overwriting existing files.

### Finder Integration

After successful copy, the system automatically:
1. Opens the output directory in Finder
2. Selects the newly created file
3. Brings Finder to the foreground

## Implementation Details

### Module Structure
```

├── pricing_tool_accelerator.py    # Main CLI entry point
└── src/
    ├── file_operations.py         # File discovery and copying
    ├── cli_interface.py           # User input collection
    ├── naming_utils.py            # Filename generation
    └── system_integration.py      # Finder integration
```

### Key Functions

```python
# Main workflow
def main():
    user_input = collect_user_input()
    source_file = discover_template_file()
    output_file = copy_with_naming(source_file, user_input)
    open_in_finder(output_file.path)

# Core operations
def collect_user_input() -> UserInput
def discover_template_file() -> SourceFile  
def copy_with_naming(source: SourceFile, input: UserInput) -> OutputFile
def open_in_finder(file_path: Path) -> bool
```

## Testing

### Manual Testing Steps

1. **Basic Operation**:
   - Run command with valid inputs
   - Verify file created with correct name
   - Confirm Finder opens with file selected

2. **Error Scenarios**:
   - Test with missing template file
   - Test with invalid permissions
   - Test with empty inputs

3. **Edge Cases**:
   - Test filename collision handling
   - Test special characters in input
   - Test very long client/gig names

### Automated Testing

```bash
cd .
python -m pytest tests/ -v
```

## Configuration

### System Requirements
- **OS**: macOS (primary), Linux/Windows (future)
- **Python**: 3.11+
- **Dependencies**: Standard library only

### Directory Structure
Ensure these directories exist:
```
/10-LATEST-PRICING-TOOLS/  # Source templates
/20-OUTPUT/                # Generated files
```

## Troubleshooting

### Debug Mode
For detailed operation logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Common Fixes

1. **Permission Issues**:
   ```bash
   chmod 755 /20-OUTPUT/
   ```

2. **Template File Issues**:
   - Verify filename contains "Low Complexity"
   - Ensure file extension is `.xlsb`
   - Check file is not corrupted

3. **Finder Not Opening**:
   - Verify running on macOS
   - Check system security settings
   - Test with `open -R <filepath>` manually

## Next Steps

After successful file creation, proceed to:
1. **Feature 002**: Populate data from constants file
2. **Feature 003**: Integrate CLI fields into spreadsheet
3. **Feature 004**: Add date and duration fields

## Support

For issues or questions:
1. Check error messages for specific guidance
2. Verify prerequisites are met
3. Test with minimal example first
4. Check file permissions and directory structure