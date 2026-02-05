# Sovereign Lineage Display Fix

## Problem
Sovereign lineage values were not appearing in the UI tags table, even though they were being stored correctly in the database.

## Root Cause
The "SIMPLE PATH" enrichment logic in `app.py` (around line 10080) was only querying the `Lineage` column from the products table, not the `sovereign_lineage` column. This meant that when tags were enriched with database values, the `sovereign_lineage` field was never added to the tag data sent to the frontend.

## Solution
Updated the database query in the SIMPLE PATH enrichment to:
1. Include `sovereign_lineage` in the SELECT statement using a COALESCE priority: `p.sovereign_lineage > s.sovereign_lineage > s.canonical_lineage > p.Lineage`
2. Join with the strains table to get strain-level sovereign lineage
3. Store both the effective lineage AND the sovereign lineage value in the lineage_map
4. Set the `sovereign_lineage` field on tags when enriching them
5. **CRITICAL FIX**: Clean `sovereign_lineage` values to convert `'NONE'` strings to `null`
6. **JavaScript FIX**: Filter out invalid values (`'NONE'`, empty, null) when selecting lineage priority

## Changes Made

### File: `app.py`

**Location: Lines 10080-10120**

Changed from:
```python
cursor.execute(f'''
    SELECT "Product Name*", "Lineage"
    FROM products
    WHERE LOWER("Product Name*") IN ({placeholders})
''', chunk_lower)
```

To:
```python
cursor.execute(f'''
    SELECT p."Product Name*",
           COALESCE(p.sovereign_lineage, s.sovereign_lineage, s.canonical_lineage, p."Lineage") as effective_lineage,
           p.sovereign_lineage as product_sovereign
    FROM products p
    LEFT JOIN strains s ON p.strain_id = s.id
    WHERE LOWER(p."Product Name*") IN ({placeholders})
''', chunk_lower)
```

Added cleaning function:
```python
def _clean_sovereign(val):
    """Clean sovereign lineage value - return None for empty/invalid values"""
    if val is None:
        return None
    txt = str(val).strip().upper()
    if txt in ['', 'NONE', 'NULL', 'NAN', '0', '0.0']:
        return None
    return txt
```

**Location: Lines 10121-10142**

Updated tag enrichment logic to:
```python
lineage_data = lineage_map[product_name]
# Handle both old format (string) and new format (dict)
if isinstance(lineage_data, dict):
    db_lineage_clean = lineage_data['lineage']
    # CRITICAL: Set sovereign_lineage if present
    if lineage_data['sovereign']:
        tag['sovereign_lineage'] = lineage_data['sovereign']
else:
    db_lineage_clean = lineage_data

tag['currentLineage'] = db_lineage_clean
tag['canonical_lineage'] = db_lineage_clean
tag['Lineage'] = db_lineage_clean
tag['Lineage*'] = db_lineage_clean
tag['lineage'] = db_lineage_clean.lower()
```

### File: `static/js/tags_table.js`

**Location: Lines 115-132 and 297-314**

Added validation to filter out `'NONE'` strings:
```javascript
// Helper to check if a value is valid (not null, undefined, empty, or 'NONE')
const isValid = (val) => val && String(val).trim().toUpperCase() !== 'NONE';

const rawLineage = (isValid(tag.sovereign_lineage) ? tag.sovereign_lineage : null)
                || (isValid(tag.canonical_lineage) ? tag.canonical_lineage : null)
                || (isValid(tag.currentLineage) ? tag.currentLineage : null)
                || tag.Lineage
                || tag['Lineage*']
                || tag.lineage
                || '';
```

## How It Works Now

1. **Database Query**: Fetches both the effective lineage (using COALESCE priority) AND the sovereign_lineage value
2. **Tag Enrichment**: Sets the `sovereign_lineage` field on tags that have it in the database
3. **JavaScript Display**: Uses the existing priority system that already prioritizes `sovereign_lineage` first:
   ```javascript
   const rawLineage = tag.sovereign_lineage || tag.canonical_lineage || tag.currentLineage || ...
   ```

## Priority System

The complete priority chain for lineage display is:

1. **`tag.sovereign_lineage`** - Manual user edits (highest priority)
2. **`tag.canonical_lineage`** - Database canonical lineage
3. **`tag.currentLineage`** - Current database value
4. **`tag.Lineage`** / **`tag['Lineage*']`** - Excel column values
5. **`tag.lineage`** - Lowercase fallback

## Verification

Run `python3 verify_sovereign_lineage_fix.py` to verify:
- ✅ Database query includes sovereign_lineage
- ✅ Tag enrichment sets sovereign_lineage field
- ✅ JavaScript uses sovereign_lineage as highest priority

## Testing

To test the fix:
1. Update a product's lineage in the UI
2. Reload the available tags
3. The sovereign_lineage should now appear and be used for display

The fix ensures that manual lineage edits (sovereign_lineage) are now visible in the UI tags table and will be prioritized over database-imported lineages.
