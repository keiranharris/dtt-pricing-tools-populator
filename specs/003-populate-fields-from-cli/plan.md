# Feature 003: Populate Fields from CLI - Implementation Plan

## Overview
**Implementation Strategy**: Extend existing Feature 002 infrastructure to include CLI-collected user inputs  
**Total Estimated Time**: 2 hours  
**Implementation Phases**: 4 phases with clear dependencies  

## Architecture Decision

### Integration Approach: Extend Feature 002
Rather than creating new modules, we'll extend the existing proven Feature 002 data population infrastructure:

- **Data Flow**: CLI Input → Data Merging → Field Matching → Population
- **Reuse**: Leverage existing fuzzy matching, Excel writing, and error handling
- **Minimal Risk**: Additive changes that don't break existing functionality

### Key Design Decisions

#### Decision 1: Data Merging Strategy
- **Approach**: Merge CLI data with constants file data before field matching
- **Precedence**: CLI values override constants file values for same field names
- **Location**: Add merging step in `data_population_orchestrator.py`

#### Decision 2: CLI Interface Updates
- **Change**: Update prompts from "Gig Name" → "Opportunity Name"  
- **Maintain**: Keep existing sanitization and validation logic
- **Location**: Modify `cli_interface.py`

#### Decision 3: Field Matching Integration
- **Reuse**: Existing fuzzy matching algorithm handles CLI fields automatically
- **No Changes**: Field matcher doesn't need updates - it processes merged data
- **Benefit**: Consistent matching behavior across all data sources

## Implementation Phases

### Phase 1: CLI Interface Updates
**Duration**: 30 minutes  
**Priority**: High  
**Dependencies**: None  

**Objectives**:
- Update CLI prompts to use correct terminology
- Maintain backward compatibility in data structures
- Preserve existing input validation

**Tasks**:
1. **Update Prompts** (10 min)
   - Change "Gig Name" → "Opportunity Name" in user-facing text
   - Maintain "Client Name" prompt (already correct)

2. **Verify Data Flow** (10 min)
   - Ensure sanitized inputs are properly returned
   - Validate existing input cleaning continues to work

3. **Test CLI Changes** (10 min)
   - Run manual tests with various input scenarios
   - Verify special character handling still works

**Deliverables**:
- Updated `cli_interface.py` with correct prompts
- Verified input collection functionality

### Phase 2: Data Integration Logic  
**Duration**: 45 minutes  
**Priority**: High  
**Dependencies**: Phase 1 complete  

**Objectives**:
- Create CLI data to constants data merging capability
- Implement precedence rules (CLI overwrites constants)
- Add comprehensive error handling and logging

**Tasks**:
1. **Create Data Merge Function** (25 min)
   - Function to combine CLI inputs with constants file data
   - Handle field name normalization and conflicts
   - Add logging for merge operations and precedence decisions

2. **Add Precedence Logic** (10 min)
   - CLI values take priority over constants file values
   - Clear logging when CLI values override constants
   - Preserve non-conflicting constants file data

3. **Error Handling** (10 min)
   - Handle empty or invalid CLI inputs gracefully
   - Manage scenarios where constants file is missing
   - Ensure robust operation with partial data

**Deliverables**:
- New data merging function with precedence handling
- Comprehensive error handling and logging
- Unit-testable merge logic

### Phase 3: Integration & Testing
**Duration**: 30 minutes  
**Priority**: High  
**Dependencies**: Phase 2 complete  

**Objectives**:
- Integrate CLI data merging into existing orchestrator workflow
- Validate end-to-end functionality with real Excel templates
- Ensure no regression in existing Feature 002 behavior

**Tasks**:
1. **Orchestrator Integration** (15 min)
   - Add CLI data merging step before field matching
   - Pass merged data to existing field matching logic
   - Maintain existing error handling patterns

2. **End-to-End Testing** (15 min)
   - Test with multiple Excel template configurations
   - Verify CLI fields are found and populated correctly
   - Confirm constants file population continues unchanged
   - Test precedence scenarios (CLI overwrites constants)

