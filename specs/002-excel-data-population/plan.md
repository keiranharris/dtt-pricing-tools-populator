# Feature 002: Excel Data Population - Implementation Plan

## Overview
**Feature**: Excel Data Population from Constants  
**Dependencies**: Feature 001 (Spreadsheet Copy)  
**Architecture**: Modular design with atomic functions following constitution principles  
**Integration**: Automatic execution after Feature 001 completion  

## Architecture Design

### Module Structure
Following the established pattern from Feature 001, create modular components:

```
src/
├── excel_constants_reader.py    # Read constants file (Column C→E)
├── field_matcher.py            # Core matching algorithm (strip 2 chars)
├── excel_data_populator.py     # Write data to target spreadsheet
└── data_population_orchestrator.py  # Coordinate the population process
```

### Integration Point
```python
# In pricing_tool_accelerator.py (main file)
CONSTANTS_FILENAME = "lowcomplexity_const_KHv1.xlsx"  # Global constant at top

# After successful Feature 001 execution:
if copy_success:
    populate_data_from_constants(output_file, CONSTANTS_FILENAME)
```

## Technical Architecture

### 1. Excel Constants Reader Module
**File**: `src/excel_constants_reader.py`

**Primary Functions**:
- `read_constants_data(constants_dir: Path, filename: str) -> Dict[str, str]`
- `validate_constants_file(file_path: Path) -> bool`
- `parse_field_value_mapping(worksheet, col_c: str, col_e: str) -> Dict[str, str]`

**Design Principles**:
- Handle missing files gracefully (return empty dict)
- Support both .xlsx and .xlsb files
- Validate "Pricing Setup" tab exists
- Map Column C (field names) → Column E (values)

### 2. Field Matcher Module  
**File**: `src/field_matcher.py`

**Primary Functions**:
- `find_matching_fields(source_fields: Dict[str, str], target_sheet) -> List[FieldMatch]`
- `core_string_match(source_field: str, target_field: str) -> float`
- `strip_decorations(field_name: str) -> str`
- `scan_worksheet_for_fields(worksheet) -> List[CellLocation]`

**Matching Algorithm**:
```python
def core_string_match(source: str, target: str) -> float:
    """
    Strip first 2 and last 2 characters, compare middle content
    Return similarity score 0.0-1.0
    """
    source_core = source[2:-2] if len(source) > 4 else source
    target_core = target[2:-2] if len(target) > 4 else target
    
    return fuzzy_similarity(source_core.lower(), target_core.lower())
```

**Data Structures**:
```python
@dataclass
class FieldMatch:
    source_field: str
    target_location: CellLocation
    confidence: float
    source_value: str

@dataclass 
class CellLocation:
    row: int
    column: int
    cell_reference: str  # e.g., "B15"
```

### 3. Excel Data Populator Module
**File**: `src/excel_data_populator.py`

**Primary Functions**:
- `populate_matched_fields(target_file: Path, matches: List[FieldMatch]) -> PopulationResult`
- `write_value_to_cell(worksheet, location: CellLocation, value: str) -> bool`
- `validate_population_success(worksheet, matches: List[FieldMatch]) -> ValidationResult`

**Dropdown Handling**:
- Write text values directly to cells
- Let Excel handle dropdown validation
- Continue on validation errors (Excel will show dropdown options)

### 4. Data Population Orchestrator
**File**: `src/data_population_orchestrator.py`

**Primary Functions**:
- `populate_spreadsheet_data(target_file: Path, constants_filename: str) -> PopulationSummary`
- `integrate_with_feature_001(output_file: Path) -> bool`

**Orchestration Flow**:
1. Check if constants file exists (skip gracefully if missing)
2. Read constants data (Column C→E mapping)
3. Open target spreadsheet "Pricing Setup" tab
4. Find matching fields using core matching algorithm
5. Populate matched fields with values
6. Validate and report results

## Implementation Phases

### Phase 0: Foundation & Configuration (30 minutes)
**Objective**: Set up basic structure and configuration

**Tasks**:
1. Add `CONSTANTS_FILENAME` global variable to main application
2. Create module structure (`excel_constants_reader.py`, etc.)
3. Set up data classes (`FieldMatch`, `CellLocation`, etc.)
4. Configure Excel library imports (openpyxl recommended for .xlsx/.xlsb support)

### Phase 1: Constants File Reading (45 minutes)
**Objective**: Implement robust constants file reading

**Tasks**:
1. Implement `read_constants_data()` with graceful error handling
2. Add support for .xlsx and .xlsb file formats
3. Parse Column C (field names) and Column E (values)
4. Handle missing files, sheets, or columns gracefully
5. Create comprehensive test cases with mock Excel files

**Key Considerations**:
- Skip empty rows in constants file
- Trim whitespace from field names and values
- Handle special characters in field names

### Phase 2: Field Matching Engine (60 minutes)
**Objective**: Implement intelligent field matching algorithm

