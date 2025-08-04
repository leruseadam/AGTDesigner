# Edible Brand Label Fix Summary

## Issue Description
Edibles were showing "CBD" or "CBD Blend" in the yellow bars of the label content instead of the brand name. This was happening because both the Lineage and ProductStrain fields were being populated with lineage information (CBD) instead of brand information.

## Root Cause Analysis
The issue was in the `TemplateProcessor` class in `src/core/generation/template_processor.py`:

1. **Lineage Field**: The lineage processing logic was using the actual lineage value ("CBD") for edibles instead of the brand
2. **ProductStrain Field**: The ProductStrain field was being set to the actual strain value, which for edibles was often "CBD Blend" or similar lineage-based values
3. **Template Usage**: The horizontal template uses both `{{Label1.Lineage}}` and `{{Label1.ProductStrain}}` in the same cell, so both fields needed to be fixed

## Solution Implemented

### Backend Changes (`src/core/generation/template_processor.py`)

**Modified lineage processing logic** (lines 562-575):
```python
# For edibles, use brand instead of lineage
if product_type in edible_types:
    # Get brand directly from the record to avoid marker wrapping issues
    product_brand = record.get('ProductBrand', '') or record.get('Product Brand', '')
    if product_brand:
        lineage_value = product_brand.upper()
    else:
        lineage_value = label_context['Lineage']
```

**Modified ProductStrain processing logic** (lines 602-614):
```python
# For edibles, use brand instead of strain
if product_type in edible_types:
    product_brand = record.get('ProductBrand', '') or record.get('Product Brand', '')
    if product_brand:
        label_context['ProductStrain'] = product_brand.upper()
    else:
        label_context['ProductStrain'] = record.get('ProductStrain', '') or record.get('Product Strain', '')
else:
    # For non-edibles, use the actual strain
    label_context['ProductStrain'] = record.get('ProductStrain', '') or record.get('Product Strain', '')
```

## Product Type Classification

**Edible Types** (use brand instead of lineage):
- `edible (solid)`
- `edible (liquid)`
- `high cbd edible liquid`
- `tincture`
- `topical`
- `capsule`

**Non-Edible Types** (continue to use lineage):
- `flower`
- `pre-roll`
- `infused pre-roll`
- `concentrate`
- `solventless concentrate`
- `vape cartridge`
- `rso/co2 tankers`

## Testing Results

### Before Fix:
- Edibles showed: "CBD Blend" in yellow bars
- Non-edibles showed: "SATIVA", "INDICA", "HYBRID", etc. (correct)

### After Fix:
- Edibles show: "CONSTELLATION CANNABIS", "GRAVITY GUMMIES", etc. (brand names)
- Non-edibles show: "SATIVA", "INDICA", "HYBRID", etc. (unchanged)

## Files Modified

1. **`src/core/generation/template_processor.py`**:
   - Modified `_build_label_context()` method
   - Updated lineage processing for edibles
   - Updated ProductStrain processing for edibles

## Test Files Created

1. **`test_edible_label_content.py`**: Comprehensive test for edible vs non-edible label content
2. **`test_edible_debug_content.py`**: Detailed debug test to analyze document content
3. **`test_edible_filename_fix.py`**: Test for filename generation (already existed)

## Impact

- ✅ **Edibles now show brand names** instead of "CBD" in label content
- ✅ **Non-edibles continue to show lineage** as expected
- ✅ **Filename generation** already worked correctly (uses brand for edibles)
- ✅ **No breaking changes** to existing functionality

## Verification

The fix has been verified with comprehensive testing:
- Edible products with CBD lineage now show brand names in labels
- Non-edible products continue to show lineage information
- Both Lineage and ProductStrain fields are properly handled for edibles
- Template rendering works correctly for all product types 