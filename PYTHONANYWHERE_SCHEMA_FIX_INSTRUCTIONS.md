# PythonAnywhere Database Schema Fix

## Problem
The database on PythonAnywhere is missing the `normalized_name` column in the `strains` table, causing the error:
```
sqlite3.OperationalError: no such column: normalized_name
```

## Solution

### Step 1: Pull Latest Code
SSH into your PythonAnywhere console and pull the latest changes:

```bash
cd ~/AGTDesigner
git pull origin main
```

### Step 2: Run the Schema Fix Script
Run the automated fix script to add the missing column:

```bash
cd ~/AGTDesigner
python3 fix_pythonanywhere_schema.py
```

The script will:
1. Check if the `normalized_name` column exists
2. Add the column if it's missing
3. Update all existing strain records with normalized names
4. Verify the fix was successful

### Step 3: Reload Your Web App
After the script completes successfully:
1. Go to your PythonAnywhere dashboard
2. Navigate to the "Web" tab
3. Click the green "Reload" button

### Expected Output
If successful, you should see:
```
============================================================
PythonAnywhere Database Schema Fix
============================================================
Checking database at: /home/adamcordova/AGTDesigner/uploads/product_database_AGT_Bothell.db

Current strains table columns: [...]

⚠️  normalized_name column is MISSING
Adding normalized_name column to strains table...
✓ Column added successfully
Updating existing strain records...
✓ Updated XXXX existing strain records

✅ Database schema fixed successfully!

============================================================
SUCCESS! You can now reload your web app.
============================================================
```

### Alternative: Manual SQL Fix
If you prefer to run the SQL manually:

```bash
cd ~/AGTDesigner
sqlite3 uploads/product_database_AGT_Bothell.db
```

Then run these SQL commands:
```sql
-- Add the column
ALTER TABLE strains ADD COLUMN normalized_name TEXT;

-- Populate existing records
UPDATE strains 
SET normalized_name = LOWER(REPLACE(REPLACE(strain_name, ' ', ''), '-', ''))
WHERE normalized_name IS NULL;

-- Verify
PRAGMA table_info(strains);

-- Exit
.quit
```

### Troubleshooting

**If the script fails:**
1. Check that the database file exists at the expected path
2. Ensure you have write permissions to the database file
3. Check the error messages for specific issues

**If the error persists after the fix:**
1. Make sure you reloaded the web app
2. Check the error logs for any new errors
3. Verify the column was actually added: `sqlite3 uploads/product_database_AGT_Bothell.db "PRAGMA table_info(strains);"`

## What This Fixes

The code now includes automatic migration that will:
- Check for the `normalized_name` column before creating indexes
- Automatically add the column if it's missing during database initialization
- Prevent the "no such column" error from occurring in the future

This fix ensures backward compatibility with older database schemas while supporting the new functionality.

