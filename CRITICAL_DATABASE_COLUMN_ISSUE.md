# CRITICAL: Database Column Mismatch Issue

## 🚨 ROOT CAUSE IDENTIFIED

The ProductDatabase class has **12+ references to `normalized_name` column** that doesn't exist in the database schema!

### Error in Logs:
```
Error initializing database: no such column: normalized_name
Error adding/updating product: no such column: normalized_name
[ProductDB] Failed to add/update product after 3 attempts: no such column: normalized_name
```

### What's Wrong:
1. ❌ ProductDatabase code expects `normalized_name` column
2. ❌ Actual database only has `"Product Name*"` column  
3. ❌ This breaks Excel uploads, product updates, and database operations

### Affected Methods (12 locations):
- Line 795: Product lookup
- Line 943: Product update with vendor/brand
- Line 964: Product update with vendor
- Line 982: Product update excluding brand
- Line 1582: Product retrieval
- Line 1762: Product deletion
- Line 3552: Strain lookup
- Line 3654: Product update
- Line 3661: Product update (fallback)
- Line 3730: Product exists check
- Line 3857: Product exists check
- Line 4085: Bulk product lookup

## 🔧 THE FIX

Replace ALL `normalized_name` references with `"Product Name*"` directly.

### Before (BROKEN):
```python
normalized_name = self._normalize_product_name(product_name)
cursor.execute('UPDATE products SET ... WHERE normalized_name = ?', (normalized_name,))
```

### After (FIXED):
```python
cursor.execute('UPDATE products SET ... WHERE "Product Name*" = ?', (product_name,))
```

## ⚠️ WHY THIS IS CRITICAL

This issue is causing:
1. ❌ Excel uploads to fail silently
2. ❌ Database product updates to fail
3. ❌ Hundreds of errors in logs
4. ❌ Products not being added to database
5. ❌ Lineage updates might be affected

## 🚀 IMMEDIATE ACTION REQUIRED

The entire `src/core/data/product_database.py` file needs to be reviewed and fixed to remove ALL `normalized_name` references.

This is beyond a simple find-replace because:
- Some methods might need the normalization logic for comparison
- Some queries might need different column names based on context
- Error handling needs to be preserved

**This requires a comprehensive audit and fix of the ProductDatabase class.**

## 💡 TEMPORARY WORKAROUND

Add `normalized_name` column to the database:

```sql
ALTER TABLE products ADD COLUMN normalized_name TEXT;
UPDATE products SET normalized_name = LOWER(TRIM("Product Name*"));
CREATE INDEX idx_normalized_name ON products(normalized_name);
```

But this is NOT recommended - better to fix the code to use the correct column names.

## 📋 SUMMARY

**Status**: 🔴 CRITICAL BUG  
**Impact**: Excel uploads, database operations, product updates  
**Cause**: Code expects `normalized_name` column that doesn't exist  
**Fix**: Remove all `normalized_name` references from ProductDatabase class  
**Priority**: IMMEDIATE - This is blocking core functionality