**Deliverables**:
- Integrated CLI data flow in orchestrator
- Verified end-to-end functionality
- No regressions in existing features

### Phase 4: Documentation & Cleanup
**Duration**: 15 minutes  
**Priority**: Medium  
**Dependencies**: Phase 3 complete  

**Objectives**:
- Update code documentation and comments
- Clean up any debug code or temporary implementations
- Verify all edge cases are properly handled

**Tasks**:
1. **Documentation Updates** (10 min)
   - Update function docstrings for modified functions
   - Add comments explaining CLI data integration
   - Update any architectural documentation

2. **Code Cleanup** (5 min)
   - Remove any debug logging not needed for production
   - Verify code style consistency
   - Final edge case validation

**Deliverables**:
- Updated documentation and comments
- Clean, production-ready code
- Verified edge case handling

## Technical Implementation Details

### CLI Interface Changes
**File**: `cli_interface.py`
**Function**: `collect_user_inputs()`

**Current Implementation**:
```python
def collect_user_inputs():
    client_name = input("Enter Client Name: ")
    gig_name = input("Enter Gig Name: ")
    return sanitize_user_input(client_name), sanitize_user_input(gig_name)
```

**Proposed Implementation**:
```python
def collect_user_inputs():
    client_name = input("Enter Client Name: ")
    opportunity_name = input("Enter Opportunity Name: ")
    return sanitize_user_input(client_name), sanitize_user_input(opportunity_name)
```

### Data Merging Logic
**File**: `data_population_orchestrator.py`
**New Function**: `merge_cli_with_constants()`

**Proposed Signature**:
```python
def merge_cli_with_constants(cli_client_name: str, cli_opportunity_name: str, 
                           constants_data: Dict[str, str]) -> Dict[str, str]:
    """Merge CLI inputs with constants file data, giving CLI precedence."""
```

**Merge Strategy**:
1. Start with constants file data as base
2. Add/override with CLI data:
   - "Client Name" → `cli_client_name`
   - "Opportunity Name" → `cli_opportunity_name`
3. Log any overrides for transparency
4. Return merged dictionary

### Integration Point
**File**: `data_population_orchestrator.py`
**Function**: `populate_spreadsheet_data()`

**Integration Location**: After constants loading, before field matching
```python
# Step 1: Read constants data (existing)
constants_data = read_constants_data(constants_dir, constants_filename)

# Step 1.5: Merge CLI data (NEW)
merged_data = merge_cli_with_constants(client_name, opportunity_name, constants_data)

# Step 2: Find matching fields (existing, but uses merged_data)
matches = find_matching_fields(merged_data, worksheet, threshold)
```

## Risk Mitigation

### Technical Risks
1. **Integration Complexity**: Minimize changes to existing proven code
2. **Data Conflicts**: Clear precedence rules and logging
3. **Performance Impact**: Lightweight merge operation, minimal overhead

### Testing Strategy
1. **Unit Tests**: Test merge function in isolation
2. **Integration Tests**: Full workflow with various Excel templates
3. **Regression Tests**: Ensure Feature 002 continues working unchanged
4. **Edge Case Tests**: Empty inputs, missing fields, conflicting data

### Rollback Plan
- Changes are additive and can be easily disabled
- CLI interface changes are non-breaking (just prompt text)
- Data merge step can be bypassed if needed

## Success Metrics

### Functional Metrics
- CLI fields successfully populated in Excel (target: 100% when fields exist)
- Constants file population unchanged (target: no regression)
- Field matching accuracy maintained (target: same as Feature 002)

### Performance Metrics
- CLI data integration overhead < 2 seconds
- Total workflow time increase < 10%
- Memory usage impact < 5MB

### Quality Metrics
- Zero regressions in existing Feature 002 functionality
- Comprehensive error handling for all edge cases
- Clear user feedback for unpopulated CLI fields

---
**Plan Status**: Ready for Implementation  
**Created**: October 12, 2025  
**Next Step**: Begin Phase 1 - CLI Interface Updates