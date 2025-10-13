# EMERGENCY DATABASE RECOVERY

## Problem
Database worked briefly but is now empty again:
- 0 TOTAL PRODUCTS
- 0 UNIQUE VENDORS
- 0 UNIQUE BRANDS
- 0 PRODUCT TYPES
- 500 Internal Server Error

## Emergency Recovery Steps

### Step 1: Check Current Database Status
```bash
cd ~/AGTDesigner

# Check if database exists
ls -la uploads/product_database_AGT_Bothell.db

# Check database size
du -h uploads/product_database_AGT_Bothell.db

# Test database integrity
sqlite3 uploads/product_database_AGT_Bothell.db "SELECT COUNT(*) FROM products;"
```

### Step 2: Kill All Processes (Nuclear Option)
```bash
# Kill all Python/Flask processes
pkill -f python
pkill -f flask
pkill -f wsgi

# Wait 10 seconds
sleep 10

# Check for remaining processes
ps aux | grep -i python
ps aux | grep -i flask
```

### Step 3: Remove All Database Files
```bash
cd ~/AGTDesigner

# Remove ALL database files and locks
rm -f uploads/*.db*
rm -f uploads/*.wal
rm -f uploads/*.shm
rm -f uploads/*.db-journal
rm -f uploads/*.db-corrupted*

# Remove any backup directories
rm -rf uploads/backups_old
```

### Step 4: Deploy Fresh Database
```bash
# Go back to local machine and create fresh database
cd "/Users/adamcordova/Desktop/labelMaker_ QR copy final"
./upload_database_to_pythonanywhere.sh

# Upload the new zip file to PythonAnywhere
# Then in PythonAnywhere bash console:
cd ~/AGTDesigner
unzip -o database_for_pythonanywhere_*.zip
mv product_database_AGT_Bothell.db uploads/

# Verify new database
sqlite3 uploads/product_database_AGT_Bothell.db "SELECT COUNT(*) FROM products;"
# Should show: 10543
```

### Step 5: Restart Everything
```bash
# In PythonAnywhere:
# 1. Go to Web tab
# 2. Click "Reload" button
# 3. Wait 60 seconds for full restart
```

### Step 6: Test
1. Visit: https://www.agtpricetags.com
2. Check dashboard should show:
   - ✅ 10,000+ TOTAL PRODUCTS
   - ✅ 50+ UNIQUE VENDORS
   - ✅ 100+ UNIQUE BRANDS
   - ✅ 20+ PRODUCT TYPES

## If Still Not Working

### Nuclear Database Reset
```bash
cd ~/AGTDesigner

# Remove EVERYTHING
rm -rf uploads/
mkdir uploads

# Extract fresh database
unzip -o database_for_pythonanywhere_*.zip
mv product_database_AGT_Bothell.db uploads/

# Set proper permissions
chmod 644 uploads/product_database_AGT_Bothell.db

# Test database
sqlite3 uploads/product_database_AGT_Bothell.db "SELECT COUNT(*) FROM products;"
```

The database keeps getting corrupted, so we need to deploy a fresh copy and ensure no processes are locking it.
