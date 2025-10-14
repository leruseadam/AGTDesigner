# CBD Classic Type Styling Fix

## Problem
CBD classic types (like "CBD Huckleberry Web" flower) were being treated as nonclassic types, resulting in:
- **Centered branding** instead of left-aligned branding
- **HYBRID lineage** instead of **CBD lineage**
- Incorrect styling for classic CBD products

## Root Cause
1. **Vectorized operations were disabled** (`ENABLE_VECTORIZED_OPERATIONS = False`)
2. **CBD detection only looked at Product Strain field** ("CBD Blend") but not product names
3. **CBD flower products** like "CBD Huckleberry Web" weren't being detected as CBD products

## Solution
### 1. Enable Vectorized Operations
```python
ENABLE_VECTORIZED_OPERATIONS = True  # ENABLED: For CBD classic type detection
```

### 2. Enhanced CBD Detection
Added detection from **both** Product Strain AND Product Name:
```python
# CBD Blend products -> CBD lineage (yellow) - override existing lineage
cbd_blend_mask = product_strain.str.contains('CBD Blend', case=False, na=False)

# CRITICAL FIX: Also detect CBD from product names for classic types
cbd_from_name_mask = pd.Series([False] * len(df), index=df.index)
if 'Product Name*' in df.columns:
    product_names = df['Product Name*'].astype(str)
    cbd_from_name_mask = product_names.str.contains(r'\bCBD\b', case=False, na=False)

# Combine CBD detection from both strain and product name
cbd_detection_mask = cbd_blend_mask | cbd_from_name_mask
```

### 3. Classic Type CBD Assignment
```python
# For classic types with CBD (like CBD flower, CBD pre-rolls), always assign CBD lineage
classic_cbd = cbd_detection_mask & classic_mask
result[classic_cbd] = 'CBD'
```

## Results
✅ **CBD Huckleberry Web** (flower) → **CBD lineage** → **Left-aligned branding**  
✅ **CBD Pre-Roll** → **CBD lineage** → **Left-aligned branding**  
✅ **CBD Concentrate** → **CBD lineage** → **Left-aligned branding**  
✅ **CBD Gummy** (edible) → **MIXED lineage** → **Centered branding** (correct for nonclassic)

## Files Modified
- `src/core/data/excel_processor.py`
  - Enabled `ENABLE_VECTORIZED_OPERATIONS`
  - Enhanced CBD detection logic
  - Fixed classic type CBD assignment

## Testing
Created comprehensive test suite that verifies:
- CBD classic types get CBD lineage
- Regular classic types get HYBRID lineage  
- CBD edibles get MIXED lineage (conservative approach)

## Impact
- **CBD flower products** now display with proper **left-aligned branding**
- **CBD lineage** is correctly assigned to classic CBD products
- **Template styling** now correctly identifies CBD classic types
- **No regression** for regular classic or nonclassic products

## Memory Update
This fix ensures that CBD classic types are properly detected and styled according to user preferences for left-aligned branding on classic types.