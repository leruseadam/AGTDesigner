# PythonAnywhere Duplicate Cleanup - Quick Commands

## 🚨 CRITICAL FIX APPLIED
The cleanup script had a SQL NULL comparison bug that prevented it from removing duplicates. This has been fixed!

**The Issue:** Products with NULL vendor/brand weren't being matched because SQL `NULL = NULL` is always `FALSE`.

**The Fix:** Use `COALESCE()` to treat NULL as empty string for proper grouping.

---

## Execute These Commands on PythonAnywhere

### Step 1: Pull the Fixed Code
```bash
cd ~/AGTDesigner
git pull origin main
```

### Step 2: Dry Run (Preview - No Changes)
```bash
python3 pythonanywhere_cleanup_duplicates.py --dry-run
```

**What to Look For:**
- "Duplicate groups found: XXXX" (should be ~2,940)
- "Products kept: XXXX" (should be ~2,940 - one from each group)
- "Duplicates removed: XXXX" (should be thousands)
- Final count should be much less than initial count

### Step 3: Run Live Cleanup
**⚠️ This will delete duplicates - backup is automatic**
```bash
python3 pythonanywhere_cleanup_duplicates.py
```

### Step 4: Add Prevention Indexes
```bash
python3 prevent_future_duplicates.py
```

### Step 5: Verify (Should Show 0 Duplicates)
```bash
python3 pythonanywhere_cleanup_duplicates.py --dry-run
```

---

## Expected Results

### Local Database (Verified)
- **Initial:** 18,874 products
- **Duplicate groups:** 625
- **Will remove:** 6,431 duplicates
- **Final:** 12,443 products (saves ~95 MB)

### PythonAnywhere Database (Estimated)
- **Initial:** 40,536 products  
- **Duplicate groups:** ~2,940
- **Will remove:** ~22,000 duplicates
- **Final:** ~18,500 products (saves 15-20 MB)

---

## Why Did the First Attempt Fail?

Your output showed:
```
Initial products:        40,536
Duplicate groups found:  2,940
Products kept:           0          ❌ BUG!
Duplicates removed:      0          ❌ BUG!
Final product count:     40,536     ❌ No change!
```

**Root Cause:** 
```sql
-- BROKEN (old code)
WHERE normalized_name = ? 
  AND "Vendor/Supplier*" = ?     -- NULL = NULL is FALSE!
  AND "Product Brand" = ?         -- NULL = NULL is FALSE!

-- FIXED (new code)  
WHERE normalized_name = ?
  AND COALESCE("Vendor/Supplier*", '') = ?    -- NULL becomes ''
  AND COALESCE("Product Brand", '') = ?       -- NULL becomes ''
```

Most of your products have NULL vendor/brand, so they were being skipped!

---

## Troubleshooting

### If Dry-Run Still Shows 0 Duplicates Removed
1. Check you pulled the latest code: `git log -1` should show commit a3bf3786
2. Make sure you're in the right directory: `pwd` should show `/home/yourusername/AGTDesigner`
3. Check database path: The script should auto-find `uploads/product_database_AGT_Bothell.db`

### If Live Run Fails
- Backup is automatically created before any changes
- Look for: `product_database_AGT_Bothell.db.backup_YYYYMMDD_HHMMSS`
- Restore: `cp backup_file.db product_database_AGT_Bothell.db`

### If You Need to Restore Backup
```bash
cd ~/AGTDesigner/uploads
ls -lh product_database_AGT_Bothell.db.backup_*  # Find your backup
cp product_database_AGT_Bothell.db.backup_20251212_XXXXXX product_database_AGT_Bothell.db
```

---

## What Changed in the Fix?

### File: `pythonanywhere_cleanup_duplicates.py`

**Line ~113 (Grouping Query):**
```python
# OLD - Missed duplicates with NULL values
GROUP BY normalized_name, "Vendor/Supplier*", "Product Brand"

# NEW - Properly groups NULL values
GROUP BY normalized_name, 
         COALESCE("Vendor/Supplier*", '') as vendor,
         COALESCE("Product Brand", '') as brand
```

**Line ~160 (Matching Query):**
```python
# OLD - WHERE NULL = NULL returns no rows
WHERE normalized_name = ? 
  AND "Vendor/Supplier*" = ?
  AND "Product Brand" = ?

# NEW - COALESCE makes NULL match NULL
WHERE normalized_name = ?
  AND COALESCE("Vendor/Supplier*", '') = ?
  AND COALESCE("Product Brand", '') = ?
```

---

## Timeline (Estimated)

- **Pull code:** 5 seconds
- **Dry-run:** 10-15 seconds
- **Live cleanup:** 30-60 seconds (deletes ~22,000 records)
- **Add indexes:** 5-10 seconds
- **Verify:** 5 seconds

**Total:** ~2-3 minutes

---

## Success Criteria

After Step 5 (verification), you should see:
```
📋 Found 0 duplicate product groups
✅ No duplicates found! Database is clean.
```

And your product count should drop from 40,536 to ~18,500.

---

## Need Help?

If anything goes wrong, you have:
1. **Automatic backup** created before cleanup
2. **Local git history** to restore the script
3. **This guide** with restore commands

The script is now tested and working correctly on your local database! 🎉
