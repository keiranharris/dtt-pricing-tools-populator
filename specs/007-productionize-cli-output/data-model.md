# Data Model: Productionize CLI Output with Verbose Logging Toggle

**Phase 1 Output**: Data structures and entities for logging configuration system
**Feature**: CLI output productionization with global verbose logging toggle

## Core Entities

### LoggingConfiguration

Configuration entity that controls global logging behavior throughout the application.

**Purpose**: Central configuration for verbose logging toggle and output categorization
**Lifecycle**: Created at application startup, persists for application lifetime
**Scope**: Global application-wide configuration

**Attributes**:
- `verbose_enabled`: boolean - Controls whether technical diagnostic messages are displayed
- `log_level`: LogLevel enum - Base logging level (INFO, WARNING, ERROR)
- `message_categories`: Dict[MessageCategory, boolean] - Controls which message types display

**Validation Rules**:
- `verbose_enabled` must be boolean (default: False for production mode)
- `log_level` must be valid LogLevel enum value
- `message_categories` must contain all required categories

**State Transitions**:
- Initial: verbose_enabled=False (production mode)
- Toggle: verbose_enabled can be changed at runtime
- Terminal: No terminal state (persists until application exit)

### MessageCategory

Enumeration defining the three tiers of CLI output messages.

**Purpose**: Categorize log messages for selective display control
**Values**:
- `ESSENTIAL_USER`: Always displayed (input prompts, final results, errors)
- `OPERATION_STATUS`: Always displayed (major operation progress indicators)  
- `TECHNICAL_DIAGNOSTIC`: Controlled by verbose toggle (field matching, internal details)

**Usage Rules**:
- ESSENTIAL_USER messages never filtered regardless of verbose setting
- OPERATION_STATUS messages always displayed for user confidence
- TECHNICAL_DIAGNOSTIC messages only displayed when verbose_enabled=True

### LogLevel

Standard Python logging levels with application-specific usage patterns.

**Purpose**: Control base logging threshold independent of message categorization
**Values**:
- `INFO`: Technical diagnostic information and detailed progress
- `WARNING`: Non-critical issues that should be visible to users
- `ERROR`: Critical errors that must always be displayed

**Display Rules**:
- ERROR and WARNING always displayed regardless of verbose setting
- INFO messages subject to MessageCategory filtering based on verbose setting

## Message Flow Architecture

### Input Sources
```
User Input Prompts (print statements) → Always Display
├── CLI field collection → ESSENTIAL_USER category
├── Validation errors → ESSENTIAL_USER category
└── Confirmation messages → ESSENTIAL_USER category

Logger Messages (logger.info/warning/error) → Category Filter
├── logger.error() → Always Display (ERROR level)
├── logger.warning() → Always Display (WARNING level)
└── logger.info() → MessageCategory classification
    ├── Operation start/completion → OPERATION_STATUS
    ├── Field matching details → TECHNICAL_DIAGNOSTIC
    └── Internal processing → TECHNICAL_DIAGNOSTIC
```

### Output Destinations
```
Production Mode (verbose_enabled=False):
├── ESSENTIAL_USER messages → Console Output
├── OPERATION_STATUS messages → Console Output  
├── ERROR/WARNING messages → Console Output
└── TECHNICAL_DIAGNOSTIC messages → Suppressed

Verbose Mode (verbose_enabled=True):
├── All message categories → Console Output
└── Full technical details displayed
```

## Configuration Integration

### Global Constants Integration

Following existing pattern in `pricing_tool_accelerator.py`:

```python
# ============================================================================
# FEATURE 007: CLI OUTPUT CONFIGURATION
# ============================================================================
# Controls production vs verbose CLI output mode

VERBOSE_LOGGING_ENABLED = False  # Production mode by default
CLI_OUTPUT_MODE = "production"   # "production" or "verbose"
```

### Module Integration Points

**Primary Integration**: `system_integration.py`
- Currently contains `logging.basicConfig(level=logging.INFO)`  
- Enhanced to configure custom logging handler based on global settings
- Becomes centralized logging configuration point

**Secondary Integrations**:
- `data_population_orchestrator.py`: Heavy logger.info() usage requires classification
- `cli_interface.py`: Existing print() statements remain unchanged (ESSENTIAL_USER)
- All other modules: Existing logger calls enhanced with message classification

## Backward Compatibility Guarantees

### Unchanged Interfaces
- All existing function signatures remain identical
- All existing logger method calls continue to work
- All existing print() statements continue to display
- All existing error handling patterns preserved

### Enhanced Behavior
- `logger.info()` calls enhanced with intelligent message categorization
- Output volume controlled by global configuration
- Technical details available on-demand through verbose toggle
- Zero functional changes to core business logic

## Data Relationships

```
LoggingConfiguration (1) ←→ (1) Application Instance
    ├── Controls → MessageCategory filtering
    ├── Influences → Console Output content
    └── Configured by → Global Constants

MessageCategory (enum) ←→ (many) Log Messages
    ├── ESSENTIAL_USER ←→ User Input/Output messages  
    ├── OPERATION_STATUS ←→ Progress indicators
    └── TECHNICAL_DIAGNOSTIC ←→ Debug information

LogLevel (enum) ←→ (many) Logger instances
    ├── ERROR → Always displayed
    ├── WARNING → Always displayed  
    └── INFO → Subject to category filtering
```

This data model maintains constitutional principles of atomic function design and modular architecture while enabling the production CLI output enhancement.