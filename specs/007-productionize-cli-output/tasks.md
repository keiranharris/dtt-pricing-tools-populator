# Tasks: Productionize CLI Output with Verbose Logging Toggle

**Input**: Design documents from `/specs/007-productionize-cli-output/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and logging infrastructure foundation

- [x] T001 Add global configuration constant `VERBOSE_LOGGING_ENABLED = False` to pricing_tool_accelerator.py
- [x] T002 [P] Create new logging configuration module src/logging_config.py with core interfaces
- [x] T003 [P] Create MessageCategory enum and LoggingConfig dataclass in src/logging_config.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core logging infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Implement `configure_logging()` function in src/logging_config.py
- [x] T005 [P] Implement `categorize_message()` function in src/logging_config.py
- [x] T006 [P] Implement `should_display_message()` function in src/logging_config.py
- [x] T007 Create `ProductionOutputHandler` custom logging handler class in src/logging_config.py
- [x] T008 Replace `logging.basicConfig()` in src/system_integration.py with production logging setup
- [x] T009 [P] Create unit tests for logging configuration in tests/test_logging_config.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Clean Production CLI Output (Priority: P1) 🎯 MVP

**Goal**: Implement clean production CLI output that shows only essential prompts and status messages

**Independent Test**: Run CLI tool with verbose logging disabled and verify only user prompts and operation status appear (no technical details)

### Implementation for User Story 1

- [x] T010 [P] [US1] Update logging calls in src/data_population_orchestrator.py to use message categorization
- [x] T011 [P] [US1] Classify all logger.info() calls in src/excel_data_populator.py as TECHNICAL_DIAGNOSTIC
- [x] T012 [P] [US1] Classify all logger.info() calls in src/field_matcher.py as TECHNICAL_DIAGNOSTIC  
- [x] T013 [P] [US1] Add operation status messages (OPERATION_STATUS category) to major operations in src/data_population_orchestrator.py
- [x] T014 [US1] Initialize production logging in pricing_tool_accelerator.py main() function
- [x] T015 [US1] Ensure all existing print() statements remain unchanged (ESSENTIAL_USER category)
- [x] T016 [US1] Verify error and warning messages always display regardless of verbose setting

**Checkpoint**: At this point, User Story 1 should be fully functional with clean production output

---

## Phase 4: User Story 2 - Developer Debug Mode Toggle (Priority: P2)

**Goal**: Enable developers to toggle verbose logging to see full technical diagnostics

**Independent Test**: Toggle verbose logging on and verify all current detailed logging information displays

### Implementation for User Story 2

- [x] T017 [P] [US2] Implement `toggle_verbose_logging()` function in src/logging_config.py
- [x] T018 [P] [US2] Implement `is_verbose_enabled()` function in src/logging_config.py
- [x] T019 [US2] Add runtime configuration update to `ProductionOutputHandler.update_verbose_setting()` 
- [x] T020 [P] [US2] Ensure all existing technical logging displays when verbose mode enabled
- [x] T021 [US2] Test configuration change takes effect within 1 second (meets SC-004)
- [x] T022 [P] [US2] Add integration tests in tests/test_cli_integration.py for verbose mode

**Checkpoint**: Verbose mode toggle working, full backward compatibility with existing detailed logging

---

## Phase 5: User Story 3 - Operation Status Visibility (Priority: P3)

**Goal**: Provide clear progress indicators for major operations in both logging modes

**Independent Test**: Run operations and verify status messages appear at key milestones regardless of verbose setting

### Implementation for User Story 3

- [x] T023 [P] [US3] Add operation start messages to file copying in src/file_operations.py
- [x] T024 [P] [US3] Add operation completion messages to data population in src/data_population_orchestrator.py
- [x] T025 [P] [US3] Add operation status messages to resource setup in src/resource_setup_populator.py
- [x] T026 [P] [US3] Add operation status messages to rate card integration in src/excel_rate_integration.py
- [x] T027 [US3] Ensure status messages display in both verbose and production modes
- [x] T028 [P] [US3] Add progress indicators for long-running operations (data population, file copying)

**Checkpoint**: Clear operation visibility in all modes, enhanced user confidence

---

## Phase 6: Integration & Polish

**Purpose**: Cross-cutting concerns, final validation, and polish

- [x] T029 [P] Validate 80% log line reduction in production mode (meets SC-001)
- [x] T030 [P] Verify all existing workflows complete without loss of critical information (meets SC-002)
- [x] T031 [P] Confirm all current diagnostic information available in verbose mode (meets SC-003) 
- [x] T032 [P] Test configuration change performance meets <1 second requirement (meets SC-004)
- [x] T033 [P] Verify operation status messages display for all major operations (meets SC-005)
- [x] T034 Run full test suite to ensure backward compatibility
- [x] T035 [P] Update any existing tests that may be affected by logging changes
- [x] T036 [P] Add error handling for logging configuration failures
- [x] T037 Document configuration pattern in code comments

---

## Dependencies

### User Story Completion Order
```
Phase 1 (Setup) → Phase 2 (Foundation) → {
  Phase 3 (US1) - Can be implemented independently
  Phase 4 (US2) - Can be implemented independently  
  Phase 5 (US3) - Can be implemented independently
} → Phase 6 (Integration)
```

### Task Dependencies Within Stories
- **US1**: T014 depends on T010-T013 completion
- **US2**: T019 depends on T017-T018, T021 depends on T019
- **US3**: T027 depends on T023-T026 completion

---

## Parallel Execution Examples

### After Foundation Phase (Phases 1-2 complete):
```bash
# User Story 1 - Production Output (Independent team/developer)
T010, T011, T012 (parallel) → T013 (parallel) → T014 → T015, T016 (parallel)

# User Story 2 - Debug Toggle (Independent team/developer)  
T017, T018 (parallel) → T019 → T020, T022 (parallel) → T021

# User Story 3 - Status Visibility (Independent team/developer)
T023, T024, T025, T026 (all parallel) → T027 → T028 (parallel)
```

### Integration Phase:
```bash
T029, T030, T031, T032, T033 (all parallel) → T034 → T035, T036, T037 (parallel)
```

---

## Implementation Strategy

### MVP Delivery (Phase 3 only)
- **Scope**: Clean production CLI output (User Story 1)
- **Value**: Immediate production-ready experience 
- **Testable**: Complete workflow with clean output
- **Time**: ~25 minutes of focused development

### Full Feature (All Phases)
- **Scope**: Complete logging system with toggle and status visibility
- **Value**: Production experience + developer tooling + enhanced UX
- **Testable**: All success criteria met, backward compatibility maintained
- **Time**: ~60 minutes total development time

### Risk Mitigation
- Each user story independently testable
- Existing functionality preserved throughout
- Rollback possible at any checkpoint by reverting configuration constant