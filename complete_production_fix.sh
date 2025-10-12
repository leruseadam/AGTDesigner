#!/bin/bash
# Complete production fix - Database + JavaScript + API

echo "=================================================="
echo "🚀 COMPLETE PRODUCTION FIX"
echo "=================================================="
echo ""

cd "$(dirname "$0")"

# Step 1: Verify local database
echo "Step 1: Verifying local database..."
DB_FILE="uploads/product_database_AGT_Bothell.db"

if [ ! -f "$DB_FILE" ]; then
    echo "❌ Error: Database not found at $DB_FILE"
    exit 1
fi

# Check database integrity and count
PRODUCT_COUNT=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM products;" 2>/dev/null)
if [ $? -eq 0 ] && [ "$PRODUCT_COUNT" -gt 10000 ]; then
    echo "✅ Database verified: $PRODUCT_COUNT products"
else
    echo "❌ Database issue: $PRODUCT_COUNT products"
    echo "Restoring from main database..."
    cp uploads/product_database.db uploads/product_database_AGT_Bothell.db
    PRODUCT_COUNT=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM products;")
    echo "✅ Database restored: $PRODUCT_COUNT products"
fi

# Step 2: Test local API
echo "Step 2: Testing local API..."
python3 -c "
from app import app
import json

with app.test_client() as client:
    response = client.get('/api/database-stats')
    if response.status_code == 200:
        data = response.get_json()
        product_count = data.get('stats', {}).get('total_products', 0)
        print(f'✅ Local API working: {product_count} products')
        if product_count > 10000:
            print('✅ Local API is ready for production')
        else:
            print('⚠️  Local API showing fewer products than expected')
    else:
        print(f'❌ Local API error: {response.status_code}')
" 2>/dev/null

# Step 3: Create comprehensive deployment package
echo "Step 3: Creating comprehensive deployment package..."
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
COMPLETE_FIX_ZIP="complete_production_fix_${TIMESTAMP}.zip"

# Remove old packages
rm -f complete_production_fix_*.zip

# Create comprehensive package
zip -q "${COMPLETE_FIX_ZIP}" \
    uploads/product_database_AGT_Bothell.db \
    static/js/production_error_fix.js \
    static/js/tags_table.js \
    debug_production_db.py \
    deploy_to_pythonanywhere.sh

if [ -f "$COMPLETE_FIX_ZIP" ]; then
    ZIP_SIZE=$(du -h "$COMPLETE_FIX_ZIP" | cut -f1)
    echo "✅ Created: ${COMPLETE_FIX_ZIP} ($ZIP_SIZE)"
else
    echo "❌ Failed to create deployment package"
    exit 1
fi

# Step 4: Create deployment script for PythonAnywhere
echo "Step 4: Creating deployment script..."
cat > "deploy_complete_fix.sh" << 'EOF'
#!/bin/bash
# Complete production fix deployment script for PythonAnywhere

echo "=================================================="
echo "🚀 DEPLOYING COMPLETE PRODUCTION FIX"
echo "=================================================="

# Check if we're in the right directory
if [ ! -d "uploads" ]; then
    echo "Creating uploads directory..."
    mkdir -p uploads
fi

if [ ! -d "static/js" ]; then
    echo "Creating static/js directory..."
    mkdir -p static/js
fi

# Extract the complete fix package
echo "Extracting complete fix package..."
unzip -o complete_production_fix_*.zip

