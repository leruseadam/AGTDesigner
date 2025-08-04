# Classic Lineage MIXED Assignment Fix

## Problem Description

Classic product types (flower, pre-roll, concentrate, solventless concentrate, vape cartridge, rso/co2 tankers) were being incorrectly assigned "MIXED" lineage instead of proper lineage designations (SATIVA, INDICA, HYBRID, etc.).

From the logs, products like "Blue Slushie", "Goldust", "Larry Cake", "Lemon Oreo Gelato", and "Carrot Cake" were being updated to "MIXED" lineage when they should have specific lineage designations.

## Root Cause

The issue was in the lineage persistence logic in `src/core/data/excel_processor.py`. The `optimized_lineage_persistence` function was blindly applying lineage values from the database without validating that they were appropriate for classic types. The database contained "MIXED" lineage for classic products, and this was being applied incorrectly.

## Solution

### 1. Added Validation for Classic Lineage Values

**File: `src/core/constants.py`**
- Added `VALID_CLASSIC_LINEAGES` constant to define valid lineage values for classic types:
  ```python
  VALID_CLASSIC_LINEAGES = {
      "SATIVA", "INDICA", "HYBRID", "HYBRID/SATIVA", "HYBRID/INDICA", "CBD"
  }
  ```

### 2. Updated Lineage Persistence Logic

**File: `src/core/data/excel_processor.py`**
- Modified `optimized_lineage_persistence` function to validate database lineage values before applying them to classic types
- Only applies database lineage if it's in the `VALID_CLASSIC_LINEAGES` set
- Logs warnings for invalid lineage values and skips the update

### 3. Added Lineage Correction Logic

**File: `src/core/data/excel_processor.py`**
- Added logic to detect and fix classic products that already have "MIXED" lineage
- Automatically changes "MIXED" lineage to "HYBRID" for classic types
- Added logging to track these corrections

### 4. Enhanced Empty Lineage Assignment

**File: `src/core/data/excel_processor.py`**
- Ensured that classic types with empty lineage values are assigned "HYBRID" instead of "MIXED"
- Added logging for lineage assignments

## Changes Made

### `src/core/constants.py`
```python
# Valid lineage values for classic types
VALID_CLASSIC_LINEAGES = {
    "SATIVA", "INDICA", "HYBRID", "HYBRID/SATIVA", "HYBRID/INDICA", "CBD"
}
```

### `src/core/data/excel_processor.py`
1. **Import update:**
   ```python
   from src.core.constants import CLASSIC_TYPES, VALID_CLASSIC_LINEAGES, EXCLUDED_PRODUCT_TYPES, EXCLUDED_PRODUCT_PATTERNS, TYPE_OVERRIDES
   ```

2. **Lineage validation in persistence:**
   ```python
   # Only use database lineage if it's valid for classic types
   if db_lineage and db_lineage.upper() in valid_classic_lineages:
       strain_lineage_map[strain_name] = db_lineage
   else:
       # Log invalid lineage for classic types
       processor.logger.warning(f"Invalid lineage '{db_lineage}' for classic strain '{strain_name}', skipping database update")
   ```

3. **Lineage correction for existing MIXED values:**
   ```python
   # Fix invalid lineage assignments for classic types
   # Classic types should never have "MIXED" lineage
   classic_mask = self.df["Product Type*"].str.strip().str.lower().isin(CLASSIC_TYPES)
   mixed_lineage_mask = self.df["Lineage"] == "MIXED"
   classic_with_mixed_mask = classic_mask & mixed_lineage_mask
   
   if classic_with_mixed_mask.any():
       self.df.loc[classic_with_mixed_mask, "Lineage"] = "HYBRID"
       self.logger.info(f"Fixed {classic_with_mixed_mask.sum()} classic products with invalid MIXED lineage, changed to HYBRID")
   ```

## Testing

Created `test_classic_lineage_fix.py` to verify the fix works correctly:

**Test Results:**
```
Testing Classic Lineage Fix
==================================================
Original data:
            Product Name*            Product Type*     Product Strain Lineage
0       Blue Slushie - 1g                   flower       Blue Slushie   MIXED
1            Goldust - 1g              concentrate            Goldust   MIXED
2         Larry Cake - 1g                 pre-roll         Larry Cake   MIXED
3  Lemon Oreo Gelato - 1g           vape cartridge  Lemon Oreo Gelato   MIXED
4        Carrot Cake - 1g  solventless concentrate        Carrot Cake   MIXED

Applying lineage standardization...
Fixed 5 classic products with invalid MIXED lineage, changed to HYBRID

Processed data:
            Product Name*            Product Type*     Product Strain Lineage
0       Blue Slushie - 1g                   flower       Blue Slushie  HYBRID
1            Goldust - 1g              concentrate            Goldust  HYBRID
2         Larry Cake - 1g                 pre-roll         Larry Cake  HYBRID
3  Lemon Oreo Gelato - 1g           vape cartridge  Lemon Oreo Gelato  HYBRID
4        Carrot Cake - 1g  solventless concentrate        Carrot Cake  HYBRID

Verification:
Total classic products: 5
✅ PASS: No classic products have MIXED lineage
✅ PASS: All classic products have valid lineage values

Lineage distribution for classic products:
  HYBRID: 5
```

## Impact

- **Fixed:** Classic products will no longer be assigned "MIXED" lineage incorrectly
- **Preserved:** Non-classic products (edibles, tinctures, etc.) can still use "MIXED" lineage appropriately
- **Improved:** Better logging and validation for lineage assignments
- **Maintained:** Database lineage persistence still works for valid lineage values

## Files Modified

1. `src/core/constants.py` - Added `VALID_CLASSIC_LINEAGES` constant
2. `src/core/data/excel_processor.py` - Updated lineage persistence and assignment logic
3. `test_classic_lineage_fix.py` - Created test script (new file)

## Notes

- The fix is backward compatible and will correct existing data with invalid lineage assignments
- Classic products with empty lineage values will be assigned "HYBRID" as a sensible default
- The system will log warnings when it encounters invalid lineage values in the database for classic types
- Non-classic products are unaffected and can still use "MIXED" lineage as appropriate 