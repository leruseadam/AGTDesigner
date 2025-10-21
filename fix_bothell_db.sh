#!/bin/bash
# Quick fix to make ProductDatabase use the Bothell database

echo "🔧 FIXING DATABASE FOR BOTHELL STORE"
echo "======================================"

# Check if Bothell database exists
if [ ! -f "uploads/product_database_AGT_Bothell.db" ]; then
    echo "❌ Error: uploads/product_database_AGT_Bothell.db not found!"
    exit 1
fi

echo "✅ Bothell database found"

# Backup current product_database.db if it exists
if [ -f "uploads/product_database.db" ]; then
    echo "📦 Backing up current product_database.db..."
    cp uploads/product_database.db uploads/product_database.db.backup_$(date +%Y%m%d_%H%M%S)
    echo "✅ Backup created"
fi

# Copy Bothell database to product_database.db
echo "🔄 Copying Bothell database to product_database.db..."
cp uploads/product_database_AGT_Bothell.db uploads/product_database.db

if [ $? -eq 0 ]; then
    echo "✅ Database copied successfully"
    
    # Check the new database
    PRODUCT_COUNT=$(python3 -c "import sqlite3; conn = sqlite3.connect('uploads/product_database.db'); print(conn.execute('SELECT COUNT(*) FROM products').fetchone()[0]); conn.close()" 2>/dev/null)
    
    if [ -n "$PRODUCT_COUNT" ]; then
        echo "📊 New database has $PRODUCT_COUNT products"
    fi
    
    echo ""
    echo "======================================"
    echo "✅ FIX COMPLETE!"
    echo ""
    echo "Next steps:"
    echo "1. Reload web app: https://www.pythonanywhere.com/user/adamcordova/webapps/"
    echo "2. Click 'Reload www.agtpricetags.com'"
    echo "3. Wait 30 seconds"
    echo "4. Clear browser cache: Ctrl+Shift+R or Cmd+Shift+R"
    echo "5. Test lineage changes at: https://www.agtpricetags.com"
    echo "======================================"
else
    echo "❌ Failed to copy database"
    exit 1
fi

