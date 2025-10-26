# Implementation Tasks: Spreadsheet Copy and Instantiation

**Feature**: `001-spreadsheet-copy`  
**Branch**: `001-spreadsheet-copy`  
**Date**: 2025-10-12  
**Based on**: [plan.md](./plan.md)

## Task Overview

This document breaks down the implementation plan into specific, actionable tasks that can be completed incrementally. Each task is designed to be atomic, testable, and builds upon previous tasks.

## Phase 0: Research & Foundation

### Task 0.1: Validate File Operations Strategy ✅ COMPLETED
**Estimated Time**: 15 minutes  
**Priority**: Critical  
**Dependencies**: None

**Objective**: Research and validate Python file operation approaches for .xlsb files

**Actions**:
- [x] Research `shutil.copy2` vs `shutil.copy` for preserving file metadata
- [x] Test file copy operations with sample .xlsb files 
- [x] Validate that copied .xlsb files maintain integrity and can be opened
- [x] Document findings in research notes

**Acceptance Criteria**:
- ✅ File copy preserves all metadata (timestamps, permissions)
- ✅ Copied .xlsb files open correctly in Excel
- ✅ No file corruption during copy operation

**Completion Notes**: `shutil.copy2` successfully preserves metadata. File integrity verified by size comparison. Extended attributes removal added to prevent read-only warnings.

### Task 0.2: Design Version Extraction Regex ✅ COMPLETED
**Estimated Time**: 15 minutes  
**Priority**: Critical  
**Dependencies**: None

**Objective**: Create and test regex pattern for extracting version numbers from filenames

**Actions**:
- [x] Design regex pattern to match "v1.2", "v1.3", etc. from filenames
- [x] Test pattern against current filename: "FY26 Low Complexity Pricing Tool v1.2.xlsb"
- [x] Handle edge cases: missing version, malformed version, multiple versions
- [x] Create fallback strategy for unparseable versions

**Acceptance Criteria**:
- ✅ Regex correctly extracts "1.2" from "v1.2" 
- ✅ Handles edge cases gracefully with clear error messages
- ✅ Performance is acceptable for single file processing

**Completion Notes**: Regex pattern `r'v(\d+\.\d+)'` successfully extracts versions. Comprehensive edge case testing completed. ValueError raised for unparseable filenames with descriptive messages.

### Task 0.3: Research macOS Finder Integration ✅ COMPLETED
**Estimated Time**: 10 minutes  
**Priority**: High  
**Dependencies**: None

**Objective**: Validate `open -R` command for selecting files in Finder

**Actions**:
- [x] Test `subprocess.run(["open", "-R", file_path])` on macOS
- [x] Verify file selection works with .xlsb files in `/20-OUTPUT/` directory
- [x] Research error handling for failed `open` commands
- [x] Document platform-specific considerations

**Acceptance Criteria**:
- ✅ Command successfully opens Finder with file selected
- ✅ Works with absolute and relative paths
- ✅ Graceful error handling if command fails

**Completion Notes**: Finder integration working perfectly. Timeout handling implemented for UI commands. System requirements validation added to check for macOS.

## Phase 1: Core Architecture Setup

### Task 1.1: Create Project Structure ✅ COMPLETED
**Estimated Time**: 10 minutes  
**Priority**: Critical  
**Dependencies**: Task 0.1, 0.2, 0.3

**Objective**: Set up the modular code structure and empty module files

**Actions**:
- [x] Create `src/` directory structure
- [x] Create empty module files with proper `__init__.py`
- [x] Create `tests/` directory structure  
- [x] Set up basic `pricing_tool_accelerator.py` entry point
- [x] Create `pyproject.toml` or `requirements.txt` for dependencies

**Acceptance Criteria**:
- ✅ All directories and files exist as per plan.md structure
- ✅ Python can import all modules without errors
- ✅ Entry point file is executable

**Completion Notes**: Full modular structure created. Entry point executable and tested. Uses standard library only - no external dependencies required.

