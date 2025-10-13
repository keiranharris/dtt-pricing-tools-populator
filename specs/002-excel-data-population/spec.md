# Feature 002: Excel Data Population from Constants

## Overview
**Feature ID**: 002-excel-data-population  
**Dependencies**: Feature 001 (Spreadsheet Copy)  
**Status**: Specification Phase  
**Estimated Complexity**: Medium-High  

## Business Context
After Feature 001 creates a new pricing tool spreadsheet, users need to manually populate various fields with standard organizational data. This is repetitive, error-prone, and time-consuming. The data values are consistent across projects and stored in a constants file.

## Functional Requirements

### FR-001: Constants File Management
- **Configuration**: Store constants filename as a global constant in main application code
- **Current File**: `lowcomplexity_const_KHv1.xlsx` in `/00-CONSTANTS/` directory
- **Structure**: Single sheet, Field names in Column C, Values in Column E
- **Tab Name**: Must match target file tab name ("Pricing Setup")
- **Flexibility**: Easy to change filename when constants file is updated

### FR-002: Data Mapping and Population
- **Source**: Read data from constants file (`/00-CONSTANTS/lowcomplexity_const_KHv1.xlsx`) Column C (field names) → Column E (values)
- **Target**: Populate fields in newly copied pricing tool spreadsheet "Pricing Setup" tab
- **Field Types**: Dropdown selectors and text fields (populate with simple text values)
- **Mapping Strategy**: Intelligent field matching using fuzzy string comparison

### FR-003: Robust Field Matching
- **Case Insensitive**: Handle field name variations in case
- **Core Matching**: Strip first 2 and last 2 characters, match on middle content to handle prefixes/suffixes
- **Target Search**: Scan entire "Pricing Setup" tab to locate matching field names
- **Column Flexibility**: Adapt to column position changes in source/target files
- **Row Flexibility**: Adapt to row position changes in source/target files
- **Debug Output**: Print matched field snippets for verification

### FR-004: Data Fields to Copy
Based on the provided screenshot, copy the following organizational data:

#### Client Details Section:
- **Opportunity ID** → Match and populate
- **Organisation Name** → Match and populate  
- **Lead Engagement Partner** → Match and populate
- **Opportunity Owner** → Match and populate
- **Engagement Manager** → Match and populate

#### Location/Service Details:
- **Location** → Match and populate
- **Market Offering** → Match and populate
- **Service Type** → Match and populate
- **Estimate Type** → Match and populate

#### Planning Information:
- **What is the Working Hours Per Day (HPD) assumed for planning the solution and that will be charged to the client?** → Match and populate

#### Technology Questions:
- **Does the engagement involve technology vendors or Alliances** → Match and populate

## Technical Requirements

### TR-001: Excel File Operations
- **Library**: Use robust Excel reading library (openpyxl, pandas, or xlwings)
- **Format Support**: Handle both .xlsx and .xlsb files
- **Error Handling**: Graceful handling of missing files, sheets, or fields
- **Performance**: Efficient reading without loading entire workbooks unnecessarily

### TR-002: String Matching Algorithm
- **Algorithm**: Implement fuzzy string matching focusing on core content (ignoring prefixes/suffixes)
- **Core Content Strategy**: Strip first 2 and last 2 characters and match on middle portion
- **Dropdown Compatibility**: Populate dropdown fields with text values (Excel will handle validation)
- **Tolerance**: Configure similarity threshold for matches
- **Logging**: Output match confidence and field snippets
- **Missing File Handling**: Skip data population gracefully if constants file missing

### TR-003: Configuration Management
- **Constants**: Store constants filename as easily editable global variable
- **Mapping Config**: Configurable field mapping rules
- **Extensibility**: Design for easy addition of new data fields

## Non-Functional Requirements

### NFR-001: Reliability
- **Brittleness Resistance**: Handle structural changes in Excel files
- **Validation**: Verify data was copied correctly
- **Backup Strategy**: Preserve original data if copy fails

### NFR-002: Usability
- **Feedback**: Clear progress indication during data copying
- **Debugging**: Verbose logging of matching process for troubleshooting
- **Integration**: Runs automatically immediately after Feature 001 (spreadsheet copy)
- **Graceful Degradation**: Continue operation if constants file missing (skip data population)

### NFR-003: Maintainability
- **Modularity**: Separate Excel operations, string matching, and data mapping
- **Documentation**: Clear documentation of field mapping rules
- **Testing**: Comprehensive test suite for various Excel file scenarios

## Success Criteria
1. **Automated Population**: All specified fields automatically populated from constants file
2. **Robust Matching**: Field matching works despite minor structural changes
3. **Easy Configuration**: Constants filename easily changeable in main code
4. **Performance**: Data population completes within 5 seconds
5. **Error Recovery**: Clear error messages and graceful handling of missing data
6. **Integration**: Seamless integration with existing spreadsheet copy workflow

## User Stories

### US-001: Data Population
**As a** consultant setting up pricing tools  
**I want** organizational data automatically populated from constants  
**So that** I don't have to manually enter repetitive information  

**Acceptance Criteria**:
- All organizational fields populated from constants file
- No manual data entry required for standard fields
- Process completes automatically after spreadsheet copy

### US-002: Flexible Configuration
**As a** system administrator  
**I want** to easily update the constants filename  
**So that** new constants files can be used without code changes  

**Acceptance Criteria**:
- Constants filename stored as easily editable global variable
- Clear documentation on how to update filename
- System validates constants file exists before processing

### US-003: Robust Operations
**As a** user with varying Excel file structures  
**I want** the system to handle minor changes in field names and positions  
**So that** the tool remains functional despite spreadsheet updates  

**Acceptance Criteria**:
- Case-insensitive field matching
- Tolerance for minor field name variations
- Clear feedback on which fields were successfully matched

## Technical Architecture Overview

### Components:
1. **Excel Constants Reader**: Read data from constants file
2. **Field Matcher**: Intelligent string matching for field names
3. **Data Populator**: Write matched data to target spreadsheet
4. **Configuration Manager**: Handle constants filename and mapping rules
5. **Integration Layer**: Connect with existing Feature 001 workflow

### Data Flow:
1. Feature 001 creates new spreadsheet
2. **Automatic Trigger**: Feature 002 starts immediately after successful copy
3. System reads constants file from `/00-CONSTANTS/` (Column C→E mapping)
4. Field matcher scans "Pricing Setup" tab for matching field names (strip 2 chars each end)
5. Data populator writes values to matched fields (including dropdowns)
6. Validation confirms successful data transfer
7. User receives feedback on populated fields (or skip notification if constants missing)

## Future Considerations
- Support for multiple constants files
- User-configurable field mappings
- Advanced field validation rules
- Integration with other organizational data sources
- Audit trail of data population activities

---
**Document Status**: Draft v1.0  
**Last Updated**: October 12, 2025  
**Next Phase**: Planning & Architecture Design