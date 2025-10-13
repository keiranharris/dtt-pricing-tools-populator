# Feature 004: Populate Start Date and Duration - Implementation Plan

## Overview
**Implementation Strategy**: Extend Feature 003's proven CLI_FIELDS_CONFIG architecture  
**Total Estimated Time**: 2 hours  
**Implementation Phases**: 4 phases with clear dependencies  

## Architecture Decision

### Integration Approach: Extend CLI_FIELDS_CONFIG
Building on Feature 003's successful extensible architecture:

- **Proven Pattern**: Leverage existing CLI configuration system
- **Minimal Risk**: Add new fields without modifying core logic
- **Data Flow**: Enhanced CLI Input → Data Merging → Field Matching → Population
- **Validation Framework**: Extend existing sanitization with date/integer validators

### Key Design Decisions

#### Decision 1: Date Calculation Strategy
- **Approach**: Calculate Monday in 4th week from current date
- **Algorithm**: Current date + 4 weeks, then adjust to next Monday if needed
- **Edge Cases**: Handle month/year boundaries and weekend adjustments
- **User Experience**: Display calculated default with day name for clarity

#### Decision 2: Validation Architecture
- **Extensible Validators**: Add validator functions to CLI_FIELDS_CONFIG
- **Error Handling**: Consistent error messages with format examples
- **Input Sanitization**: Leverage existing framework, add date/integer parsing
- **Retry Logic**: Allow user to correct invalid inputs with clear guidance

#### Decision 3: Default Value System  
- **Generator Functions**: Support default value generators in configuration
- **User Override**: Show default, allow Enter to accept or type to override
- **Display Format**: "Enter Field [default value]: " prompt pattern
- **No Default Option**: Duration field requires explicit user input

## Implementation Phases

### Phase 1: Date Calculation Logic
**Duration**: 45 minutes  
**Priority**: High  
**Dependencies**: None  

**Objectives**:
- Create robust date calculation and formatting functions
- Handle edge cases and boundary conditions
- Implement Monday adjustment logic

**Tasks**:
1. **Date Calculation Function** (15 min)
   - Calculate current date + 4 weeks
   - Handle month/year boundary crossings
   - Return formatted DD/MM/YY string

2. **Monday Adjustment Logic** (15 min)
   - Detect if calculated date is Monday
   - Adjust to next Monday if needed
   - Account for weekend edge cases

3. **Date Validation** (15 min)
   - Parse DD/MM/YY input format
   - Validate date components and ranges
   - Handle year inference (25 → 2025)

**Deliverables**:
- `calculate_default_start_date()` function
- `validate_date_format()` function  
- `parse_date_input()` function
- Comprehensive test coverage for edge cases

### Phase 2: CLI Configuration Enhancement
**Duration**: 30 minutes  
**Priority**: High  
**Dependencies**: Phase 1 complete

**Objectives**:
- Extend CLI_FIELDS_CONFIG with new timing fields
- Add default value generator support
- Implement validation framework integration

**Tasks**:
1. **Configuration Extension** (10 min)
   - Add "Start Date (DD/MM/YY)" configuration
   - Add "No of Periods (in Weeks)" configuration
   - Define validation functions and error messages

2. **Default Value Support** (10 min)
   - Modify prompt system to show defaults
   - Handle Enter key for default acceptance
   - Support custom default generators

3. **Validation Integration** (10 min)
   - Add integer range validation (1-52 weeks)
   - Integrate date validation with CLI flow
   - Ensure error handling preserves user experience

**Deliverables**:
- Enhanced CLI_FIELDS_CONFIG with 4 total fields
- Updated `prompt_for_field()` with default support
- `validate_integer_range()` function
- Improved error handling and user feedback

### Phase 3: Integration & Testing
**Duration**: 30 minutes  
**Priority**: Critical  
**Dependencies**: Phase 2 complete

**Objectives**:
- Integrate new fields into existing population workflow
- Test complete CLI → Excel pipeline with all 4 fields
- Validate performance and user experience

**Tasks**:
1. **Workflow Integration** (10 min)
   - Verify new fields work with existing merge logic
   - Test field matching against Excel field names
   - Ensure population feedback includes timing fields

2. **End-to-End Testing** (15 min)
   - Test complete workflow with various date scenarios
   - Validate integer input handling and validation
   - Check Excel field population success rates

3. **Performance Validation** (5 min)
   - Measure impact of date calculations
   - Ensure < 1 second overhead maintained
   - Test with various input combinations

**Deliverables**:
- Verified 4-field CLI workflow
- Excel population success for timing fields
- Performance benchmarks within limits
- User experience validation complete

### Phase 4: Documentation & Cleanup
**Duration**: 15 minutes  
**Priority**: Medium  
**Dependencies**: Phase 3 complete

**Objectives**:
- Update documentation with new capabilities
- Clean up temporary code and debug statements
- Verify code quality and maintainability

**Tasks**:
1. **Code Documentation** (5 min)
   - Update function docstrings with examples
   - Add inline comments for date calculation logic
   - Document new CLI configuration options

