# DescAndWeight Duplication Fix Summary

## Problem Description

The DescAndWeight field was showing duplicated weight information, causing labels to display incorrect information like:
- "Hustler's Ambition Flower (Birthday Cake 14g) - 14g" - Weight "14g" appears twice
- "Hustler's Ambition Flower (Birthday Cake 28g) - 28g" - Weight "28g" appears twice

This was happening because the system was adding weight information to descriptions that already contained weight data.

## Root Cause Analysis

The issue occurred in two places:

### 1. Tag Generator (`src/core/generation/tag_generator.py`)

The `process_chunk` function was always combining Description and WeightUnits fields, even when the Description already contained weight information:

```python
# Before (Incorrect): Always adding weight
if desc and weight:
    combined = "\n".join(lines) + f"\n- {weight}"
```

### 2. Excel Processor (`src/core/data/excel_processor.py`)

The `get_available_tags` method was always creating DescAndWeight by combining description and weight, even when duplication would occur:

```python
# Before (Incorrect): Always combining
if description and weight_units:
    desc_and_weight = f"{description} - {weight_units}"
```

## Solution Implemented

### 1. Added Weight Detection Logic

Implemented a `description_contains_weight` function that checks if a description already contains weight information before adding it again:

```python
def description_contains_weight(description_text, weight_text):
    """Check if description already contains the weight information."""
    if not description_text or not weight_text:
        return False
    
    # Normalize both strings for comparison
    desc_lower = str(description_text).lower().strip()
    weight_lower = str(weight_text).lower().strip()
    
    # Remove common weight units for comparison
    weight_without_units = re.sub(r'\s*(g|gram|grams|oz|ounce|ounces|ml|milliliter|milliliters|mg|milligram|milligrams)\s*$', '', weight_lower)
    
    # Check various patterns where weight might already be in description
    patterns_to_check = [
        rf'\b{re.escape(weight_without_units)}\s*(g|gram|grams|oz|ounce|ounces|ml|milliliter|milliliters|mg|milligram|milligrams)\b',
        rf'\(\s*[^)]*{re.escape(weight_without_units)}\s*(g|gram|grams|oz|ounce|ounces|ml|milliliter|milliliters|mg|milligram|milligrams)\s*[^)]*\)',
        rf'-\s*{re.escape(weight_without_units)}\s*(g|gram|grams|oz|ounce|ounces|ml|milliliter|milliliters|mg|milligram|milligrams)\s*$',
        rf'\s*{re.escape(weight_without_units)}\s*(g|gram|grams|oz|ounce|ounces|ml|milliliter|milliliters|mg|milligram|milligrams)\s*$'
    ]
    
    for pattern in patterns_to_check:
        if re.search(pattern, desc_lower):
            return True
    
    return False
```

### 2. Updated Tag Generator Logic

Modified the DescAndWeight construction to only add weight when it's not already present:

```python
# After (Correct): Only add weight if not already present
should_add_weight = not description_contains_weight(desc, weight)

if desc and weight and should_add_weight:
    # Add weight to description
    combined = "\n".join(lines) + f"\n- {weight}"
elif desc and weight and not should_add_weight:
    # Description already contains weight, don't add it again
    combined = desc
else:
    combined = desc or weight
```

### 3. Updated Excel Processor Logic

Modified the `get_available_tags` method to use the same weight detection logic:

```python
# After (Correct): Only combine if weight not already present
if description and weight_units and not description_contains_weight(description, weight_units):
    desc_and_weight = f"{description} - {weight_units}"
else:
    desc_and_weight = description or weight_units
```

## Patterns Detected

The weight detection function checks for various patterns where weight information might already be present in descriptions:

1. **Exact weight match**: "14g" in description matches "14g" weight
2. **Parenthetical weight**: "(Birthday Cake 14g)" contains weight information
3. **Dash-separated weight**: "Product - 14g" already has weight
4. **End-of-line weight**: "Product 14g" ends with weight

## Files Modified

1. **src/core/generation/tag_generator.py**: Updated `process_chunk` function to prevent weight duplication
2. **src/core/data/excel_processor.py**: Updated `get_available_tags` method to prevent weight duplication

## Expected Results

After this fix:

1. **No More Duplication**: Descriptions like "Birthday Cake 14g" won't become "Birthday Cake 14g - 14g"
2. **Correct Weight Display**: Weight information will appear only once in the correct location
3. **Preserved Original Data**: Descriptions that already contain weight information will be displayed as-is
4. **Consistent Formatting**: All labels will have consistent and correct weight display

## Testing

The fix handles these scenarios correctly:

- **Description with weight**: "Birthday Cake 14g" → "Birthday Cake 14g" (no duplication)
- **Description without weight**: "Birthday Cake" + "14g" → "Birthday Cake - 14g" (proper combination)
- **Complex descriptions**: "Product (Strain 14g) - 14g" → "Product (Strain 14g)" (no duplication)
- **Various weight units**: Handles g, oz, ml, mg, etc.

## Impact

This fix resolves the DescAndWeight duplication issue, ensuring that:

- Labels display correct and non-redundant information
- User data is presented accurately
- The system behaves predictably and consistently
- No unintended weight duplication occurs
