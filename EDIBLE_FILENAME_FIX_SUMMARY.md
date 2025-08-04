# Edible Filename Fix Summary

## Issue Description
Edibles were using lineage instead of brand in the filename generation. When generating labels for edible products, the filename would include the lineage abbreviation (e.g., "MIX" for Mixed) instead of the brand name, which was not the desired behavior.

## Root Cause
The filename generation logic in `app.py` was using a single format for all product types:

```python
filename = f"AGT_{vendor_clean}_{template_display}_{lineage_abbr}_{product_type_clean}_{tag_count}{tag_suffix}_{today_str}_{time_str}.docx"
```

This meant that all products, including edibles, would use the lineage abbreviation in the filename.

## Solution Implemented

### Backend Changes (`app.py`)

**Modified filename generation logic** to differentiate between edibles and non-edibles:

1. **Added edible type detection**:
   ```python
   edible_types = {"edible (solid)", "edible (liquid)", "high cbd edible liquid", "tincture", "topical", "capsule"}
   is_edible = primary_product_type.lower() in edible_types
   ```

2. **Conditional filename generation**:
   ```python
   if is_edible:
       # For edibles, use brand instead of lineage
       filename = f"AGT_{vendor_clean}_{template_display}_{vendor_clean}_{product_type_clean}_{tag_count}{tag_suffix}_{today_str}_{time_str}.docx"
   else:
       # For non-edibles, use lineage as before
       filename = f"AGT_{vendor_clean}_{template_display}_{lineage_abbr}_{product_type_clean}_{tag_count}{tag_suffix}_{today_str}_{time_str}.docx"
   ```

3. **Enhanced debug logging** to include the `is_edible` flag for better troubleshooting.

### Example Filename Changes

**Before (Edibles)**:
```
AGT_CERES_HORIZ_MIX_Edible_Solid_235tags_20250720_044511.docx
```

**After (Edibles)**:
```
AGT_CERES_HORIZ_CERES_Edible_Solid_235tags_20250720_044511.docx
```

**Non-Edibles (Unchanged)**:
```
AGT_VENDOR_HORIZ_MIX_Flower_50tags_20250720_044511.docx
```

## Benefits

1. **Better Organization**: Edible filenames now clearly indicate the brand instead of generic lineage
2. **Consistent Logic**: Edibles use brand (which is more relevant for edibles), while non-edibles use lineage (which is more relevant for cannabis products)
3. **Improved Searchability**: Users can easily identify edible files by brand name in the filename
4. **Maintained Compatibility**: Non-edible products continue to use the existing lineage-based naming

## Testing

Created `test_edible_filename_fix.py` to verify:
- Edibles use brand in filename
- Non-edibles continue to use lineage in filename
- Both product types generate valid filenames

## Files Modified

- `app.py`: Updated filename generation logic
- `test_edible_filename_fix.py`: New test script
- `EDIBLE_FILENAME_FIX_SUMMARY.md`: This documentation

## Impact

This change affects only the filename generation for edible products. The actual label content and functionality remain unchanged. Users will now see more descriptive filenames for edible products that include the brand name instead of the generic lineage. 