2. **Example Updates** (5 min)
   - Update CLI flow examples in documentation
   - Add date format examples and edge cases
   - Document error message formats

3. **Code Cleanup** (5 min)
   - Remove debug print statements
   - Verify consistent code style
   - Check import organization

**Deliverables**:
- Updated documentation with Feature 004 examples
- Clean, production-ready code
- Comprehensive error message coverage

## Technical Implementation Details

### Date Calculation Algorithm
```python
def calculate_default_start_date() -> tuple[str, str]:
    """
    Calculate Monday in 4th week from current date.
    
    Returns:
        Tuple of (formatted_date, display_string)
        
    Example:
        >>> calculate_default_start_date()
        ('15/11/25', '15/11/25 (Monday)')
    """
    from datetime import datetime, timedelta
    
    current_date = datetime.now()
    future_date = current_date + timedelta(weeks=4)
    
    # Calculate days until Monday (0 = Monday)
    days_until_monday = (0 - future_date.weekday()) % 7
    if days_until_monday == 0 and future_date.weekday() != 0:
        days_until_monday = 7
    
    monday_date = future_date + timedelta(days=days_until_monday)
    
    formatted_date = monday_date.strftime("%d/%m/%y")
    display_string = f"{formatted_date} ({monday_date.strftime('%A')})"
    
    return formatted_date, display_string
```

### Enhanced CLI Configuration
```python
CLI_FIELDS_CONFIG = {
    # Existing Feature 003 fields
    "Client Name": {
        "prompt": "Enter Client Name:",
        "field_key": "client_name",
        "validator": None,
        "error_empty": "❌ Client name cannot be empty. Please try again.",
        "error_invalid": "❌ Client name contains only invalid characters. Please try again."
    },
    
    "Opportunity Name": {
        "prompt": "Enter Opportunity Name:",
        "field_key": "opportunity_name",
        "validator": None,
        "error_empty": "❌ Opportunity name cannot be empty. Please try again.",
        "error_invalid": "❌ Opportunity name contains only invalid characters. Please try again."
    },
    
    # New Feature 004 fields
    "Start Date (DD/MM/YY)": {
        "prompt": "Enter Start Date (DD/MM/YY)",
        "field_key": "start_date",
        "default_generator": calculate_default_start_date,
        "validator": validate_date_format,
        "error_empty": "❌ Start date cannot be empty. Please try again.",
        "error_invalid": "❌ Invalid date format. Please use DD/MM/YY (e.g., 15/11/25)"
    },
    
    "No of Periods (in Weeks)": {
        "prompt": "Enter No of Periods (in Weeks)",
        "field_key": "duration_weeks",
        "validator": validate_integer_range,
        "error_empty": "❌ Duration cannot be empty. Please try again.",
        "error_invalid": "❌ Duration must be a whole number between 1-52 weeks (e.g., 12, 26, 52)"
    }
}
```

### Validation Functions
```python
def validate_date_format(date_string: str) -> bool:
    """Validate DD/MM/YY date format."""
    try:
        datetime.strptime(date_string, "%d/%m/%y")
        return True
    except ValueError:
        return False

def validate_integer_range(duration_string: str) -> bool:
    """Validate integer duration between 1-52 weeks."""
    try:
        duration = int(duration_string.strip())
        return 1 <= duration <= 52
    except ValueError:
        return False
```

## Risk Mitigation

### Date Calculation Risks
- **Month Boundaries**: Test calculations across December/January boundary
- **Leap Years**: Verify February handling in leap years  
- **Weekday Logic**: Test Monday adjustment for all days of week
- **Year Inference**: Handle 2-digit year interpretation consistently

### User Input Risks
- **Format Variations**: Users may enter DD-MM-YY or DD.MM.YY formats
- **Invalid Dates**: Handle 32/15/25 or February 30th gracefully
- **Duration Edge Cases**: Very large numbers, negative numbers, decimals
- **Empty Inputs**: Consistent handling with existing field validation

### Integration Risks
- **Excel Field Matching**: Ensure exact field name matches in Excel templates
- **Performance Impact**: Date calculations shouldn't slow CLI significantly
- **Backward Compatibility**: Existing Feature 003 functionality must remain unchanged

## Success Metrics

### Functional Success
- All 4 CLI fields collect and validate input correctly
- Start date defaults to correct Monday calculation
- Duration accepts only valid integer ranges
- Excel population works for timing fields when present

### Technical Success  
- Code follows established architecture patterns
- Performance impact < 1 second additional
- Error handling provides clear user guidance
- Documentation updated with complete examples

### User Experience Success
- Prompts are clear and show helpful defaults
- Error messages guide users to correct format
- CLI feedback shows status of all 4 fields
- Overall workflow feels smooth and intuitive

---
**Implementation Plan Status**: Ready for Development  
**Created**: October 12, 2025  
**Estimated Completion**: 2 hours of focused development  
**Risk Level**: Low (building on proven Feature 003 architecture)