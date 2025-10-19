# Feature Specification: Populate Start Date and Duration

**Feature Branch**: `004-populate-start-date-and-duration`  
**Created**: 2025-10-12  
**Status**: Implemented  
**Input**: User description: "Extend CLI field collection to include project timing fields (start date, duration) with intelligent defaults and validation"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Project Timing Collection (Priority: P1)

Users need to provide project start date and duration through CLI with intelligent defaults to support project planning and scheduling.

**Why this priority**: Project timing is essential for pricing calculations and project planning - must be collected upfront.

**Independent Test**: Can be tested by running CLI and verifying start date defaults to 4 weeks from now (Monday) and duration accepts integer weeks.

**Acceptance Scenarios**:

1. **Given** current date is any day, **When** CLI prompts for start date, **Then** default is Monday of 4th week from now
2. **Given** user provides duration in weeks, **When** validation occurs, **Then** only positive integers 1-52 are accepted
3. **Given** user provides start date and duration, **When** population occurs, **Then** both fields are populated in Excel using fuzzy matching

---

### User Story 2 - Date Calculation and Validation (Priority: P2)

The system provides intelligent date defaults and robust validation for user convenience and data quality.

**Why this priority**: Automation and validation reduce user errors and improve experience, but core functionality works without them.

**Independent Test**: Can be tested by verifying date calculations are correct, business day adjustment works, and validation rejects invalid inputs.

**Acceptance Scenarios**:

1. **Given** calculated start date falls on weekend, **When** default is shown, **Then** date is adjusted to next Monday
2. **Given** user enters invalid date format, **When** validation runs, **Then** clear error message prompts for correct format
3. **Given** duration exceeds 52 weeks, **When** validation runs, **Then** error explains maximum project duration limit

## Technical Requirements *(mandatory)*

### Date Handling and Calculation
- **Default Calculation**: Current date + 4 weeks, adjusted to next business day (Monday-Friday)
- **Format Support**: DD/MM/YY input format with flexible parsing (DD-MM-YY, DD.MM.YY accepted)
- **Year Inference**: Two-digit years (25 = 2025), handle century boundaries appropriately
- **Business Day Logic**: Skip weekends, adjust to next Monday if calculated date falls on weekend

### Duration Validation and Processing
- **Input Format**: Integer weeks only, no decimals or fractions
- **Range Validation**: 1-52 weeks (maximum 1 year project duration)
- **Input Sanitization**: Remove non-numeric characters, validate integer conversion
- **Error Messages**: Clear feedback with examples for invalid inputs

### CLI Configuration Extension
- **Architecture**: Extend existing CLI_FIELDS_CONFIG from Feature 003
- **Field Mapping**: "Start Date (DD/MM/YY)" and "No of Periods (in Weeks)" exact Excel field matches
- **Integration**: Seamless addition to existing CLI field collection workflow

## Data Model *(mandatory)*

### Extended CLI Configuration
```python
CLI_FIELDS_CONFIG.update({
    "start_date": {
        "prompt": "Start Date (DD/MM/YY)",
        "excel_field_pattern": "Start Date (DD/MM/YY)",
        "required": True,
        "default_calculator": calculate_default_start_date,
        "validator": validate_date_format
    },
    "duration_weeks": {
        "prompt": "No of Periods (in Weeks)",
        "excel_field_pattern": "No of Periods (in Weeks)",
        "required": True,
        "validator": validate_duration_weeks
    }
})
```

### Date Processing Functions
```python
def calculate_default_start_date() -> str:
    """Calculate Monday of 4th week from now"""
    base_date = datetime.now() + timedelta(weeks=4)
    # Adjust to next Monday if needed
    days_ahead = 0 - base_date.weekday()  # Monday = 0
    if days_ahead <= 0:
        days_ahead += 7
    monday = base_date + timedelta(days=days_ahead)
    return monday.strftime("%d/%m/%y")

def validate_duration_weeks(value: str) -> bool:
    """Validate duration is integer 1-52"""
    try:
        weeks = int(value.strip())
        return 1 <= weeks <= 52
    except ValueError:
        return False
```

## Implementation Notes *(mandatory)*

### Architecture Integration
- **Module Extension**: Extend existing CLI interface module, no new modules required
- **Date Library**: Use Python `datetime` module for reliable date calculations and validation
- **Configuration Driven**: New fields added through configuration, core logic unchanged

### Business Logic
- **Default Display**: Show calculated default with explanation: "Default: 15/11/25 (Monday - 4 weeks from now)"
- **User Override**: Allow user to override default or press Enter to accept
- **Validation Loop**: Re-prompt with clear error messages for invalid inputs

## Requirements

### Functional Requirements