**Tasks**:
1. Implement core string matching (strip 2 chars from each end)
2. Scan target worksheet for all text cells
3. Calculate similarity scores for potential matches
4. Filter matches by confidence threshold (>= 0.8)
5. Handle multiple potential matches (select highest confidence)

**Matching Strategy**:
```python
# Example matching:
source: "01. Opportunity ID"     -> core: "pportunity I"
target: "A. Opportunity ID:"     -> core: "pportunity I" 
# High match confidence

source: "Location"               -> core: "catio" 
target: ">> Location (City) <<"  -> core: "cation (City) " 
# Medium match confidence
```

### Phase 3: Data Population (45 minutes)
**Objective**: Write matched data to target spreadsheet

**Tasks**:
1. Implement cell writing with proper error handling
2. Support dropdown fields (write text values)
3. Validate successful data writing
4. Handle write permission issues
5. Preserve existing Excel formatting

**Error Scenarios**:
- Read-only files
- Protected worksheets  
- Invalid cell references
- Data validation failures

### Phase 4: Integration & Orchestration (30 minutes)
**Objective**: Integrate with Feature 001 workflow

**Tasks**:
1. Add automatic trigger after successful spreadsheet copy
2. Implement orchestration flow with proper error handling
3. Add user feedback and progress indication
4. Create comprehensive logging for debugging
5. Handle edge cases (missing constants, no matches, etc.)

## Error Handling Strategy

### Graceful Degradation
- **Missing Constants File**: Skip data population, continue with success message
- **No Field Matches**: Report "no matching fields found", continue
- **Partial Population**: Populate successful matches, report failures
- **Excel Errors**: Log errors, continue with remaining operations

### User Feedback
```python
# Success scenarios:
"✅ Populated 8/11 fields from constants file"
"📋 Skipping data population - constants file not found" 

# Partial success:
"⚠️  Populated 5/11 fields - 3 fields not found, 3 fields failed validation"

# Debug information:
"🔍 Field matches found:"
"   Opportunity ID -> B12 (confidence: 95%)"  
"   Location -> D25 (confidence: 88%)"
```

## Performance Considerations

### Target Performance
- **Constants Reading**: < 1 second
- **Field Matching**: < 2 seconds  
- **Data Population**: < 1 second
- **Total Feature Time**: < 5 seconds (per specification)

### Optimization Strategies
- Load only required worksheet (not entire workbook)
- Cache field scanning results for target sheet
- Batch write operations where possible
- Use efficient string matching algorithms

## Testing Strategy

### Unit Tests
- Constants file reading with various Excel formats
- Field matching algorithm with different string patterns
- Data population with mock Excel worksheets
- Error handling for all failure scenarios

### Integration Tests  
- End-to-end workflow with real Excel files
- Integration with Feature 001 success/failure scenarios
- Performance testing with large spreadsheets
- Cross-platform compatibility (macOS focus)

### Test Data Structure
```
test_data/
├── constants/
│   ├── valid_constants.xlsx
│   ├── missing_columns.xlsx
│   └── empty_file.xlsx
├── templates/
│   ├── standard_pricing_tool.xlsb
│   └── modified_field_names.xlsb
└── expected_results/
    └── populated_spreadsheet.xlsx
```

## Configuration Management

### Global Constants (in main file)
```python
# === CONFIGURATION CONSTANTS ===
CONSTANTS_FILENAME = "lowcomplexity_const_KHv1.xlsx"  # Easy to update
CONSTANTS_DIR_NAME = "00-CONSTANTS"
TARGET_WORKSHEET_NAME = "Pricing Setup" 
FIELD_MATCH_THRESHOLD = 0.8  # Minimum similarity for matches
CHAR_STRIP_COUNT = 2  # Characters to strip from start/end
```

### Field Mapping Overrides (future extensibility)
```python
# Optional: Manual overrides for difficult matches
FIELD_MAPPING_OVERRIDES = {
    "Working Hours Per Day": ["HPD", "Hours Per Day", "Daily Hours"],
    "Technology Vendors": ["Tech Vendors", "Vendor Involvement"]
}
```

## Success Metrics

### Functional Success
1. **Automatic Integration**: Runs seamlessly after Feature 001
2. **Robust Matching**: Handles field name variations with >80% accuracy
3. **Graceful Errors**: Never crashes, always provides useful feedback
4. **Performance**: Completes within 5-second target
5. **Configuration**: Constants filename easily changeable

### Quality Metrics
- **Test Coverage**: >90% code coverage
- **Error Handling**: All error paths tested and documented
- **User Experience**: Clear feedback for all scenarios
- **Maintainability**: Modular design following constitution principles

## Future Extensibility

### Phase 2 Enhancements (out of scope)
- Multiple constants files support
- User-configurable field mappings  
- Advanced field validation
- Backup/restore functionality
- Audit trail of population activities

### Integration Points
- Design interfaces to support future enhancements
- Maintain backward compatibility with Feature 001
- Structure for additional data sources beyond constants files

---
**Document Status**: Implementation Plan v1.0  
**Last Updated**: October 12, 2025  
**Next Phase**: Task Breakdown & Implementation