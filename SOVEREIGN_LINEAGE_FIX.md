# Sovereign Lineage Fix - Strain Changes Now Remembered

## Problem
Manual strain/lineage changes weren't being remembered. When Excel files were uploaded, they would overwrite the manually-set lineages back to the Excel values.

## Root Cause
The database has two lineage fields:
1. **`canonical_lineage`** - From Excel/automatic sources
2. **`sovereign_lineage`** - Manually set by user (should take absolute priority)

The issue was that when products were added or updated during Excel uploads, the code wasn't checking for `sovereign_lineage` before using the Excel lineage. This meant manual changes were being overwritten.

## Fix Applied

### 1. Product Updates - Check Sovereign Lineage First (Lines 3113-3156)
**Added**: When updating existing products, check if the strain has a `sovereign_lineage` set and use it instead of Excel lineage.

```python
# CRITICAL: Check for sovereign_lineage FIRST - it takes absolute priority
cursor.execute('SELECT strain_id FROM products WHERE id = ?', (product_id,))
strain_id_result = cursor.fetchone()
strain_id = strain_id_result[0] if strain_id_result else None

sovereign_lineage = None
if strain_id:
    # Check if this strain has a manually-set sovereign_lineage
    cursor.execute('SELECT sovereign_lineage FROM strains WHERE id = ?', (strain_id,))
    sovereign_result = cursor.fetchone()
    if sovereign_result and sovereign_result[0]:
        sovereign_lineage = str(sovereign_result[0]).strip()
        logger.info(f"🔒 SOVEREIGN LINEAGE: Found manually-set lineage '{sovereign_lineage}'")

# If sovereign lineage exists, USE IT and ignore Excel lineage
if sovereign_lineage:
    final_lineage = sovereign_lineage
    logger.info(f"✅ LINEAGE PRIORITY: Using sovereign lineage (ignoring Excel)")
else:
    # Use normal Excel/database priority logic
    ...
```

### 2. New Product Insertion - Check Sovereign Lineage (Lines 1029-1036)
**Added**: When inserting new products, check if the strain has a `sovereign_lineage` and use it instead of Excel lineage.

```python
# CRITICAL: Check if strain has sovereign_lineage before using Excel lineage
lineage_to_use = self._normalize_lineage(product_data.get('Lineage'))
if strain_id:
    cursor.execute('SELECT sovereign_lineage FROM strains WHERE id = ?', (strain_id,))
    sovereign_result = cursor.fetchone()
    if sovereign_result and sovereign_result[0]:
        lineage_to_use = str(sovereign_result[0]).strip()
        logger.info(f"🔒 NEW PRODUCT: Using sovereign lineage '{lineage_to_use}' (ignoring Excel)")
```

### 3. Strain Updates - Protect Sovereign Lineage (Lines 823-856)
**Added**: When Excel uploads update strains, don't overwrite canonical_lineage if sovereign_lineage is set.

```python
# CRITICAL: If sovereign lineage is set, DON'T update canonical lineage from Excel
if existing_sovereign:
    logger.info(f"🔒 SOVEREIGN PROTECTION: Strain '{strain_name}' has sovereign lineage '{existing_sovereign}' - ignoring Excel lineage update")
    # Just update occurrence count, don't touch lineage
    cursor.execute('''
        UPDATE strains 
        SET total_occurrences = ?, last_seen_date = ?, updated_at = ?
        WHERE id = ?
    ''', (new_occurrences, current_date, current_date, strain_id))
else:
    # No sovereign lineage - update canonical lineage from Excel as normal
    ...
```

## How It Works

### Lineage Priority Order:
```
1. sovereign_lineage (HIGHEST - manually set by user)
   ↓
2. canonical_lineage (from Excel uploads)
   ↓
3. existing database lineage (preserved if Excel has none)
```

### When User Updates Strain Lineage:
1. User clicks "Edit Lineage" in UI
2. Calls `/api/set-strain-lineage` with `sovereign=True`
3. Sets `sovereign_lineage` in strains table
4. Updates all products with that strain to use the new lineage

### When Excel is Uploaded:
1. Excel contains products with lineages
2. Code checks if strain has `sovereign_lineage` set
3. If YES: Use `sovereign_lineage` (ignore Excel)
4. If NO: Use Excel lineage normally

### Result:
✅ **Manual lineage changes are PROTECTED** from Excel overwrites
✅ **Sovereign lineage takes absolute priority** over Excel
✅ **Excel lineage still works** for strains without manual changes

## Example Scenario

**Step 1**: User sets "Blackberry Kush" lineage to SATIVA manually
- `strains.sovereign_lineage` = 'SATIVA'
- All products with this strain get lineage = 'SATIVA'

**Step 2**: User uploads new Excel file with "Blackberry Kush" as INDICA
- System checks: Does strain have `sovereign_lineage`? YES
- System uses: 'SATIVA' (from sovereign_lineage)
- System ignores: Excel lineage (INDICA)

**Step 3**: User generates labels
- Products show lineage as 'SATIVA' ✅
- Manual change is preserved ✅

## Files Modified
- `src/core/data/product_database.py`
  - `_update_existing_product()` - Check sovereign_lineage before updating (lines 3113-3156)
  - `add_or_update_product()` - Check sovereign_lineage for new products (lines 1029-1036)
  - `add_or_update_strain()` - Protect sovereign_lineage from Excel overwrites (lines 823-856)

## Testing Recommendations
1. **Set Manual Lineage**: Update a strain's lineage manually
2. **Upload Excel**: Upload Excel file with different lineage for that strain
3. **Verify Persistence**: Check that manual lineage is preserved
4. **Generate Labels**: Verify labels show the manual lineage, not Excel lineage
5. **Test Multiple Strains**: Try with several different strains

## Date
November 6, 2025

