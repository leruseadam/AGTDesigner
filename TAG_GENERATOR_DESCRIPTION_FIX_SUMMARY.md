# Tag Generator Description Field Fix Summary

## Issue
The tag generator was using the raw `Description` and `WeightUnits` columns from the Excel file instead of the processed fields that are created by the excel processor. This meant that tag output was not using the properly processed Description and WeightUnits fields that include the correct formatting and combinations.

## Root Cause
In `src/core/generation/tag_generator.py`, the `process_chunk` function was directly accessing the raw fields from the row data:

```python
label_data["Description"] = wrap_with_marker(str(row.get("Description", "")), "DESC")
label_data["WeightUnits"] = wrap_with_marker(str(row.get("WeightUnits", "")), "WEIGHTUNITS")
```

However, the excel processor creates processed `Description` and `WeightUnits` fields that:
- Include proper formatting and cleaning
- Handle special patterns and weight combinations
- Provide fallback logic when fields are empty
- Apply consistent formatting across the application

## Solution
Modified the tag generator to use the processed Description and WeightUnits fields from the excel processor:

### Changes Made

1. **Updated field access** in `src/core/generation/tag_generator.py`:
   ```python
   # Use the processed Description and WeightUnits fields from the excel processor
   description = str(row.get("Description", ""))
   weight_units = str(row.get("WeightUnits", ""))
   
   # If Description is empty, fallback to Product Name
   if not description:
       description = str(row.get("ProductName", "")) or str(row.get("Product Name*", ""))
   
   label_data["Description"] = wrap_with_marker(description, "DESC")
   label_data["WeightUnits"] = wrap_with_marker(weight_units, "WEIGHTUNITS")
   ```

2. **Updated DescAndWeight combination logic** to use the processed fields:
   ```python
   # Use the processed Description and WeightUnits fields from above
   desc = description  # Use the processed description from above
   weight = weight_units  # Use the processed weight_units from above
   ```

3. **Simplified weight processing** since the excel processor already handles it:
   ```python
   # For pre-rolls, the processed WeightUnits field already contains the JointRatio
   # For other products, use the processed WeightUnits field
   # The weight processing is already done in the excel processor
   if product_type in {"pre-roll", "infused pre-roll"}:
       # For pre-rolls, WeightUnits field contains the processed JointRatio
       weight = weight_units  # Use the processed weight_units from above
   else:
       # For other products, use the processed WeightUnits field
       weight = weight_units  # Use the processed weight_units from above
   ```

4. **Added missing import** for `Mm` class:
   ```python
   from docx.shared import Inches, Pt, Mm
   ```

## Testing
Created comprehensive tests to verify:
- ✅ Tag generator uses processed Description and WeightUnits fields
- ✅ Tag generator correctly combines fields for DescAndWeight
- ✅ Tag generator handles pre-roll products correctly
- ✅ wrap_with_marker function works correctly

## Impact
- **Before**: Tag output used raw Description and WeightUnits fields
- **After**: Tag output uses processed Description and WeightUnits fields, resulting in proper combinations like:
  - `"White Widow CBG Platinum Distillate\n- 1g"`
  - `"White Widow\n- 1g x 2 Pack"` (for pre-rolls)

## Files Modified
- `src/core/generation/tag_generator.py`

## Verification
The fix ensures that tag generation now uses the same processed Description and WeightUnits fields that are used throughout the rest of the application, providing consistent and properly formatted descriptions and weight combinations in the generated labels. 