# Double Template Duplication Fix Summary

## Issue
The double template was showing duplicated product names like "Afghani Kush Wax Wax -1g" instead of the correct "Afghani Kush Wax -1g". This was happening because the Description field was being set to the full product name including the weight, and then the weight was being added again during template processing.

## Root Cause
The issue was in the Description field processing in `src/core/data/excel_processor.py`. The code was:

1. **Setting Description to full ProductName**: The Description field was being set to the complete product name including the weight (e.g., "Afghani Kush Wax -1g")

2. **Incorrect dash pattern matching**: The code was looking for `' - '` (space-dash-space) but the actual data contained just `'-'` (dash without spaces)

3. **Weight duplication in template processing**: In the tag generator, the Description was being combined with the weight again, causing duplication

## Solution

### 1. Fixed Dash Pattern Matching
**File**: `src/core/data/excel_processor.py`  
**Lines**: 1290-1295

Updated the dash pattern matching to handle both `' - '` and `'-'` patterns:

```python
# Handle ' - ' pattern - remove weight part from Description to prevent duplication
mask_dash = self.df["Description"].str.contains(' - ', na=False)
# Also check for just '-' without spaces
mask_single_dash = self.df["Description"].str.contains('-', na=False)
# Remove weight part from Description for all types to prevent duplication
# The weight will be added back in the tag generator using the WeightUnits field
if mask_dash.any():
    self.df.loc[mask_dash, "Description"] = self.df.loc[mask_dash, "Description"].str.rsplit(' - ', n=1).str[0].str.strip()
if mask_single_dash.any():
    self.df.loc[mask_single_dash, "Description"] = self.df.loc[mask_single_dash, "Description"].str.rsplit('-', n=1).str[0].str.strip()
```

### 2. Updated Processing Logic
**File**: `src/core/data/excel_processor.py`  
**Lines**: 1280-1285

Modified the Description processing to remove weight parts for all product types, not just non-classic types:

```python
# Set Description to ProductName values, but remove weight part to prevent duplication
self.df["Description"] = product_names.str.strip()
```

## Testing Results

### Before Fix
- Description field contained: "Afghani Kush Wax -1g"
- Template output showed: "Afghani Kush Wax Wax -1g" (duplicated)

### After Fix
- Description field contains: "Afghani Kush Wax" (weight removed)
- Template output shows: "Afghani Kush Wax -1g" (correct)

## Verification
Created and ran comprehensive tests that verify:
- ✅ Description field correctly removes weight part
- ✅ No duplication in double template output
- ✅ Weight is properly added back during template processing
- ✅ All product types are handled correctly

## Impact
This fix resolves the double template duplication issue while maintaining compatibility with all other template types. The weight information is still preserved and displayed correctly, but it's no longer duplicated in the product names.

## Files Modified
- `src/core/data/excel_processor.py` - Fixed Description field processing
- `test_double_template_fix.py` - Added comprehensive test
- `debug_description_fix.py` - Added debug script for verification 