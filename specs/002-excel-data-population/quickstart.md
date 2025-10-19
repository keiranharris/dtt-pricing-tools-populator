# Quick Start: Excel Data Population from Constants

**Feature**: 002-excel-data-population  
**Status**: Implemented  
**Last Updated**: 2025-10-12

## Overview

This feature automatically populates organizational data fields in Excel pricing spreadsheets from a constants file, eliminating manual data entry for standard information.

## Prerequisites

- Feature 001 (Spreadsheet Copy) completed
- Constants file: `/00-CONSTANTS/lowcomplexity_const_KHv1.xlsx`
- openpyxl library installed: `pip install openpyxl`

## Usage

### Automatic Operation
The data population runs automatically after Feature 001 spreadsheet copy:

```bash
python pricing_tool_accelerator.py
# Enter client/gig information
# File is copied AND populated automatically
```

### Manual Operation (if needed)
```python
from src.data_population_orchestrator import populate_data_from_constants

result = populate_data_from_constants(
    target_file="20-OUTPUT/your-spreadsheet.xlsb",
    constants_filename="lowcomplexity_const_KHv1.xlsx"
)
print(result.summary)
```

## Configuration

### Constants File Setup
Update the filename in `pricing_tool_accelerator.py`:
```python
CONSTANTS_FILENAME = "your_constants_file.xlsx"  # Change this line
```

### Constants File Format
The constants file must have:
- **Sheet Name**: "Pricing Setup"
- **Column C**: Field names (e.g., "Organisation Name")
- **Column E**: Field values (e.g., "Deloitte")

## Populated Fields

The system automatically populates these organizational fields:
- Organisation Name
- Lead Engagement Partner
- Opportunity Owner
- Engagement Manager
- Location
- Market Offering
- Service Type
- Estimate Type
- Working Hours Per Day (HPD)
- Technology vendors/Alliances involvement

## Troubleshooting

### Common Issues
| Issue | Solution |
|-------|----------|
| "Constants file not found" | Verify file exists in `/00-CONSTANTS/` |
| "No fields populated" | Check field names match between constants and target |
| "Low match confidence" | Review field name variations in constants file |

### Field Matching
The system uses fuzzy matching:
- Case insensitive
- Strips first/last 2 characters for core matching
- 80% confidence threshold for automatic population

## Expected Output
```
✓ Constants file loaded: 15 field mappings
✓ Target file scanned: 47 fields found
✓ Field matching completed: 12/15 fields matched
✓ Data population: 12 fields successfully populated
✓ Operation completed in 0.8 seconds
```