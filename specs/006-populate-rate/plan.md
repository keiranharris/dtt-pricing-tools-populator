# Implementation Plan: Populate Rate Card at Given Margin

**Branch**: `006-populate-rate` | **Date**: 2025-10-13 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/006-populate-rate/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Feature 006 extends the existing pricing tool automation by adding client margin percentage collection via CLI and automated rate card calculation. The system will prompt users for a margin percentage (35-65%) at the beginning of the workflow, then use this input to calculate engineering rates for all seven staff levels using the formula: Standard Cost Rate / (1 - Client Margin %). This feature integrates with the existing Excel automation infrastructure and executes after Feature 005 Resource Setup to ensure dependency data is available.

## Technical Context

**Language/Version**: Python 3.8+ (existing codebase compatibility)  
**Primary Dependencies**: xlwings (Excel automation), existing CLI infrastructure from src/cli_interface.py  
**Storage**: Excel files (.xlsb format), no additional database required  
**Testing**: Python unittest framework (consistent with existing test structure)  
**Target Platform**: Windows/macOS desktop (Excel compatibility requirement)
**Project Type**: Single project (CLI tool extending existing automation)  
**Performance Goals**: <5 seconds for rate calculation across 7 staff levels, <30 seconds for user input collection  
**Constraints**: Must work with existing Excel automation, maintain backward compatibility with Features 001-005  
**Scale/Scope**: Single-user desktop tool, 7 staff level calculations per execution

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

✓ **I. Automation Over Manual Work**: Feature eliminates manual rate card calculation and Excel formula entry  
✓ **II. Atomic Function Design**: Separate functions for CLI input validation, margin conversion, and rate calculation  
✓ **III. Python Best Practices**: Will follow PEP 8, use type hints, comprehensive docstrings per existing codebase standards  
✓ **IV. Modular Architecture**: Extends existing CLI and Excel modules without disrupting current functionality  
✓ **V. Data Source Flexibility**: Integrates with existing CLI input patterns and Excel data source infrastructure  
✓ **Code Quality**: Will include type hints, docstrings, input validation, and isolated testability  
✓ **Performance**: Meets <5 second calculation target, handles Excel operations efficiently  
✓ **Development Workflow**: Following spec-driven development with proper feature branching

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

├── src/
│   ├── cli_interface.py           # EXTEND: Add margin percentage input
│   ├── data_population_orchestrator.py  # EXTEND: Add rate calculation step  
│   ├── rate_card_calculator.py    # NEW: Rate calculation logic
│   └── margin_validator.py        # NEW: Input validation for 35-65% range
├── tests/
│   ├── test_rate_card_calculator.py  # NEW: Rate calculation tests
│   └── test_margin_validator.py      # NEW: Input validation tests
└── pricing_tool_accelerator.py   # EXTEND: Integrate margin input and rate calculation
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# [REMOVE IF UNUSED] Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# [REMOVE IF UNUSED] Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure: feature modules, UI flows, platform tests]
```

**Structure Decision**: Single project extension using existing  structure with new modules for rate calculation logic

## Implementation Notes

**Rate Calculation Enhancement (2025-10-13)**:
- Engineering rates will be rounded to nearest whole integer (no cents) for easier handling
- Rounding applied after formula calculation: `round(cost_rate / (1 - margin_decimal))`
- Excel output format changed from "$XXX.XX" to "$XXX" (whole numbers only)
- This change affects rate_card_calculator.py and related test expectations

## Complexity Tracking

*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
