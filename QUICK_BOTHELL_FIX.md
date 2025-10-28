# Quick Bothell Database Fix for PythonAnywhere

## Your Current Database Status (Local)
- ✅ **Integrity**: OK
- ✅ **Products**: 8,825 products
- ✅ **Size**: 5.8MB (healthy, optimized)

## What's Wrong on PythonAnywhere?
The database might be corrupted, too large, or have WAL/SHM files causing issues.

## Quick Fix (3 Steps)

### Step 1: Open PythonAnywhere Bash Console
1. Go to https://www.pythonanywhere.com
2. Click "Consoles" tab
3. Click "Bash"

### Step 2: Copy & Paste This Command
```bash
cd ~/AGTDesigner && \
cp uploads/product_database_AGT_Bothell.db uploads/product_database_AGT_Bothell.db.backup_$(date +%Y%m%d_%H%M%S) && \
echo "✅ Backup created" && \
rm -f uploads/product_database_AGT_Bothell.db-wal uploads/product_database_AGT_Bothell.db-shm && \
echo "✅ Removed WAL/SHM files" && \
python3 rebuild_bothell_db_fixed.py && \
echo "✅ Database rebuilt" && \
python3 -c "import sqlite3; conn = sqlite3.connect('uploads/product_database_AGT_Bothell.db'); cursor = conn.cursor(); cursor.execute('PRAGMA integrity_check'); integrity = cursor.fetchone()[0]; cursor.execute('SELECT COUNT(*) FROM products'); count = cursor.fetchone()[0]; print(f'Integrity: {integrity}'); print(f'Products: {count}'); conn.close()"
```

### Step 3: Reload Your Web App
1. Go to "Web" tab on PythonAnywhere
2. Click the big green "Reload www.agtpricetags.com" button
3. Wait 30 seconds
4. Visit https://www.agtpricetags.com

## If That Doesn't Work

### Option 1: Replace with Local Database
Your local database is healthy. Upload it to PythonAnywhere:

```bash
# On PythonAnywhere, delete the old database:
cd ~/AGTDesigner && rm uploads/product_database_AGT_Bothell.db*

# Then upload your local database file to PythonAnywhere via Files tab
# and verify it works:
python3 -c "import sqlite3; conn = sqlite3.connect('uploads/product_database_AGT_Bothell.db'); print('OK')"
```

### Option 2: Build Fresh from Excel
If you need to rebuild from Excel files:

```bash
# On PythonAnywhere:
cd ~/AGTDesigner && \
python3 rebuild_bothell_db_fixed.py
```

## What Each Script Does

**rebuild_bothell_db_fixed.py**
- Creates clean database schema (without problematic UNIQUE constraints)
- Copies all product data
- Optimizes the database with VACUUM
- Adds proper indices
- Verifies integrity

**fix_corrupted_database.py**
- Fixes SQLite database corruption
- Recovers data where possible
- Repairs table structure

## Verification
Run this to check if everything works:

```bash
python3 -c "import sqlite3; conn = sqlite3.connect('uploads/product_database_AGT_Bothell.db'); cursor = conn.cursor(); cursor.execute('PRAGMA integrity_check'); integrity = cursor.fetchone()[0]; cursor.execute('SELECT COUNT(*) FROM products'); count = cursor.fetchone()[0]; print(f'✅ Integrity: {integrity}'); print(f'✅ Products: {count}'); conn.close()"
```

Expected: Integrity = "ok", Products = [number > 0]

## Contact Info
If you need help, check the logs:
```bash
cat ~/AGTDesigner/app_output.log | tail -50
```
