# Push New Database to PythonAnywhere Web
================================================

## ✅ Database Ready for Upload!

Your database has been compressed and is ready to deploy:

- **File**: `uploads/product_database_AGT_Bothell.db.gz`
- **Size**: 27.5 MB (compressed from 250 MB)
- **Products**: 7,853 products
- **Status**: ✅ Ready to upload

---

## 🚀 Method 1: Manual Upload (Recommended - Fastest)

### Step 1: Upload the Database File

1. **Download/Locate** the compressed database:
   - Path: `/Users/adamcordova/Desktop/labelMaker_ QR copy SAFEST copy 24/uploads/product_database_AGT_Bothell.db.gz`
   
2. **Go to PythonAnywhere Files**:
   - Visit: https://www.pythonanywhere.com/user/adamcordova/files/
   - Navigate to: `/home/adamcordova/AGTDesigner/uploads/`
   
3. **Upload the file**:
   - Click "Upload a file"
   - Select: `product_database_AGT_Bothell.db.gz`
   - Wait for upload to complete (should take 1-2 minutes)

### Step 2: Extract and Deploy on PythonAnywhere

Open a **Bash console** on PythonAnywhere and run:

```bash
cd ~/AGTDesigner/uploads

# Extract the compressed database
gunzip -f product_database_AGT_Bothell.db.gz

# Verify the database
python3.11 -c "
import sqlite3
conn = sqlite3.connect('product_database_AGT_Bothell.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM products')
print(f'✅ Products in database: {cursor.fetchone()[0]:,}')
conn.close()
"

# Make sure the database is readable
chmod 644 product_database_AGT_Bothell.db
```

### Step 3: Reload Your Web App

1. Go to the **Web** tab in PythonAnywhere
2. Click the green **"Reload"** button
3. Wait for reload to complete
4. Visit your site: https://adamcordova.pythonanywhere.com

---

## 🔧 Method 2: API Upload (Alternative)

If you prefer to use the API for automated upload:

### Step 1: Get Your API Token

1. Go to: https://www.pythonanywhere.com/user/adamcordova/
2. Click on **"API Token"** tab
3. Copy your API token

### Step 2: Set Environment Variable

```bash
export PYTHONANYWHERE_API_TOKEN="your_token_here"
```

### Step 3: Run Upload Script

```bash
cd "/Users/adamcordova/Desktop/labelMaker_ QR copy SAFEST copy 24"
python3 push_db_to_pythonanywhere.py
```

The script will:
- Upload the compressed database (27.5 MB)
- Provide extraction commands
- Verify the upload

---

## 📊 What's Included in This Database

- **7,853 products** (your complete inventory)
- **All product types**: Flower, Pre-Roll, Vape Cartridge, Edible, Concentrate
- **All strains** from your database
- **Complete vendor and brand information**
- **Full JointRatio functionality**
- **All THC/CBD percentages and pricing**

---

## 🧪 Testing After Deployment

After reloading your web app, verify it's working:

1. **Visit your site**: https://adamcordova.pythonanywhere.com
2. **Check the dashboard** - should show 7,853 products
3. **Test file upload** - upload a test Excel file
4. **Generate a label** - verify label generation works
5. **Check stats** - verify product counts are correct

---

## ⚠️ Important Notes

1. **Disk Space**: The uncompressed database is 250 MB
   - Make sure you have enough space on PythonAnywhere
   - You may need a paid plan for this size

2. **Backup**: The compressed file is saved locally:
   - Path: `uploads/product_database_AGT_Bothell.db.gz`
   - Keep this as a backup

3. **Old Database**: The extraction will replace any existing database
   - Make sure this is what you want
   - The old database will be overwritten

---

## 🔍 Troubleshooting

### If Upload Fails
- **File too large**: Your plan may have file size limits
- **No space**: Check available disk space on PythonAnywhere
- **Timeout**: Try the manual upload method instead

### If Database Doesn't Work
```bash
# Check database integrity
cd ~/AGTDesigner/uploads
sqlite3 product_database_AGT_Bothell.db "PRAGMA integrity_check;"

# Check product count
sqlite3 product_database_AGT_Bothell.db "SELECT COUNT(*) FROM products;"
```

### If Web App Won't Start
```bash
# Check error log
tail -f /var/log/adamcordova.pythonanywhere.com.error.log

# Test app import
cd ~/AGTDesigner
python3.11 -c "from app import app; print('✅ App OK')"
```

---

## 🎉 Success!

Once deployed, your web app will have:
- ✅ 7,853 products available
- ✅ All product matching features
- ✅ Complete label generation
- ✅ Full AI matching capabilities
- ✅ JointRatio support for pre-rolls

Your database is ready to go! 🚀

