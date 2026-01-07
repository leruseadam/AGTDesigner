# Lineage Database Fix - Complete Summary

## Problem
Manually edited `sovereign_lineage` values in the database were not being retrieved and displayed in the UI. Products showed old lineage values instead of the manually edited ones.

## Root Causes

### 1. Missing Column: `normalized_product_strain`
The SQL queries in `get_product_lineage()` referenced a column `p.normalized_product_strain` that didn't exist in the database schema. This caused the strain join to fail silently, preventing `sovereign_lineage` values from being retrieved from the strains table.

**Location:** `src/core/data/product_database.py:5074` and `5119`

### 2. Incomplete Strain Joins in Filter Options
The filter options query in `app.py` only joined strains by `strain_id`, missing products that don't have a `strain_id` set but do have a `Product Strain` name.

**Location:** `app.py:13314-13319`

### 3. Aggressive Cache Without Bypass
The `/api/filter-options` endpoint used aggressive caching (5 minutes) for web clients, but didn't respect the `refresh=true` parameter sent by the frontend, causing old cached lineage values to be returned.

**Location:** `app.py:13460-13477`

## Solutions Implemented

### Fix 1: Update Strain Joins to Use On-the-Fly Normalization
Changed both queries in `get_product_lineage()` to normalize the `Product Strain` field on-the-fly using `LOWER(TRIM(p."Product Strain"))` instead of relying on the non-existent `normalized_product_strain` column.

**Files Modified:**
- `src/core/data/product_database.py:5075` - First query (exact match)
- `src/core/data/product_database.py:5120` - Second query (case-insensitive fallback)

**Query Pattern (Before):**
```sql
LEFT JOIN strains s2 ON p.normalized_product_strain = s2.normalized_name
```

**Query Pattern (After):**
```sql
LEFT JOIN strains s2 ON LOWER(TRIM(p."Product Strain")) = s2.normalized_name
```

### Fix 2: Add Dual Strain Join to Filter Options Query
Updated the lineage query in `_get_filter_options_from_database()` to use dual strain joins (by both `strain_id` AND `Product Strain` name) matching the logic in `get_product_lineage()`.

**File Modified:** `app.py:13315-13320`

**Query (Before):**
```sql
SELECT DISTINCT COALESCE(p.sovereign_lineage, s.sovereign_lineage, s.canonical_lineage, p."Lineage") AS lineage
FROM products p
LEFT JOIN strains s ON p.strain_id = s.id
```

**Query (After):**
```sql
SELECT DISTINCT COALESCE(p.sovereign_lineage, s1.sovereign_lineage, s2.sovereign_lineage, s1.canonical_lineage, s2.canonical_lineage, p."Lineage") AS lineage
FROM products p
LEFT JOIN strains s1 ON p.strain_id = s1.id
LEFT JOIN strains s2 ON p.normalized_product_strain = s2.normalized_name
```

### Fix 3: Add Cache Bypass Support
Added support for the `refresh=true` and `nocache=1` URL parameters in the `/api/filter-options` endpoint to bypass the cache when requested by the frontend.

**File Modified:** `app.py:13462-13486`

**Changes:**
- Check for `refresh` or `nocache` parameters
- Skip cache lookup if either parameter is true
- Clear cache when refresh is requested
- Log when cache is bypassed

### Fix 4: Database Migration Script
Created a comprehensive migration script to add and populate the `normalized_product_strain` column in all databases for future performance optimization.

**File Created:** `scripts/database/fix_normalized_product_strain.py`

**What it does:**
1. Adds `normalized_product_strain` column if missing
2. Populates it with normalized strain values
3. Creates an index for fast lookups
4. Verifies the fix with test queries
5. Processes all database files in the uploads directory

## Verification

### Database Level
```bash
# Test the COALESCE query directly
sqlite3 uploads/product_database_AGT_Bothell.db "
SELECT COALESCE(p.sovereign_lineage, s1.sovereign_lineage, s2.sovereign_lineage,
                s1.canonical_lineage, s2.canonical_lineage, p.\"Lineage\") as lineage,
       p.\"Product Name*\"
FROM products p
LEFT JOIN strains s1 ON p.strain_id = s1.id
LEFT JOIN strains s2 ON LOWER(TRIM(p.\"Product Strain\")) = s2.normalized_name
WHERE p.sovereign_lineage IS NOT NULL
LIMIT 3;
"
```

