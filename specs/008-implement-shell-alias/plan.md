# Implementation Plan: Shell Alias Auto-Setup for Easy Access

**Branch**: `008-implement-shell-alias` | **Date**: 2025-10-26 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/008-implement-shell-alias/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Primary requirement: Automatic shell alias creation on first run that transforms complex path-based invocation (`python3 /full/path/pricing_tool_accelerator.py`) into simple memorable command (`priceup`) that works from anywhere in terminal. Technical approach uses pure Python standard library with startup check function integrated into existing CLI workflow, zsh-only support with informational user feedback and comment markers for safe alias management.

## Technical Context

**Language/Version**: Python 3.11+ (existing codebase requirement)  
**Primary Dependencies**: Python standard library only (os.path, pathlib, shlex for shell escaping)  
**Storage**: ~/.zshrc file modification with comment markers for identification  
**Testing**: pytest (existing project standard)  
**Target Platform**: macOS with zsh shell (hard requirement per clarifications)
**Project Type**: CLI enhancement - single project structure  
**Performance Goals**: <30 seconds for first-time setup, <60 seconds timeout for file operations  
**Constraints**: No external dependencies, zsh-only support, informational messages only (no interactive prompts)  
**Scale/Scope**: Individual developer tool, single user per installation, idempotent operations

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Automation Over Manual Work ✅
- **PASS**: Feature eliminates manual alias creation and path memorization
- **PASS**: Transforms complex command invocation into zero-touch automation after first run
- **PASS**: Manual intervention only required for exceptional error handling (permission errors)

### II. Atomic Function Design ✅ 
- **PASS**: Shell detection, path resolution, file modification, and alias validation will be separate functions
- **PASS**: Each function performs single task (detect shell, read ~/.zshrc, write alias, validate existing alias)
- **PASS**: Functions designed for composition without side effects

### III. Python Best Practices ✅
- **PASS**: Will follow PEP 8 naming conventions (snake_case functions, clear variable names)
- **PASS**: Type hints required for all functions (Path objects, shell detection results)  
- **PASS**: Comprehensive docstrings with parameter descriptions and usage examples

### IV. Modular Architecture ✅
- **PASS**: Shell alias functionality will be discrete module interfacing with existing CLI
- **PASS**: Clear separation between detection, file operations, and user messaging
- **PASS**: Configuration externalized (shell markers, timeout values)

### V. Data Source Flexibility ✅
- **PASS**: Design supports future extension to other shells (bash, fish) if requirements change
- **PASS**: Clear separation between shell detection and alias creation logic

### Post-Design Constitution Re-Check ✅

**Re-evaluated after Phase 1 design completion:**

#### I. Automation Over Manual Work ✅
- **CONFIRMED**: ShellAliasManager eliminates all manual alias configuration
- **CONFIRMED**: Idempotent operations with automatic path correction on repository moves
- **CONFIRMED**: Manual intervention only for permission errors (provides fallback instructions)

#### II. Atomic Function Design ✅  
- **CONFIRMED**: Each function has single responsibility (detect_shell, resolve_path, write_config)
- **CONFIRMED**: Comprehensive type hints in API contract (Path, Optional, dataclasses)
- **CONFIRMED**: Clear error propagation with custom exception hierarchy

#### III. Python Best Practices ✅
- **CONFIRMED**: PEP 8 compliance in API design (snake_case, clear naming)
- **CONFIRMED**: Comprehensive docstrings specified in contract
- **CONFIRMED**: Type hints required for all public interfaces

#### IV. Modular Architecture ✅
- **CONFIRMED**: ShellAliasManager as discrete module with clear interface
- **CONFIRMED**: Externalized configuration (timeout, alias name, markers)
- **CONFIRMED**: Independent testability with mocked file system

#### V. Data Source Flexibility ✅
- **CONFIRMED**: Extensible design allows future shell support via enum expansion
- **CONFIRMED**: Clean separation of shell detection from alias file operations

## Project Structure

### Documentation (this feature)

```
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```
src/
├── shell_alias_manager.py      # NEW: Core alias detection and creation logic
├── cli_interface.py           # MODIFY: Integrate alias setup check
├── constants.py               # MODIFY: Add alias-related constants
└── logging_config.py          # EXISTING: Use for informational messages

tests/
├── test_shell_alias_manager.py # NEW: Unit tests for alias functionality
├── test_cli_integration.py     # MODIFY: Integration tests with CLI startup
└── integration/
    └── test_alias_workflow.py   # NEW: End-to-end alias creation tests

pricing_tool_accelerator.py     # MODIFY: Add startup alias check hook
README.md                        # MODIFY: Add git clone and usage instructions
```

**Structure Decision**: Single project structure using existing src/ organization. New shell_alias_manager.py module for core functionality, minimal modifications to existing CLI interface for integration hook. Follows established pattern of discrete modules with clear interfaces.

## Complexity Tracking

*No constitutional violations - all principles satisfied by design*

## Phase Completion Status

✅ **Phase 0: Research** - Complete  
✅ **Phase 1: Design & Contracts** - Complete  
⏳ **Phase 2: Tasks** - Ready for `/speckit.tasks` command  

## Generated Artifacts

### Documentation
- `plan.md` - This implementation plan
- `research.md` - Technology decisions and implementation patterns  
- `data-model.md` - Core entities, relationships, and data flow
- `quickstart.md` - Step-by-step implementation guide (4-6 hours)
- `contracts/shell-alias-api.md` - Complete API specification

### Agent Context
- `.github/copilot-instructions.md` - Updated with shell alias technologies

### Implementation Readiness
- **Clear API Contract** - All interfaces and data structures defined
- **Comprehensive Error Handling** - All edge cases from spec covered
- **Testing Strategy** - Unit and integration test requirements specified
- **Performance Requirements** - Timeout and user experience targets set
- **Constitution Compliance** - All principles satisfied, no violations

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
