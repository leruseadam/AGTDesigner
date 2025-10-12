# 🚀 QUICK FIX GUIDE FOR PYTHONANYWHERE

## 🎯 What This Fixes
- ✅ **API 500 Errors** (database-vendor-stats, database-analytics)
- ✅ **Database restoration** from backup
- ✅ **Product count** display issues
- ✅ **0 products** showing on website

---

## 📦 OPTION 1: Complete Automated Fix (RECOMMENDED)

### File: `complete_fix_20251012_152424.zip`

**Steps:**

1. **Upload to PythonAnywhere**
   - Go to **Files** tab
   - Click **"Upload a file"**
   - Select `complete_fix_20251012_152424.zip`

2. **Extract and Deploy**
   ```bash
   # In PythonAnywhere Bash console:
   unzip complete_fix_20251012_152424.zip
   cd temp_fix_*
   chmod +x deploy_fix.sh
   ./deploy_fix.sh
   ```

3. **Reload Web App**
   - Go to **Web** tab
   - Click **"Reload"** button
   - Wait 30-60 seconds

4. **Verify**
   - Visit https://www.agtpricetags.com
   - Should show correct product count
   - API endpoints should return 200 (not 500)

---

## 📦 OPTION 2: Manual Database Restore Only

### If you just need to restore the database:

```bash
# Copy from the specific backup file
cp uploads/product_database_AGT_Bothell.db.corrupted.20251012_213432 uploads/product_database_AGT_Bothell.db

# Verify
sqlite3 uploads/product_database_AGT_Bothell.db "SELECT COUNT(*) FROM products;"

# Should show 1000+ products
```

**Then reload your web app.**

---

## 📦 OPTION 3: Quick API Fix Only

### File: `api_fixes_20251012_152216.zip`

If database is fine but APIs have 500 errors:

```bash
# In PythonAnywhere:
unzip api_fixes_20251012_152216.zip
cp app.py /home/yourusername/mysite/
# Reload web app
```

---

## 🧪 Testing After Deployment

### Test URLs:
- https://www.agtpricetags.com
- https://www.agtpricetags.com/api/database-stats
- https://www.agtpricetags.com/api/database-vendor-stats
- https://www.agtpricetags.com/api/database-analytics

### Expected Results:
- ✅ Product count > 1000
- ✅ Vendor count > 50
- ✅ API endpoints return 200 status
- ✅ No JavaScript errors in console

---

## 🆘 Troubleshooting

### If still showing 0 products:

1. **Check database file exists:**
   ```bash
   ls -lh uploads/product_database_AGT_Bothell.db
   ```

2. **Check product count:**
   ```bash
   sqlite3 uploads/product_database_AGT_Bothell.db "SELECT COUNT(*) FROM products;"
   ```

3. **Check error logs:**
   - Web tab → Log files → Error log

4. **Manual database copy:**
   ```bash
   # If main database is good:
   cp uploads/product_database.db uploads/product_database_AGT_Bothell.db
   ```

### If API endpoints still return 500:

1. **Check PythonAnywhere error log** for specific errors
2. **Verify app.py was copied** to correct directory
3. **Check pandas is installed:**
   ```bash
   pip3 install --user pandas
   ```

---

## 📋 What Was Fixed

### Code Changes:
1. **app.py** - Added `import pandas as pd` to:
   - `/api/database-vendor-stats` endpoint (line 6403)
   - `/api/database-analytics` endpoint (line 7088)

### Database Changes:
1. Restored from backup: `product_database_AGT_Bothell.db.corrupted.20251012_213432`
2. Verified product count and integrity

---

## ✅ Success Indicators

After deployment, you should see:
- 🟢 **Product Count**: 1000+ products
- 🟢 **Vendor Count**: 50+ vendors  
- 🟢 **API Status**: All endpoints return 200
- 🟢 **No Errors**: JavaScript console is clean

---

## 📞 Need Help?

If the automated fix doesn't work:
1. Check the error logs in PythonAnywhere
2. Run the diagnostic script: `python3 check_production_status.py`
3. Manually verify database files exist and have correct data
