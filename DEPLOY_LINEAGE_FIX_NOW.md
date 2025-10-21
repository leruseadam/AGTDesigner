# Deploy Lineage Color Fix to Web Version

## 🚨 CRITICAL: The fix is working locally but NOT deployed to PythonAnywhere yet!

All tests pass locally, but the web version needs to be updated with the latest code.

## 🚀 DEPLOY TO PYTHONANYWHERE NOW

### Step 1: SSH into PythonAnywhere
```bash
ssh adamcordova@ssh.pythonanywhere.com
```

### Step 2: Navigate to the directory
```bash
cd ~/AGTDesigner
```

### Step 3: Check current branch and status
```bash
git status
git branch
```

### Step 4: Pull the latest fixes
```bash
git pull origin main
```

**Expected output:**
```
Updating bdc5880b..2a9f15f7
Fast-forward
 src/core/data/product_database.py | 16 +++++++-------
 verify_lineage_fix.py             | 144 +++++++++++++++++++++++++
 ...
```

### Step 5: Verify the fix was pulled
```bash
python3 verify_lineage_fix.py
```

**Expected output:**
```
🎉 ALL CHECKS PASSED!
✅ ProductDatabase imported successfully
✅ get_product_lineage method exists
✅ update_product_lineage method exists
...
```

### Step 6: Reload the web app
1. Go to: https://www.pythonanywhere.com/user/adamcordova/webapps/
2. Click the **"Reload www.agtpricetags.com"** button
3. Wait 15-30 seconds for the reload to complete

### Step 7: Clear browser cache
**Important**: Clear your browser cache or use hard refresh:
- **Chrome/Edge**: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
- **Firefox**: Ctrl+F5 (Windows) or Cmd+Shift+R (Mac)

### Step 8: Test lineage changes
1. Go to: https://www.agtpricetags.com
2. Select a product with lineage
3. Change the lineage dropdown (e.g., from SATIVA to INDICA)
4. Click "Generate Tags"
5. Download and open the DOCX file
6. **Check if the lineage bar has the new color**

### Step 9: Monitor logs for debugging
```bash
tail -f /var/log/www.agtpricetags.com.error.log
```

Look for these messages:
- `LINEAGE OVERRIDE: Checking for updated lineage in database...`
- `LINEAGE OVERRIDE: 'ProductName' - Record: 'OLD' -> Database: 'NEW'`
- `Starting lineage color application...`
- `LINEAGE COLOR: 'SATIVA' -> SATIVA -> #ED4123`
- `LINEAGE COLOR SUMMARY: Processed X cells, applied colors to Y cells`

## 🎨 Expected Lineage Colors

After deployment, these colors should appear:

| Lineage Type | Color | Hex Code |
|--------------|-------|----------|
| SATIVA | 🔴 Red | #ED4123 |
| INDICA | 🟣 Purple | #9900FF |
| HYBRID | 🟢 Green | #009900 |
| HYBRID/SATIVA | 🔴 Red | #ED4123 |
| HYBRID/INDICA | 🟣 Purple | #9900FF |
| CBD | 🟡 Yellow | #F1C232 |
| CBD BLEND | 🟡 Yellow | #F1C232 |
| MIXED | 🔵 Blue | #0021F5 |
| PARAPHERNALIA | 🩷 Pink | #FFC0CB |

## 🔍 Troubleshooting

### If colors still don't change after deployment:

#### 1. Verify code was pulled
```bash
cd ~/AGTDesigner
git log --oneline -5
```

Should show:
- `2a9f15f7` - Add lineage fix verification script
- `fe0376c0` - Add comprehensive lineage color fix documentation
- `b6ff2c76` - Add lineage color fix deployment script
- `1ad10162` - CRITICAL FIX: Fix lineage changes not working
- `bdc5880b` - Add comprehensive lineage color debugging

#### 2. Check database exists and has products
```bash
python3 -c "import sqlite3; conn = sqlite3.connect('uploads/product_database.db'); print(f'Products: {conn.execute(\"SELECT COUNT(*) FROM products\").fetchone()[0]}'); conn.close()"
```

#### 3. Check if lineage update endpoint is working
```bash
curl -X POST https://www.agtpricetags.com/api/update-lineage \
  -H "Content-Type: application/json" \
  -d '{"tag_name": "Test Product", "lineage": "SATIVA"}'
```

#### 4. Check for Python errors
```bash
grep -i error /var/log/www.agtpricetags.com.error.log | tail -20
```

#### 5. Verify the correct database is being used
```bash
python3 -c "from src.core.data.product_database import ProductDatabase; db = ProductDatabase(); print(f'Database: {db.db_path}')"
```

#### 6. Test lineage retrieval directly
```bash
python3 -c "from src.core.data.product_database import ProductDatabase; db = ProductDatabase(); print(db.get_product_lineage('Test Product Name'))"
```

## 📋 Quick Test Checklist

- [ ] SSH into PythonAnywhere
- [ ] Navigate to ~/AGTDesigner
- [ ] Pull latest code (`git pull origin main`)
- [ ] Verify fix installed (`python3 verify_lineage_fix.py`)
- [ ] Reload web app at pythonanywhere.com
- [ ] Clear browser cache
- [ ] Test lineage change in UI
- [ ] Generate DOCX
- [ ] Check lineage color in DOCX
- [ ] Monitor logs for debugging output

## 🆘 If Still Not Working

If lineage colors still don't change after following all steps:

1. **Check if database has Lineage column**:
   ```bash
   sqlite3 uploads/product_database.db "PRAGMA table_info(products);" | grep -i lineage
   ```

2. **Create fresh database** (if Lineage column is missing):
   ```bash
   python3 create_fresh_database.py
   ```

3. **Manually test lineage update**:
   ```bash
   python3 test_lineage_end_to_end.py
   ```

4. **Check file permissions**:
   ```bash
   ls -la uploads/product_database.db
   chmod 664 uploads/product_database.db
   ```

5. **Restart web app** (not just reload):
   - Go to Web tab on PythonAnywhere
   - Click "Reload" button
   - Wait 30 seconds
   - Try again

## ✅ Success Indicators

You'll know it's working when:
- ✅ Logs show: `LINEAGE OVERRIDE: Checking for updated lineage in database...`
- ✅ Logs show: `LINEAGE COLOR: 'SATIVA' -> SATIVA -> #ED4123`
- ✅ DOCX file has colored lineage bars
- ✅ Changing lineage in UI changes the color in generated DOCX

## 🎉 Summary

**Local version**: ✅ Working perfectly (all tests pass)
**Web version**: ⚠️ Needs deployment

**Files changed** (need to be deployed):
1. `src/core/data/product_database.py` - Fixed database column names
2. `src/core/generation/docx_formatting.py` - Added debugging & color logic
3. `src/core/generation/tag_generator.py` - Added record debugging
4. `app.py` - Lineage override logic (already deployed)

**Next step**: Follow the deployment steps above to update the web version! 🚀

