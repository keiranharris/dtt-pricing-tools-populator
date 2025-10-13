# Feature 004: Populate Start Date and Duration - Task Breakdown

## Overview
**Feature**: Populate Start Date and Duration  
**Total Estimated Time**: 2 hours  
**Implementation Phases**: 4 phases with 8 detailed tasks  
**Progress Tracking**: Tasks will be marked with ✅ COMPLETED during implementation  

## Phase 1: Date Calculation Logic (45 minutes)

### Task 1.1: Create Date Calculation Function ✅ COMPLETED
**Estimated Time**: 15 minutes  
**Priority**: High  
**Dependencies**: None

**Objective**: Implement robust date calculation for Monday in 4th week

**Actions**:
- [x] Create `calculate_default_start_date()` function
- [x] Implement current date + 4 weeks calculation  
- [x] Handle month/year boundary crossings correctly
- [x] Return both formatted string and display version
- [x] Add comprehensive docstring with examples

**Acceptance Criteria**:
- ✅ Function calculates correct date 4 weeks from current date
- ✅ Handles month boundaries (e.g., December → January)
- ✅ Returns formatted DD/MM/YY string
- ✅ Provides display version with day name
- ✅ Function is well-documented with examples

**Function Signature**:
```python
def calculate_default_start_date() -> tuple[str, str]:
    """Returns (formatted_date, display_string)"""
```

### Task 1.2: Implement Monday Adjustment Logic ✅ COMPLETED
**Estimated Time**: 15 minutes  
**Priority**: High  
**Dependencies**: Task 1.1

**Objective**: Ensure calculated date is always a Monday

**Actions**:
- [x] Detect current weekday of calculated date
- [x] Calculate days needed to reach next Monday
- [x] Handle case where calculated date is already Monday
- [x] Test across all days of the week
- [x] Verify logic works with month boundaries

**Acceptance Criteria**:
- ✅ If calculated date is Monday, keep it unchanged  
- ✅ If calculated date is Tuesday-Sunday, advance to next Monday
- ✅ Monday adjustment works across month/year boundaries
- ✅ Logic tested for all 7 starting weekdays
- ✅ Algorithm is efficient and reliable

**Test Cases**:
- Current date: Monday → Default: Monday 4 weeks later
- Current date: Friday → Default: Monday 4+ weeks later  
- Edge case: December date → January Monday

### Task 1.3: Create Date Validation Functions ✅ COMPLETED
**Estimated Time**: 15 minutes  
**Priority**: High  
**Dependencies**: None (parallel to Tasks 1.1-1.2)

**Objective**: Robust validation and parsing of DD/MM/YY user input

**Actions**:
- [x] Create `validate_date_format()` function for DD/MM/YY
- [x] Implement `parse_date_input()` with error handling
- [x] Handle 2-digit year inference (25 → 2025)
- [x] Validate date component ranges (day 1-31, month 1-12)
- [x] Test with various invalid inputs
- [x] Added flexible format support (DD/MM/YY, DD-MM-YY, DD.MM.YY)
- [x] Implemented `validate_duration_input()` for integer range validation

**Acceptance Criteria**:
- ✅ Validates correct DD/MM/YY format (15/11/25)
- ✅ Accepts flexible formats (15-11-25, 15.11.25) 
- ✅ Handles year inference correctly (25 → 2025)
- ✅ Validates date component ranges appropriately
- ✅ Provides clear error feedback for invalid inputs

**Function Signatures**:
```python
def validate_date_format(date_string: str) -> bool
def parse_date_input(date_string: str) -> datetime | None
```

## Phase 2: CLI Configuration Enhancement (30 minutes)

### Task 2.1: Extend CLI_FIELDS_CONFIG ✅ COMPLETED
**Estimated Time**: 10 minutes  
**Priority**: High  
**Dependencies**: Phase 1 complete

**Objective**: Add timing fields to existing CLI configuration

**Actions**:
- [x] Add "Start Date (DD/MM/YY)" configuration entry
- [x] Add "No of Periods (in Weeks)" configuration entry  
- [x] Define appropriate prompts and error messages
- [x] Link validation functions to field configurations
- [x] Test configuration loading and access

