# JSON Match - DOH Handling and Description Values Fix

## Summary
Fixed JSON matcher to properly handle DOH values, Description field, Price, and Product Type according to Excel Priority rules and intelligent product type detection.

## Issues Fixed

### 1. Hardcoded DOH Values (Line 3174)
**Problem**: All unmatched JSON products were getting `DOH = 'YES'` regardless of product type.

**Solution**: Implemented intelligent `_determine_doh_value()` function that determines DOH based on product type:
- **High CBD products** → `DOH = 'CBD'`
- **Classic types** (flower, pre-roll, concentrates, vapes) → `DOH = 'THC'`
- **High THC products** → `DOH = 'THC'`
- **Non-classic types** (edibles, tinctures, topicals) → `DOH = 'YES'`
- **Unknown types** → `DOH = 'THC'` (default)

### 2. Excel Priority Fields
**Enhanced**: Added comments and proper field mapping to ensure Excel Priority rules are followed:
- **Description**: Always reflects Product Name* (line 3141)
- **Product Type***: Always from inferred/mapped data (line 3144)
- **Price**: Always from intelligent price matching (line 3153)
- **DOH**: Always determined by product type (line 3182)

### 3. Field Consistency
**Added**: Missing duplicate fields for consistency:
- `ProductType` (line 3145)
- `ProductBrand` (line 3147)
- `ProductStrain` (line 3149)
- `Vendor/Supplier*` (line 3152)
- `Price*` (line 3154)

## Changes Made

### File: `src/core/data/json_matcher.py`

#### New Function: `_determine_doh_value()` (Lines 9561-9614)
```python
def _determine_doh_value(self, product_type: str, product_name: str = '') -> str:
    """
    Determine the appropriate DOH value based on product type.
    
    Returns:
        DOH value string: 'THC', 'CBD', 'YES', or 'NO'
    """
```

**Logic**:
1. **High CBD Detection**:
   - Product type contains "high cbd" or "highcbd" → 'CBD'
   - Product type contains "cbd" but not "thc" → 'CBD'

2. **Classic Types** (THC designation):
   - Flower, bud, pre-roll, blunt, joint
   - Concentrates: wax, shatter, rosin, resin, hash
   - Vapes: cartridge, pen, disposable, distillate
   - Returns: 'THC'

3. **High THC Detection**:
   - Product type contains "high thc" or "highthc" → 'THC'

4. **Non-Classic Types** (Generic DOH):
   - Edibles, tinctures, topicals, capsules
   - Returns: 'YES'

5. **Default Fallback**:
   - Unknown or empty product type → 'THC'

#### Updated Function: `_create_product_from_json()` (Lines 3134-3185)

**Before**:
```python
'DOH': 'YES',  # JSON matched products should show DOH compliance stamp
```

**After**:
```python
# Determine DOH value based on product type (proper DOH handling)
doh_value = self._determine_doh_value(final_assigned_type, cleaned_product_name)

product = {
    ...
    'Description': cleaned_product_name,  # EXCEL PRIORITY: Description reflects product name
    'Product Type*': final_assigned_type,  # EXCEL PRIORITY: Product Type from inferred/mapped data
    'ProductType': final_assigned_type,
    'Price': final_price,  # EXCEL PRIORITY: Price from intelligent matching
    'Price*': final_price,
    ...
    'DOH': doh_value,  # EXCEL PRIORITY: DOH value based on product type (THC/CBD/YES/NO)
    'DOH Compliant (Yes/No)': 'Yes' if doh_value in ['YES', 'THC', 'CBD'] else 'No',
}
```

## How It Works

### For Matched JSON Products (Excel/Database Match):
1. DOH comes directly from matched Excel/database record (line 2894, 2962)
2. Description comes from Excel/database record (line 2876, 2917)
3. Product Type* comes from Excel/database record (line 2881, 2930)
4. Price comes from Excel/database record (line 2886, 2939)

### For Unmatched JSON Products (JSON Only):
1. DOH is determined by `_determine_doh_value()` based on product type (line 3182)
2. Description is set to cleaned product name (line 3141)
3. Product Type* is from inferred/mapped data (line 3144)
4. Price is from intelligent price matching (line 3153)

## DOH Value Examples

| Product Type | DOH Value | Reason |
|-------------|-----------|--------|
| `flower` | `THC` | Classic type |
| `High CBD flower` | `CBD` | High CBD type |
| `pre-roll` | `THC` | Classic type |
| `cartridge` | `THC` | Classic vape type |
| `wax` | `THC` | Classic concentrate type |
| `edible (solid)` | `YES` | Non-classic type |
| `tincture` | `YES` | Non-classic type |
| `topical` | `YES` | Non-classic type |
| `High CBD tincture` | `CBD` | High CBD type |
| `High THC edible` | `THC` | High THC type |

## Impact

### Benefits
✅ **Correct DOH Images**: Labels now show appropriate compliance images (High THC, High CBD, or generic)
✅ **Excel Priority Maintained**: Description, Price, and Product Type follow Excel priority rules
✅ **Intelligent Defaults**: Unmatched JSON products get intelligent DOH values based on product type
✅ **Field Consistency**: All field variations (Price/Price*, ProductType/Product Type*, etc.) are populated
✅ **No Hardcoded Values**: DOH is dynamic based on actual product characteristics

### Testing Recommendations
1. **Test High CBD Products**: Verify High CBD image appears for High CBD products
2. **Test Classic Types**: Verify High THC image appears for flower, pre-rolls, concentrates, vapes
3. **Test Non-Classic Types**: Verify generic DOH image appears for edibles, tinctures, topicals
4. **Test Matched Products**: Verify matched products use DOH from database
5. **Test Unmatched Products**: Verify unmatched products get correct DOH based on product type
6. **Test Description**: Verify Description field correctly reflects product name
7. **Test Price/Product Type**: Verify these fields are populated from correct sources

## Related Documentation
- `EXCEL_PRIORITY_FOR_DOH_PRICE_PRODUCTTYPE.md` - Excel priority rules for these fields
- `VENDOR_ISOLATION_FIX.md` - Cross-brand contamination prevention

## Files Modified
- `src/core/data/json_matcher.py`
  - Added `_determine_doh_value()` function (lines 9561-9614)
  - Updated `_create_product_from_json()` function (lines 3134-3185)
  - Added Excel Priority comments for clarity

## Date
November 7, 2025

