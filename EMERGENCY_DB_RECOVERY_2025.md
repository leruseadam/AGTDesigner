# EMERGENCY DATABASE RECOVERY - 2025

## 🚨 **DATABASE EMPTY AGAIN - QUICK FIX**

The database has gone empty again on PythonAnywhere. Here's the fastest way to get it working:

## **STEP 1: KILL EVERYTHING**

```bash
# Kill all Python processes
pkill -f python
pkill -f flask
pkill -f wsgi

# Wait a moment
sleep 5
```

## **STEP 2: NUCLEAR DATABASE CLEANUP**

```bash
cd ~/AGTDesigner

# Remove ALL database files
rm -rf uploads/*.db*
rm -rf uploads/*.wal
rm -rf uploads/*.shm
rm -rf uploads/*.db-journal
rm -rf uploads/backups_old

# Create fresh uploads directory
rm -rf uploads
mkdir -p uploads
```

## **STEP 3: EXTRACT FRESH DATABASE**

```bash
# Extract the latest database
unzip -o production_database_fix_20251012_142615.zip
mv product_database_AGT_Bothell.db uploads/

# Test the database
sqlite3 uploads/product_database_AGT_Bothell.db "SELECT COUNT(*) FROM products;"
```

**Expected output: `10543` (or similar large number)**

## **STEP 4: RELOAD WEB APP**

1. Go to PythonAnywhere Web tab
2. Click **"Reload"** on your web app
3. Wait for it to reload

## **STEP 5: TEST**

1. Go to your website
2. Check if products are loading
3. Try generating some tags

## **IF STILL NOT WORKING:**

### **Option A: Use the Full Database**

If you have the full database zip file (10,543 products), extract that instead:

```bash
# If you have a different database file
unzip -o [YOUR_FULL_DATABASE_FILE].zip
mv product_database_AGT_Bothell.db uploads/
```

### **Option B: Upload Excel File**

1. Go to your website
2. Upload an Excel file with products
3. This will create a working database from the Excel data

## **PREVENTION:**

The database keeps going empty because:
1. **PythonAnywhere restarts** can cause database locks
2. **Concurrent access** issues
3. **Session timeouts** on the platform

**Quick fix:** Always have a backup Excel file ready to upload if the database goes empty.

## **EMERGENCY CONTACT:**

If this doesn't work, the issue might be deeper in the PythonAnywhere configuration or database corruption.