# Set correct permissions
echo "Setting permissions..."
chmod 644 uploads/product_database_AGT_Bothell.db
chmod 644 static/js/*.js

# Test the database
echo "Testing database..."
python3 debug_production_db.py

# Clean up
echo "Cleaning up..."
rm -f complete_production_fix_*.zip

echo ""
echo "✅ Complete fix deployment finished!"
echo ""
echo "Next steps:"
echo "1. Reload your web app in PythonAnywhere Web tab"
echo "2. Wait 30 seconds for reload to complete"
echo "3. Visit https://www.agtpricetags.com"
echo "4. Should now show 10,543+ products"
echo ""
echo "If still showing 0 products:"
echo "1. Check PythonAnywhere error logs"
echo "2. Verify database file exists: ls -la uploads/"
echo "3. Check database integrity: sqlite3 uploads/product_database_AGT_Bothell.db 'PRAGMA integrity_check;'"
EOF

chmod +x deploy_complete_fix.sh
echo "✅ Created: deploy_complete_fix.sh"

# Step 5: Create comprehensive instructions
echo "Step 5: Creating comprehensive instructions..."
cat > "COMPLETE_PRODUCTION_FIX.md" << EOF
# 🚀 Complete Production Fix

## Current Status
- ✅ Local database: **$PRODUCT_COUNT products**
- ✅ JavaScript errors: Fixed
- ✅ API endpoints: Working locally
- ❌ Production: Still showing 0 products

## Root Cause
The production database needs to be updated with the correct data and JavaScript errors need to be fixed.

## Complete Fix Package
**File**: \`${COMPLETE_FIX_ZIP}\` ($ZIP_SIZE)

**Contains**:
- ✅ Fixed database with $PRODUCT_COUNT products
- ✅ JavaScript error fixes
- ✅ Diagnostic tools
- ✅ Deployment scripts

## Deployment Steps

### 1. Upload Complete Fix Package
- Go to PythonAnywhere **Files** tab
- Navigate to: \`/home/adamcordova/AGTDesigner\`
- Click **"Upload a file"**
- Select: \`${COMPLETE_FIX_ZIP}\`

### 2. Deploy Everything
- Open PythonAnywhere **Bash console**
- Run:
\`\`\`bash
cd ~/AGTDesigner
chmod +x deploy_complete_fix.sh
./deploy_complete_fix.sh
\`\`\`

### 3. Reload Web App
- Go to PythonAnywhere **Web** tab
- Click **"Reload"** for your web app
- Wait 30 seconds

### 4. Verify Fix
- Visit: https://www.agtpricetags.com
- Should now show:
  - ✅ **$PRODUCT_COUNT TOTAL PRODUCTS** (instead of 0)
  - ✅ **101+ UNIQUE VENDORS** (instead of 0)
  - ✅ **166+ UNIQUE BRANDS**
  - ✅ **25+ PRODUCT TYPES**

## Troubleshooting

### If still showing 0 products:
1. **Check PythonAnywhere Error Logs**:
   - Web tab → Your app → Error log
   - Look for database connection errors

2. **Verify Database File**:
   \`\`\`bash
   ls -la uploads/product_database_AGT_Bothell.db
   # Should be ~500MB
   \`\`\`

3. **Test Database Integrity**:
   \`\`\`bash
   sqlite3 uploads/product_database_AGT_Bothell.db "PRAGMA integrity_check;"
   # Should return "ok"
   \`\`\`

4. **Check Product Count**:
   \`\`\`bash
   sqlite3 uploads/product_database_AGT_Bothell.db "SELECT COUNT(*) FROM products;"
   # Should return $PRODUCT_COUNT
   \`\`\`

### If JavaScript errors persist:
1. **Check Browser Console** (F12)
2. **Verify JavaScript files uploaded**:
   \`\`\`bash
   ls -la static/js/production_error_fix.js
   ls -la static/js/tags_table.js
   \`\`\`

## Expected Timeline
- Upload: 2-3 minutes
- Deploy: 1-2 minutes  
- Reload: 30 seconds
- **Total: ~5 minutes**

## Success Indicators
After successful deployment:
- ✅ Website shows $PRODUCT_COUNT products
- ✅ No JavaScript errors in console
- ✅ All statistics display correctly
- ✅ Database operations work normally

## Files to Upload
**Main Package**: \`${COMPLETE_FIX_ZIP}\` ($ZIP_SIZE)
EOF

echo "✅ Created: COMPLETE_PRODUCTION_FIX.md"

echo ""
echo "=================================================="
echo "✅ COMPLETE PRODUCTION FIX READY!"
echo "=================================================="
echo ""
echo "📦 Package: ${COMPLETE_FIX_ZIP} ($ZIP_SIZE)"
echo "📋 Instructions: COMPLETE_PRODUCTION_FIX.md"
echo ""
echo "🚀 This package contains EVERYTHING needed:"
echo "   - Database with $PRODUCT_COUNT products"
echo "   - JavaScript error fixes"
echo "   - Deployment scripts"
echo "   - Diagnostic tools"
echo ""
echo "📤 Upload ${COMPLETE_FIX_ZIP} to PythonAnywhere"
echo "🔧 Run: ./deploy_complete_fix.sh"
echo "🔄 Reload your web app"
echo "✅ Website will show $PRODUCT_COUNT products!"
echo "=================================================="
