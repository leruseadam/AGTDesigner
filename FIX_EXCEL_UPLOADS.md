# Fix Excel Uploads Not Adding to Database

## 🚨 Problem
Excel files upload successfully but products don't appear in the database.

## 🔍 Diagnosis Steps

### Step 1: Run Diagnostic on PythonAnywhere

```bash
cd ~/AGTDesigner
git pull origin main
python3 test_excel_upload_to_db.py
```

### Step 2: Check Server Logs During Upload

**In one terminal:**
```bash
tail -f /var/log/www.agtpricetags.com.error.log
```

**In browser:**
- Upload an Excel file
- Watch the terminal for errors

### Step 3: Check Database Before/After Upload

**Before uploading:**
```bash
sqlite3 uploads/product_database.db "SELECT COUNT(*) FROM products;"
```

**Upload a file via web interface**

**After uploading:**
```bash
sqlite3 uploads/product_database.db "SELECT COUNT(*) FROM products;"
```

If the count doesn't increase, the upload isn't adding to database.

## 🔧 Common Issues and Fixes

### Issue 1: `store_excel_data` Method Not Found

**Check:**
```bash
python3 -c "from src.core.data.product_database import ProductDatabase; db = ProductDatabase(); print('store_excel_data:', hasattr(db, 'store_excel_data'))"
```

**Fix:** The method might be named differently. Check what methods exist:
```bash
python3 -c "from src.core.data.product_database import ProductDatabase; db = ProductDatabase(); print([m for m in dir(db) if 'store' in m or 'add' in m])"
```

### Issue 2: Background Processing Not Working

The upload uses background threading which might fail silently.

**Check app.py line 1710-1720:**
```python
if product_db and hasattr(product_db, 'store_excel_data'):
    logging.info(f"[BACKGROUND] Storing {row_count} products in database...")
    result = product_db.store_excel_data(processor.df, file_path)
    logging.info(f"[BACKGROUND] Database storage result: {result}")
```

**Fix:** Add error handling and logging:
```python
try:
    if product_db:
        logging.info(f"[BACKGROUND] Attempting to store {row_count} products...")
        if hasattr(product_db, 'store_excel_data'):
            result = product_db.store_excel_data(processor.df, file_path)
            logging.info(f"[BACKGROUND] Storage result: {result}")
        else:
            logging.error("[BACKGROUND] store_excel_data method not found!")
            logging.error(f"[BACKGROUND] Available methods: {[m for m in dir(product_db) if not m.startswith('_')]}")
except Exception as db_error:
    logging.error(f"[BACKGROUND] Database storage failed: {db_error}")
    import traceback
    logging.error(f"[BACKGROUND] Traceback: {traceback.format_exc()}")
```

### Issue 3: Wrong Database File

**Check which database file is being used:**
```bash
python3 -c "from src.core.data.product_database import ProductDatabase; db = ProductDatabase(); print('Database path:', db.db_path)"
```

**If it's using the wrong file:**
- Upload should use: `uploads/product_database.db`
- If it's using a different file, that's the problem

### Issue 4: Database Permissions

**Check permissions:**
```bash
ls -la uploads/product_database.db
```

**Should show:** `-rw-r--r--` or `-rw-rw-r--`

**Fix if needed:**
```bash
chmod 664 uploads/product_database.db
```

### Issue 5: ExcelProcessor Not Calling Database Storage

**Check if ExcelProcessor._store_upload_in_database is being called:**

Look in logs for:
- `"Starting database storage for Excel upload"`
- `"Stored X products in database"`

**If not appearing:** The method isn't being called from the upload endpoint.

## 🚀 Quick Fix Script

Create this script and run it on PythonAnywhere:

```python
#!/usr/bin/env python3
"""
Quick fix to manually add Excel data to database
Run this after uploading an Excel file
"""

import pandas as pd
import sqlite3
import glob
from datetime import datetime

# Find most recent Excel file
excel_files = glob.glob('uploads/*.xlsx') + glob.glob('uploads/*.xls')
if not excel_files:
    print("❌ No Excel files found")
    exit(1)

latest_excel = max(excel_files, key=lambda x: os.path.getmtime(x))
print(f"📊 Processing: {latest_excel}")

# Load Excel
df = pd.read_excel(latest_excel, engine='openpyxl')
print(f"📦 Loaded {len(df)} rows")

# Connect to database
db_path = 'uploads/product_database.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check current count
cursor.execute("SELECT COUNT(*) FROM products;")
before_count = cursor.fetchone()[0]
print(f"📊 Products before: {before_count}")

# Insert products
inserted = 0
for _, row in df.iterrows():
    try:
        # Prepare data
        data = {
            'Product Name*': str(row.get('Product Name*', '')),
            'Product Brand': str(row.get('Product Brand', '')),
            'Product Type*': str(row.get('Product Type*', '')),
            'Vendor/Supplier*': str(row.get('Vendor/Supplier*', '')),
            'Weight*': str(row.get('Weight*', '')),
            'Weight Unit*': str(row.get('Weight Unit*', '')),
            'Price*': str(row.get('Price*', '')),
            'Lineage': str(row.get('Lineage', 'MIXED')),
            'Product Strain': str(row.get('Product Strain', '')),
            'Source': f'Manual Import - {latest_excel}',
            'created_at': datetime.now().isoformat()
        }
        
        # Insert
        columns = ', '.join(f'"{k}"' for k in data.keys())
        placeholders = ', '.join('?' * len(data))
        cursor.execute(f'INSERT INTO products ({columns}) VALUES ({placeholders})', list(data.values()))
        inserted += 1
        
    except Exception as e:
        print(f"⚠️  Row error: {e}")
        continue

conn.commit()

# Check final count
cursor.execute("SELECT COUNT(*) FROM products;")
after_count = cursor.fetchone()[0]

conn.close()

print(f"✅ Inserted {inserted} products")
print(f"📊 Products after: {after_count}")
print(f"📈 Increase: {after_count - before_count}")
```

Save as `manual_import_excel.py` and run:
```bash
python3 manual_import_excel.py
```

## ✅ Verification

After fixing, verify uploads work:

1. **Upload a small test Excel file**
2. **Check database count increases:**
   ```bash
   sqlite3 uploads/product_database.db "SELECT COUNT(*) FROM products;"
   ```
3. **Check logs for success:**
   ```bash
   tail -20 /var/log/www.agtpricetags.com.error.log | grep -i "storage"
   ```

## 📋 Summary

The Excel upload issue is separate from the lineage color issue:

- ✅ **Lineage colors:** Fixed, just need web app reload
- ❌ **Excel uploads:** Need to diagnose and fix

**Next step:** Run `python3 test_excel_upload_to_db.py` and share the output to identify the specific issue.

