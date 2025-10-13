# Feature Specification: Populate Rate Card at Given Margin

**Feature Branch**: `006-populate-rate`  
**Created**: 2025-10-13  
**Status**: Draft  
**Input**: User description: "006-populate-rate-card-at-given-margin - ok, i need to ask for another field at execution time from the CLI. Its 'Client Margin %:' and needs to be a whole number between 35 and 65 (reject all others and loop around to ask again). When you have this number, we will use it in a formula to populate the rates in our rate card. It is importnt this step happens after the feature-005 code as it relies on those resources being in the sheet. For this step, we are filling out the 'Eng Rate $ (excl GST)*' column, per each of the 7 staff levels on the rate card from the previous feature. This column is 'O' and the 7 levels are O28 -> O34. The formula for each row is: = 'FY 26 Std Cost Rate' / (1 - 'Client Margin %') noting that - 'FY 26 Std Cost Rate' = column 'Q' - 'Client Margin %' is what the user entered at the CLI converted to a 2 decimal place bewteen 0 and 1 (e.g. 44% is 0.44)"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - CLI Margin Input Collection (Priority: P1)

The user provides their desired client margin percentage through an interactive command-line prompt. The system validates the input and ensures it falls within acceptable business parameters before proceeding.

**Why this priority**: This is the foundational input required for all rate calculations. Without valid margin input, no rate card population can occur.

**Independent Test**: Can be fully tested by running the CLI prompt, entering various margin values (valid and invalid), and verifying proper validation behavior and data collection.

**Acceptance Scenarios**:

1. **Given** the user is prompted for "Client Margin %:", **When** they enter a valid whole number between 35-65, **Then** the system accepts the input and proceeds to rate calculation
2. **Given** the user enters an invalid margin (below 35, above 65, or non-whole number), **When** the validation runs, **Then** the system displays an error message and re-prompts for input
3. **Given** the user enters non-numeric input, **When** the validation runs, **Then** the system displays an appropriate error message and re-prompts for input

---

### User Story 2 - Automated Rate Card Calculation (Priority: P2)

The system automatically calculates engineering rates for all seven staff levels using the provided margin percentage and existing standard cost rates, applying the formula consistently across all positions.

**Why this priority**: This delivers the core business value by automating complex rate calculations that would otherwise require manual Excel formula entry for each staff level.

**Independent Test**: Can be tested by providing a known margin percentage and verifying that the calculated rates in column O (O28-O34) match expected mathematical results based on the formula.

**Acceptance Scenarios**:

1. **Given** a valid client margin of 40% and existing standard cost rates in column Q, **When** the rate calculation executes, **Then** each cell O28-O34 contains the correct calculated rate using the formula
2. **Given** the Resource Setup data exists from Feature 005, **When** rate calculation runs, **Then** all seven staff levels receive appropriate rate calculations
3. **Given** the calculation completes successfully, **When** the user opens the spreadsheet, **Then** the "Eng Rate $ (excl GST)*" column displays properly formatted currency values

---

### User Story 3 - Integrated Workflow Execution (Priority: P3)

The rate card population integrates seamlessly into the existing pricing tool workflow, executing after resource setup completion and maintaining the established user experience pattern.

**Why this priority**: Ensures the feature works cohesively with the existing automation system rather than as an isolated component.

**Independent Test**: Can be tested by running the complete workflow from file copy through rate card population, verifying proper sequencing and data dependencies.

**Acceptance Scenarios**:

1. **Given** Features 001-005 have completed successfully, **When** Feature 006 executes, **Then** rate card population occurs without errors and produces expected results
2. **Given** the integrated workflow completes, **When** the user reviews the final spreadsheet, **Then** all previous data remains intact and rate card shows calculated values

### Edge Cases

- What happens when Feature 005 Resource Setup data is missing or incomplete?
- How does the system handle extremely high or low standard cost rates that might produce unrealistic calculated rates?
- What occurs if column Q (standard cost rates) contains non-numeric data or formulas instead of values?
- How does the system respond when the target column O already contains data or formulas?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST prompt user for "Client Margin %:" during CLI execution
- **FR-002**: System MUST validate margin input as whole number between 35 and 65 inclusive
- **FR-003**: System MUST reject invalid margin inputs and re-prompt until valid input received
- **FR-004**: System MUST convert margin percentage to decimal format (e.g., 44% becomes 0.44) for calculations
- **FR-005**: System MUST calculate engineering rates using formula: Standard Cost Rate / (1 - Client Margin %)
- **FR-006**: System MUST populate cells O28 through O34 with calculated rates for all seven staff levels
- **FR-007**: System MUST execute after Feature 005 Resource Setup completion to ensure data dependencies
- **FR-008**: System MUST read standard cost rates from column Q (Q28-Q34) for calculation inputs
- **FR-009**: System MUST preserve existing spreadsheet data and formatting while adding rate calculations
- **FR-010**: System MUST provide clear feedback on successful rate card population completion

### Key Entities *(include if feature involves data)*

- **Client Margin**: User-provided percentage value (35-65) representing desired profit margin for client billing
- **Standard Cost Rate**: Existing cost basis values stored in column Q for each staff level
- **Engineering Rate**: Calculated billing rate stored in column O, derived from cost rate and margin
- **Staff Level**: Seven organizational levels (rows 28-34) requiring individual rate calculations
- **Rate Card**: Collection of calculated engineering rates for all staff levels in the pricing tool

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can input client margin percentage in under 30 seconds with clear validation feedback
- **SC-002**: System calculates and populates all seven engineering rates in under 5 seconds
- **SC-003**: Rate calculations are mathematically accurate to 2 decimal places for currency formatting
- **SC-004**: 100% of valid margin inputs (35-65) result in successful rate card population
- **SC-005**: Invalid margin inputs are rejected with clear error messages and re-prompt functionality
- **SC-006**: Feature integrates seamlessly with existing workflow without disrupting previous automation steps

## Assumptions

- Feature 005 Resource Setup has been completed and populated the necessary staff level data
- Column Q contains valid numeric standard cost rate data for all seven staff levels (Q28-Q34)
- Column O is available for rate population and not protected or containing critical existing formulas
- Standard cost rates represent annual or hourly costs that can be directly used in margin calculations
- The pricing spreadsheet follows the established structure with consistent row positioning for staff levels

## Dependencies

- **Feature 005**: Resource Setup must be completed to ensure staff level data exists in the spreadsheet
- **Existing CLI Infrastructure**: Utilizes established command-line interface patterns for user input
- **Excel Integration**: Leverages existing xlwings Excel automation for cell manipulation and data access
