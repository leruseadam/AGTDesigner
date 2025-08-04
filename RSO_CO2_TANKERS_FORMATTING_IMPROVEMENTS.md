# RSO/CO2 Tankers Formatting Improvements

## Overview
Enhanced the formatting for RSO/CO2 Tankers products to match the requirements:
1. **Product Brand centering** - Applied to RSO/CO2 Tankers category
2. **Actual Ratio formatting** - Same as edibles (line breaks after every 2nd space)
3. **Weight in grams** - RSO/CO2 Tankers now stay in grams instead of converting to ounces

## Changes Made

### 1. Weight Formatting (Grams Instead of Ounces)
**File Modified:** `src/core/data/excel_processor.py`

**Changes:**
- Modified the `_format_weight_units` method to keep RSO/CO2 Tankers weight in grams
- Added special handling for "rso/co2 tankers" product type to bypass the g→oz conversion
- Other edibles still convert grams to ounces as before

**Before:**
```python
if product_type in edible_types and units_val in {"g", "grams"} and weight_val is not None:
    weight_val = weight_val * 0.03527396195
    units_val = "oz"
```

**After:**
```python
# For RSO/CO2 Tankers, keep weight in grams instead of converting to ounces
if product_type == "rso/co2 tankers" and units_val in {"g", "grams"} and weight_val is not None:
    # Keep in grams for RSO/CO2 Tankers
    pass
elif product_type in edible_types and units_val in {"g", "grams"} and weight_val is not None:
    weight_val = weight_val * 0.03527396195
    units_val = "oz"
```

### 2. Product Brand Centering
**File Modified:** `src/core/generation/template_processor.py`

**Changes:**
- Added `_add_brand_markers_for_rso_co2_tankers()` method to ensure RSO/CO2 Tankers get Product Brand centering on all template types
- Modified `_post_process_and_replace_content()` to call the new method for all template types
- RSO/CO2 Tankers now get `PRODUCTBRAND_CENTER` markers applied regardless of template type

**New Method:**
```python
def _add_brand_markers_for_rso_co2_tankers(self, doc):
    """
    Add PRODUCTBRAND_CENTER markers around brand content specifically for RSO/CO2 Tankers.
    This ensures RSO/CO2 Tankers get Product Brand centering on all template types.
    """
```

### 3. Ratio Formatting (Already Working)
**Status:** ✅ Already implemented correctly

RSO/CO2 Tankers were already included in the `edible_types` set, so they automatically get the same ratio formatting as edibles:
- Line breaks after every 2nd space
- Example: "THC 10mg CBD 5mg CBG 2mg" → "THC 10mg\nCBD 5mg\nCBG 2mg"

## Testing Results

### Weight Formatting Test
✅ **RSO/CO2 Tankers**: 1g → 1g (stays in grams)
✅ **Edible (solid)**: 1g → 0.04oz (converts to ounces)
✅ **Flower**: 3.5g → 3.5g (unchanged)

### Ratio Formatting Test
✅ **Original**: "THC 10mg CBD 5mg CBG 2mg"
✅ **Formatted**: "THC 10mg\nCBD 5mg\nCBG 2mg"
✅ **Line breaks**: Applied correctly after every 2nd space

### Product Brand Centering Test
✅ **RSO/CO2 Tankers**: Recognized as edible type
✅ **Brand markers**: Applied for centering on all template types
✅ **Font sizing**: Uses unified font sizing system

### Tag Generation Test
✅ **Available tags**: Generated correctly with proper formatting
✅ **Selected records**: Weight and ratio formatting applied correctly
✅ **Product type recognition**: RSO/CO2 Tankers properly identified

## Benefits

1. **Consistent Weight Display**: RSO/CO2 Tankers now display weight in grams as requested
2. **Proper Brand Centering**: Product Brand is centered for RSO/CO2 Tankers on all template types
3. **Edible-Style Ratio Formatting**: Ratios display with proper line breaks for better readability
4. **Maintained Compatibility**: Other product types continue to work as before
5. **Unified Formatting**: RSO/CO2 Tankers get the same professional formatting as other edibles

## Backward Compatibility

- ✅ All existing functionality preserved
- ✅ Other edibles still convert grams to ounces
- ✅ Classic product types unchanged
- ✅ All tests pass
- ✅ No breaking changes to existing data

## Files Modified

1. **`src/core/data/excel_processor.py`**
   - Modified `_format_weight_units()` method for gram retention

2. **`src/core/generation/template_processor.py`**
   - Added `_add_brand_markers_for_rso_co2_tankers()` method
   - Modified `_post_process_and_replace_content()` to call new method

3. **`test_rso_co2_tankers_formatting.py`** (new)
   - Comprehensive test for all formatting improvements

The RSO/CO2 Tankers category now has the exact formatting requested: Product Brand centering, edible-style ratio formatting, and weight displayed in grams. 