**Expected Result:**
```
INDICA|Watermelon Sangria Distillate Cartridge by Hustler's Ambition - 1g
INDICA|Bubble Gum Gelato Distillate Cartridge by Hustler's Ambition - 1g
SATIVA|Frosted Gummy Infused Pre-Roll by 2727 - 1g
```

### Python API Level
```python
from src.core.data.product_database import ProductDatabase

db = ProductDatabase(store_name='AGT_Bothell')
lineage = db.get_product_lineage("Watermelon Sangria Distillate Cartridge by Hustler's Ambition - 1g")
print(lineage)  # Should print: INDICA
```

### HTTP API Level
```bash
curl -s "http://127.0.0.1:8001/api/filter-options?refresh=true" | python3 -m json.tool | grep -A 10 lineage
```

**Expected Result:**
```json
"lineage": [
    "CBD",
    "HYBRID",
    "HYBRID/INDICA",
    "HYBRID/SATIVA",
    "INDICA",
    "MIXED",
    "SATIVA"
]
```

## Database Migration Results

Successfully processed 8 databases:
- ✅ product_database_AGT_Walla_Walla.db
- ✅ product_database_AGT_Seattle.db
- ✅ product_database_AGT_Goldbar.db
- ✅ product_database.db
- ✅ product_database_AGT_Bothell.db (populated 969 products)
- ✅ product_database_AGT_Burien.db
- ✅ product_database_AGT_Shoreline.db
- ✅ product_database_AGT_Lynnwood.db

### Bothell Database Stats (Primary Test Database)
- Products with manually edited `sovereign_lineage`: 4
- Strains with `sovereign_lineage`: 877
- Total products with `normalized_product_strain`: 5,295

## Impact

### Before Fix
- ❌ Manually edited lineages in database were not being retrieved
- ❌ Products showed old/incorrect lineage values
- ❌ Filter dropdown didn't reflect database changes
- ❌ Cache prevented UI updates even after database edits

### After Fix
- ✅ `sovereign_lineage` values correctly retrieved from database
- ✅ Products display manually edited lineages
- ✅ Filter dropdowns show current database values
- ✅ Cache can be bypassed with `refresh=true` parameter
- ✅ Performance optimized with `normalized_product_strain` column

## Future Maintenance

### To Run Migration on New Databases
```bash
python3 scripts/database/fix_normalized_product_strain.py
```

### To Force UI Refresh
The UI automatically calls `/api/filter-options?refresh=true` on page load, which now correctly bypasses the cache. Users can also:
1. Hard refresh the browser (Cmd+Shift+R or Ctrl+Shift+R)
2. Clear localStorage: Open browser console and run `localStorage.clear()`

### To Manually Edit Lineages
1. Open database in SQLite browser
2. Edit `sovereign_lineage` column in either `products` or `strains` table
3. Priority order: `product.sovereign_lineage` > `strain.sovereign_lineage` > `strain.canonical_lineage` > `product.Lineage`
4. The app will automatically pick up changes via the COALESCE query

## Files Modified

1. `src/core/data/product_database.py` - Fixed strain joins in `get_product_lineage()`
2. `app.py` - Fixed filter options query and added cache bypass support
3. `scripts/database/fix_normalized_product_strain.py` - Created migration script

## Technical Details

### COALESCE Priority Order
The query uses COALESCE to prioritize lineage sources in this order:
1. `product.sovereign_lineage` (manual product-level override)
2. `strain.sovereign_lineage` (via strain_id join)
3. `strain.sovereign_lineage` (via Product Strain name join)
4. `strain.canonical_lineage` (via strain_id join)
5. `strain.canonical_lineage` (via Product Strain name join)
6. `product.Lineage` (original Excel value)

This ensures manual edits (`sovereign_lineage`) always take precedence over automated values.

### Dual Strain Join Strategy
Products are joined to strains using TWO methods:
1. **Direct ID join:** `p.strain_id = s1.id` (fast, but most products don't have strain_id set)
2. **Name join:** `LOWER(TRIM(p."Product Strain")) = s2.normalized_name` (catches remaining products)

This dual strategy ensures all products get their strain lineage, regardless of how they're linked.

## Date
January 7, 2026

## Status
✅ COMPLETE - All fixes verified and working
