# Excel Lineage Removal - Complete Fix

## Problem
User reported "still uses excel db" - Excel lineage values were still appearing in the UI despite previous fixes to use database lineage.

## Root Cause
Excel lineage was being **set at tag creation time** in `excel_processor.py`, before being stripped or overwritten by database values. This meant:
1. Tags were created with Excel lineage values
2. App.py would strip these after loading (line 10272-10276)
3. Background fetch would overwrite with DB values (main.js 11489-11522)
4. But there was a window where Excel values existed, and they might persist in some cases

## Solution
**Removed ALL Excel lineage at source** - tags are never created with Excel lineage values. Lineage is now:
- Set to 'MIXED' placeholder during tag creation
- Only populated from database via:
  - `_align_tags_with_db_lineage()` (when fast_load=0)
  - Background fetch with fast_load=0 (main.js)

## Changes Made

### Files Modified:
1. `/Users/adamcordova/Desktop/labelMaker_ QR copy final/src/core/data/excel_processor.py`
2. `/Users/adamcordova/Desktop/labelMaker_ QR copy final/core/data/excel_processor.py` (backup)

### Specific Changes (Applied to Both Files):

#### Location 1: Line ~3498-3548 (minimal_load_file method)
**Before:**
```python
'lineage': get_val('Lineage') or 'MIXED',

# Sanitize lineage - prioritize existing lineage, fall back to inference from name
existing_lineage = get_val('Lineage').strip().upper() if get_val('Lineage') else ''
if existing_lineage and existing_lineage in VALID_LINEAGES:
    lineage = existing_lineage
else:
    # No valid lineage column - infer from product name and type
    product_type_for_inference = get_val('Product Type*')
    lineage = self._infer_lineage_from_name(product_name, product_type_for_inference)
```

**After:**
```python
# CRITICAL: DO NOT include Excel lineage - lineage ONLY comes from database
# 'lineage': get_val('Lineage') or 'MIXED',  # REMOVED - database only

# CRITICAL: Excel lineage inference REMOVED - lineage ONLY comes from database
# Excel lineage column and name-based inference are completely ignored
# Lineage will be populated by _align_tags_with_db_lineage() or background fetch
lineage = 'MIXED'  # Placeholder - will be replaced by database lineage
```

#### Location 2: Line ~7860 (pythonanywhere_fast_load method)
**Before:**
```python
'Lineage': get_val('Lineage') or 'MIXED',
```

**After:**
```python
# CRITICAL: DO NOT include Excel lineage - lineage ONLY comes from database
# 'Lineage': get_val('Lineage') or 'MIXED',  # REMOVED - database only
```

#### Location 3: Line ~7890-7915 (pythonanywhere_fast_load method continued)
**Before:**
```python
'lineage': get_val('Lineage') or 'MIXED',

# Sanitize lineage - prioritize existing lineage, fall back to inference from name
existing_lineage = get_val('Lineage').strip().upper() if get_val('Lineage') else ''
if existing_lineage and existing_lineage in VALID_LINEAGES:
    lineage = existing_lineage
else:
    # No valid lineage column - infer from product name and type
    product_type_for_inference = get_val('Product Type*')
    lineage = self._infer_lineage_from_name(product_name, product_type_for_inference)
```

**After:**
```python
# CRITICAL: DO NOT include Excel lineage - lineage ONLY comes from database
# 'lineage': get_val('Lineage') or 'MIXED',  # REMOVED - database only

# CRITICAL: Excel lineage inference REMOVED - lineage ONLY comes from database
# Excel lineage column and name-based inference are completely ignored
# Lineage will be populated by _align_tags_with_db_lineage() or background fetch
lineage = 'MIXED'  # Placeholder - will be replaced by database lineage
```

## Lineage Flow (After Fix)

### 1. Tag Creation (excel_processor.py)
```python
tag['Lineage'] = 'MIXED'  # Placeholder only
tag['lineage'] = 'MIXED'  # Placeholder only
```

### 2. Fast Load (fast_load=1) - Initial Response
- Tags load instantly with lineage = 'MIXED'
- No database enrichment (skip_db_enrichment = True)
- Lineage colors will be gray/neutral

### 3. Background Fetch (main.js, lines 11489-11522)
- After initial load, triggers fetch with fast_load=0
- Database enrichment runs (skip_db_enrichment = False)
- Database lineage overwrites 'MIXED' placeholder
- Priority: sovereign_lineage > canonical_lineage > currentLineage
- UI updates with correct lineage colors

### 4. Database Alignment (app.py, when fast_load=0)
```python
# Line 10455-10468: _align_tags_with_db_lineage()
if not skip_db_enrichment:
    _align_tags_with_db_lineage(tags, product_db, ...)
    # Populates lineage from database ONLY
```

## Verification

### Excel Lineage References (Should Only Be Commented):
```bash
grep -n "get_val('Lineage')" src/core/data/excel_processor.py
# All results should be comments starting with #
```

### Expected Results:
- Line 3528: `# 'lineage': get_val('Lineage') or 'MIXED',  # REMOVED - database only`
- Line 7858: `# 'Lineage': get_val('Lineage') or 'MIXED',  # REMOVED - database only`
- Line 7889: `# 'lineage': get_val('Lineage') or 'MIXED',  # REMOVED - database only`

### Database Lineage Only:
```bash
grep -n "sovereign_lineage\|canonical_lineage\|currentLineage" app.py
```

## Testing

### Test 1: Verify Excel Lineage is Ignored
1. Upload Excel file with Lineage column containing values
2. Check network response for /api/available-tags?fast_load=1
3. **Expected**: All lineage values should be 'MIXED'
4. Wait 2 seconds for background fetch
5. **Expected**: Lineage values updated from database, NOT Excel

### Test 2: Verify Database is Only Source
1. Update lineage in database via UI
2. Refresh tags
3. **Expected**: Updated lineage appears immediately (from cache or background fetch)
4. Excel lineage column completely ignored

### Test 3: Verify Lineage Priority
1. Product with sovereign_lineage='INDICA' in database
2. Excel has Lineage='SATIVA'
3. **Expected**: Tag displays INDICA (database wins)

## Benefits

1. **Single Source of Truth**: Database is the ONLY lineage source
2. **No Excel Interference**: Excel lineage column completely ignored
3. **Consistent Behavior**: Lineage always comes from same place
4. **Performance Maintained**: Fast load still instant (lineage added later)
5. **Clear Intent**: Comments explain why Excel lineage is removed

## Related Files

### Previous Fixes (Still Active):
- **app.py (line 10267)**: `skip_db_enrichment = fast_load` (always skip for fast_load=1)
- **app.py (line 10272-10276)**: Strip Excel lineage after loading (now redundant but kept as safeguard)
- **main.js (line 11489-11522)**: Background fetch with fast_load=0 to get database lineage

### Lineage Database Tables:
- **ProductCoreInfo**: sovereign_lineage (user-edited, highest priority)
- **ProductPublicData**: canonical_lineage (from public database)
- **ProductEntry**: currentLineage (legacy field)

## Deployment

1. Deploy updated `excel_processor.py` to PythonAnywhere
2. No need to clear cache (tags will be recreated on next upload)
3. Existing cached tags will be updated by background fetch
4. Test with Excel file containing Lineage column to verify it's ignored

## Summary

✅ Excel lineage completely removed from tag creation
✅ All lineage inference logic removed
✅ Database is now the ONLY source of lineage data
✅ Fast load performance maintained (instant with 'MIXED', updated via background fetch)
✅ User can confidently update lineage in UI knowing it won't be overridden by Excel
