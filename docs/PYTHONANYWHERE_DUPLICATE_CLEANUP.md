# PythonAnywhere Database Duplicate Cleanup Guide

## Quick Start

### 1. Upload the Script
Upload `pythonanywhere_cleanup_duplicates.py` to your PythonAnywhere account.

### 2. Test First (Dry Run)
Always run with `--dry-run` first to see what will be deleted:

```bash
python3 pythonanywhere_cleanup_duplicates.py --dry-run
```

This shows you:
- How many duplicates exist
- Which products will be kept (most recent)
- Which duplicates will be deleted
- No actual changes are made

### 3. Run the Cleanup
Once you're satisfied with the dry run results:

```bash
python3 pythonanywhere_cleanup_duplicates.py
```

This will:
- Create an automatic backup
- Remove duplicate products (keeps most recent)
- Vacuum the database to reclaim space
- Show a summary of changes

## How It Works

### Duplicate Detection
Products are considered duplicates if they have the same:
1. **Normalized name** (case-insensitive, cleaned)
2. **Vendor/Supplier**
3. **Brand**

### Which Product is Kept?
For each duplicate group, the script keeps the **most recently updated** product and deletes the older ones.

### Safety Features
- ✅ Automatic backup created before any changes
- ✅ Database integrity check before processing
- ✅ Dry-run mode to preview changes
- ✅ Transaction rollback on errors
- ✅ Detailed logging of all actions

## Examples

### Dry run for Bothell store (default)
```bash
python3 pythonanywhere_cleanup_duplicates.py --dry-run
```

### Clean up Bothell store (live)
```bash
python3 pythonanywhere_cleanup_duplicates.py
```

### Dry run for different store
```bash
python3 pythonanywhere_cleanup_duplicates.py --dry-run --store AGT_Issaquah
```

### Clean up different store (live)
```bash
python3 pythonanywhere_cleanup_duplicates.py --store AGT_Issaquah
```

## Expected Output

```
============================================================
PYTHONANYWHERE DATABASE DUPLICATE CLEANUP
============================================================

Database: uploads/product_database_AGT_Bothell.db
Mode: LIVE (will delete duplicates)

📊 Database size: 45.23 MB

🔍 Checking database integrity...
✅ Database integrity OK

📦 Initial product count: 2,450

📁 Creating backup: uploads/product_database_AGT_Bothell.db.backup_20251211_143022
✅ Backup created

🔍 Finding duplicates...
📋 Found 127 duplicate product groups

Processing duplicates...
  [1/127] Processing 'Blue Dream - 3.5g'...
  [10/127] Processing 'Wedding Cake Pre-Roll - 1g'...
  ...

✅ Changes committed to database

============================================================
CLEANUP SUMMARY
============================================================
Initial products:        2,450
Duplicate groups found:  127
Products kept:           127
Duplicates removed:      253
Final product count:     2,197

🧹 Vacuuming database to reclaim space...
✅ Database vacuumed
📊 New size: 38.15 MB (saved 7.08 MB)

✅ Cleanup completed successfully!
```

## Alternative: Use API Endpoint

You can also call the cleanup endpoint from your app:

```python
import requests

# From within your PythonAnywhere app
response = requests.post('/api/cleanup-duplicate-products')
result = response.json()

print(f"Deleted: {result['deleted_count']} duplicates")
print(f"Remaining: {result['final_product_count']} products")
```

## Troubleshooting

### "Database not found"
Make sure you're in the correct directory. The script searches:
- `uploads/product_database_STORENAME.db`
- `product_database_STORENAME.db`
- Current directory and subdirectories

### "Permission denied"
Ensure you have write access to the database file and directory.

### "Database is locked"
Stop your web app before running the cleanup:
1. Go to PythonAnywhere Web tab
2. Click "Stop" to stop your app
3. Run the cleanup script
4. Click "Reload" to restart your app

### Restore from Backup
If something goes wrong, restore from the automatic backup:

```bash
# List backups
ls -lh uploads/*.backup_*

# Restore (replace timestamp with your backup)
cp uploads/product_database_AGT_Bothell.db.backup_20251211_143022 \
   uploads/product_database_AGT_Bothell.db
```

## Best Practices

1. **Always run dry-run first** to preview changes
2. **Run during low-traffic times** to avoid locking issues
3. **Keep the backup** until you verify everything works
4. **Run regularly** (monthly) to keep database clean
5. **Monitor database size** - significant reduction indicates many duplicates were removed

## Questions?

- Check the backup file if you need to restore
- The script is safe - it creates backups and validates integrity
- Contact support if you encounter issues
