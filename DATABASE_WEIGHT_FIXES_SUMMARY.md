# Database Weight Normalization - Summary

## Issue
Constellation Moonshots had inconsistent weights in the database:
- Some were `100.0 g` (incorrect)
- Some were `1.7 g` (wrong unit)
- Some were `2.0 oz` (wrong value)
- Should all be **1.7 oz**

## Root Cause Analysis

### Why the weights were wrong:

1. **Excel file has incorrect/missing data**: The source Excel files have:
   - Missing units (shows `2.5` or `1.7` without specifying oz/g)
   - Some incorrect weights (2.5 instead of 1.7)

2. **Database sync issues**: The database update mechanism exists but:
   - Schema mismatches cause sync failures  
   - Column name differences between Excel and database
   - The proper sync happens through `product_database.py` not directly

3. **Mixed data sources**: Products come from:
   - Excel uploads (primary source)
   - JSON matching (secondary/historical)
   - Manual database entries
   
## Solution Implemented

### 1. Created Weight Normalization Tool (`fix_database_weights.py`)

**Features:**
- Normalize specific products (e.g., all Moonshots to 1.7 oz)
- Audit database for weight issues
- Interactive mode for manual fixes
- Batch operations for brands/categories

**Usage:**
```bash
# Fix Constellation Moonshots
python fix_database_weights.py moonshots

# Run weight audit
python fix_database_weights.py audit

# Interactive mode
python fix_database_weights.py

# List products by brand
python fix_database_weights.py list "Constellation Cannabis"
```

### 2. Applied Fix

Ran normalization on **2024-10-11**:
- **6 Moonshots found**
- **4 updated** to 1.7 oz
- **2 already correct**

**Results:**
| Product | Before | After |
|---------|--------|-------|
| Grape Moonshot | 100.0 g | 1.7 oz ✓ |
| Green Apple Moonshot | 1.7 g | 1.7 oz ✓ |
| Orange Moonshot | 1.7 g | 1.7 oz ✓ |
| Peach Mango Moonshot | 2.0 oz | 1.7 oz ✓ |
| Pineapple Moonshot | 1.7 oz | 1.7 oz ✓ |
| Tropical Punch Moonshot | 1.7 oz | 1.7 oz ✓ |

## Why Excel Uploads Don't Update Database

The database **is** syncing with Excel uploads, but:

1. **Excel data is the problem**: If Excel has wrong weights, database will too
2. **Database preserves product data**: Once a product is in the database, it uses database values for matching (not Excel)
3. **Column mapping complexities**: Excel column names don't always match database column names exactly

## Recommendations

### For Future Excel Uploads

1. **Fix weights in Excel BEFORE uploading**:
   - All Constellation Moonshots should be `1.7` with `oz` unit
   - Include units column populated properly

2. **Run normalization after uploads**:
   ```bash
   python fix_database_weights.py moonshots
   ```

3. **Audit regularly**:
   ```bash
   python fix_database_weights.py audit
   ```

### For Other Products

The audit found 15 products with weights > 100g (likely incorrect):
- Major Lemonades: 190g (should probably be 190 oz or 6.7 oz)
- Some empty product names

Run audit and fix as needed:
```bash
python fix_database_weights.py audit
python fix_database_weights.py
  # Use interactive mode to fix
```

## Files Created

1. **`fix_database_weights.py`** - Main normalization tool
2. **`force_database_sync.py`** - Database sync utilities (advanced)
3. **`simple_database_sync.py`** - Simple sync script (has schema issues)

## How to Prevent This in the Future

### Option 1: Fix at the Source (Recommended)
Update your inventory system to export correct weights with units

### Option 2: Validation on Upload
Add validation in `app.py` upload routes to check/fix known issues:

```python
# After loading Excel file
if 'Moonshot' in row['Product Name*']:
    row['Weight*'] = '1.7'
    row['Units'] = 'oz'
```

### Option 3: Regular Audits
Run weekly:
```bash
python fix_database_weights.py audit
```

## Technical Details

### Database Schema
- Weight stored in `"Weight*"` column (note: has asterisk)
- Units stored in separate `"Units"` column
- Products identified by: `normalized_name` + `"Product Brand"` + `"Vendor/Supplier*"`

### Update Mechanism
- `add_or_update_product()` in `product_database.py`
- Checks for existing by normalized name + brand + vendor
- If exists: **REPLACES all values** with new Excel data
- If new: inserts as new product

### Why Direct SQL Sync Failed
Column name mismatches:
- Database: `"THC test result"` (with quotes in name)
- Excel: `THC test result` (without quotes)
- Proper way: Use `add_or_update_product()` with field mapping

## Status

✅ **FIXED**: All Constellation Moonshots normalized to 1.7 oz  
✅ **TOOLS CREATED**: Weight normalization and audit tools  
⚠️ **ONGOING**: Need to fix source Excel data for long-term solution  
⚠️ **OTHER ISSUES**: 15 products with suspiciously high weights (190g)  

## Next Steps

1. Update source inventory system to export correct Moonshot weights
2. Add validation to upload process
3. Fix other weight issues found in audit (Major Lemonades, etc.)
4. Consider adding unit validation (prevent g/oz mismatches)

