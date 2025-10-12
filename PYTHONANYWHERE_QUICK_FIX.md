# PythonAnywhere Quick Fix - 500 Error

## The Problem

Your site (www.agtpricetags.com) is showing:
- ✗ 500 Internal Server Error
- ✗ Strange URL: `https://true/static/...`

## Root Cause

The PythonAnywhere database still has the old schema without the `normalized_name` column, causing the app to crash on startup.

## Quick Fix (5 minutes)

### Step 1: Open PythonAnywhere Bash Console

Go to PythonAnywhere → Consoles → Start a new Bash console

### Step 2: Navigate and Pull Latest Code

```bash
cd ~/AGTDesigner
git pull origin main
```

### Step 3: Fix the Database Schema

```bash
python3 fix_pythonanywhere_schema.py
```

You should see:
```
✅ SUCCESS! You can now reload your web app.
```

### Step 4: Reload Web App

1. Go to PythonAnywhere → Web tab
2. Click the green **"Reload www.agtpricetags.com"** button
3. Wait 10-15 seconds

### Step 5: Test Your Site

Visit: https://www.agtpricetags.com/

It should now load properly! 🎉

## If That Doesn't Work - Check Error Log

### View the Error Log

In PythonAnywhere Web tab, click on the **Error log** link to see what's failing.

Common issues:

### Issue: "ModuleNotFoundError"
```bash
cd ~/AGTDesigner
pip3 install --user -r requirements.txt
```
Then reload web app.

### Issue: Still "no such column: normalized_name"

The fix script didn't work. Use the manual method:

```bash
cd ~/AGTDesigner
python3 initialize_database_schema.py
```

Then upload your Excel file through the web interface.

### Issue: Database is locked

```bash
cd ~/AGTDesigner/uploads
rm -f product_database_AGT_Bothell.db-shm
rm -f product_database_AGT_Bothell.db-wal
```

Then run the fix script again.

## Alternative: Fresh Start (if above doesn't work)

If the quick fix doesn't resolve it:

### 1. Create Fresh Database

```bash
cd ~/AGTDesigner
python3 initialize_database_schema.py
```

### 2. Reload Web App

Click the green "Reload" button in PythonAnywhere Web tab.

### 3. Upload Excel File

1. Go to https://www.agtpricetags.com/
2. Upload your Excel inventory file
3. Wait for processing to complete

## Verify It's Working

Your site should show:
- ✓ Main page loads without errors
- ✓ Upload button is functional
- ✓ Static files (CSS, JS) load correctly
- ✓ No `https://true/` URLs

## After It's Working

### Test These Features:
1. Upload Excel file
2. Generate a test label
3. Check strain dropdowns populate
4. Verify lineage information displays

## Need More Help?

Check the PythonAnywhere error log for specific error messages:
1. Go to Web tab
2. Click "Error log" link
3. Look at the most recent errors
4. Share those with me if you need help debugging

---

**TL;DR:**
```bash
cd ~/AGTDesigner
git pull origin main
python3 fix_pythonanywhere_schema.py
# Then reload web app in dashboard
```

