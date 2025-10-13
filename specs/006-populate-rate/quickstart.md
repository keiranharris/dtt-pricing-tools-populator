# Quickstart: Populate Rate Card at Given Margin

**Feature**: 006-populate-rate  
**Date**: 2025-10-13  
**Purpose**: Quick reference for implementing and using rate card population

## Implementation Overview

This feature extends the existing pricing tool automation to collect client margin percentages and calculate engineering rates automatically.

### Key Components

1. **CLI Extension**: Collect margin percentage (35-65%) at startup
2. **Rate Calculator**: Apply formula `cost_rate / (1 - margin_decimal)` 
3. **Excel Integration**: Read from column Q, write to column O (rows 28-34)
4. **Error Handling**: Skip invalid data, report results

### Integration Points

- **CLI Interface**: Extend `src/cli_interface.py` for margin input
- **Orchestrator**: Add rate calculation step to `src/data_population_orchestrator.py`
- **Excel Automation**: Leverage existing xlwings patterns from Feature 005

## Development Workflow

### 1. Create New Modules
```bash
# Create rate calculation module
touch 90-CODE/src/rate_card_calculator.py

# Create input validation module  
touch 90-CODE/src/margin_validator.py

# Create test files
touch 90-CODE/tests/test_rate_card_calculator.py
touch 90-CODE/tests/test_margin_validator.py
```

### 2. Implement Core Functions

**Priority Order**:
1. `margin_validator.py` - Input validation logic
2. `rate_card_calculator.py` - Mathematical calculations  
3. CLI integration in `cli_interface.py`
4. Orchestrator integration in `data_population_orchestrator.py`
5. Main application integration in `pricing_tool_accelerator.py`

### 3. Testing Strategy

```bash
# Run unit tests for calculation logic
python -m pytest 90-CODE/tests/test_rate_card_calculator.py -v

# Run integration tests with mock Excel data
python -m pytest 90-CODE/tests/test_margin_validator.py -v

# Test full workflow integration
python 90-CODE/pricing_tool_accelerator.py
```

## Usage Example

### User Workflow
1. User runs `python pricing_tool_accelerator.py`
2. System prompts: `Client Name:` → user enters client name
3. System prompts: `Gig Name:` → user enters gig name  
4. **NEW**: System prompts: `Client Margin %:` → user enters 40
5. System validates margin (35-65 range)
6. System proceeds with existing Features 001-005
7. **NEW**: System calculates and populates rate card using 40% margin
8. System reports results: "Rate card populated for 7 staff levels"

### Sample Calculation
```
Given:
- Cost Rate (Q28): $100.00
- Client Margin: 40% (0.40 decimal)

Calculation:
- Engineering Rate = $100.00 / (1 - 0.40) = $100.00 / 0.60 = $166.67

Result:
- Cell O28 gets value: $166.67
```

## Configuration

### Constants (add to existing configuration)
```python
# Margin validation
MIN_MARGIN_PERCENTAGE = 35
MAX_MARGIN_PERCENTAGE = 65

# Excel cell ranges  
COST_RATE_RANGE = "Q28:Q34"
ENGINEERING_RATE_RANGE = "O28:O34"
RATE_CARD_WORKSHEET = "Resource Setup"

# Performance targets
MAX_CALCULATION_TIME_SECONDS = 5
MAX_INPUT_TIME_SECONDS = 30
```

## Error Scenarios & Handling

### Invalid Margin Input
```
User enters: "75"
System response: "Error: Margin must be between 35-65%. Please try again."
System action: Re-prompt for input
```

### Missing Cost Rate Data
```
Scenario: Cell Q30 is empty or contains text
System response: "Warning: Skipped Senior Manager (row 30) - invalid cost rate"  
System action: Continue processing other rows, report at end
```

### Excel Access Issues
```
Scenario: Excel file is locked by another process
System response: "Error: Cannot access Excel file. Please close other Excel windows."
System action: Exit gracefully with clear instructions
```

## Performance Expectations

- **Margin Input**: <30 seconds (user-dependent)
- **Rate Calculation**: <5 seconds for all 7 levels
- **Excel Operations**: <2 seconds (read + write)
- **Memory Usage**: Minimal (7 float calculations)

## Integration Checklist

### Pre-Implementation
- [ ] Review existing CLI patterns in `cli_interface.py`
- [ ] Understand Excel automation from Feature 005
- [ ] Study error handling patterns in existing features
- [ ] Review constitutional requirements for atomic functions

### Implementation
- [ ] Create margin validation with comprehensive error handling
- [ ] Implement rate calculation with formula accuracy
- [ ] Extend CLI interface for margin collection
- [ ] Integrate with existing orchestrator workflow
- [ ] Add Excel read/write operations using xlwings
- [ ] Implement user feedback and progress reporting

### Testing  
- [ ] Unit test margin validation edge cases
- [ ] Unit test rate calculation mathematical accuracy
- [ ] Integration test CLI input collection
- [ ] Integration test Excel operations with mock data
- [ ] End-to-end test complete workflow
- [ ] Performance test calculation timing

### Deployment
- [ ] Update main application to include margin prompt
- [ ] Verify backward compatibility with existing features
- [ ] Test with real Excel files and data
- [ ] Validate user experience and error messages
- [ ] Document any configuration changes needed

This quickstart provides the essential information needed to implement Feature 006 efficiently while maintaining consistency with the existing codebase and constitutional requirements.