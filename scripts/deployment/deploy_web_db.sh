#!/bin/bash
# One-command deployment script for PythonAnywhere web database

echo "🚀 Deploying Database to PythonAnywhere Web"
echo "============================================="

cd ~/AGTDesigner || exit 1

# Step 1: Backup current database
echo "📦 Backing up current database..."
cp uploads/product_database_AGT_Bothell.db uploads/product_database_AGT_Bothell.db.backup_$(date +%Y%m%d_%H%M%S) 2>/dev/null

# Step 2: Extract new database
echo "📂 Extracting database..."
if [ -f "product_database_AGT_Bothell_20251027_084251.zip" ]; then
    unzip -o product_database_AGT_Bothell_20251027_084251.zip
    mv product_database_AGT_Bothell.db uploads/ 2>/dev/null
    echo "✅ Database extracted"
else
    echo "⚠️  Database zip not found. Looking for latest..."
    LATEST_ZIP=$(ls -t product_database_AGT_Bothell_*.zip 2>/dev/null | head -1)
    if [ -n "$LATEST_ZIP" ]; then
        echo "Found: $LATEST_ZIP"
        unzip -o "$LATEST_ZIP"
        mv product_database_AGT_Bothell.db uploads/ 2>/dev/null
        echo "✅ Database extracted from $LATEST_ZIP"
    else
        echo "❌ No database zip file found!"
        exit 1
    fi
fi

# Step 3: Set permissions
echo "🔐 Setting permissions..."
chmod 644 uploads/product_database_AGT_Bothell.db

# Step 4: Verify database
echo "🔍 Verifying database..."
python3 << 'EOF'
import sqlite3
try:
    conn = sqlite3.connect('uploads/product_database_AGT_Bothell.db')
    cursor = conn.cursor()
    cursor.execute('PRAGMA integrity_check')
    integrity = cursor.fetchone()[0]
    print(f"   Integrity: {integrity}")
    cursor.execute('SELECT COUNT(*) FROM products')
    products = cursor.fetchone()[0]
    print(f"   Products: {products}")
    conn.close()
    if integrity == 'ok' and products > 0:
        print("✅ Database verified successfully")
    else:
        print("❌ Database verification failed")
        exit(1)
except Exception as e:
    print(f"❌ Database error: {e}")
    exit(1)
EOF

# Step 5: Update code (optional)
echo ""
read -p "Update code from GitHub? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔄 Updating code..."
    git fetch origin
    git reset --hard origin/main
    git clean -fd
    echo "✅ Code updated"
fi

echo ""
echo "============================================="
echo "✅ DEPLOYMENT COMPLETE!"
echo "============================================="
echo ""
echo "Next steps:"
echo "1. Go to PythonAnywhere Web tab"
echo "2. Click 'Reload' button for www.agtpricetags.com"
echo "3. Wait 15-20 seconds"
echo "4. Visit https://www.agtpricetags.com"
echo ""
