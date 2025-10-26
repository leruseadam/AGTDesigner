#!/bin/bash
# Quick fix for PythonAnywhere database issue

echo "🔧 QUICK FIX FOR PYTHONANYWHERE DATABASE"
echo "========================================"

# Check current database
echo "Checking current database..."
if [ -f "uploads/product_database_AGT_Bothell.db" ]; then
    size_mb=$(du -h "uploads/product_database_AGT_Bothell.db" | cut -f1)
    echo "Current AGT_Bothell database: $size_mb"
    
    # Check product count
    count=$(sqlite3 "uploads/product_database_AGT_Bothell.db" "SELECT COUNT(*) FROM products;" 2>/dev/null)
    echo "Current product count: $count"
else
    echo "❌ AGT_Bothell database not found"
fi

# Check main database
echo "Checking main database..."
if [ -f "uploads/product_database.db" ]; then
    size_mb=$(du -h "uploads/product_database.db" | cut -f1)
    echo "Main database: $size_mb"
    
    # Check product count
    count=$(sqlite3 "uploads/product_database.db" "SELECT COUNT(*) FROM products;" 2>/dev/null)
    echo "Main database product count: $count"
    
    # If main database has more products, restore from it
    if [ "$count" -gt 10000 ]; then
        echo "✅ Main database has correct number of products"
        echo "🔄 Restoring AGT_Bothell database from main database..."
        
        # Backup current database
        timestamp=$(date +%Y%m%d_%H%M%S)
        cp "uploads/product_database_AGT_Bothell.db" "uploads/product_database_AGT_Bothell.db.backup.$timestamp"
        echo "✅ Backed up current database"
        
        # Copy main database to AGT_Bothell
        cp "uploads/product_database.db" "uploads/product_database_AGT_Bothell.db"
        echo "✅ Restored AGT_Bothell database"
        
        # Verify restoration
        new_count=$(sqlite3 "uploads/product_database_AGT_Bothell.db" "SELECT COUNT(*) FROM products;" 2>/dev/null)
        echo "✅ New product count: $new_count"
        
        if [ "$new_count" -gt 10000 ]; then
            echo "🎉 SUCCESS! Database restored successfully"
        else
            echo "❌ Restoration failed"
        fi
    else
        echo "⚠️  Main database also has few products"
    fi
else
    echo "❌ Main database not found"
fi

echo ""
echo "========================================"
echo "📋 NEXT STEPS:"
echo "1. Go to PythonAnywhere Web tab"
echo "2. Click 'Reload' for your web app"
echo "3. Wait 30-60 seconds"
echo "4. Visit https://www.agtpricetags.com"
echo "5. Should now show 10,000+ products"
echo "========================================"