#### FR-001: Start Date Field
- **Field Name**: "Start Date (DD/MM/YY)" (exact match with Excel field)
- **Input Format**: DD/MM/YY (e.g., "15/11/25")
- **Default Value**: Monday of the 4th week from current date
- **Validation**: Must be a valid date format
- **User Experience**: Show calculated default, allow override

#### FR-002: Duration Field
- **Field Name**: "No of Periods (in Weeks)" (exact match with Excel field)
- **Input Format**: Integer only (no decimals)
- **Default Value**: None (user must specify)
- **Validation**: Must be positive integer between 1-52 weeks (1 year max)
- **User Experience**: Clear prompt for whole number entry

#### FR-003: Date Calculation Logic
- **Base Calculation**: Current date + 4 weeks
- **Business Day Adjustment**: Adjust to next business day (Mon-Fri) after 4 weeks
- **Display Format**: Show calculated date, day of week, and explanation
- **Example**: "Default: 15/11/25 (Monday - 4 weeks from now)" when current date is 18/10/25

#### FR-004: CLI Integration
- **Architecture**: Extend existing CLI_FIELDS_CONFIG from Feature 003
- **Field Addition**: Add new fields without modifying core logic
- **Validation**: Integrate with existing sanitization framework
- **Error Handling**: Graceful handling of invalid date/number inputs

### Technical Requirements

#### TR-001: Date Handling
- **Library**: Use Python's `datetime` module for reliable date calculations
- **Format Parsing**: Support flexible date input (DD/MM/YY, DD-MM-YY, DD.MM.YY) with year inference (25 = 2025)
- **Business Day Calculation**: Implement next business day logic (Mon-Fri, skip weekends)
- **Edge Cases**: Handle month boundaries, leap years, weekend adjustments

#### TR-002: Integer Validation  
- **Input Sanitization**: Remove any non-numeric characters
- **Range Validation**: 1 ≤ weeks ≤ 52 (maximum 1 year project duration)
- **Error Messages**: Clear feedback with valid format examples for invalid inputs
- **Type Conversion**: Robust string-to-integer conversion with error handling

#### TR-003: CLI Configuration Extension
- **Configuration Structure**: Add new entries to CLI_FIELDS_CONFIG
- **Prompt Customization**: Support default value display in prompts
- **Validation Functions**: Extensible validation system for different field types
- **Backward Compatibility**: Ensure existing CLI fields continue to work unchanged

## User Experience

### Current CLI Flow (Feature 003)
```
📋 Please provide the following information:
   (Special characters will be automatically removed)
Enter Client Name: [user input]
Enter Opportunity Name: [user input]
```

### Enhanced CLI Flow (Feature 004)
```
📋 Please provide the following information:
   (Special characters will be automatically removed)
Enter Client Name: [user input]
Enter Opportunity Name: [user input]
Enter Start Date (DD/MM/YY) [15/11/25 (Monday - 4 weeks from now)]: [user input or Enter for default]
Enter No of Periods (in Weeks): [user input]
```

### Expected Population Behavior
1. User provides timing information via enhanced CLI prompts
2. Start date defaults to intelligent Monday calculation
3. Duration requires explicit user input (no default)
4. System validates date format and integer constraints
5. Fields are populated into Excel using existing fuzzy matching
6. Enhanced feedback shows all 4 CLI fields in population summary

## Success Criteria

### Primary Success Criteria
- ✅ CLI prompts include "Start Date (DD/MM/YY)" and "No of Periods (in Weeks)"
- ✅ Start date defaults to Monday in 4th week with user override capability
- ✅ Duration accepts only positive integers with validation
- ✅ Fields populate correctly into Excel "Pricing Setup" worksheet
- ✅ Existing CLI fields (Client Name, Opportunity Name) continue working unchanged

### Secondary Success Criteria
- ✅ Date calculation handles edge cases (month boundaries, weekends)
- ✅ Input validation provides clear error messages
- ✅ CLI_FIELDS_CONFIG architecture demonstrates extensibility
- ✅ Performance impact remains minimal (< 1 second additional time)

## Edge Cases

### EC-001: Invalid Date Inputs
- **Scenario**: User enters "32/15/25" or "abc" for start date
- **Expected Behavior**: Show error, re-prompt with format example
- **User Feedback**: "Invalid date format. Please use DD/MM/YY (e.g., 15/11/25)"

### EC-002: Invalid Duration Inputs
- **Scenario**: User enters "2.5", "0", or "60" for duration
- **Expected Behavior**: Validate range and integer constraint, re-prompt with examples
- **User Feedback**: "Duration must be a whole number between 1-52 weeks (e.g., 12, 26, 52)"

### EC-003: Date Boundary Conditions
- **Scenario**: Current date near month/year boundary when calculating +4 weeks
- **Expected Behavior**: Correct date calculation across boundaries
- **Example**: Current date 28/12/24 → Default date 27/01/25 (next Monday)

