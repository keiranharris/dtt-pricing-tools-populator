# Data Model: Populate Rate Card at Given Margin

**Feature**: 006-populate-rate  
**Date**: 2025-10-13  
**Purpose**: Define data entities and relationships for rate card population

## Core Entities

### ClientMargin
**Purpose**: User-provided margin percentage for rate calculations

**Attributes**:
- `percentage: int` - Raw user input (35-65)
- `decimal: float` - Calculated decimal representation (0.35-0.65)
- `is_valid: bool` - Validation status

**Validation Rules**:
- Must be whole number between 35 and 65 inclusive
- Must be numeric input only
- Converted to decimal by dividing by 100

**State Transitions**:
- Raw Input → Validated → Converted to Decimal → Ready for Calculation

### StandardCostRate
**Purpose**: Cost basis data for each staff level from column Q

**Attributes**:
- `staff_level: str` - Staff level identifier (from Resource Setup)
- `row_number: int` - Excel row number (28-34)
- `cost_value: float | None` - Cost rate value or None if invalid
- `is_valid: bool` - Whether the cell contains valid numeric data
- `cell_reference: str` - Excel cell reference (Q28-Q34)

**Validation Rules**:
- Must be numeric value > 0
- Must exist in expected cell range Q28-Q34
- Invalid cells are skipped with logging

### EngineeringRate
**Purpose**: Calculated billing rate for each staff level

**Attributes**:
- `staff_level: str` - Staff level identifier
- `row_number: int` - Excel row number (28-34)  
- `cost_rate: float` - Source standard cost rate
- `margin_decimal: float` - Applied margin percentage (0.35-0.65)
- `calculated_rate: float` - Result of formula calculation
- `cell_reference: str` - Target Excel cell reference (O28-O34)

**Calculation Formula**:
```python
calculated_rate = cost_rate / (1 - margin_decimal)
```

**Business Rules**:
- Always rounded to nearest whole integer (no cents) for easier handling
- Must overwrite existing cell data without warning
- Skipped if corresponding cost_rate is invalid

### RateCardBatch
**Purpose**: Collection entity for processing all seven staff levels

**Attributes**:
- `margin: ClientMargin` - Applied margin for all calculations
- `cost_rates: List[StandardCostRate]` - Source data for calculation
- `engineering_rates: List[EngineeringRate]` - Calculated results
- `processed_count: int` - Number of successfully processed rates
- `skipped_count: int` - Number of skipped due to invalid data
- `processing_status: str` - Overall batch status

**Processing States**:
- `initialized` - Batch created but not processed
- `processing` - Calculations in progress  
- `completed` - All valid calculations finished
- `partial_success` - Some calculations completed, some skipped

## Data Relationships

```
ClientMargin (1) ──────── (1) RateCardBatch
                              │
                              ├── (7) StandardCostRate
                              └── (7) EngineeringRate
                              
StandardCostRate (1) ────── (1) EngineeringRate
[by row_number]
```

## Data Flow

1. **Input Collection**: User provides margin → ClientMargin entity
2. **Source Reading**: Excel Q28-Q34 → StandardCostRate entities  
3. **Validation**: Filter valid StandardCostRate entities
4. **Calculation**: Valid StandardCostRate + ClientMargin → EngineeringRate entities
5. **Output Writing**: EngineeringRate entities → Excel O28-O34

## Excel Cell Mapping

| Entity | Source Cells | Target Cells | Purpose |
|--------|--------------|--------------|---------|
| StandardCostRate | Q28-Q34 | N/A | Read cost basis |
| EngineeringRate | N/A | O28-O34 | Write calculated rates |
| ClientMargin | CLI Input | N/A | User-provided percentage |

## Error Handling Data

### ValidationError
**Purpose**: Capture validation failures for user feedback

**Attributes**:
- `entity_type: str` - Type of entity that failed validation
- `field_name: str` - Specific field that failed  
- `provided_value: Any` - What the user/system provided
- `error_message: str` - User-friendly error description
- `recovery_suggestion: str` - How to fix the issue

### ProcessingResult
**Purpose**: Capture outcomes for user reporting

**Attributes**:
- `successful_calculations: int` - Count of completed rate calculations
- `skipped_cells: List[str]` - Cell references that were skipped  
- `error_details: List[ValidationError]` - Any validation failures
- `execution_time_seconds: float` - Performance metrics
- `overall_status: str` - Success, partial success, or failure

This data model supports the constitutional requirements for clear interfaces, comprehensive error handling, and atomic function design while enabling the rate card calculation workflow.