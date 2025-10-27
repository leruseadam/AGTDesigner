# Backfill Web Database on PythonAnywhere

## Quick Deploy Steps

### Step 1: Upload Database to PythonAnywhere

**Option A: Using PythonAnywhere Files Interface (Easiest)**
1. Go to https://www.pythonanywhere.com
2. Click **"Files"** tab
3. Navigate to: `/home/adamcordova/AGTDesigner/uploads/`
4. Click **"Upload a file"** button
5. Select: `product_database_AGT_Bothell_20251027_084251.zip`
6. Wait for upload to complete

**Option B: Using Command Line**
```bash
cd /Users/adamcordova/Desktop/labelMaker_\ QR\ copy\ final
scp product_database_AGT_Bothell_20251027_084251.zip adamcordova@ssh.pythonanywhere.com:~/AGTDesigner/
```

### Step 2: Deploy Database on PythonAnywhere

Open a **Bash console** on PythonAnywhere and run:

```bash
cd ~/AGTDesigner

# Backup current database
cp uploads/product_database_AGT_Bothell.db uploads/product_database_AGT_Bothell.db.backup_$(date +%Y%m%d_%H%M%S)

# Extract new database
unzip -o product_database_AGT_Bothell_20251027_084251.zip

# Move to uploads folder
mv product_database_AGT_Bothell.db uploads/

# Set correct permissions
chmod 644 uploads/product_database_AGT_Bothell.db

# Verify database integrity
python3 << 'EOF'
import sqlite3
conn = sqlite3.connect('uploads/product_database_AGT_Bothell.db')
cursor = conn.cursor()
cursor.execute('PRAGMA integrity_check')
print(f"Integrity: {cursor.fetchone()[0]}")
cursor.execute('SELECT COUNT(*) FROM products')
print(f"Products: {cursor.fetchone()[0]}")
cursor.execute('SELECT COUNT(*) FROM strains')
print(f"Strains: {cursor.fetchone()[0]}")
conn.close()
EOF
```

### Step 3: Deploy Latest Code

```bash
cd ~/AGTDesigner

# Pull latest changes from GitHub (includes price fixes)
git fetch origin
git reset --hard origin/main

# Clean untracked files
git clean -fd

echo "✅ Code updated"
```

### Step 4: Reload Web App

1. Go to PythonAnywhere **"Web"** tab
2. Click the big green **"Reload"** button for `www.agtpricetags.com`
3. Wait 15-20 seconds for reload to complete

### Step 5: Verify

Visit: https://www.agtpricetags.com

Expected results:
- ✅ Products load correctly
- ✅ No default $25 prices (prices will be empty if missing in source data)
- ✅ Can generate labels

## What Changed

The latest code includes:
- ✅ Removed all default `$25` prices
- ✅ Missing prices now show as empty (easy to identify)
- ✅ Added logging to trace price issues
- ✅ Better debugging for missing price data

## File Location

Local database backup:
- File: `product_database_AGT_Bothell_20251027_084251.zip`
- Location: `/Users/adamcordova/Desktop/labelMaker_ QR copy final/`
- Size: 1.1MB
