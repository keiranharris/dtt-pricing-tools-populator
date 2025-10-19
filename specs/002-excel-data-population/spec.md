# Feature Specification: Excel Data Population from Constants

**Feature Branch**: `002-excel-data-population`  
**Created**: 2025-10-12  
**Status**: Implemented  
**Input**: User description: "Automatically populate organizational data fields in Excel spreadsheets from a constants file to eliminate manual data entry"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Basic Data Population (Priority: P1)

After creating a new pricing spreadsheet, a consultant needs organizational data automatically populated from a constants file to avoid manual entry of repetitive information.

**Why this priority**: This is the core value proposition - eliminating manual data entry for standard organizational fields that are consistent across projects.

**Independent Test**: Can be fully tested by running the population after a spreadsheet copy and verifying that fields like "Organisation Name", "Lead Engagement Partner", etc. are correctly populated from the constants file.

**Acceptance Scenarios**:

1. **Given** a constants file exists with organizational data, **When** a new spreadsheet is created, **Then** all matching fields are automatically populated with correct values
2. **Given** the constants file contains dropdown field values, **When** data is populated, **Then** dropdown fields receive appropriate text values
3. **Given** organizational data fields exist in the target spreadsheet, **When** population occurs, **Then** user receives confirmation of which fields were successfully populated

---

### User Story 2 - Robust Field Matching (Priority: P1)

Users need the system to handle variations in field names and Excel structure changes while maintaining accurate data population.

**Why this priority**: Excel files change over time, and the system must be resilient to minor structural modifications to remain reliable.

**Independent Test**: Can be tested by creating variations of field names (different cases, extra prefixes/suffixes) and verifying the fuzzy matching algorithm still correctly identifies and populates fields.

**Acceptance Scenarios**:

1. **Given** field names have minor variations in case or formatting, **When** matching occurs, **Then** fields are correctly identified using fuzzy matching
2. **Given** Excel structure changes (row/column positions), **When** scanning occurs, **Then** fields are found regardless of position changes
3. **Given** field names have prefixes or suffixes, **When** core matching algorithm runs, **Then** fields are matched based on core content

---

### User Story 3 - Configuration Management (Priority: P2)

System administrators need easy configuration management for constants files and field mappings without code modifications.

**Why this priority**: Operational flexibility is important but secondary to core functionality - enables easy maintenance and updates.

**Independent Test**: Can be tested by changing the constants filename configuration and verifying the system uses the new file correctly.

**Acceptance Scenarios**:

1. **Given** a new constants file is available, **When** the filename is updated in configuration, **Then** the system uses the new file for data population
2. **Given** the constants file is missing, **When** population is attempted, **Then** the system gracefully skips population with appropriate user notification
3. **Given** field mapping rules need adjustment, **When** configuration is updated, **Then** the new rules are applied correctly

---

### User Story 4 - Error Handling and Validation (Priority: P3)

Users encounter robust error handling and clear feedback when issues occur during data population.

**Why this priority**: Error handling enhances user experience but is not critical for core functionality - helps with troubleshooting and reliability.

**Independent Test**: Can be tested by creating scenarios with missing files, invalid data, or permission issues and verifying appropriate error handling and user feedback.

**Acceptance Scenarios**:

1. **Given** the constants file is corrupted or unreadable, **When** population is attempted, **Then** clear error messages guide the user to resolution
2. **Given** field matching confidence is low, **When** population occurs, **Then** user receives detailed feedback about match quality and potential issues
3. **Given** Excel file permissions prevent writing, **When** data population is attempted, **Then** appropriate error handling prevents data corruption

## Technical Requirements *(mandatory)*

### Excel File Operations
- **Library Support**: Use robust Excel libraries (openpyxl preferred) for reading both .xlsx and .xlsb files
- **Constants File Reading**: Read field-value mappings from Column C (field names) → Column E (values) in "Pricing Setup" tab
- **Target File Writing**: Write populated data to matching fields in newly created spreadsheet "Pricing Setup" tab
- **Format Preservation**: Maintain Excel formatting, dropdown functionality, and cell properties

### Intelligent Field Matching Algorithm
- **Fuzzy Matching**: Implement core content matching by stripping first 2 and last 2 characters from field names
- **Case Insensitive**: Handle field name variations in case and formatting
- **Position Flexibility**: Scan entire worksheet to locate fields regardless of row/column position changes
- **Confidence Scoring**: Provide match confidence levels and detailed logging for debugging

### Data Population Strategy
- **Field Type Support**: Handle both text fields and dropdown selectors with appropriate value insertion
- **Column/Row Adaptation**: Adapt to structural changes in Excel file layout
- **Priority Handling**: Constants file data takes precedence over any existing values
- **Validation**: Verify successful data transfer and provide feedback on populated fields

### Configuration and Integration
- **Constants Filename**: Store as easily configurable global constant (`CONSTANTS_FILENAME = "lowcomplexity_const_KHv1.xlsx"`)
- **Automatic Integration**: Execute automatically after Feature 001 spreadsheet copy completion
- **Graceful Degradation**: Skip population if constants file missing, continue with appropriate user notification
- **Error Recovery**: Comprehensive error handling for missing files, sheets, fields, or permission issues

## Data Model *(mandatory)*

