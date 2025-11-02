# Upload Fresh Database to PythonAnywhere

## Overview

This guide helps you upload your fresh, working local database to PythonAnywhere to replace the corrupted one.

## Method 1: Upload Via Web Interface (Recommended - Easiest)

### Step 1: Prepare the Database Zip

On your Mac, run:

```bash
cd "/Users/adamcordova/Desktop/labelMaker_ QR copy final"
chmod +x upload_database_to_pythonanywhere.sh
./upload_database_to_pythonanywhere.sh
```

This will create a file like: `database_for_pythonanywhere_YYYYMMDD_HHMMSS.zip`

### Step 2: Upload to PythonAnywhere

1. Go to **PythonAnywhere** (https://www.pythonanywhere.com)
2. Click on the **"Files"** tab
3. Navigate to: `/home/adamcordova/AGTDesigner`
4. Click **"Upload a file"**
5. Select the zip file created in Step 1
6. Wait for upload to complete

### Step 3: Extract and Install on PythonAnywhere

Open a **Bash console** on PythonAnywhere and run:

```bash
cd ~/AGTDesigner
# Find your uploaded zip file
ls -lh database_for_pythonanywhere_*.zip

# Backup the old database (just in case)
mkdir -p uploads/backups_old
mv uploads/product_database_AGT_Bothell.db uploads/backups_old/corrupted_$(date +%Y%m%d).db 2>/dev/null

# Extract the new database
unzip -o database_for_pythonanywhere_20251012_141821*.zip
mv product_database_AGT_Bothell.db uploads/

# Verify it worked
sqlite3 uploads/product_database_AGT_Bothell.db "PRAGMA integrity_check;"
# Should show: ok

# Verify schema
sqlite3 uploads/product_database_AGT_Bothell.db "PRAGMA table_info(strains);" | grep normalized_name
# Should show: 2|normalized_name|TEXT|1||0

# Clean up
rm database_for_pythonanywhere_*.zip
```

### Step 4: Reload Web App

1. Go to **PythonAnywhere** → **Web** tab
2. Click the green **"Reload www.agtpricetags.com"** button
3. Wait 10-15 seconds
4. Visit: https://www.agtpricetags.com/

✅ Your site should now work!

---

## Method 2: Use SCP/SFTP (For Advanced Users)

If you have SCP access configured:

```bash
# From your Mac
cd "/Users/adamcordova/Desktop/labelMaker_ QR copy final"
./upload_database_to_pythonanywhere.sh

# Upload via SCP
scp database_for_pythonanywhere_*.zip adamcordova@ssh.pythonanywhere.com:~/AGTDesigner/
```

Then follow Step 3 and 4 from Method 1.

---

## Method 3: Create Fresh Database on PythonAnywhere

Instead of uploading, create a fresh database directly on PythonAnywhere:

### On PythonAnywhere Bash Console:

```bash
cd ~/AGTDesigner

# Make sure you have latest code
git pull origin main

# Backup old database
mkdir -p uploads/backups_old
mv uploads/product_database_AGT_Bothell.db uploads/backups_old/corrupted_$(date +%Y%m%d).db 2>/dev/null

# Create fresh database
python3 initialize_database_schema.py

# Verify it
sqlite3 uploads/product_database_AGT_Bothell.db "PRAGMA integrity_check;"
```

Then reload your web app and **upload your Excel inventory file** through the web interface.

---

## Verification Checklist

After uploading and reloading, verify:

- [ ] Site loads without 500 error
- [ ] No `https://true/` URLs in browser console
- [ ] Can upload Excel file
- [ ] Strain dropdowns populate
- [ ] Can generate labels
- [ ] Lineage information displays

---

## Troubleshooting

### "Permission denied" Error

```bash
chmod 644 uploads/product_database_AGT_Bothell.db
```

### "Database is locked" Error

```bash
cd ~/AGTDesigner/uploads
rm -f product_database_AGT_Bothell.db-shm
rm -f product_database_AGT_Bothell.db-wal
```

Then reload web app.

### Still Getting 500 Error

Check the error log:
1. Go to PythonAnywhere → Web tab
2. Click "Error log" link
3. Look for specific error messages
4. Share the error with me

### Upload is Too Slow

If your database is large, the web upload might time out. Use Method 3 instead (create fresh database on PythonAnywhere, then upload Excel file).

---

## What's in the Fresh Database?

The fresh database includes:
- ✓ Correct schema with all required tables
- ✓ `normalized_name` column in strains table
- ✓ All required indexes
- ✓ No corruption
- ✓ Verified integrity

**Note:** The database is empty. You'll need to upload your Excel inventory file through the web interface to populate it with your products.

---

## Keep Your Excel File!

Always keep your latest Excel inventory file as your source of truth. If anything goes wrong with the database, you can always:
1. Create a fresh database
2. Upload your Excel file
3. You're back in business!

---

## Quick Reference

**Prepare zip:**
```bash
cd "/Users/adamcordova/Desktop/labelMaker_ QR copy final"
./upload_database_to_pythonanywhere.sh
```

**Extract on PythonAnywhere:**
```bash
cd ~/AGTDesigner
unzip -o database_for_pythonanywhere_*.zip
mv product_database_AGT_Bothell.db uploads/
rm database_for_pythonanywhere_*.zip
```

**Reload web app and test!**

