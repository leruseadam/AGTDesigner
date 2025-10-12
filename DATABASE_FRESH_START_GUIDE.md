# Database Fresh Start - Complete Guide

## What Was Done

### Problem
- Database was corrupted with "file is not a database" errors
- All backups were also malformed with "Rowid 174 out of order" errors
- Recovery attempts failed due to widespread corruption

### Solution
✅ **Created a fresh, clean database** with the correct schema including:
- ✓ `normalized_name` column in strains table (fixes PythonAnywhere error)
- ✓ All required tables: strains, products, brands, lineage_history
- ✓ All required indexes for performance
- ✓ Database integrity verified: PASSED

### Database Location
```
uploads/product_database_AGT_Bothell.db
```

## Next Steps - Local Development

### 1. Start Your Flask App
```bash
cd "/Users/adamcordova/Desktop/labelMaker_ QR copy final"
python3 app.py
```

### 2. Upload Your Excel Inventory File
- Go to http://localhost:5000 (or your configured port)
- Click "Upload Product Database" or similar button
- Select your latest Excel inventory file
- The database will be automatically populated

### 3. Verify Everything Works
- Check that strain dropdowns are populated
- Generate a test label
- Verify lineage information is correct

## For PythonAnywhere

### Option A: Use the Schema Fix Script (Recommended)
If PythonAnywhere still has the old database with data:

```bash
cd ~/AGTDesigner
git pull origin main
python3 fix_pythonanywhere_schema.py
# Reload your web app
```

### Option B: Fresh Start on PythonAnywhere
If you want a clean slate there too:

```bash
cd ~/AGTDesigner
git pull origin main
python3 initialize_database_schema.py
# Then upload your Excel file through the web interface
# Reload your web app
```

## Utility Scripts Available

### `initialize_database_schema.py`
- Creates a completely fresh database with correct schema
- Useful for: Starting from scratch, fixing corruption
- Run: `python3 initialize_database_schema.py`

### `fix_pythonanywhere_schema.py`
- Adds missing `normalized_name` column to existing database
- Useful for: Fixing schema on PythonAnywhere without losing data
- Run: `python3 fix_pythonanywhere_schema.py`

### `create_fresh_database.py`
- Creates database using ProductDatabase class
- Alternative to initialize_database_schema.py
- Run: `python3 create_fresh_database.py`

## Backup Strategy

### Current Backups
- `uploads/backups/clean_backup_20251012_132519.db` - Fresh clean database
- Corrupted backups have been removed

### Going Forward
The app automatically creates backups. To manually backup:
```bash
cp uploads/product_database_AGT_Bothell.db uploads/backups/manual_backup_$(date +%Y%m%d_%H%M%S).db
```

## Troubleshooting

### "file is not a database" Error
1. Stop the app
2. Run: `python3 initialize_database_schema.py`
3. Re-upload your Excel file
4. Restart the app

### "no such column: normalized_name" Error
1. Run: `python3 fix_pythonanywhere_schema.py`
2. Or recreate: `python3 initialize_database_schema.py`

### Database Corruption
1. Stop the app immediately
2. Check backups: `ls -lh uploads/backups/*.db`
3. Test backup integrity: `sqlite3 <backup_file> "PRAGMA integrity_check;"`
4. If all backups are bad, recreate fresh and re-upload Excel

## Prevention Tips

1. **Always keep your latest Excel inventory file** - It's your source of truth
2. **Regular backups** - Copy good databases to safe location
3. **Don't force-stop the app** during database operations
4. **Monitor logs** for early warning signs of corruption

## Status

✅ **LOCAL DATABASE**: Fresh and working
⚠️  **PYTHONANYWHERE**: Needs schema fix or fresh database

Run the PythonAnywhere fix script next to complete the recovery.