### Core Data Structures
```python
@dataclass
class FieldMapping:
    source_field_name: str      # From constants file Column C
    source_value: str           # From constants file Column E
    target_field_name: str      # Matched field in target spreadsheet
    match_confidence: float     # Matching algorithm confidence score
    populated: bool             # Whether value was successfully written

@dataclass
class ConstantsData:
    file_path: Path            # Path to constants file
    field_mappings: Dict[str, str]  # Raw field name → value mappings
    sheet_name: str            # Target sheet name ("Pricing Setup")
    
@dataclass
class PopulationResult:
    total_fields_found: int    # Total fields in constants file
    successful_matches: int    # Fields successfully matched and populated
    failed_matches: List[str]  # Field names that couldn't be matched
    errors: List[str]          # Any errors encountered
    success: bool              # Overall operation success
```

### Field Data Requirements
Target organizational data fields to populate:
- **Client Details**: Opportunity ID, Organisation Name, Lead Engagement Partner, Opportunity Owner, Engagement Manager
- **Location/Service**: Location, Market Offering, Service Type, Estimate Type  
- **Planning**: Working Hours Per Day (HPD) assumptions
- **Technology**: Technology vendors/Alliances involvement

### File System Structure
- **Constants Directory**: `/00-CONSTANTS/`
- **Constants File**: Configurable filename (default: `lowcomplexity_const_KHv1.xlsx`)
- **Target Sheet**: "Pricing Setup" tab in both constants and target files
- **Mapping Structure**: Column C (field names) → Column E (values)

## Implementation Notes *(mandatory)*

### Architecture Overview
The implementation extends the modular design established in Feature 001:

- **`excel_constants_reader.py`**: Read field-value mappings from constants file
- **`field_matcher.py`**: Implement fuzzy matching algorithm for field identification
- **`excel_data_populator.py`**: Write matched data to target spreadsheet fields
- **`data_population_orchestrator.py`**: Coordinate the complete population workflow

### Key Implementation Details

#### Fuzzy Matching Algorithm
```python
def core_string_match(source_field: str, target_field: str) -> float:
    """
    Match fields by comparing core content (strip first/last 2 chars)
    Returns confidence score 0.0-1.0
    """
    source_core = source_field.lower().strip()[2:-2] if len(source_field) > 4 else source_field.lower()
    target_core = target_field.lower().strip()[2:-2] if len(target_field) > 4 else target_field.lower()
    
    # Use similarity algorithm (e.g., difflib.SequenceMatcher)
    return similarity_score(source_core, target_core)
```

#### Integration Point
```python
# In pricing_tool_accelerator.py
CONSTANTS_FILENAME = "lowcomplexity_const_KHv1.xlsx"  # Global configuration

def main():
    # After Feature 001 completion
    if spreadsheet_copy_success:
        result = populate_data_from_constants(output_file, CONSTANTS_FILENAME)
        display_population_feedback(result)
```

### Dependencies and Libraries
- **openpyxl**: Primary Excel file manipulation (handles both .xlsx and .xlsb)
- **difflib**: String similarity matching for fuzzy field matching
- **pathlib**: File path operations
- **logging**: Detailed operation logging for debugging

### Error Handling Strategy
- **Missing Constants File**: Skip population, notify user, continue operation
- **Excel Permission Issues**: Clear error messages with resolution guidance  
- **Field Matching Failures**: Log unmatched fields, continue with successful matches
- **Data Write Failures**: Rollback capability, preserve original data integrity

### Performance Considerations
- **File Loading**: Load only necessary worksheets, avoid full workbook loading
- **Memory Usage**: Stream processing for large files when possible
- **Matching Algorithm**: Optimize for typical field count (10-20 fields)
- **User Feedback**: Progress indication for operations taking >2 seconds

## Research & External Dependencies *(if applicable)*

### Technical Research Areas
- **Excel Library Comparison**: Evaluation of openpyxl vs xlwings vs pandas for .xlsb support and performance
- **String Matching Algorithms**: Analysis of different fuzzy matching approaches for field name variations
- **Excel Field Type Detection**: Investigation of dropdown vs text field identification and appropriate population methods

### External Dependencies
- **openpyxl**: Primary dependency for Excel file operations
- **difflib**: Standard library for string similarity matching
- **Optional**: xlwings for advanced Excel integration if needed

### Platform Considerations
- **Cross-platform**: Excel file operations work on Windows, macOS, Linux
- **Excel Version Compatibility**: Support for Excel 2016+ file formats
---

## Research & External Dependencies *(if applicable)*

### Technical Research Areas
- **Excel Library Comparison**: Evaluation of openpyxl vs xlwings vs pandas for .xlsb support and performance
- **String Matching Algorithms**: Analysis of different fuzzy matching approaches for field name variations
- **Excel Field Type Detection**: Investigation of dropdown vs text field identification and appropriate population methods

### External Dependencies
- **openpyxl**: Primary dependency for Excel file operations
- **difflib**: Standard library for string similarity matching
- **Optional**: xlwings for advanced Excel integration if needed

### Platform Considerations
- **Cross-platform**: Excel file operations work on Windows, macOS, Linux
- **Excel Version Compatibility**: Support for Excel 2016+ file formats