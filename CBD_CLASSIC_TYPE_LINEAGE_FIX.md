# CBD Classic Type Lineage Fix

## Problem Identified
CBD classic types (like "CBD Huckleberry Web" flower) were missing proper CBD lineage assignment, resulting in:
- **HYBRID lineage** instead of **CBD lineage** for classic CBD products
- **Green color styling** instead of **yellow CBD color styling**
- Incorrect product categorization for classic CBD products

## Root Cause Analysis
1. **Vectorized operations were disabled** (`ENABLE_VECTORIZED_OPERATIONS = False`)
2. **CBD detection logic only handled non-classic types** 
3. **Classic CBD products** like "CBD Huckleberry Web" weren't being detected as CBD products
4. **Missing CBD lineage assignment** for classic product types with "CBD" in the product name

## Solution Implemented

### 1. Enable Vectorized Operations
```python
ENABLE_VECTORIZED_OPERATIONS = True  # ENABLED: For CBD classic type detection
```

### 2. Enhanced CBD Detection for Classic Types
Added detection from **both** Product Strain AND Product Name for classic types:
```python
# CRITICAL FIX: Enhanced CBD detection for classic types
cbd_from_name_mask = pd.Series([False] * len(df), index=df.index)
if 'Product Name*' in df.columns:
    product_names = df['Product Name*'].astype(str)
    cbd_from_name_mask = product_names.str.contains(r'\bCBD\b', case=False, na=False)

# For classic types with CBD in product name, assign CBD lineage
classic_cbd_mask = classic_mask & cbd_from_name_mask
result[classic_cbd_mask] = 'CBD'
```

### 3. Classic Type CBD Assignment Priority
```python
# Set default lineage for classic types with empty lineage (HYBRID) - but only if not CBD
classic_default_mask = classic_mask & empty_lineage_mask & ~cbd_from_name_mask
result[classic_default_mask] = 'HYBRID'
```

## Results Verified by Testing

✅ **CBD Huckleberry Web - 1g** (flower) → **CBD lineage** → **Yellow styling**  
✅ **CBD Pre-Roll** → **CBD lineage** → **Yellow styling**  
✅ **CBD Concentrate** → **CBD lineage** → **Yellow styling**  
✅ **Regular flower products** → **Existing lineage preserved** → **Correct styling**  
✅ **CBD Gummy** (edible) → **CBD/MIXED lineage** → **Blue/Yellow styling** (correct for non-classic)

## Test Coverage
Created comprehensive test suite (`test_cbd_classic_lineage_fix.py`) that verifies:
- CBD classic types get CBD lineage
- Regular classic types keep HYBRID/SATIVA/INDICA lineage  
- CBD edibles get appropriate lineage (conservative approach)
- Edge cases like "Subcbd" (substring) correctly rejected
- Word boundary detection (`\bCBD\b`) working properly

## Files Modified
- `src/core/data/excel_processor.py`
  - Enabled `ENABLE_VECTORIZED_OPERATIONS` 
  - Enhanced `optimized_lineage_assignment()` function
  - Added classic type CBD detection logic
  - Fixed undefined variable reference

## Impact
- **CBD flower, pre-rolls, concentrates, vape cartridges** now display with proper **yellow CBD styling**
- **CBD lineage** is correctly assigned to classic CBD products
- **Template styling** now correctly identifies CBD classic types
- **No regression** for regular classic or non-classic products
- **Backward compatibility** maintained for existing products

## Deployment Notes
- Changes require application restart to take effect
- No database migration required
- Existing products will be re-processed with new logic on next data load
- Test script included for verification

## Validation
Run the test script to verify the fix:
```bash
python test_cbd_classic_lineage_fix.py
```

---

**Status: ✅ FIXED**  
**Date: October 14, 2025**  
**Issue: CBD classic type lineage missing**  
**Solution: Enhanced CBD detection for classic product types**