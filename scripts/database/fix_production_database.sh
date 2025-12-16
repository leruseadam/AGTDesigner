#!/bin/bash
# Comprehensive fix for PythonAnywhere production database issues

echo "=================================================="
echo "🔧 FIXING PRODUCTION DATABASE ISSUES"
echo "=================================================="
echo ""

cd "$(dirname "$0")"

# Step 1: Verify local database is working
echo "Step 1: Verifying local database..."
DB_FILE="uploads/product_database_AGT_Bothell.db"

if [ ! -f "$DB_FILE" ]; then
    echo "❌ Error: Database not found at $DB_FILE"
    exit 1
fi

# Check database integrity
if sqlite3 "$DB_FILE" "PRAGMA integrity_check;" | grep -q "ok"; then
    echo "✅ Database integrity: OK"
else
    echo "❌ Database integrity check failed!"
    exit 1
fi

# Check product count
PRODUCT_COUNT=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM products;")
echo "✅ Product count: $PRODUCT_COUNT"

if [ "$PRODUCT_COUNT" -lt 10000 ]; then
    echo "❌ Warning: Database has very few products ($PRODUCT_COUNT)"
    echo "This might cause the 500 error on production"
fi

# Get database size
DB_SIZE=$(du -h "$DB_FILE" | cut -f1)
echo "✅ Database size: $DB_SIZE"
echo ""

# Step 2: Create optimized database package
echo "Step 2: Creating optimized database package..."
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
ZIP_NAME="production_database_fix_${TIMESTAMP}.zip"

# Remove any existing zip files with similar names
rm -f production_database_fix_*.zip

# Create zip with database and diagnostic tools
cd uploads
zip -q "../${ZIP_NAME}" "product_database_AGT_Bothell.db"
cd ..

# Add diagnostic script to zip
zip -q "${ZIP_NAME}" "debug_production_db.py"

if [ -f "$ZIP_NAME" ]; then
    ZIP_SIZE=$(du -h "$ZIP_NAME" | cut -f1)
    echo "✅ Created: $ZIP_NAME ($ZIP_SIZE)"
else
    echo "❌ Failed to create zip file"
    exit 1
fi
echo ""

# Step 3: Create deployment script for PythonAnywhere
echo "Step 3: Creating PythonAnywhere deployment script..."
cat > "deploy_to_pythonanywhere.sh" << 'EOF'
#!/bin/bash
# Run this script on PythonAnywhere to deploy the database

echo "=================================================="
echo "🚀 DEPLOYING DATABASE TO PYTHONANYWHERE"
echo "=================================================="

# Check if we're in the right directory
if [ ! -d "uploads" ]; then
    echo "Creating uploads directory..."
    mkdir -p uploads
fi

# Extract the database
echo "Extracting database..."
unzip -o production_database_fix_*.zip

# Move database to uploads directory
echo "Moving database to uploads directory..."
mv product_database_AGT_Bothell.db uploads/

# Set correct permissions
echo "Setting database permissions..."
chmod 644 uploads/product_database_AGT_Bothell.db

# Clean up
echo "Cleaning up..."
rm -f production_database_fix_*.zip

# Test the database
echo "Testing database..."
python3 debug_production_db.py

echo ""
echo "✅ Database deployment complete!"
echo "Now reload your web app in the PythonAnywhere Web tab"
EOF

chmod +x deploy_to_pythonanywhere.sh
echo "✅ Created: deploy_to_pythonanywhere.sh"
echo ""

# Step 4: Create comprehensive fix instructions
echo "Step 4: Creating fix instructions..."
cat > "PRODUCTION_FIX_COMPLETE.md" << EOF
# 🔧 Complete Production Database Fix

## Problem
- Production website showing **0 TOTAL PRODUCTS**
- **500 Internal Server Error** in browser console
- Database not accessible on PythonAnywhere

## Solution
The local database is working correctly with **$PRODUCT_COUNT products**. 
We need to deploy it to PythonAnywhere.

## Files Created
- \`${ZIP_NAME}\` - Database package (${ZIP_SIZE})
- \`deploy_to_pythonanywhere.sh\` - Deployment script
- \`debug_production_db.py\` - Diagnostic tool

## Deployment Steps

### 1. Upload to PythonAnywhere
- Go to PythonAnywhere **Files** tab
- Navigate to: \`/home/adamcordova/AGTDesigner\`
- Click **"Upload a file"**
- Select: \`${ZIP_NAME}\`

### 2. Deploy Database
- Open PythonAnywhere **Bash console**
- Run these commands:
\`\`\`bash
cd ~/AGTDesigner
chmod +x deploy_to_pythonanywhere.sh
./deploy_to_pythonanywhere.sh
\`\`\`

### 3. Reload Web App
- Go to PythonAnywhere **Web** tab
- Click **"Reload"** for your web app
- Wait 30 seconds for reload to complete

### 4. Verify Fix
- Visit: https://www.agtpricetags.com
- Should now show:
  - **$PRODUCT_COUNT TOTAL PRODUCTS** ✅
  - **101+ UNIQUE VENDORS** ✅
  - **166+ UNIQUE BRANDS** ✅

## Troubleshooting

### If still showing 0 products:
1. Check PythonAnywhere **Error log** (Web tab)
2. Run diagnostic: \`python3 debug_production_db.py\`
3. Verify database file exists: \`ls -la uploads/\`

### If 500 error persists:
1. Check file permissions: \`chmod 644 uploads/product_database_AGT_Bothell.db\`
2. Verify database integrity: \`sqlite3 uploads/product_database_AGT_Bothell.db "PRAGMA integrity_check;"\`
3. Check PythonAnywhere error logs for specific error message

## Expected Result
After successful deployment, the website should display:
- ✅ **$PRODUCT_COUNT TOTAL PRODUCTS** (instead of 0)
- ✅ **101 UNIQUE VENDORS** (instead of 0)  
- ✅ **166 UNIQUE BRANDS** (instead of 0)
- ✅ **25 PRODUCT TYPES** (instead of 0)
- ✅ No more 500 errors in browser console

## Files to Upload
Upload this zip file to PythonAnywhere:
**${ZIP_NAME}** (${ZIP_SIZE})
EOF

echo "✅ Created: PRODUCTION_FIX_COMPLETE.md"
echo ""

# Step 5: Test local functionality
echo "Step 5: Testing local database functionality..."
python3 -c "
from src.core.data.product_database import get_product_database
import sqlite3

try:
    db = get_product_database()
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM products')
    count = cursor.fetchone()[0]
    conn.close()
    
    print(f'✅ Local database working: {count} products')
    if count > 10000:
        print('✅ Database is ready for production deployment')
    else:
        print('⚠️  Database has fewer products than expected')
        
except Exception as e:
    print(f'❌ Local database error: {e}')
"
echo ""

echo "=================================================="
echo "✅ PRODUCTION FIX READY!"
echo "=================================================="
echo ""
echo "📦 Package created: ${ZIP_NAME} (${ZIP_SIZE})"
echo ""
echo "🚀 Next steps:"
echo "1. Upload ${ZIP_NAME} to PythonAnywhere"
echo "2. Run: ./deploy_to_pythonanywhere.sh"
echo "3. Reload your web app"
echo "4. Visit https://www.agtpricetags.com"
echo ""
echo "📋 Full instructions: PRODUCTION_FIX_COMPLETE.md"
echo "=================================================="