### Task 1.2: Implement Naming Utilities Module ✅ COMPLETED
**Estimated Time**: 30 minutes  
**Priority**: Critical  
**Dependencies**: Task 1.1

**Objective**: Create atomic functions for filename generation and input sanitization

**Actions**:
- [x] Implement `sanitize_user_input(text: str) -> str` function
- [x] Implement `generate_output_filename(date: str, client: str, gig: str, version: str) -> str`
- [x] Implement `handle_filename_collision(base_path: Path) -> Path` function
- [x] Add comprehensive type hints and docstrings
- [x] Create unit tests for all functions

**Acceptance Criteria**:
- ✅ All functions have type hints and docstrings
- ✅ Special characters are properly stripped from user input
- ✅ Filename generation follows exact specification format (updated with extra hyphen)
- ✅ Collision handling appends timestamp correctly
- ✅ 100% test coverage for the module

**Completion Notes**: All atomic functions implemented with comprehensive error handling. Filename format updated to include extra hyphen: `date - client - project - (version).xlsb`. Extensive testing completed.

### Task 1.3: Implement CLI Interface Module ✅ COMPLETED
**Estimated Time**: 25 minutes  
**Priority**: Critical  
**Dependencies**: Task 1.2

**Objective**: Create user input collection and validation functions

**Actions**:
- [x] Implement `prompt_for_client_name() -> str` function
- [x] Implement `prompt_for_gig_name() -> str` function  
- [x] Implement `validate_user_input(input_text: str) -> bool` function
- [x] Add input re-prompting for empty/invalid inputs
- [x] Create unit tests with mocked input

**Acceptance Criteria**:
- ✅ Clear, user-friendly prompts with instructions
- ✅ Input validation prevents empty strings
- ✅ Re-prompting works for invalid input
- ✅ Functions are easily testable with mocks
- ✅ All functions have comprehensive docstrings

**Completion Notes**: Full CLI interface with validation loops. User-friendly prompts with clear instructions. Automatic sanitization integration. Comprehensive error handling for edge cases.

## Phase 2: Core Functionality Implementation

### Task 2.1: Implement File Operations Module ✅ COMPLETED
**Estimated Time**: 40 minutes  
**Priority**: Critical  
**Dependencies**: Task 1.2, 1.3

**Objective**: Create file discovery, version extraction, and copy operations

**Actions**:
- [x] Implement `find_source_file(source_dir: Path, pattern: str) -> Path` function
- [x] Implement `extract_version_from_filename(filename: str) -> str` function
- [x] Implement `copy_file_with_rename(source: Path, destination: Path) -> bool` function
- [x] Add comprehensive error handling for file operations
- [x] Create unit tests with temporary directories and mock files

**Acceptance Criteria**:
- ✅ Source file discovery works with "Low Complexity" pattern (excludes temp files)
- ✅ Version extraction handles all expected filename formats
- ✅ File copying preserves metadata and handles permissions
- ✅ Error messages are clear and actionable
- ✅ All edge cases are tested

**Completion Notes**: Advanced file operations with temp file exclusion (~$ prefix). Extended attributes removal (quarantine/provenance) to prevent read-only warnings. Comprehensive error handling with descriptive messages.

### Task 2.2: Implement System Integration Module ✅ COMPLETED
**Estimated Time**: 20 minutes  
**Priority**: High  
**Dependencies**: Task 2.1

**Objective**: Create Finder integration and system operation functions

**Actions**:
- [x] Implement `open_file_in_finder(file_path: Path) -> bool` function
- [x] Add error handling for failed system calls
- [x] Create fallback behavior if Finder integration fails
- [x] Add logging for system operations
- [x] Create unit tests with mocked subprocess calls

**Acceptance Criteria**:
- ✅ Finder integration works on macOS systems (subprocess 'open -R' command)
- ✅ Graceful degradation if system calls fail
- ✅ Clear error messages for system operation failures
- ✅ Comprehensive test coverage with mocks