### EC-004: Missing Excel Fields
- **Scenario**: Excel template doesn't contain the exact field names
- **Expected Behavior**: Log warning, show in CLI feedback summary
- **User Experience**: "⚠️ Start Date (DD/MM/YY): Field not found in Excel template"

## Technical Integration Points

### Integration with Feature 003
- **CLI Configuration**: Extend CLI_FIELDS_CONFIG with new field definitions
- **Validation Framework**: Add date and integer validation functions
- **Data Merging**: New fields integrate seamlessly with existing merge logic
- **Population Feedback**: Enhanced summary shows all CLI field statuses

### Date Calculation Implementation
```python
def calculate_default_start_date() -> str:
    """Calculate Monday in 4th week from current date."""
    current_date = datetime.now()
    future_date = current_date + timedelta(weeks=4)
    
    # Adjust to Monday (0 = Monday in Python weekday())
    days_until_monday = (7 - future_date.weekday()) % 7
    if days_until_monday == 0 and future_date.weekday() != 0:
        days_until_monday = 7
    
    monday_date = future_date + timedelta(days=days_until_monday)
    return monday_date.strftime("%d/%m/%y")
```

### CLI Configuration Extension
```python
CLI_FIELDS_CONFIG = {
    # Existing fields (Feature 003)
    "Client Name": {...},
    "Opportunity Name": {...},
    
    # New fields (Feature 004)
    "Start Date (DD/MM/YY)": {
        "prompt": "Enter Start Date (DD/MM/YY)",
        "field_key": "start_date",
        "default_generator": calculate_default_start_date,
        "validator": validate_date_format,
        "error_invalid": "Invalid date format. Please use DD/MM/YY (e.g., 15/11/25)"
    },
    "No of Periods (in Weeks)": {
        "prompt": "Enter No of Periods (in Weeks)",
        "field_key": "duration_weeks",
        "validator": validate_integer_range,
        "error_invalid": "Duration must be a whole number between 1-104 weeks"
    }
}
```

## Risk Assessment

### Low Risk Items
- Date calculation logic (well-established datetime operations)
- Integer validation (straightforward numeric processing)
- CLI configuration extension (proven architecture from Feature 003)

### Medium Risk Items
- Date parsing with DD/MM/YY format (year inference complexity)
- Monday calculation across month/year boundaries
- Integration with existing field population workflow

### Mitigation Strategies
- **Comprehensive Testing**: Test date calculations across various scenarios
- **Input Validation**: Robust error handling for all edge cases
- **Fallback Behavior**: Graceful degradation if date calculation fails
- **User Guidance**: Clear examples and error messages

## Implementation Phases

### Phase 1: Date Calculation Logic (45 minutes)
- Implement default start date calculation function
- Add Monday adjustment logic with boundary handling
- Create date format validation and parsing
- Test with various current dates and edge cases

### Phase 2: CLI Configuration Enhancement (30 minutes)
- Extend CLI_FIELDS_CONFIG with new field definitions
- Add support for default value generators in prompt system
- Implement date and integer validation functions
- Update CLI collection logic to handle defaults and validation

### Phase 3: Integration & Testing (30 minutes)
- Integrate new fields into existing population workflow
- Test end-to-end CLI → Excel population process
- Verify all 4 CLI fields work together correctly
- Validate enhanced user feedback displays timing fields

### Phase 4: Documentation & Cleanup (15 minutes)
- Update code comments and documentation
- Clean up any temporary debug code
- Verify performance impact within acceptable limits

## Acceptance Criteria

### Must Have
1. CLI prompts include both timing fields with appropriate validation
2. Start date defaults to Monday in 4th week from current date
3. Duration accepts only positive integers within reasonable range
4. Fields populate into Excel when matching field names found
5. Existing CLI functionality (Client Name, Opportunity Name) preserved
6. Enhanced CLI feedback shows all 4 field statuses

### Should Have
1. Intelligent date calculation handles month/year boundaries
2. Clear error messages for invalid inputs with format examples
3. Performance overhead remains < 1 second
4. Comprehensive input validation prevents system errors

### Could Have
1. Alternative date input formats (DD-MM-YY, DD.MM.YY)
2. Duration input with units specification (e.g., "12 weeks")
3. Date range validation (not too far in past/future)
4. Holiday/business day awareness in Monday calculation

## Definition of Done
- [ ] All acceptance criteria met
- [ ] Date calculation logic tested across edge cases
- [ ] CLI configuration architecture demonstrates extensibility
- [ ] Integration testing with Excel field population
- [ ] No regression in existing Feature 003 functionality
- [ ] Documentation updated with new field examples
- [ ] Performance benchmarks within acceptable limits

---
**Specification Status**: Draft  
**Created**: October 12, 2025  
**Author**: DTT Pricing Tool Accelerator - Feature 004  
**Review Required**: Implementation team