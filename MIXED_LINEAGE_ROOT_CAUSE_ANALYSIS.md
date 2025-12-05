# Root Cause Analysis: Why Products Were Showing MIXED Lineage

## Problem Summary
Products in Excel were showing as MIXED (displayed as "THC" in UI) even though the database had correct lineage for most products.

## Root Cause Flow

### 1. **Initial MIXED Assignment During Excel Load** (Line 3156)
When Excel file is loaded:
- **Non-classic types** (edibles, capsules, etc.) with missing lineage get **MIXED** as default
- **Classic types** (flower, concentrate, etc.) with missing lineage get **HYBRID** as default
- This happens in `excel_processor.py` line 3156: `self.df.loc[nonclassic_mask & not_cbd, "Lineage"] = "MIXED"`

### 2. **DataFrame Update from Database** (Line 3208-3239)
After Excel loads, the system tries to update DataFrame from database:
- Calls `_update_dataframe_lineage_from_database()` 
- Queries database for all product names
- **PROBLEM**: If products aren't found in database (name mismatches, not yet stored, etc.), they keep their MIXED lineage from step 1

### 3. **Tag Creation from DataFrame** (Line 3350-3663)
Tags are created from DataFrame:
- Uses `Lineage` column from DataFrame
- If DataFrame still has MIXED (because database update failed), tags get MIXED
- Tags are created with `currentLineage` and `canonical_lineage` fields set from DataFrame Lineage

### 4. **Enrichment Step** (Line 3663)
Tags are enriched with database values:
- Calls `_enrich_tags_with_database_values()`
- **PROBLEM 1**: Can be skipped if `_skip_enrichment` flag is set (line 3815)
- **PROBLEM 2**: If product not found in database during enrichment:
  - Line 4003: Logs warning but doesn't set lineage fields
  - Tag keeps MIXED from Excel/DataFrame
  - For classic types, this MIXED should be HYBRID but wasn't being converted

### 5. **UI Display** (main.js, tags_table.js)
UI reads lineage from tag object:
- Looks for `canonical_lineage` or `currentLineage` first
- Falls back to `Lineage` field
- **PROBLEM**: If these fields have MIXED for classic types, UI displays "THC" (abbreviation for MIXED)

## Why Database Lineage Wasn't Being Applied

### Scenario 1: Products Not in Database Yet
- New products from Excel haven't been stored in database yet
- Database lookup fails → keeps Excel MIXED lineage
- **FIX**: Convert MIXED to HYBRID for classic types even when not in database

### Scenario 2: Name Mismatches
- Excel product name doesn't exactly match database product name
- Normalized matching might fail due to:
  - Punctuation differences (apostrophes, hyphens)
  - Case differences
  - Whitespace differences
  - Suffix differences (" - 1g" vs "1g")
- **FIX**: Better name matching + fallback to Excel lineage with MIXED→HYBRID conversion

### Scenario 3: Enrichment Skipped
- `_skip_enrichment` flag is set for fast loading
- Database enrichment is skipped entirely
- Tags keep Excel MIXED lineage
- **FIX**: Ensure MIXED→HYBRID conversion happens even when enrichment is skipped

### Scenario 4: Database Record Found But No Lineage Field
- Product exists in database but `Lineage` field is NULL/empty
- `currentLineage` and `canonical_lineage` are also NULL
- Enrichment finds product but has no lineage to apply
- **FIX**: Use Excel lineage and convert MIXED to HYBRID for classic types

## Fixes Applied

### Fix 1: Enrichment - Products Not Found in Database (Line 4045-4075)
- When product not found in database, convert MIXED/THC to HYBRID for classic types
- Set all lineage fields (`currentLineage`, `canonical_lineage`, `Lineage`) from Excel
- Ensures UI can find lineage even when database lookup fails

### Fix 2: Enrichment - Database Record Found But No Lineage (Line 4002-4027)
- When db_record exists but has no lineage field, use Excel lineage
- Convert MIXED/THC to HYBRID for classic types
- Set all lineage fields to ensure UI consistency

### Fix 3: UI Dropdown - Classic Type Conversion (main.js line 4677-4685)
- Convert MIXED/THC to HYBRID for classic types BEFORE setting dropdown value
- Ensures dropdown shows HYBRID instead of MIXED/THC

### Fix 4: UI Dropdown - Fallback Logic (main.js line 4710-4728)
- Fallback to HYBRID (not MIXED) for classic types when lineage is invalid
- Prevents classic types from ever showing MIXED in dropdown

### Fix 5: Tags Table - Dropdown Creation (tags_table.js line 312-319, 150-155)
- Convert MIXED/THC to HYBRID for classic types before creating dropdown options
- Ensures correct option is selected in dropdown

### Fix 6: Tag Normalization (main.js line 2448-2454)
- Convert MIXED/THC to HYBRID for classic types during tag normalization
- Preserves database lineage fields when they exist

### Fix 7: Tag Display (main.js line 4322-4329)
- Convert MIXED/THC to HYBRID for classic types before displaying
- Ensures correct lineage is shown even if database has wrong value

## Prevention Strategy

1. **Database is Source of Truth**: Always query database first for lineage
2. **Excel as Fallback**: If database lookup fails, use Excel lineage but convert MIXED→HYBRID for classic types
3. **UI-Level Protection**: Convert MIXED/THC to HYBRID at multiple UI points as safety net
4. **Better Logging**: Added warnings when products aren't found in database to help identify name matching issues

## Expected Behavior After Fixes

1. **Products in Database**: Use database lineage (correct)
2. **Products Not in Database (Classic Types)**: Use Excel lineage, convert MIXED→HYBRID (correct)
3. **Products Not in Database (Non-Classic Types)**: Use Excel lineage, keep MIXED if that's what Excel has (correct)
4. **UI Display**: Always show HYBRID (not MIXED/THC) for classic types, even if database/Excel has MIXED

## Debugging Tips

If products still show MIXED/THC:
1. Check logs for: `"⚠️ EXCEL ENRICHMENT: Tag 'X' not found in database"`
2. Check if product name in Excel exactly matches database product name
3. Check if `_skip_enrichment` flag is set (should only be for fast loading)
4. Check DataFrame lineage update logs: `"✅ DataFrame lineage update"` or `"⚠️ DataFrame lineage check complete but NO updates"`
