# Implementation Plan: Spreadsheet Copy and Instantiation

**Branch**: `001-spreadsheet-copy` | **Date**: 2025-10-12 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-spreadsheet-copy/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Automate the weekly task of copying and renaming Excel templates from `/10-LATEST-PRICING-TOOLS/` to `/20-OUTPUT/` with dynamic naming based on CLI input and automatic version extraction. The system will eliminate manual file operations while ensuring proper naming conventions and user experience through Finder integration.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: `shutil` (stdlib), `pathlib` (stdlib), `re` (stdlib), `subprocess` (stdlib), `datetime` (stdlib)  
**Storage**: File system operations, no database required  
**Testing**: pytest with mock file operations  
**Target Platform**: macOS (for Finder integration via `open` command)  
**Project Type**: Single-script CLI tool  
**Performance Goals**: Sub-second execution for file copy operations  
**Constraints**: Must preserve original .xlsb format, handle filename collisions gracefully  
**Scale/Scope**: Single-user tool, processing one file at a time

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

✓ **Automation Over Manual Work**: Eliminates weekly repetitive file copy/rename tasks  
✓ **Code Quality & Maintainability**: Modular design with atomic functions  
✓ **Python Best Practices**: PEP 8 compliance, type hints, comprehensive docstrings  
✓ **Atomic Function Design**: Each function performs single responsibility  
✓ **Data Source Flexibility**: Structured for future template type extensions  

## Project Structure

### Documentation (this feature)

```
specs/001-spreadsheet-copy/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```
90-CODE/
├── pricing_tool_accelerator.py  # Main CLI entry point
├── src/
│   ├── __init__.py
│   ├── file_operations.py       # File discovery, copying, version extraction
│   ├── cli_interface.py         # User input collection and validation
│   ├── naming_utils.py          # Filename generation and sanitization
│   └── system_integration.py   # Finder integration and OS operations
└── tests/
    ├── __init__.py
    ├── test_file_operations.py
    ├── test_cli_interface.py
    ├── test_naming_utils.py
    └── test_system_integration.py
```

## Implementation Phases

### Phase 0: Research & Foundation (30 minutes)

**Objective**: Research technical approaches and validate core assumptions

**Deliverables**:
- Research document covering file operations, regex patterns, macOS integration
- Validation of .xlsb file handling capabilities
- Investigation of Finder integration options

**Key Research Areas**:
1. Python standard library file operations (`shutil.copy2` vs `shutil.copy`)
2. Regex patterns for version extraction from filenames
3. macOS `open -R` command for Finder selection
4. File timestamp collision handling strategies
5. Cross-platform considerations (future-proofing)

### Phase 1: Core Architecture Design (45 minutes)

**Objective**: Design atomic functions and data flow architecture

**Deliverables**:
- Data model definitions for file paths, user input, and system state
- Function contracts and API specifications
- Module interface definitions
- Error handling strategy

**Key Design Elements**:
1. **FileOperations Module**: Source discovery, version parsing, file copying
2. **CLIInterface Module**: Input collection, validation, sanitization
3. **NamingUtils Module**: Filename generation, collision resolution
4. **SystemIntegration Module**: Finder integration, OS-specific operations

### Phase 2: Implementation (90 minutes)

**Objective**: Implement all functionality following atomic function principles

**Implementation Order**:
1. **Core Utilities** (20 min): Naming utils and input sanitization
2. **File Operations** (30 min): Source discovery and version extraction
3. **CLI Interface** (20 min): User input collection and validation
4. **Integration** (20 min): File copying and Finder opening

### Phase 3: Testing & Validation (45 minutes)

**Objective**: Comprehensive testing with mock file operations

**Testing Strategy**:
1. **Unit Tests**: Each atomic function tested in isolation
2. **Integration Tests**: End-to-end workflow with temporary directories
3. **Error Condition Tests**: Missing files, permission errors, invalid input
4. **Edge Case Tests**: Special characters, long filenames, version parsing edge cases

## Risk Analysis & Mitigation

### Technical Risks

**Risk**: .xlsb file corruption during copy operations  
**Mitigation**: Use `shutil.copy2` to preserve file metadata and timestamps

**Risk**: Version regex fails to match filename patterns  
**Mitigation**: Comprehensive test cases for version extraction, graceful fallback

**Risk**: Finder integration fails on different macOS versions  
**Mitigation**: Error handling around `subprocess` calls, fallback to folder opening

### User Experience Risks

**Risk**: Special characters in user input break filename generation  
**Mitigation**: Aggressive input sanitization with clear feedback

**Risk**: File collisions create confusing filenames  
**Mitigation**: Clear timestamp format (HHMMSS) and user feedback

## Dependencies & Requirements

### Python Standard Library
- `pathlib`: Modern path handling and file operations
- `shutil`: High-level file operations with metadata preservation
- `re`: Regular expression matching for version extraction
- `datetime`: Timestamp generation for naming and collision resolution
- `subprocess`: System integration for Finder operations
- `sys`: Error handling and exit codes

### Development Dependencies
- `pytest`: Test framework
- `pytest-mock`: Mocking file operations for testing
- `mypy`: Type checking validation

### System Requirements
- **Python**: 3.11+ (for modern type hints and pathlib features)
- **OS**: macOS (for Finder integration)
- **Permissions**: Read access to `/10-LATEST-PRICING-TOOLS/`, write access to `/20-OUTPUT/`

## Configuration & Settings

### Directory Configuration
```python
# Default paths (configurable)
SOURCE_DIR = Path("10-LATEST-PRICING-TOOLS")
OUTPUT_DIR = Path("20-OUTPUT") 
SEARCH_PATTERN = "Low Complexity"
```

### Filename Patterns
```python
# Version extraction regex
VERSION_PATTERN = r"v(\d+\.\d+)"
# Output filename template  
OUTPUT_TEMPLATE = "{date} - {client} - {gig} (LowComp{version}).xlsb"
# Collision timestamp format
COLLISION_FORMAT = "_%H%M%S"
```

## Success Metrics & Validation

### Performance Metrics
- **Execution Time**: < 2 seconds end-to-end
- **File Copy Speed**: Preserve original file size and timestamps
- **User Input Time**: Clear prompts with immediate feedback

### Quality Metrics
- **Test Coverage**: 100% of atomic functions
- **Error Handling**: All failure modes handled gracefully
- **Code Compliance**: Pass mypy type checking and PEP 8 linting

### User Experience Metrics
- **Input Validation**: Clear error messages for invalid input
- **Success Feedback**: Confirmation of file creation with path
- **Integration**: Successful Finder selection of created file

---

*This plan provides the roadmap for implementing the foundational spreadsheet copying functionality that will serve as the base for more complex data population features.*