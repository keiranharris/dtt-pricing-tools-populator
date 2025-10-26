# Tasks: Populate Rate Card at Given Margin

**Input**: Design documents from `/specs/006-populate-rate/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions
- **Single project**: `src/`, `tests/` at repository root
- Paths follow existing codebase structure

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create new module files per implementation plan structure
- [x] T002 [P] Set up development environment validation for Feature 006
- [x] T003 [P] Configure testing framework for new rate calculation modules

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Create base margin validator module with core validation logic in `src/margin_validator.py`
- [x] T005 Create base rate card calculator module structure in `src/rate_card_calculator.py`
- [x] T006 [P] Set up Excel integration utilities for reading column Q and writing column O
- [x] T007 [P] Create error handling framework for invalid cost rate data scenarios
- [x] T008 Establish data model classes (ClientMargin, StandardCostRate, EngineeringRate) in appropriate modules

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - CLI Margin Input Collection (Priority: P1) 🎯 MVP

**Goal**: Enable users to provide client margin percentage (35-65%) via CLI with proper validation

**Independent Test**: Run CLI prompt, test valid/invalid inputs, verify validation behavior

- [x] T009 [US1] Implement `collect_margin_percentage()` function in `src/cli_interface.py`
- [x] T010 [US1] Implement `validate_margin_input()` function in `src/margin_validator.py`
- [x] T011 [US1] Implement `convert_margin_to_decimal()` function in `src/margin_validator.py`
- [x] T012 [US1] Add margin percentage prompt to main CLI workflow in `pricing_tool_accelerator.py`
- [x] T013 [US1] Implement input validation loop with error messages and re-prompting
- [x] T014 [US1] [P] Create unit tests for margin validation logic in `tests/test_margin_validator.py`
- [x] T015 [US1] [P] Create integration tests for CLI margin collection in `tests/test_cli_interface.py`

**Checkpoint**: User Story 1 Complete - CLI can collect and validate margin input independently

---

## Phase 4: User Story 2 - Automated Rate Card Calculation (Priority: P2)

**Goal**: Calculate engineering rates for all seven staff levels using margin and standard cost rates

**Independent Test**: Provide known margin and cost rates, verify calculated rates match formula results

- [x] T016 [US2] Implement `read_standard_cost_rates()` function in `src/rate_card_calculator.py`
- [x] T017 [US2] Implement `calculate_engineering_rates()` function with formula logic
- [x] T017.1 [US2] Add whole-integer rounding logic to rate calculations (no cents)
- [x] T018 [US2] Implement `write_engineering_rates()` function for Excel column O population
- [x] T019 [US2] Add invalid cost rate handling (skip cells, report skipped items)
- [x] T020 [US2] Implement currency formatting for whole-number rate values
- [x] T021 [US2] Add data overwrite logic for existing column O data
- [x] T022 [US2] [P] Create unit tests for rate calculation logic in `tests/test_rate_card_calculator.py`
- [x] T023 [US2] [P] Create tests for Excel integration (reading Q, writing O) 
- [x] T024 [US2] Add error handling for Excel access issues and missing worksheet scenarios

**Checkpoint**: User Story 2 Complete - Rate calculation works independently with test data

---

## Phase 5: User Story 3 - Integrated Workflow Execution (Priority: P3)

**Goal**: Integrate rate card population into existing pricing tool workflow seamlessly

**Independent Test**: Run complete workflow from file copy through rate calculation, verify all data intact

- [ ] T025 [US3] Extend `data_population_orchestrator.py` to include rate card calculation step
- [ ] T026 [US3] Implement workflow integration after Feature 005 Resource Setup completion
- [ ] T027 [US3] Add rate card calculation to main workflow sequence in `pricing_tool_accelerator.py`
- [ ] T028 [US3] Implement dependency validation (ensure Feature 005 data exists)
- [ ] T029 [US3] Add progress feedback for rate calculation step
- [ ] T030 [US3] [P] Create end-to-end integration tests for complete workflow
- [ ] T031 [US3] [P] Test backward compatibility with existing Features 001-005
- [ ] T032 [US3] Add final success reporting with rate card population confirmation

**Checkpoint**: User Story 3 Complete - Full workflow integration with rate card calculation

---

## Phase 6: Excel Session Consolidation ✅ COMPLETED

**Purpose**: Optimize Excel operations to use single session instead of multiple open/close cycles

- [x] T033.1 Implement ExcelSessionManager for single session management
- [x] T033.2 Create consolidated_data_population function
- [x] T033.3 Integrate consolidated approach into data_population_orchestrator
- [x] T033.4 Update main application to use consolidated approach with fallback
- [x] T033.5 Create test script to validate consolidated session functionality

**Checkpoint**: Excel Session Consolidation Complete - Single session eliminates 6+ permission dialogs

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final integration, documentation, and quality assurance

- [x] T034 [P] Add comprehensive error logging for rate calculation failures
- [x] T035 [P] Performance optimization for Excel operations (consolidated session approach)
- [ ] T036 [P] Add configuration options for margin range limits (if needed)
- [x] T037 Create comprehensive integration test covering all edge cases
- [x] T038 Final validation: Complete workflow test with real pricing tool files
- [x] T039 [P] Update project documentation with Feature 006 capabilities
- [x] T040 Code review and refactoring for consistency with existing codebase

---

## Dependencies & Execution Strategy

### User Story Dependencies
1. **US1 (CLI Input)**: No dependencies - can implement first as MVP
2. **US2 (Rate Calculation)**: Independent of US1 (can use mock margin data for testing)
3. **US3 (Integration)**: Depends on US1 + US2 being complete

### Parallel Execution Opportunities
- **Within US1**: Tests (T014, T015) can run parallel to implementation
- **Within US2**: Tests (T022, T023) can run parallel to core implementation
- **Within US3**: Tests (T030, T031) can run parallel to integration work
- **Cross-cutting**: Polish tasks (T033-T040) can mostly run in parallel

### MVP Delivery Strategy
**Minimal Viable Product**: Complete US1 only
- Delivers margin input collection and validation
- Can be tested and demonstrated independently
- Provides foundation for US2 development

**Full Feature**: US1 + US2 + US3
- Complete rate card automation
- Integrated workflow experience
- Production ready

### Implementation Notes
- All tasks include specific file paths for clarity
- Tests are integrated throughout but not blocking (optional approach)
- Excel operations are isolated to specific modules for maintainability
- Error handling is distributed across modules following atomic function principles
- Each user story delivers independent value and can be deployed separately