**Acceptance Criteria**:
- ✅ CLI_FIELDS_CONFIG contains 4 total fields (2 existing + 2 new)
- ✅ New fields have appropriate prompts and field keys
- ✅ Error messages are clear and format-specific
- ✅ Validation functions are properly linked
- ✅ Configuration structure follows existing patterns

**Configuration Example**:
```python
"Start Date (DD/MM/YY)": {
    "prompt": "Enter Start Date (DD/MM/YY)",
    "field_key": "start_date",
    "default_generator": calculate_default_start_date,
    "validator": validate_date_format,
    "error_invalid": "❌ Invalid date format. Please use DD/MM/YY (e.g., 15/11/25)"
}
```

### Task 2.2: Add Default Value Support ✅ COMPLETED  
**Estimated Time**: 10 minutes  
**Priority**: High  
**Dependencies**: Task 2.1

**Objective**: Enhance prompt system to support default values

**Actions**:
- [x] Modify `prompt_for_field()` to handle default generators
- [x] Display default value in prompt (e.g., "[15/11/25 (Monday)]:")
- [x] Allow Enter key to accept default value
- [x] Support fields without defaults (duration field)
- [x] Test default acceptance and override scenarios

**Acceptance Criteria**:
- ✅ Prompts show default values when available
- ✅ Enter key accepts default without additional input
- ✅ Users can override defaults by typing new values
- ✅ Fields without defaults work as before
- ✅ Prompt display is clear and user-friendly

**Enhanced Prompt Format**:
```
Enter Start Date (DD/MM/YY) [15/11/25 (Monday)]: 
Enter No of Periods (in Weeks): 
```

### Task 2.3: Implement Integer Validation ✅ COMPLETED
**Estimated Time**: 10 minutes  
**Priority**: High  
**Dependencies**: Task 2.1

**Objective**: Create robust integer validation for duration field

**Actions**:
- [x] Create `validate_duration_input()` function  
- [x] Implement range checking (1-52 weeks)
- [x] Handle non-numeric inputs gracefully
- [x] Provide clear error messages for invalid ranges
- [x] Test boundary conditions (0, 1, 52, 53)

**Acceptance Criteria**:
- ✅ Accepts valid integers between 1-52 weeks
- ✅ Rejects decimals, negative numbers, zero
- ✅ Rejects non-numeric inputs (abc, 12.5, -5)
- ✅ Provides clear error messages with valid range
- ✅ Handles edge cases and boundary values correctly

**Function Signature**:
```python  
def validate_integer_range(duration_string: str, min_val: int = 1, max_val: int = 52) -> bool
```

## Phase 3: Integration & Testing (30 minutes)

### Task 3.1: Integrate New Fields into Workflow ✅ COMPLETED
**Estimated Time**: 10 minutes  
**Priority**: Critical  
**Dependencies**: Phase 2 complete

**Objective**: Ensure new fields work with existing population pipeline

**Actions**:
- [x] Verify new fields are collected by `collect_cli_fields()`
- [x] Test data merging includes timing fields
- [x] Confirm field matching works with Excel field names
- [x] Check population feedback shows all 4 fields
- [x] Test backward compatibility with existing fields

**Acceptance Criteria**:
- ✅ All 4 CLI fields are collected in single workflow
- ✅ Data merging preserves timing field values
- ✅ Excel field matching finds timing fields when present
- ✅ Population feedback displays timing field status
- ✅ Existing Client Name/Opportunity Name functionality unchanged

**Integration Test**:
```python
cli_data = collect_cli_fields()  
# Should return: {"Client Name": "...", "Opportunity Name": "...", 
#                "Start Date (DD/MM/YY)": "...", "No of Periods (in Weeks)": "..."}
```

### Task 3.2: End-to-End Testing ✅ COMPLETED
**Estimated Time**: 15 minutes  
**Priority**: Critical  
**Dependencies**: Task 3.1

**Objective**: Comprehensive testing of complete workflow

**Actions**:
- [x] Test CLI collection with various date scenarios
- [x] Verify date validation with edge cases
- [x] Test integer validation with boundary values
- [x] Run complete CLI → Excel population workflow
- [x] Validate user experience and error handling

