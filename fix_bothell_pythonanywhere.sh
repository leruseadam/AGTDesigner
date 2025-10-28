#!/bin/bash
echo "=========================================================================="
echo "COMPREHENSIVE BOTHELL DATABASE FIX FOR PYTHONANYWHERE"
echo "=========================================================================="
echo ""

# Navigate to project directory
cd ~/AGTDesigner || { echo "❌ Error: Project directory not found"; exit 1; }

echo "📍 Current directory: $(pwd)"
echo ""

# STEP 1: Backup current database
echo "Step 1: Creating backup..."
if [ -f "uploads/product_database_AGT_Bothell.db" ]; then
    cp uploads/product_database_AGT_Bothell.db "uploads/product_database_AGT_Bothell.db.backup_$(date +%Y%m%d_%H%M%S)"
    echo "✅ Backup created"
else
    echo "⚠️  No existing database to backup"
fi
echo ""

# STEP 2: Remove WAL/SHM files (can cause corruption)
echo "Step 2: Removing WAL/SHM files..."
rm -f uploads/product_database_AGT_Bothell.db-wal
rm -f uploads/product_database_AGT_Bothell.db-shm
echo "✅ Removed WAL/SHM files"
echo ""

# STEP 3: Check current database status
echo "Step 3: Checking current database status..."
python3 << 'PYTHONEOF'
import sqlite3
import os

db_path = 'uploads/product_database_AGT_Bothell.db'

if os.path.exists(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check integrity
        cursor.execute('PRAGMA integrity_check')
        integrity = cursor.fetchone()[0]
        print(f"Integrity check: {integrity}")
        
        # Count products
        cursor.execute('SELECT COUNT(*) FROM products')
        count = cursor.fetchone()[0]
        print(f"Product count: {count}")
        
        conn.close()
    except Exception as e:
        print(f"Error checking database: {e}")
else:
    print("Database file not found")
PYTHONEOF

echo ""

# STEP 4: Run rebuild script
echo "Step 4: Rebuilding database with clean schema..."
python3 rebuild_bothell_db_fixed.py

echo ""

# STEP 5: Verify the rebuild
echo "Step 5: Verifying rebuilt database..."
python3 << 'PYTHONEOF'
import sqlite3
import os

db_path = 'uploads/product_database_AGT_Bothell.db'

if os.path.exists(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check integrity
        cursor.execute('PRAGMA integrity_check')
        integrity = cursor.fetchone()[0]
        print(f"✅ Integrity check: {integrity}")
        
        # Count products
        cursor.execute('SELECT COUNT(*) FROM products')
        count = cursor.fetchone()[0]
        print(f"✅ Product count: {count}")
        
        if integrity == 'ok' and count > 0:
            print(f"✅ Database is healthy with {count} products")
        else:
            print(f"❌ Database issues detected")
        
        conn.close()
    except Exception as e:
        print(f"❌ Error: {e}")
else:
    print("❌ Database file not found after rebuild")
PYTHONEOF

echo ""
echo "=========================================================================="
echo "✅ FIX COMPLETE!"
echo "=========================================================================="
echo ""
echo "Next steps:"
echo "1. Go to https://www.pythonanywhere.com/user/adamcordova/webapps/"
echo "2. Click the big green 'Reload www.agtpricetags.com' button"
echo "3. Wait 30 seconds for the app to restart"
echo "4. Visit https://www.agtpricetags.com to verify the fix"
echo ""