**Completion Notes**: Full macOS Finder integration with graceful error handling. System requirement validation (macOS check, directory existence). User-friendly success messaging with file path display.

### Task 2.3: Integrate Main CLI Entry Point ✅ COMPLETED
**Estimated Time**: 30 minutes  
**Priority**: Critical  
**Dependencies**: Task 2.1, 2.2

**Objective**: Wire together all modules into cohesive CLI application

**Actions**:
- [x] Implement main execution flow in `pricing_tool_accelerator.py`
- [x] Implement end-to-end error handling and user feedback
- [x] Add logging configuration for debugging
- [x] Create integration tests for full workflow

**Acceptance Criteria**:
- ✅ Complete end-to-end functionality works as specified
- ✅ User sees clear progress feedback and success messages
- ✅ Error conditions are handled gracefully with helpful messages
- ✅ Simple direct execution without command arguments
- ✅ Integration tests cover happy path and error scenarios

**Completion Notes**: Complete CLI orchestration with comprehensive error handling. Full workflow integration from user input to file operations to system integration. Performance optimized for sub-2-second execution.

## Phase 3: Testing & Polish

### Task 3.1: Comprehensive Error Scenario Testing ✅ COMPLETED
**Estimated Time**: 25 minutes  
**Priority**: High  
**Dependencies**: Task 2.3

**Objective**: Test all error conditions and edge cases

**Actions**:
- [x] Test missing source file scenarios
- [x] Test permission denied scenarios (read/write)
- [x] Test invalid user input scenarios
- [x] Test file collision scenarios
- [x] Test system integration failures

**Acceptance Criteria**:
- ✅ All error scenarios produce clear, actionable messages
- ✅ Application never crashes unexpectedly
- ✅ User can recover from all error conditions
- ✅ Error messages include guidance for resolution

**Completion Notes**: Comprehensive test suite covers all error paths including file not found, permission issues, invalid inputs, and system failures. Error messages provide clear guidance for user resolution.

### Task 3.2: Performance and Integration Validation ✅ COMPLETED
**Estimated Time**: 20 minutes  
**Priority**: Medium  
**Dependencies**: Task 3.1

**Objective**: Validate performance goals and integration points

**Actions**:
- [x] Test with actual .xlsb files from `/10-LATEST-PRICING-TOOLS/`
- [x] Validate execution time meets < 2 second goal
- [x] Test Finder integration on target macOS system
- [x] Verify file integrity after copy operations
- [x] Test with various input lengths and characters

**Acceptance Criteria**:
- ✅ Execution time consistently under 2 seconds (actual: sub-1-second performance)
- ✅ Finder integration works reliably (subprocess 'open -R' tested)
- ✅ File integrity maintained through copy process (shutil.copy2 preserves metadata)
- ✅ User experience is smooth and intuitive

**Completion Notes**: Performance exceeds targets with sub-1-second execution. Full integration testing with real .xlsb files confirmed functionality. Extended attributes handling ensures no read-only warnings. Finder integration tested on macOS.

## Definition of Done

### Code Quality Requirements
- [ ] All functions have type hints and comprehensive docstrings
- [ ] Code passes mypy type checking
- [ ] Code follows PEP 8 style guidelines
- [ ] All modules have 100% test coverage for core functionality
- [ ] No hardcoded paths (use configuration)

### Functionality Requirements  
- [ ] Successfully copies Low Complexity template with dynamic naming
- [ ] Extracts version number from source filename correctly
- [ ] Handles user input sanitization properly
- [ ] Manages file collisions with timestamp appending
- [ ] Opens Finder with created file selected
- [ ] Provides clear error messages for all failure modes

### Documentation Requirements
- [ ] All functions documented with examples
- [ ] Error conditions documented with resolutions
- [ ] User-facing documentation created (quickstart.md)
- [ ] Code comments explain complex logic

---

*These tasks provide a step-by-step roadmap for implementing the spreadsheet copy functionality while maintaining code quality and following the project constitution.*