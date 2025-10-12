#!/bin/bash
# Complete fix for PythonAnywhere: Database restoration + API fixes

echo "🔧 COMPLETE PYTHONANYWHERE FIX"
echo "==============================="
echo ""

# Create timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
ZIP_FILE="complete_fix_${TIMESTAMP}.zip"

echo "📦 Creating comprehensive fix package..."

# Create a temporary directory for the fix
TEMP_DIR="temp_fix_${TIMESTAMP}"
mkdir -p "$TEMP_DIR"

# Copy the fixed app.py
cp app.py "$TEMP_DIR/"

# Create the deployment script for PythonAnywhere
cat > "$TEMP_DIR/deploy_fix.sh" << 'DEPLOY_SCRIPT'
#!/bin/bash
# Deploy script to run on PythonAnywhere

echo "🚀 DEPLOYING COMPLETE FIX"
echo "========================="

# Step 1: Restore database from backup
echo ""
echo "📊 Step 1: Restoring database..."
BACKUP_FILE="uploads/product_database_AGT_Bothell.db.corrupted.20251012_213432"
CURRENT_DB="uploads/product_database_AGT_Bothell.db"

if [ -f "$BACKUP_FILE" ]; then
    # Backup current database
    cp "$CURRENT_DB" "uploads/product_database_AGT_Bothell.db.backup.$(date +%Y%m%d_%H%M%S)"
    
    # Restore from backup
    cp "$BACKUP_FILE" "$CURRENT_DB"
    
    # Verify restoration
    PRODUCT_COUNT=$(sqlite3 "$CURRENT_DB" "SELECT COUNT(*) FROM products;" 2>/dev/null)
    echo "✅ Database restored: $PRODUCT_COUNT products"
else
    echo "⚠️  Backup file not found, checking main database..."
    
    # Alternative: copy from main database if it exists and has products
    MAIN_DB="uploads/product_database.db"
    if [ -f "$MAIN_DB" ]; then
        MAIN_COUNT=$(sqlite3 "$MAIN_DB" "SELECT COUNT(*) FROM products;" 2>/dev/null)
        if [ "$MAIN_COUNT" -gt 5000 ]; then
            echo "📋 Found main database with $MAIN_COUNT products"
            cp "$MAIN_DB" "$CURRENT_DB"
            echo "✅ Copied main database to AGT_Bothell database"
        fi
    fi
fi

# Step 2: Deploy fixed app.py
echo ""
echo "🔧 Step 2: Deploying fixed app.py..."

# Find the web app directory
if [ -d "/home/$(whoami)/mysite" ]; then
    WEB_DIR="/home/$(whoami)/mysite"
elif [ -d "/home/$(whoami)/AGTDesigner" ]; then
    WEB_DIR="/home/$(whoami)/AGTDesigner"
else
    WEB_DIR="$(pwd)"
fi

echo "Web directory: $WEB_DIR"

# Backup current app.py
if [ -f "$WEB_DIR/app.py" ]; then
    cp "$WEB_DIR/app.py" "$WEB_DIR/app.py.backup.$(date +%Y%m%d_%H%M%S)"
    echo "✅ Backed up current app.py"
fi

# Copy fixed app.py
cp app.py "$WEB_DIR/"
echo "✅ Deployed fixed app.py"

# Step 3: Verify database
echo ""
echo "🔍 Step 3: Verifying database..."
FINAL_COUNT=$(sqlite3 "$CURRENT_DB" "SELECT COUNT(*) FROM products;" 2>/dev/null)
FINAL_SIZE=$(du -h "$CURRENT_DB" | cut -f1)
echo "Database size: $FINAL_SIZE"
echo "Product count: $FINAL_COUNT"

if [ "$FINAL_COUNT" -gt 1000 ]; then
    echo "✅ Database verification passed"
else
    echo "⚠️  Low product count - may need manual database restoration"
fi

# Step 4: Check database integrity
echo ""
echo "🔍 Step 4: Checking database integrity..."
INTEGRITY=$(sqlite3 "$CURRENT_DB" "PRAGMA integrity_check;" 2>/dev/null | head -1)
if [ "$INTEGRITY" = "ok" ]; then
    echo "✅ Database integrity: OK"
