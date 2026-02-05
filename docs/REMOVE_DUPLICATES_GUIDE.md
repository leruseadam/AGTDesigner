# Complete Duplicate Removal Guide for PythonAnywhere

## You have 619 duplicate product groups to clean up!

Follow these steps IN ORDER:

---

## Step 1: Pull Latest Code
```bash
cd ~/AGTDesigner
git pull origin main
```

## Step 2: Repair Database (If Needed)
The database had corruption ("Rowid out of order"). Already fixed, but verify:

```bash
python3 pythonanywhere_repair_database.py
```

**Expected output**: "Database is already healthy - no repair needed!"

---

## Step 3: Preview Duplicates (Dry Run)
See what will be removed WITHOUT making changes:

```bash
python3 pythonanywhere_cleanup_duplicates.py --dry-run
```

**Expected**: Shows 619 duplicate groups and which products will be kept

---

## Step 4: Remove Duplicates (LIVE)
Actually remove the duplicates:

```bash
python3 pythonanywhere_cleanup_duplicates.py
```

**Expected results**:
- Creates automatic backup
- Removes ~600+ duplicate products
- Keeps most recent version of each
- Saves 5-10 MB of database space

---

## Step 5: Prevent Future Duplicates
Add indexes and prevention measures:

```bash
python3 prevent_future_duplicates.py
```

**This adds**:
- Database indexes for faster duplicate detection
- Composite index on (name + vendor + brand)
- Optimizes query performance

---

## Step 6: Verify Results
Check that duplicates are gone:

```bash
python3 pythonanywhere_cleanup_duplicates.py --dry-run
```

**Expected**: "Found 0 duplicate product groups"

---

## What Gets Removed?

Duplicates are products with the same:
1. **Normalized name** (case-insensitive, cleaned)
2. **Vendor/Supplier**
3. **Brand**

**What's kept**: Most recently updated product
**What's deleted**: Older duplicates

---

## Safety Features

✅ Automatic backups before any changes
✅ Database integrity checks
✅ Dry-run mode to preview
✅ Detailed logging of all actions
✅ Can restore from backup if needed

---

## Backup & Restore

### View Backups
```bash
ls -lh uploads/*.backup_*
```

### Restore from Backup (if needed)
```bash
# Replace TIMESTAMP with your backup timestamp
cp uploads/product_database_AGT_Bothell.db.backup_TIMESTAMP \
   uploads/product_database_AGT_Bothell.db
```

---

## Expected Timeline

- **Step 1-2**: 30 seconds (already done)
- **Step 3**: 30 seconds (preview)
- **Step 4**: 2-3 minutes (actual cleanup)
- **Step 5**: 30 seconds (prevention)
- **Step 6**: 30 seconds (verify)

**Total time**: ~5 minutes

---

## After Completion

Your database will:
- ✅ Be 5-10 MB smaller
- ✅ Have no duplicates
- ✅ Have faster queries (indexes added)
- ✅ Prevent future duplicates automatically

The enhanced duplicate detection in the code will now:
- Detect duplicates 3 different ways
- Update existing products instead of creating duplicates
- Log warnings when similar products are found
- Use indexes for 10-100x faster duplicate checks

---

## Troubleshooting

### "Database is locked"
Stop your web app first:
```bash
# On PythonAnywhere Web tab: click "Stop"
# Then run cleanup
# Then click "Reload" to restart
```

### "Permission denied"
```bash
chmod +x pythonanywhere_cleanup_duplicates.py
chmod +x prevent_future_duplicates.py
```

### Still seeing duplicates after cleanup?
Run cleanup again - some edge cases may need multiple passes:
```bash
python3 pythonanywhere_cleanup_duplicates.py
```

---

## Questions?

- All operations create backups first
- Dry-run mode is always safe to use
- You can restore from backup anytime
- Contact support if you encounter issues

**Ready to start? Begin with Step 1!**
