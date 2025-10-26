# Tasks: Shell Alias Auto-Setup for Easy Access

**Input**: Design documents from `/specs/008-implement-shell-alias/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/shell-alias-api.md ✅

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and core shell alias infrastructure

- [ ] T001 Create core data model classes in `src/shell_alias_manager.py`
  - ShellEnvironment, ShellAlias, AliasOperation dataclasses
  - AliasOperationType, ShellType, OperationResult enums  
  - Custom exception classes (ShellAliasError, UnsupportedShellError, AliasPermissionError)

- [ ] T002 [P] Add shell alias constants to `src/constants.py`
  - ALIAS_NAME = "priceup"
  - ALIAS_MARKERS = ("# DTT Pricing Tool - START (auto-generated)", "# DTT Pricing Tool - END")
  - TIMEOUT_SECONDS = 60
  - SUPPORTED_SHELLS = ["zsh"]

## Phase 2: Foundational Tasks (Blocking Prerequisites)

**Purpose**: Core utilities needed by all user stories

- [ ] T003 Implement shell detection utilities in `src/shell_alias_manager.py`
  - `detect_current_shell() -> str` using os.environ['SHELL'] and ps validation
  - `get_shell_config_path(shell_type: str) -> Path` for ~/.zshrc resolution
  - `validate_shell_environment(shell_type: str) -> ShellEnvironment`

- [ ] T004 Implement path resolution utilities in `src/shell_alias_manager.py`  
  - `resolve_script_path(script_path: Optional[Path]) -> Path` using pathlib.Path(__file__).resolve()
  - `escape_shell_command(command_path: Path) -> str` using shlex.quote()
  - `generate_alias_command(alias_name: str, script_path: Path) -> str`

- [ ] T005 Implement file manipulation utilities in `src/shell_alias_manager.py`
  - `read_shell_config(config_path: Path) -> str` with error handling
  - `write_shell_config_atomic(config_path: Path, content: str) -> None` with backup/rollback
  - `find_existing_alias_block(content: str, markers: Tuple[str, str]) -> Optional[str]`

## Phase 3: User Story 1 - First-Time Setup with Automatic Alias Creation (P1)

**Goal**: Developer clones repo, runs tool first time, gets automatic 'priceup' alias creation
**Independent Test**: Clone repo to clean directory, run once, verify alias works from any location

- [ ] T006 [US1] Implement alias validation logic in `src/shell_alias_manager.py`
  - `validate_existing_alias() -> AliasValidationResult`
  - Check if alias exists in shell config using markers
  - Compare existing alias command with expected command
  - Return validation result with exists/is_correct flags

- [ ] T007 [US1] Implement alias creation logic in `src/shell_alias_manager.py`
  - `_create_new_alias_block(alias_name: str, script_path: Path, markers: Tuple[str, str]) -> str`
  - Generate properly formatted alias block with comment markers
  - Handle shell escaping for paths with spaces/special characters

- [ ] T008 [US1] Implement main orchestration logic in `src/shell_alias_manager.py`
  - `ShellAliasManager.check_and_setup_alias() -> AliasOperationResult`
  - Shell detection and zsh validation
  - Existing alias check and creation decision
  - Success/failure result with user-facing messages

- [ ] T009 [US1] Add timeout protection to file operations in `src/shell_alias_manager.py`
  - Wrap file operations with 60-second timeout using signal.alarm()
  - Graceful timeout handling with TimeoutError exceptions
  - Cleanup on timeout (restore backup files)

- [ ] T010 [US1] Implement CLI integration hook in `pricing_tool_accelerator.py`
  - `setup_shell_alias_if_needed() -> bool` function
  - Add call at start of main() with exception handling
  - Log success/failure messages using existing logging system
  - Return True to continue main app, never raise exceptions

**Checkpoint US1**: First-time alias creation works end-to-end

## Phase 4: User Story 2 - Subsequent Usage with Existing Alias (P1)

**Goal**: User with existing correct alias gets silent operation, no duplicate setup
**Independent Test**: Run tool with existing correct alias, verify no setup messages and normal operation

- [ ] T011 [US2] Implement silent operation for existing correct aliases in `src/shell_alias_manager.py`
  - Modify `check_and_setup_alias()` to return silent success for correct existing aliases
  - Ensure no user messages when alias already exists and is correct
  - Skip all file operations when alias validation passes

- [ ] T012 [US2] Add idempotency validation in `src/shell_alias_manager.py`
  - `_is_alias_current(existing_command: str, expected_command: str) -> bool`
  - Ensure multiple runs don't create duplicate entries
  - Handle whitespace and formatting variations in comparison

**Checkpoint US2**: Existing alias detection and silent operation works

## Phase 5: User Story 3 - Cross-Team Repository Location Flexibility (P2)

**Goal**: Team members in different directories get location-specific aliases automatically  
**Independent Test**: Clone to various paths, verify each gets correct absolute path in alias

- [ ] T013 [US3] Implement alias update logic for moved repositories in `src/shell_alias_manager.py`
  - Detect when existing alias points to different/invalid path
  - `_update_existing_alias_block(content: str, new_command: str, markers: Tuple[str, str]) -> str`
  - Replace old alias block with updated path, preserve other config

- [ ] T014 [US3] Add path validation and correction in `src/shell_alias_manager.py`
  - `_validate_script_path_exists(script_path: Path) -> bool`
  - Handle case where alias exists but script moved/deleted
  - Generate appropriate user messages for path corrections

- [ ] T015 [US3] Implement special character handling in `src/shell_alias_manager.py`
  - Comprehensive testing of shlex.quote() for edge cases
  - Handle paths with spaces, unicode, special shell characters
  - Validate generated aliases work in actual shell environment

**Checkpoint US3**: Repository location flexibility and path updating works

## Phase 6: User Story 4 - Git-Unfamiliar User First-Time Setup (P1)

**Goal**: Non-technical users can follow README to successfully download and set up tool
**Independent Test**: Follow README instructions on fresh machine without git experience

- [ ] T016 [US4] Create comprehensive git instructions in `README.md`
  - "Getting Started" section with git explanation for beginners
  - Step-by-step git clone instructions with copy-paste commands
  - Terminal opening and navigation instructions for non-technical users

- [ ] T017 [US4] Add first-time setup section in `README.md`  
  - Clear instructions for initial tool run and alias creation
  - Expected success messages and next steps
  - Screenshots or examples of successful setup (optional)

- [ ] T018 [US4] Add troubleshooting section in `README.md`
  - Common error scenarios (wrong shell, permission denied, git not installed)
  - Manual alias setup instructions for fallback cases
  - Clear error message explanations and solutions

- [ ] T019 [US4] Add alternative download methods in `README.md`
  - ZIP download instructions for users who can't/won't use git
  - Explain differences and limitations compared to git clone
  - Update instructions for ZIP-based installations

**Checkpoint US4**: Complete documentation enables non-technical user success

## Phase 7: Error Handling & Edge Cases

**Purpose**: Comprehensive error handling for all edge cases identified in spec

- [ ] T020 [P] Implement unsupported shell error handling in `src/shell_alias_manager.py`
  - Clear error messages for non-zsh shells (bash, fish, etc.)
  - Instructions for switching to zsh when detected
  - Graceful failure that doesn't block main application

- [ ] T021 [P] Implement permission error handling in `src/shell_alias_manager.py`
  - Handle ~/.zshrc not writable scenarios  
  - Generate manual setup instructions in error messages
  - Test with read-only home directory scenarios

- [ ] T022 [P] Add comprehensive logging integration in `src/shell_alias_manager.py`
  - Use existing `src/logging_config.py` patterns
  - INFO level for successful alias creation
  - WARNING level for non-critical issues (wrong path, already exists)
  - ERROR level for critical failures with fallback instructions

- [ ] T023 [P] Implement `get_manual_setup_instructions()` in `src/shell_alias_manager.py`
  - Generate shell commands for manual alias creation
  - Include current script path and proper escaping
  - Format as copy-paste ready commands for users

## Phase 8: Testing Suite (Optional - Not explicitly requested in spec)

**Note**: Tests not explicitly requested in feature specification, but included for comprehensive validation

- [ ] T024 [P] Create unit test suite in `tests/test_shell_alias_manager.py`
  - Test shell detection with mocked environment variables
  - Test path resolution with various script locations  
  - Test file manipulation with temporary directories
  - Test all error scenarios with appropriate mocks

- [ ] T025 [P] Create integration test suite in `tests/test_shell_alias_integration.py`
  - End-to-end workflow tests with real temporary directories
  - Test CLI integration with main application
  - Test alias functionality in actual shell environment
  - Performance validation (timeout testing)

- [ ] T026 [P] Add CLI integration tests in `tests/test_cli_integration.py`
  - Modify existing test to include alias setup verification
  - Test main application continues normally after alias setup
  - Test error handling doesn't crash main application

## Dependencies & Execution Order

### User Story Dependencies
- **US1 (First-Time Setup)**: Foundational → US1 (independent)
- **US2 (Existing Alias)**: US1 → US2 (extends US1 validation logic)  
- **US3 (Repository Flexibility)**: US1 → US3 (extends US1 with update logic)
- **US4 (Git-Unfamiliar Users)**: US1 → US4 (documents US1 functionality)

### Parallel Execution Opportunities

#### Phase 1-2 (Foundations): All tasks sequential (same file)
#### Phase 3 (US1): 
- T006, T007 can run in parallel (different functions)
- T008 depends on T006, T007 completion
- T009, T010 can run in parallel after T008

#### Phase 4 (US2): Can run in parallel with Phase 5 (US3) - different logic areas

#### Phase 6 (US4): All documentation tasks can run in parallel with code tasks

#### Phase 7 (Error Handling): All tasks marked [P] can run in parallel

## Implementation Strategy

### MVP Scope (Minimal Viable Product)
**Recommended MVP**: User Story 1 only
- Core alias creation functionality
- Basic error handling
- CLI integration
- **Deliverable**: Working automatic alias creation on first run

### Incremental Delivery
1. **MVP Release**: US1 (First-time alias creation)
2. **Enhancement 1**: US2 (Silent operation for existing aliases) 
3. **Enhancement 2**: US3 (Repository location flexibility)
4. **Documentation Release**: US4 (Git-unfamiliar user support)
5. **Polish Release**: Comprehensive error handling and testing

### Risk Mitigation
- **Shell Detection**: Test early on various macOS versions
- **File Operations**: Validate atomic write/backup logic thoroughly
- **Path Escaping**: Test with comprehensive special character scenarios
- **CLI Integration**: Ensure main application never crashes due to alias setup

## Summary

**Total Tasks**: 26 (23 implementation + 3 optional testing)
**User Story Breakdown**:
- Setup & Foundations: 5 tasks
- US1 (First-Time Setup): 5 tasks  
- US2 (Existing Alias): 2 tasks
- US3 (Repository Flexibility): 3 tasks
- US4 (Git-Unfamiliar Users): 4 tasks
- Error Handling: 4 tasks
- Testing (Optional): 3 tasks

**Parallel Opportunities**: 12 tasks marked [P] can run concurrently  
**Independent Testing**: Each user story has clear acceptance criteria  
**MVP Timeline**: ~4-6 hours for US1 implementation (Tasks T001-T010)
**Full Feature Timeline**: ~8-12 hours for complete implementation