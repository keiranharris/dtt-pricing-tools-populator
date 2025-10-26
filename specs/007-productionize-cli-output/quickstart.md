# Quick Start: Productionize CLI Output with Verbose Logging Toggle

**Feature**: CLI output productionization with global verbose logging toggle  
**Goal**: Implement clean production CLI output with optional verbose diagnostics

## Overview

This feature adds a global toggle to control CLI output verbosity, providing clean production output by default while preserving full diagnostic capabilities for development and debugging.

## Key Components

### 1. Global Configuration (5 min)
- Add `VERBOSE_LOGGING_ENABLED = False` constant to main configuration
- Follows existing pattern in `pricing_tool_accelerator.py` 
- Default: production mode (verbose disabled)

### 2. Logging System Enhancement (15 min)
- Create new `logging_config.py` module for centralized logging control
- Enhance `system_integration.py` to use custom logging handler
- Replace `logging.basicConfig()` with production-aware configuration

### 3. Message Classification (10 min)
- Implement three-tier message categorization system:
  - **Essential User**: Input prompts, results, errors (always show)
  - **Operation Status**: Major operation progress (always show)  
  - **Technical Diagnostic**: Field details, internal operations (verbose only)

### 4. Output Control (10 min)
- Custom logging handler filters messages based on category and verbose setting
- Preserve all existing `print()` statements for user interaction
- Control `logger.info()` visibility through message classification

## Implementation Steps

### Step 1: Add Global Configuration
```python
# In pricing_tool_accelerator.py, add to existing constants section:
VERBOSE_LOGGING_ENABLED = False  # Production mode by default
```

### Step 2: Create Logging Configuration Module
```python
# New file: src/logging_config.py
def setup_production_logging(verbose_enabled: bool = False) -> None:
    """Configure logging for production or verbose mode."""
    
def get_message_category(message: str, context: str = "") -> MessageCategory:
    """Classify log message for display control."""
```

### Step 3: Enhance System Integration
```python
# Modify src/system_integration.py
# Replace: logging.basicConfig(level=logging.INFO)
# With: setup_production_logging(VERBOSE_LOGGING_ENABLED)
```

### Step 4: Add Message Classification
- Essential messages: User input prompts, final results, errors
- Operation status: "Starting data population...", "Population complete"
- Technical details: Field matching scores, internal processing steps

## Testing Approach

### Functional Testing (5 min)
```python
# Test both output modes work correctly
test_production_mode_output()  # Verify clean output
test_verbose_mode_output()     # Verify full diagnostics
test_toggle_runtime_change()   # Verify immediate effect
```

### Integration Testing (5 min) 
```python
# Verify existing functionality unchanged
test_all_current_workflows()   # All user scenarios still work
test_backward_compatibility()  # Existing tests still pass
```

## Success Criteria Verification

✅ **80% log reduction**: Count output lines in production vs verbose mode  
✅ **Preserve critical info**: All user prompts and results still display  
✅ **Full diagnostics available**: Verbose mode shows all current detail  
✅ **Immediate toggle effect**: Configuration change takes effect in <1 second  
✅ **Zero functionality loss**: All existing workflows continue to work  

## File Changes Summary

### New Files
- `src/logging_config.py` - Centralized logging configuration
- `tests/test_logging_config.py` - Unit tests for logging system

### Modified Files  
- `pricing_tool_accelerator.py` - Add global configuration constant
- `src/system_integration.py` - Replace basic logging with custom handler
- `src/data_population_orchestrator.py` - Add message classification hints
- `tests/test_cli_integration.py` - Test both output modes

### Unchanged Files
- All existing module interfaces remain identical
- All existing `print()` statements for user interaction preserved
- All existing error handling and business logic unchanged

## Development Time Estimate

- **Setup & Configuration**: 10 minutes
- **Core Implementation**: 25 minutes  
- **Testing & Validation**: 15 minutes
- **Integration & Cleanup**: 10 minutes

**Total**: ~60 minutes for complete feature implementation

## Rollback Plan

If issues arise, feature can be disabled by:
1. Set `VERBOSE_LOGGING_ENABLED = True` (restores current verbose output)
2. Revert `system_integration.py` to use `logging.basicConfig()` 
3. All existing functionality remains completely unaffected