else
    echo "❌ Database integrity check failed: $INTEGRITY"
fi

echo ""
echo "================================="
echo "🎉 DEPLOYMENT COMPLETE!"
echo "================================="
echo ""
echo "📋 NEXT STEPS:"
echo "1. Go to PythonAnywhere Web tab"
echo "2. Click 'Reload' button for your web app"
echo "3. Wait 30-60 seconds for reload to complete"
echo "4. Visit https://www.agtpricetags.com"
echo "5. Check that:"
echo "   - Product count shows correct number"
echo "   - API endpoints work (no 500 errors)"
echo "   - Database analytics loads correctly"
echo ""
echo "🧪 Test these URLs:"
echo "   - https://www.agtpricetags.com/api/database-stats"
echo "   - https://www.agtpricetags.com/api/database-vendor-stats"
echo "   - https://www.agtpricetags.com/api/database-analytics"
echo ""
DEPLOY_SCRIPT

chmod +x "$TEMP_DIR/deploy_fix.sh"

# Create instructions file
cat > "$TEMP_DIR/INSTRUCTIONS.txt" << 'INSTRUCTIONS'
🚀 COMPLETE PYTHONANYWHERE FIX
==============================

This package contains:
✅ Fixed app.py (with pandas imports for API endpoints)
✅ Automated deployment script

📋 DEPLOYMENT STEPS:
====================

1. Upload this zip file to PythonAnywhere:
   - Go to Files tab
   - Click "Upload a file"
   - Select the zip file

2. Extract the zip file:
   $ unzip complete_fix_TIMESTAMP.zip

3. Run the deployment script:
   $ cd temp_fix_TIMESTAMP
   $ chmod +x deploy_fix.sh
   $ ./deploy_fix.sh

4. Reload your web app:
   - Go to Web tab
   - Click "Reload" button
   - Wait 30-60 seconds

5. Verify the fix:
   - Visit https://www.agtpricetags.com
   - Check product count displays correctly
   - Test API endpoints (should return 200, not 500)

🔧 WHAT THIS FIX DOES:
======================

✅ Restores database from backup (product_database_AGT_Bothell.db.corrupted.20251012_213432)
✅ Deploys fixed app.py with pandas imports
✅ Verifies database integrity
✅ Checks product count

🆘 IF PROBLEMS PERSIST:
========================

1. Check PythonAnywhere error logs:
   - Web tab → Log files → Error log

2. Manually verify database:
   $ sqlite3 uploads/product_database_AGT_Bothell.db "SELECT COUNT(*) FROM products;"

3. Check which database file is being used:
   $ ls -lh uploads/product_database*.db

4. If database is still wrong, manually copy:
   $ cp uploads/product_database.db uploads/product_database_AGT_Bothell.db

INSTRUCTIONS

# Create the zip file
echo "Creating $ZIP_FILE..."
cd "$TEMP_DIR"
zip -r "../$ZIP_FILE" .
cd ..

# Cleanup
rm -rf "$TEMP_DIR"

echo "✅ Created: $ZIP_FILE"
echo ""

# Show what's in the package
echo "📦 Package contents:"
unzip -l "$ZIP_FILE"
echo ""

echo "==============================="
echo "📋 DEPLOYMENT INSTRUCTIONS"
echo "==============================="
echo ""
echo "1. Upload $ZIP_FILE to PythonAnywhere"
echo ""
echo "2. In PythonAnywhere Bash console, run:"
echo "   unzip $ZIP_FILE"
echo "   cd temp_fix_*"
echo "   chmod +x deploy_fix.sh"
echo "   ./deploy_fix.sh"
echo ""
echo "3. Reload your web app in PythonAnywhere Web tab"
echo ""
echo "4. Visit https://www.agtpricetags.com to verify"
echo ""
echo "==============================="
echo "🎯 This will fix:"
echo "  ✅ Database restoration"
echo "  ✅ API 500 errors"
echo "  ✅ Product count display"
echo "==============================="
