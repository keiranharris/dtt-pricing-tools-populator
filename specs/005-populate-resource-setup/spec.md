# Feature 005: Populate Resource Setup

## Overview
**Feature ID**: 005-populate-resource-setup  
**Dependencies**: Feature 002 (Excel Data Population), Feature 003 (CLI Population), Feature 004 (Start Date/Duration)  
**Status**: Specification Complete  
**Estimated Complexity**: Medium  

## Business Context
After populating the "Pricing Setup" tab with organizational data and user-specific information, users need to populate the "Resource Setup" tab with standardized resource configurations. This data includes pre-defined staff levels, roles, and resource templates that are consistent across pricing tools and stored in the constants file.

## Functional Requirements

### FR-001: Resource Setup Data Source
- **Source File**: Same constants file `lowcomplexity_const_KHv1.xlsx` in `/00-CONSTANTS/` directory
- **Source Tab**: "Resource Setup" worksheet in constants file
- **Source Range**: Dynamically detected 7×6 block of resource data (typically C28:H34 but may vary)
- **Data Type**: Structured resource information including staff levels, roles, and configurations

### FR-002: Target Population
- **Target File**: User's newly created pricing tool (.xlsb file)
- **Target Tab**: "Resource Setup" worksheet in target file  
- **Target Range**: Last 7 available editable rows in the worksheet (dynamic positioning)
- **Population Method**: Copy 7 rows of resource data to the bottom editable section
- **Positioning Logic**: Scan worksheet from bottom up to identify 7 consecutive unlocked/unprotected cells, avoiding merged cells and formula ranges

### FR-003: Data Integrity and Validation
- **Source Validation**: Verify source contains 7 rows of resource data in constants file
- **Target Validation**: Confirm "Resource Setup" tab exists in target file
- **Editable Area Detection**: Identify the last 7 editable rows in target worksheet (avoid locked areas)
- **Data Preservation**: Copy values while preserving any existing formatting in target cells
- **Overwrite Policy**: Silently overwrite existing data in target range without warning

### FR-004: Resource Data Structure
The resource data MUST include the following structured information in a 7×6 cell format:
- **Column A**: Staff Levels (Consultant, Director, Senior Manager, Manager, Senior Consultant, Associate, Admin)
- **Column B**: Role Assignments (specific role definitions and codes)
- **Column C**: Resource Configurations (hourly rates, utilization factors)
- **Column D**: Group Classifications (staff categorization identifiers)
- **Column E**: Project Allocation (default allocation percentages)
- **Column F**: Billing Categories (client-facing billing classifications)

### FR-005: Error Handling and Feedback
- **Missing Source**: Handle case where constants file doesn't have "Resource Setup" tab
- **Missing Target**: Handle case where target file doesn't have "Resource Setup" tab
- **Range Issues**: Validate that specified range exists and is accessible
- **Permission Errors**: Handle Excel file access issues gracefully
- **Success Feedback**: Confirm successful population with cell count and range information

## Technical Requirements

### TR-001: Excel Integration
- **Format Support**: Handle .xlsb files (binary Excel format) using existing Excel automation
- **Worksheet Access**: Access specific worksheets by name in both source and target files
- **Range Operations**: Perform cell range copying with exact positioning
- **Application Reuse**: Leverage existing Excel application instance from previous features

### TR-002: Integration with Existing Architecture
- **Module Extension**: Extend existing data population modules to support Resource Setup
- **Consistent Interface**: Follow same pattern as existing population functions
- **Error Handling**: Use established error handling patterns from previous features
- **Logging**: Provide consistent feedback messaging with existing population features

### TR-003: Configuration Management
- **Source Configuration**: Define source range detection for 7-row resource data block
- **Dynamic Positioning**: Implement logic to find last 7 editable rows in target worksheet
- **Tab Names**: Use configurable worksheet names for flexibility
- **Feature Toggle**: Allow Resource Setup population to be enabled/disabled
- **Backward Compatibility**: Ensure existing features continue to work unchanged

## Non-Functional Requirements

### NFR-001: Performance
- **Efficient Copying**: Copy entire range in single operation rather than cell-by-cell
- **Resource Management**: Minimize Excel application interactions for performance
- **Memory Usage**: Handle range copying efficiently without excessive memory consumption

### NFR-002: Reliability  
- **Robust Operation**: Handle edge cases like missing tabs or invalid ranges gracefully
- **Data Consistency**: Ensure copied data maintains integrity and structure
- **Rollback Safety**: Don't modify source constants file, only read from it

### NFR-003: Maintainability
- **Code Organization**: Follow established module structure and patterns
- **Documentation**: Include clear function documentation and examples
- **Testing Considerations**: Design for easy testing with mock Excel files

## Success Criteria

### Acceptance Criteria
1. **AC-001**: Resource Setup data (7 rows) is successfully copied from constants file
2. **AC-002**: Data appears in the last 7 available editable rows in target "Resource Setup" tab  
3. **AC-003**: All cell values are preserved exactly as they appear in source
4. **AC-004**: Operation integrates seamlessly with existing population workflow
5. **AC-005**: Clear success/failure feedback is provided to user
6. **AC-006**: Graceful error handling for missing tabs or ranges
7. **AC-007**: No impact on existing features (Pricing Setup population still works)

### Definition of Done
- [ ] Resource Setup population function implemented and tested
- [ ] Integration with existing data population orchestrator complete
- [ ] Error handling covers all identified edge cases  
- [ ] User feedback provides clear status information
- [ ] Code follows established patterns and conventions
- [ ] Feature works with both .xlsx and .xlsb file formats
- [ ] Documentation updated to reflect new capability

## Risk Assessment

### Technical Risks
- **Excel Compatibility**: Resource Setup tab structure may vary between file versions
- **Range Validity**: Source range C28:H34 may not always contain expected data structure
- **File Access**: Concurrent Excel operations may cause file locking issues

### Mitigation Strategies
- **Validation Checks**: Verify tab existence and range validity before attempting copy
- **Flexible Positioning**: Use relative range detection if absolute positioning fails
- **Error Recovery**: Provide clear error messages and continue with other operations if Resource Setup fails

## Implementation Notes

### Integration Points
- **Data Population Orchestrator**: Extend existing orchestrator to include Resource Setup step
- **Excel Utilities**: Leverage existing Excel automation utilities for worksheet and range operations
- **Configuration Constants**: Add new configuration constants for Resource Setup ranges and tab names

### Sequence in Workflow
1. Pricing Setup population (existing)
2. CLI field population (existing) 
3. Start date/duration population (existing)
4. **Resource Setup population (new)**
5. Final success reporting

This feature represents a natural progression in the pricing tool automation, moving from basic organizational data to structured resource configurations that form the foundation for accurate pricing calculations.