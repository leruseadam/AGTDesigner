# Fix Duplicates on PythonAnywhere - Quick Guide

## Step 1: Open PythonAnywhere Bash Console
1. Go to https://www.pythonanywhere.com
2. Click **"Consoles"** tab
3. Click **"Bash"** to open a new console

## Step 2: Navigate and Pull Latest Code
```bash
cd ~/AGTDesigner
git pull origin main
```

You should see:
```
remote: Enumerating objects...
Updating bee332ce..5ab541c4
Fast-forward
 pythonanywhere_cleanup_duplicates.py | 15 ++++++++-------
 1 file changed, 8 insertions(+), 7 deletions(-)
```

## Step 3: Stop Your Web App
This is **CRITICAL** - the database must not be locked!

### Option A: Via Web Interface
1. Go to **"Web"** tab
2. Click **"Reload"** button (or "Stop" if running)
3. Wait 5 seconds

### Option B: Via Console
```bash
touch /var/www/yourusername_pythonanywhere_com_wsgi.py
```

## Step 4: Check Database Location
```bash
ls -lh uploads/*.db
```

You should see something like:
```
-rw-r--r-- 1 user user 30M Dec 12 08:00 uploads/product_database_AGT_Bothell.db
```

## Step 5: Preview What Will Be Deleted (Dry Run)
```bash
python3 pythonanywhere_cleanup_duplicates.py --dry-run
```

**Look for:**
- ✅ "Database integrity OK"
- "Duplicate groups found: XXXX" (likely ~2,940)
- "Duplicates removed: XXXX" (should show thousands, NOT 0!)
- "Final product count: XXXX" (should be much lower than initial)

If you see "Duplicates removed: 0" - **STOP and message me!**

## Step 6: Run Live Cleanup
**⚠️ This will delete duplicates (backup created automatically)**

```bash
python3 pythonanywhere_cleanup_duplicates.py
```

**Expected output:**
```
📁 Creating backup: uploads/product_database_AGT_Bothell.db.backup_YYYYMMDD_HHMMSS
✅ Backup created

Processing duplicates...
  [10/2940] Processing 'product name'...
  [20/2940] Processing 'product name'...
  ...

✅ Changes committed to database

CLEANUP SUMMARY
Initial products:        40,536
Duplicate groups found:  2,940
Products kept:           2,940
Duplicates removed:      ~22,000
Final product count:     ~18,500

🧹 Vacuuming database to reclaim space...
✅ Database vacuumed
📊 New size: XX.XX MB (saved 15-20 MB)
```

## Step 7: Add Prevention Measures
```bash
python3 prevent_future_duplicates.py
```

**Expected output:**
```
✅ Database integrity OK
📦 Total products: ~18,500
✅ Added 4 new indexes
✅ Database analyzed
🔍 Checking for remaining duplicates...
   Found 0 duplicate groups  ← THIS IS WHAT YOU WANT!
```

## Step 8: Verify Clean Database
```bash
python3 pythonanywhere_cleanup_duplicates.py --dry-run
```

**Should show:**
```
📋 Found 0 duplicate product groups
✅ No duplicates found! Database is clean.
```

## Step 9: Restart Your Web App
1. Go to **"Web"** tab
2. Click **"Reload"** button
3. Your app is now running with clean database!

---

## Troubleshooting

### "Database is locked"
```bash
# Kill any Python processes
pkill -9 python

# Try again
python3 pythonanywhere_cleanup_duplicates.py
```

### "Duplicates removed: 0" (BUG!)
This means you pulled old code. Run:
```bash
cd ~/AGTDesigner
git fetch origin
git reset --hard origin/main
git pull origin main
```

Then verify the fix is there:
```bash
grep -n "GROUP BY normalized_name, COALESCE" pythonanywhere_cleanup_duplicates.py
```

Should show line ~120 with:
```python
GROUP BY normalized_name, COALESCE("Vendor/Supplier*", ''), COALESCE("Product Brand", '')
```

### Need to Restore Backup
```bash
cd ~/AGTDesigner/uploads
ls -lh *.backup_*  # Find your backup
cp product_database_AGT_Bothell.db.backup_20251212_XXXXXX product_database_AGT_Bothell.db
```

---

## Success Criteria

✅ Dry-run shows actual numbers to remove (not 0)  
✅ Live run removes thousands of duplicates  
✅ Database size reduced by 15-20 MB  
✅ Prevention script shows 0 remaining duplicates  
✅ Final verification shows "Database is clean"  
✅ Web app reloaded and working  

---

## Summary of Fixes

**Bug #1:** SQL NULL comparison (`NULL = NULL` is FALSE)  
**Fix #1:** Use `COALESCE()` to convert NULL to empty string

**Bug #2:** SQL GROUP BY alias mismatch  
**Fix #2:** Remove aliases, use COALESCE in GROUP BY clause

Both bugs are now fixed in commit **5ab541c4**

---

## Timeline

- **Step 1-2:** 30 seconds (pull code)
- **Step 3:** 10 seconds (stop app)
- **Step 4-5:** 20 seconds (check + dry-run)
- **Step 6:** 60-90 seconds (remove ~22K duplicates)
- **Step 7:** 10 seconds (add indexes)
- **Step 8:** 5 seconds (verify)
- **Step 9:** 10 seconds (restart app)

**Total: ~3 minutes**

---

Last updated: 2025-12-12  
Commits: a3bf3786, bee332ce, 5ab541c4
