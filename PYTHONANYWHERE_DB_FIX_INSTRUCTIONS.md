# Fix PythonAnywhere Database - Step-by-Step Instructions

## Quick Fix (5 minutes)

### Step 1: Open PythonAnywhere Bash Console
1. Go to https://www.pythonanywhere.com
2. Click **"Consoles"** tab
3. Click **"Bash"** to open a new console

### Step 2: Navigate to Project
```bash
cd ~/AGTDesigner
```

### Step 3: Pull Latest Code
```bash
git pull origin main
```

This will download:
- `fix_database_weights.py` - The weight normalization tool
- `fix_pythonanywhere_db.sh` - Automated fix script
- Documentation files

### Step 4: Run the Fix
```bash
python3 fix_database_weights.py moonshots
```

**Expected Output:**
```
================================================================================
NORMALIZING CONSTELLATION MOONSHOT WEIGHTS
================================================================================

Found 6 Constellation Moonshots

Updating: Grape Moonshot by Constellation Cannabis - 100mg THC
  Old: 100.0 g
  New: 1.7 oz
  ✓ Updated

[... more updates ...]

================================================================================
COMPLETE: Updated X of 6 Moonshots
================================================================================
```

### Step 5: Reload Web App
1. Go to **"Web"** tab on PythonAnywhere
2. Click the big green **"Reload"** button
3. Wait for reload to complete

### Step 6: Verify the Fix
```bash
python3 << 'EOF'
import sqlite3
conn = sqlite3.connect('uploads/product_database_AGT_Bothell.db')
cursor = conn.cursor()
cursor.execute('''
    SELECT "Product Name*", "Weight*", "Units"
    FROM products
    WHERE "Product Name*" LIKE '%Moonshot%' 
    AND "Product Brand" = 'Constellation Cannabis'
    ORDER BY "Product Name*"
''')
print("\nConstellation Moonshots:")
for name, weight, units in cursor.fetchall():
    print(f"  {name}: {weight} {units}")
conn.close()
EOF
```

**Expected Result:** All Moonshots should show `1.7 oz`

---

## Alternative: Use Automated Script

### Option A: Using the Shell Script
```bash
cd ~/AGTDesigner
chmod +x fix_pythonanywhere_db.sh
./fix_pythonanywhere_db.sh
```

### Option B: Copy-Paste Quick Fix
If git pull doesn't work, copy this into PythonAnywhere Bash console:

```bash
cd ~/AGTDesigner

# Create the fix script
cat > /tmp/fix_moonshots.py << 'EOFPYTHON'
import sqlite3
from datetime import datetime

DB_PATH = 'uploads/product_database_AGT_Bothell.db'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("Fixing Constellation Moonshots...")

cursor.execute('''
    SELECT id, "Product Name*", "Weight*", "Units"
    FROM products
    WHERE "Product Name*" LIKE '%Moonshot%' 
    AND "Product Brand" = 'Constellation Cannabis'
''')

moonshots = cursor.fetchall()
updated = 0

for product_id, name, weight, units in moonshots:
    if str(weight) != "1.7" or str(units or "").lower() != "oz":
        cursor.execute('''
            UPDATE products
            SET "Weight*" = ?, 
                "Units" = ?,
                "updated_at" = ?
            WHERE id = ?
        ''', ("1.7", "oz", datetime.now().isoformat(), product_id))
        print(f"✓ Updated: {name}")
        updated += 1

conn.commit()
conn.close()

print(f"\nComplete! Updated {updated} of {len(moonshots)} Moonshots")
EOFPYTHON

# Run it
python3 /tmp/fix_moonshots.py

# Clean up
rm /tmp/fix_moonshots.py
```

---

## Troubleshooting

### Error: "Database not found"
**Solution:** Check your project path
```bash
# Find your project
find ~ -name "product_database_AGT_Bothell.db" -type f

# Or check common locations
ls -la ~/AGTDesigner/uploads/
ls -la ~/your-project/uploads/
```

### Error: "Permission denied"
**Solution:** Check file permissions
```bash
chmod 644 uploads/product_database_AGT_Bothell.db
```

### Error: "Database is locked"
**Solution:** Stop web app first
1. Go to Web tab
2. Click "Stop" button (if running)
3. Run the fix
4. Click "Reload" button

### Changes Don't Appear on Website
**Solution:** Hard reload browser
- **Chrome/Firefox:** Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
- **Safari:** Cmd+Option+R
- Or clear browser cache

---

## Verify Fix is Working

### Check Database Directly
```bash
cd ~/AGTDesigner
sqlite3 uploads/product_database_AGT_Bothell.db "SELECT \"Product Name*\", \"Weight*\", \"Units\" FROM products WHERE \"Product Name*\" LIKE '%Moonshot%' AND \"Product Brand\" = 'Constellation Cannabis';"
```

### Check Through Web App
1. Upload an Excel file (or use existing data)
2. Filter for "Constellation Cannabis" brand
3. Select a Moonshot product
4. Generate labels
5. Check that labels show **1.7 oz** weight

---

## Run Weight Audit (Optional)

To find other weight issues:

```bash
python3 fix_database_weights.py audit
```

This will show:
- Products with missing units
- Products with unusually high weights
- Potential g/oz unit mismatches

---

## Backup Database (Recommended)

Before making changes, backup your database:

```bash
cd ~/AGTDesigner/uploads
cp product_database_AGT_Bothell.db product_database_AGT_Bothell.db.backup_$(date +%Y%m%d_%H%M%S)
```

To restore from backup:
```bash
cp product_database_AGT_Bothell.db.backup_YYYYMMDD_HHMMSS product_database_AGT_Bothell.db
```

---

## After the Fix

### What's Fixed
✅ All Constellation Moonshots now: **1.7 oz**  
✅ Consistent weight values across all Moonshot variants  
✅ Proper unit designation (oz instead of g)

### What to Do Next
1. **Update your inventory system** to export correct weights (1.7 oz for Moonshots)
2. **Run audit periodically** to catch other weight issues
3. **Consider adding validation** in upload process

### Monitor for Issues
If weights revert to wrong values:
- Check source Excel files - they may have wrong weights
- Re-run the fix script
- Contact support if issue persists

---

## Get Help

If you run into issues:

1. Check PythonAnywhere error log:
   - Go to Web tab
   - Click "Log files" section
   - Check error.log

2. Check database connection:
   ```bash
   python3 -c "import sqlite3; conn = sqlite3.connect('uploads/product_database_AGT_Bothell.db'); print('✓ Database connected OK'); conn.close()"
   ```

3. Verify Python version:
   ```bash
   python3 --version  # Should be 3.8 or higher
   ```

4. Check project structure:
   ```bash
   ls -la ~/AGTDesigner/
   ls -la ~/AGTDesigner/uploads/
   ```

---

## Summary

**Time Required:** ~5 minutes  
**Difficulty:** Easy (copy-paste commands)  
**Risk:** Low (non-destructive, only updates weight values)  
**Rollback:** Simple (restore from backup or re-run fix)

**Commands in Order:**
```bash
cd ~/AGTDesigner
git pull origin main
python3 fix_database_weights.py moonshots
# Then reload web app from Web tab
```

Done! 🎉