**Acceptance Criteria**:
- ✅ Date calculation works across month boundaries
- ✅ Monday adjustment handles all weekday scenarios
- ✅ Date validation rejects invalid formats appropriately
- ✅ Integer validation enforces range constraints
- ✅ Complete workflow performs within time limits

**Test Scenarios**:
1. Default date acceptance (Enter key)
2. Date override with valid format
3. Invalid date format handling
4. Valid duration range (1, 26, 52)
5. Invalid duration handling (0, 105, 12.5, abc)

### Task 3.3: Performance Validation ✅ COMPLETED
**Estimated Time**: 5 minutes  
**Priority**: Medium  
**Dependencies**: Task 3.2

**Objective**: Ensure performance impact remains minimal

**Actions**:
- [x] Measure time impact of date calculations
- [x] Test CLI collection performance with 4 fields
- [x] Verify overall workflow time < 1 second overhead
- [x] Check memory usage impact of new functions
- [x] Document performance benchmarks

**Acceptance Criteria**:
- ✅ Date calculation adds < 0.1 seconds
- ✅ CLI collection with 4 fields completes quickly  
- ✅ Overall performance impact < 1 second
- ✅ Memory usage remains reasonable
- ✅ Performance meets Feature 003 standards

## Phase 4: Documentation & Cleanup (15 minutes)

### Task 4.1: Update Documentation ⏳ NOT STARTED
**Estimated Time**: 10 minutes  
**Priority**: Medium  
**Dependencies**: Phase 3 complete

**Objective**: Update all documentation with Feature 004 capabilities

**Actions**:
- [ ] Update function docstrings with examples
- [ ] Document CLI_FIELDS_CONFIG extension pattern  
- [ ] Add date format examples and validation rules
- [ ] Update user-facing documentation with new prompts
- [ ] Document error message formats and meanings

**Acceptance Criteria**:
- ✅ All functions have comprehensive docstrings
- ✅ Configuration extension is clearly documented
- ✅ Date format examples are provided
- ✅ Error messages are documented with solutions
- ✅ User workflow examples include timing fields

### Task 4.2: Code Quality & Cleanup ⏳ NOT STARTED
**Estimated Time**: 5 minutes  
**Priority**: Low  
**Dependencies**: Task 4.1  

**Objective**: Ensure production-ready code quality

**Actions**:
- [ ] Remove debug print statements and temporary code
- [ ] Verify consistent code style and formatting
- [ ] Check import organization and dependencies
- [ ] Validate error handling completeness
- [ ] Confirm type hints where appropriate

**Acceptance Criteria**:
- ✅ No debug code or print statements remain
- ✅ Code style is consistent with existing modules
- ✅ Imports are organized and minimal
- ✅ Error handling covers all identified scenarios
- ✅ Code is ready for production deployment

## Progress Tracking

### Phase Completion Status
- [ ] **Phase 1**: Date Calculation Logic (0/3 tasks complete)
- [ ] **Phase 2**: CLI Configuration Enhancement (0/3 tasks complete)  
- [ ] **Phase 3**: Integration & Testing (0/3 tasks complete)
- [ ] **Phase 4**: Documentation & Cleanup (0/2 tasks complete)

**Overall Progress**: 0/11 tasks completed (0%)

### Time Tracking
- **Estimated Total**: 2 hours
- **Actual Time**: TBD during implementation
- **Efficiency Target**: Complete within 150% of estimate (3 hours max)

### Quality Checkpoints
- [ ] Start date defaults to Monday in 4th week
- [ ] Duration accepts only valid integer ranges (1-52)
- [ ] Date validation handles DD/MM/YY format correctly
- [ ] CLI prompts show helpful defaults and validation  
- [ ] Excel field population works for timing fields
- [ ] Existing Feature 003 functionality preserved
- [ ] Performance impact < 1 second additional time
- [ ] All edge cases handled with clear error messages

---
**Task Status**: Ready for Implementation  
**Created**: October 12, 2025  
**Implementation Approach**: Systematic phase-by-phase development  
**Quality Focus**: Robust validation and user experience