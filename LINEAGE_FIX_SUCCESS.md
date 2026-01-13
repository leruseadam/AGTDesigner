# ✅ LINEAGE FIX - SUCCESS! (January 13, 2026)

## Problem
- Classic lineage types (SATIVA, INDICA, HYBRID) were being incorrectly set to MIXED
- UI tag elements were showing wrong lineage values
- Strains table values weren't being reflected in the UI
- Only 9.4% of products were linked to the strains table via strain_id

## Root Causes

### 1. `get_mode_lineage()` Was Including MIXED Values
**Location:** `src/core/data/product_database.py:1189` and `core/data/product_database.py:989`

**Problem:** This function calculates the most common lineage from products to update `canonical_lineage` in the strains table. It was including MIXED values, which corrupted the canonical lineage for classic product types.

**Fix:** Modified the function to exclude MIXED and only consider valid classic lineages:
```python
valid_lineages = ('SATIVA', 'INDICA', 'HYBRID', 'HYBRID/SATIVA', 'HYBRID/INDICA', 'CBD', 'CBD_BLEND')

cursor.execute('''
    SELECT "Lineage", COUNT(*) as count
    FROM products
    WHERE "Product Strain" = ?
      AND "Lineage" IS NOT NULL
      AND "Lineage" != ''
      AND UPPER(TRIM("Lineage")) IN (?, ?, ?, ?, ?, ?, ?)
    GROUP BY "Lineage"
    ORDER BY count DESC
    LIMIT 1
''', (strain_name,) + valid_lineages)
```

### 2. Missing strain_id Linkage
**Problem:** 90.6% of products had NULL strain_id, so they couldn't use canonical_lineage or sovereign_lineage from the strains table.

**Fix:** Created `fix_strain_id_linkage.py` script that:
- Matches products to strains by exact Product Strain name
- Matches by normalized strain name
- Extracts strain names from product names for classic types without Product Strain field
- **Result:** Fixed 5,820 products (now 64.2% are linked)

## Files Modified

1. **src/core/data/product_database.py** - Fixed `get_mode_lineage()` at line 1189
2. **core/data/product_database.py** - Fixed `get_mode_lineage()` at line 989
3. **fix_strains_lineage.py** - Created script to clean MIXED from strains table (found only 1 strain needed fixing)
4. **fix_strain_id_linkage.py** - Created script to link products to strains table

## How the System Works Now

### Lineage Priority Chain (COALESCE)
```sql
COALESCE(
    p.sovereign_lineage,      -- Manual edits on individual products (highest priority)
    s.sovereign_lineage,      -- Manual edits on strain (via lineage editor)
    s.canonical_lineage,      -- Auto-calculated from Excel (most common valid lineage)
    p."Lineage"               -- Excel data (lowest priority)
)
```

### Manual Lineage Edits Are Protected
When you edit a strain's lineage via the UI:
1. Sets `sovereign_lineage` in strains table (app.py:21122-21127)
2. Updates all products with that strain
3. Manual edits ALWAYS take priority over auto-calculated values
4. Auto-refresh functions SKIP strains with sovereign_lineage set
5. Excel uploads won't overwrite manual changes

### Example: Blackberry Kush
**Before Fix:**
- Some products showed: HYBRID/INDICA
- Some showed: HYBRID
- Some showed: INDICA
- Reason: Products weren't linked to strains table, using individual product lineage values

**After Fix:**
- All products now show: **INDICA** (from strains table canonical_lineage)
- Linked via strain_id to strains table
- Consistent across all products

### Example: '72 Haze (Manual Edit)
- Manual edit (sovereign_lineage): HYBRID/SATIVA
- Auto-calculated (canonical_lineage): HYBRID
- **UI displays: HYBRID/SATIVA** ✅ (manual edit wins!)

## Prevention Measures

1. **`get_mode_lineage()` now filters MIXED** - Will never corrupt canonical_lineage again
2. **Products linked to strains table** - UI uses authoritative source
3. **Manual edits protected** - sovereign_lineage always takes priority
4. **Web endpoint filters MIXED** - Extra safeguard in tag generation (app.py:14376-14387)

## Scripts Created

### fix_strains_lineage.py
- Cleans MIXED values from strains table canonical_lineage
- Replaces with most common valid lineage from products
- Skips strains with sovereign_lineage (manual edits)

### fix_strain_id_linkage.py
- Links products to strains table via strain_id
- Uses 3 strategies: exact match, normalized match, extract from product name
- Fixed 5,820 products in single run

