# Quick Start: Dynamic OneDrive Path Configuration

**Created**: 2025-10-28  
**Purpose**: Rapid implementation guide for OneDrive path configuration feature

## Overview

This feature enables the pricing tool to work across different OneDrive organizational structures by allowing users to configure their specific OneDrive base path rather than relying on hardcoded paths.

## Key Files Created

```
src/
├── path_configuration.py        # NEW: Core path management functionality
├── constants.py                 # MODIFIED: Dynamic path resolution
└── cli_interface.py            # MODIFIED: Setup wizard integration

tests/
├── test_path_configuration.py  # NEW: Path configuration tests
└── test_cli_integration.py     # MODIFIED: Setup wizard tests

specs/009-dynamic-onedrive-path/
├── plan.md                     # This implementation plan
├── data-model.md               # Data structures and relationships  
├── research.md                 # Technical decisions and alternatives
├── contracts/                  # API interfaces and integration points
└── quickstart.md              # This file
```

## Implementation Phases

### Phase 1: Core Configuration Module

Create `src/path_configuration.py`:

```python
# Core classes: PathConfiguration, ConfigurationManager, SetupWizard
# Key methods: load_configuration(), save_configuration(), validate_configuration()
# Configuration file: ~/.dtt-pricing-tool-populator-config (JSON format)
```

**Acceptance**: Configuration can be saved/loaded with basic validation

### Phase 2: Setup Wizard Integration  

Modify `src/cli_interface.py`:

```python  
# Add setup wizard triggers in main application startup
# Interactive command-line prompts for path input
# Integration with existing CLI argument handling
```

**Acceptance**: First-time users guided through setup wizard

### Phase 3: Dynamic Path Resolution

Modify `src/constants.py`:

```python
# Replace hardcoded paths with dynamic resolution
# Fallback to existing hardcoded values for backwards compatibility  
# Integration point for all existing modules
```

**Acceptance**: All existing functionality works with configured paths

### Phase 4: Error Handling and Recovery

Enhance path validation and error scenarios:

```python
# Custom exception classes for different error types
# User-friendly error messages with recovery suggestions
# Graceful handling of OneDrive offline scenarios
```

**Acceptance**: Clear guidance provided for all error scenarios

## Testing Strategy

### Unit Tests
- Configuration file operations (save/load/validate)
- Path validation logic with various input scenarios
- Setup wizard flow with mocked user input

### Integration Tests  
- End-to-end configuration workflow
- Backwards compatibility with existing installations
- Error handling with inaccessible OneDrive paths

### Manual Testing
- Fresh installation configuration
- Reconfiguration scenarios
- Different OneDrive organizational structures

## Key Implementation Decisions

1. **Configuration Storage**: JSON file in user home directory (`~/.dtt-pricing-tool-populator-config`)
2. **User Interface**: Interactive command-line prompts (consistent with existing CLI tool)
3. **Validation Strategy**: Lazy validation (validate only when path access fails)
4. **Backwards Compatibility**: Fallback to existing hardcoded paths if no configuration exists
5. **Error Handling**: Custom exception hierarchy with user-friendly messages

## Development Workflow

1. Create feature branch: `009-dynamic-onedrive-path`
2. Implement core configuration module with tests
3. Add setup wizard integration  
4. Modify existing constants module for dynamic resolution
5. Add comprehensive error handling
6. Test across different OneDrive configurations
7. Update documentation and user guides

## Success Criteria Verification

- ✅ 100% of users with different OneDrive mappings can complete initial setup
- ✅ Tool startup remains under 5 seconds after configuration  
- ✅ Path validation catches 95% of common OneDrive accessibility issues
- ✅ Users can reconfigure paths in under 30 seconds
- ✅ Setup wizard has less than 5% error rate for valid OneDrive structures  
- ✅ Zero hardcoded OneDrive paths remain in production code

## Next Steps

1. Run `/speckit.tasks` to generate detailed implementation tasks
2. Begin Phase 1 implementation with core configuration module
3. Set up comprehensive test coverage for path operations
4. Plan testing across different OneDrive organizational structures