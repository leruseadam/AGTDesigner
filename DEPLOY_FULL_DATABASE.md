# Deploy Full Database to Fix Small Database Issue

## Problem
Web database shows only 198 products instead of 10,543+ products:
- **Web:** 198 TOTAL PRODUCTS, 46 UNIQUE VENDORS, 71 UNIQUE BRANDS
- **Local:** 10,543 TOTAL PRODUCTS (503MB database)

## Solution: Deploy Fresh Full Database

### Step 1: Upload Fresh Database
The script has created a fresh database zip file. Upload it to PythonAnywhere:

1. **Go to:** https://www.pythonanywhere.com
2. **Files tab** → Navigate to `/home/adamcordova/AGTDesigner`
3. **Upload** the fresh database zip file (created by the script)

### Step 2: Replace Database on PythonAnywhere
Open a **Bash console** and run:

```bash
cd ~/AGTDesigner

# Backup old database
mkdir -p uploads/backups_old
mv uploads/product_database_AGT_Bothell.db uploads/backups_old/old_$(date +%Y%m%d_%H%M%S).db 2>/dev/null

# Extract new database
unzip -o database_for_pythonanywhere_*.zip
mv product_database_AGT_Bothell.db uploads/

# Verify new database
sqlite3 uploads/product_database_AGT_Bothell.db "SELECT COUNT(*) FROM products;"
# Should show: 10543

# Check file size
ls -lh uploads/product_database_AGT_Bothell.db
# Should show: ~503M
```

### Step 3: Restart Web App
1. **Web tab** → Click **"Reload"**
2. **Wait 60 seconds** for full restart

### Step 4: Test
1. **Visit:** https://www.agtpricetags.com
2. **Check dashboard** should now show:
   - ✅ **10,000+ TOTAL PRODUCTS** (instead of 198)
   - ✅ **50+ UNIQUE VENDORS** (instead of 46)
   - ✅ **100+ UNIQUE BRANDS** (instead of 71)
   - ✅ **20+ PRODUCT TYPES** (instead of 17)

## Expected Results
After deploying the full database:
- Dashboard will show correct product counts
- All statistics will be accurate
- Application will have full dataset available

## Troubleshooting
If still showing small numbers:
1. Check database file size: `ls -lh uploads/product_database_AGT_Bothell.db`
2. Verify product count: `sqlite3 uploads/product_database_AGT_Bothell.db "SELECT COUNT(*) FROM products;"`
3. Restart web app again
4. Clear browser cache and refresh

The full database deployment will fix the small database issue!
