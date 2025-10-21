#!/bin/bash
# Switch to using the Bothell database
# Run this on PythonAnywhere

echo "🔄 Switching to Bothell Database..."
echo "======================================"

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: Not in AGTDesigner directory"
    echo "Run: cd ~/AGTDesigner"
    exit 1
fi

# Find the Bothell database
BOTHELL_DB=$(find uploads -name "*Bothell*.db" -not -name "*-shm" -not -name "*-wal" | head -1)

if [ -z "$BOTHELL_DB" ]; then
    echo "❌ Error: Bothell database not found"
    echo "Looking for files with 'Bothell' in uploads/"
    ls -la uploads/*Bothell* 2>/dev/null || echo "No Bothell files found"
    exit 1
fi

echo "✅ Found Bothell database: $BOTHELL_DB"

# Check product count
PRODUCT_COUNT=$(sqlite3 "$BOTHELL_DB" "SELECT COUNT(*) FROM products;" 2>/dev/null)
if [ -n "$PRODUCT_COUNT" ]; then
    echo "📦 Bothell DB has $PRODUCT_COUNT products"
else
    echo "⚠️  Could not read product count"
fi

# Backup current database
CURRENT_DB="uploads/product_database.db"
if [ -f "$CURRENT_DB" ]; then
    BACKUP_NAME="${CURRENT_DB}.backup_$(date +%Y%m%d_%H%M%S)"
    echo "💾 Backing up current database to: $BACKUP_NAME"
    cp "$CURRENT_DB" "$BACKUP_NAME"
fi

# Copy Bothell database to product_database.db
echo "🔄 Copying Bothell database to product_database.db..."
cp "$BOTHELL_DB" "$CURRENT_DB"

if [ $? -eq 0 ]; then
    echo "✅ Successfully switched to Bothell database!"
    
    # Set proper permissions
    chmod 664 "$CURRENT_DB"
    echo "✅ Set permissions (664)"
    
    # Verify the switch
    NEW_COUNT=$(sqlite3 "$CURRENT_DB" "SELECT COUNT(*) FROM products;" 2>/dev/null)
    if [ -n "$NEW_COUNT" ]; then
        echo "✅ Verification: product_database.db now has $NEW_COUNT products"
    fi
    
    echo ""
    echo "======================================"
    echo "✅ DATABASE SWITCH COMPLETE!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Reload web app:"
    echo "   Go to: https://www.pythonanywhere.com/user/adamcordova/webapps/"
    echo "   Click 'Reload www.agtpricetags.com'"
    echo ""
    echo "2. Clear browser cache:"
    echo "   Press Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)"
    echo ""
    echo "3. Test lineage changes:"
    echo "   - Visit: https://www.agtpricetags.com"
    echo "   - Change a product's lineage"
    echo "   - Generate DOCX"
    echo "   - Check if color changed!"
    echo "======================================"
else
    echo "❌ Error: Failed to copy database"
    exit 1
fi