### fix_strain_variations.py
- Ensures strain variations (e.g., "Southern Comfort" and "Southern Comfort Small Buds") share the same lineage
- Extracts core strain names by removing common suffixes
- Core strain is the authoritative source
- Variations inherit from core
- Manual edits (sovereign_lineage) always protected

## Automatic Fixes (NEW!)

### Strain Variation Synchronization - AUTOMATIC ✨
**Runs automatically after EVERY Excel upload!**

**Location:** `src/core/data/product_database.py` and `core/data/product_database.py`
**Method:** `_fix_strain_variations_auto()`
**Triggered by:** `store_excel_data()` after successful upload

**What it does:**
- Automatically detects strain variations after each Excel upload
- Ensures all variations share the same lineage from their core strain
- Examples:
  - "Southern Comfort" → HYBRID
  - "Southern Comfort Small Buds" → HYBRID (inherits from core)
  - "Blackberry Kush" → INDICA
  - "Blackberry Kush Special" → INDICA (inherits from core)
  - "Blackberry Kush Terp Crystal" → INDICA (inherits from core)

**Recognized variation suffixes:**
- Size variations: `small buds`, `smalls`, `popcorn`, `shake`, `trim`
- Growing methods: `outdoor`, `indoor`, `greenhouse`
- Quality tiers: `special`, `original`, `classic`, `premium`
- Concentrate types: `rso tanker`, `terp crystal`, `live resin`, `live rosin`, `hash rosin`, `badder`, `batter`, `sauce`, `diamonds`, `crumble`, `wax`, `shatter`, `sugar`

**Protection:**
- ✅ Manual edits (sovereign_lineage) are ALWAYS preserved
- ✅ Only updates canonical_lineage (auto-calculated values)
- ✅ Non-fatal - if it fails, upload still succeeds
- ✅ Logs results for transparency

**You never need to run fix_strain_variations.py manually anymore!** The system handles it automatically on every upload.

## How to Run Fixes (if needed again)

```bash
# Clean strains table (removes MIXED from canonical_lineage)
python3 fix_strains_lineage.py

# Link products to strains table
python3 fix_strain_id_linkage.py

# After running, restart Flask app and hard refresh browser
```

## Verification Commands

```bash
# Check strain_id linkage status
sqlite3 "uploads/product_database_AGT_Bothell.db" "
SELECT
    COUNT(*) as total,
    SUM(CASE WHEN strain_id IS NOT NULL THEN 1 ELSE 0 END) as linked,
    SUM(CASE WHEN strain_id IS NULL THEN 1 ELSE 0 END) as unlinked
FROM products;
"

# Check for MIXED in classic product types
sqlite3 "uploads/product_database_AGT_Bothell.db" "
SELECT COUNT(*)
FROM products
WHERE UPPER(TRIM(\"Lineage\")) = 'MIXED'
  AND \"Product Type*\" IN ('Flower', 'Pre-Roll', 'Concentrate', 'Infused Pre-Roll',
                             'Solventless Concentrate', 'Vape Cartridge', 'RSO/CO2 Tankers');
"
# Should return: 0

# Check specific strain lineage
sqlite3 "uploads/product_database_AGT_Bothell.db" "
SELECT
    s.strain_name,
    s.sovereign_lineage,
    s.canonical_lineage,
    COALESCE(s.sovereign_lineage, s.canonical_lineage) as display
FROM strains s
WHERE s.strain_name LIKE '%Blackberry%Kush%';
"
```

## Key Takeaways

✅ **MIXED is only for non-classic types** (Paraphernalia, Accessories, etc.)
✅ **Classic types must use valid lineages** (SATIVA, INDICA, HYBRID, CBD, etc.)
✅ **Strains table is the source of truth** via canonical_lineage and sovereign_lineage
✅ **Manual edits are always protected** via sovereign_lineage priority
✅ **Products must be linked** via strain_id to use strains table values

## Success Metrics

- ✅ Zero classic products have MIXED lineage in database
- ✅ 64.2% of products now linked to strains table (was 9.4%)
- ✅ All Blackberry Kush products show consistent INDICA
- ✅ Manual edits verified working (878 strains have sovereign_lineage)
- ✅ UI displays correct lineage from strains table

## Date: January 13, 2026
## Status: ✅ WORKING - VERIFIED BY USER

---

**IMPORTANT:** Keep this document as a reference for:
1. Understanding how lineage priority works
2. Troubleshooting lineage display issues
3. Re-running fixes if database is reset
4. Onboarding new developers to the lineage system
