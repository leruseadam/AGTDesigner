# LINEAGE FORMAT FIX

## Problem
Indica/Hybrid lineage values were returning as "HYBRID" instead of "HYBRID/INDICA". The lineage normalization logic was missing proper handling for forward slash formats.

## Root Cause
The `normalize_lineage()` function in both `excel_processor.py` and `product_database.py` only handled underscore formats:
- `'indica_hybrid': 'HYBRID/INDICA'` ✅
- `'sativa_hybrid': 'HYBRID/SATIVA'` ✅

But it was missing forward slash formats:
- `'indica/hybrid': 'HYBRID/INDICA'` ❌ (missing)
- `'sativa/hybrid': 'HYBRID/SATIVA'` ❌ (missing)

## Solution
Added missing lineage format mappings in three locations:

### 1. `src/core/data/excel_processor.py` (line 44-60)
```python
lineage_mapping = {
    'hybrid': 'HYBRID',
    'indica_hybrid': 'HYBRID/INDICA',
    'indica/hybrid': 'HYBRID/INDICA',  # FIX: Handle forward slash format
    'hybrid/indica': 'HYBRID/INDICA',  # FIX: Handle reverse format
    'indica': 'INDICA',
    'sativa': 'SATIVA',
    'sativa_hybrid': 'HYBRID/SATIVA',
    'sativa/hybrid': 'HYBRID/SATIVA',  # FIX: Handle forward slash format
    'hybrid/sativa': 'HYBRID/SATIVA',  # FIX: Handle reverse format
    'cbd': 'CBD',
    'mixed': 'HYBRID',
    'unknown': 'HYBRID',
    'none': 'HYBRID',
    '': 'HYBRID'
}
```

### 2. `src/core/data/product_database.py` (line 2841-2857)
Same mapping added to the database normalization function.

### 3. `app.py` (line 2123-2134)
```python
df['Lineage'] = df['Lineage'].replace({
    'INDICA_HYBRID': 'HYBRID/INDICA',
    'INDICA/HYBRID': 'HYBRID/INDICA',  # FIX: Handle forward slash format
    'HYBRID/INDICA': 'HYBRID/INDICA',  # FIX: Handle correct format
    'SATIVA_HYBRID': 'HYBRID/SATIVA',
    'SATIVA/HYBRID': 'HYBRID/SATIVA',  # FIX: Handle forward slash format
    'HYBRID/SATIVA': 'HYBRID/SATIVA',  # FIX: Handle correct format
    # ... other mappings
})
```

## Expected Results
- ✅ "Indica/Hybrid" → "HYBRID/INDICA" (instead of "HYBRID")
- ✅ "Sativa/Hybrid" → "HYBRID/SATIVA" (instead of "HYBRID")
- ✅ "Hybrid/Indica" → "HYBRID/INDICA"
- ✅ "Hybrid/Sativa" → "HYBRID/SATIVA"
- ✅ All existing formats continue to work

## Testing
1. Upload Excel file with "Indica/Hybrid" lineage values
2. Check that tags show "HYBRID/INDICA" instead of "HYBRID"
3. Verify combination lineage types display correctly in generated tags

## Files Modified
- `src/core/data/excel_processor.py` - Added forward slash format mappings
- `src/core/data/product_database.py` - Added forward slash format mappings  
- `app.py` - Added forward slash format mappings in background processing
