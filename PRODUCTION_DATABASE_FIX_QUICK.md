# 🚀 Quick Production Database Fix

## Problem
Production site (https://www.agtpricetags.com) shows **"0 TOTAL PRODUCTS"** despite having data in other sections.

## Solution
Deploy the working local database to PythonAnywhere.

## Files Ready
✅ **database_for_pythonanywhere_20251013_140539.zip** (32M) - Contains 2,207+ products

## Quick Deployment Steps

### 1. Upload to PythonAnywhere
1. Go to [PythonAnywhere Files tab](https://www.pythonanywhere.com/files/)
2. Navigate to: `/home/adamcordova/AGTDesigner`
3. Click **"Upload a file"**
4. Select: `database_for_pythonanywhere_20251013_140539.zip`

### 2. Deploy Database
1. Open [PythonAnywhere Bash console](https://www.pythonanywhere.com/user/adamcordova/consoles/)
2. Run these commands:
```bash
cd ~/AGTDesigner
unzip -o database_for_pythonanywhere_20251013_140539.zip
mv product_database_AGT_Bothell.db uploads/
chmod 644 uploads/product_database_AGT_Bothell.db
rm database_for_pythonanywhere_20251013_140539.zip
```

### 3. Reload Web App
1. Go to [PythonAnywhere Web tab](https://www.pythonanywhere.com/user/adamcordova/webapps/)
2. Click **"Reload"** for your web app
3. Wait 30 seconds for reload to complete

### 4. Verify Fix
Visit: https://www.agtpricetags.com

**Should now show:**
- ✅ **2,207+ TOTAL PRODUCTS** (instead of 0)
- ✅ **82+ UNIQUE VENDORS** (instead of 0)
- ✅ **132+ UNIQUE BRANDS**
- ✅ **21+ PRODUCT TYPES**

## Troubleshooting

### If still showing 0 products:
```bash
# Check database file exists
ls -la uploads/product_database_AGT_Bothell.db

# Test database integrity
sqlite3 uploads/product_database_AGT_Bothell.db "PRAGMA integrity_check;"

# Check product count
sqlite3 uploads/product_database_AGT_Bothell.db "SELECT COUNT(*) FROM products;"
```

### If 500 error persists:
1. Check PythonAnywhere **Error log** (Web tab)
2. Verify file permissions: `chmod 644 uploads/product_database_AGT_Bothell.db`

## Expected Result
After deployment, the website should display the correct product counts and all functionality should work properly!

---
**Database file location:** `/Users/adamcordova/Desktop/labelMaker_ QR copy final/database_for_pythonanywhere_20251013_140539.zip`
