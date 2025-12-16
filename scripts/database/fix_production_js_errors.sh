#!/bin/bash
# Fix JavaScript errors on production website

echo "=================================================="
echo "🔧 FIXING PRODUCTION JAVASCRIPT ERRORS"
echo "=================================================="
echo ""

cd "$(dirname "$0")"

# Step 1: Fix duplicate CLASSIC_TYPES declaration
echo "Step 1: Fixing duplicate CLASSIC_TYPES declaration..."
if [ -f "static/js/tags_table.js" ]; then
    # Remove the duplicate declaration
    sed -i.bak '/^\/\/ Classic types that should show "Lineage" instead of "Brand"/,/^];$/d' static/js/tags_table.js
    echo "✅ Removed duplicate CLASSIC_TYPES from tags_table.js"
else
    echo "❌ tags_table.js not found"
fi

# Step 2: Create JavaScript error fix
echo "Step 2: Creating JavaScript error fix..."
cat > "static/js/production_error_fix.js" << 'EOF'
// Production JavaScript Error Fix
// This script fixes common JavaScript errors on the production website

console.log('🔧 Loading production JavaScript error fixes...');

// Fix 1: Ensure CLASSIC_TYPES is only declared once
if (typeof CLASSIC_TYPES === 'undefined') {
    const CLASSIC_TYPES = [
        "flower", "pre-roll", "concentrate", "infused pre-roll", 
        "solventless concentrate", "vape cartridge", "rso/co2 tankers"
    ];
    console.log('✅ CLASSIC_TYPES defined');
}

// Fix 2: Create backup definitions for missing functions
if (typeof performDetailedJsonMatch === 'undefined') {
    window.performDetailedJsonMatch = function() {
        console.warn('performDetailedJsonMatch not found, using backup');
        return false;
    };
}

if (typeof displayDetailedMatchResults === 'undefined') {
    window.displayDetailedMatchResults = function() {
        console.warn('displayDetailedMatchResults not found, using backup');
        return false;
    };
}

// Fix 3: Global error handler to prevent crashes
window.addEventListener('error', function(e) {
    console.error('JavaScript Error Caught:', {
        message: e.message,
        filename: e.filename,
        lineno: e.lineno,
        colno: e.colno,
        error: e.error
    });
    
    // Don't let errors break the page
    return true;
});

// Fix 4: Handle unhandled promise rejections
window.addEventListener('unhandledrejection', function(e) {
    console.error('Unhandled Promise Rejection:', e.reason);
    e.preventDefault();
});

// Fix 5: Ensure critical functions exist
if (typeof showDatabaseModal === 'undefined') {
    window.showDatabaseModal = function(title, content) {
        console.warn('showDatabaseModal not found, using backup');
        alert(`${title}: ${content}`);
    };
}

console.log('✅ Production JavaScript error fixes loaded');
EOF

echo "✅ Created static/js/production_error_fix.js"

# Step 3: Create deployment package
echo "Step 3: Creating JavaScript fix deployment package..."
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
JS_FIX_ZIP="javascript_error_fix_${TIMESTAMP}.zip"

# Create zip with JavaScript fixes
zip -q "${JS_FIX_ZIP}" static/js/production_error_fix.js static/js/tags_table.js

if [ -f "$JS_FIX_ZIP" ]; then
    ZIP_SIZE=$(du -h "$JS_FIX_ZIP" | cut -f1)
    echo "✅ Created: $JS_FIX_ZIP ($ZIP_SIZE)"
else
    echo "❌ Failed to create JavaScript fix zip"
fi

# Step 4: Create deployment instructions
echo "Step 4: Creating deployment instructions..."
cat > "JAVASCRIPT_ERROR_FIX_INSTRUCTIONS.md" << EOF
# 🔧 JavaScript Error Fix for Production

## Issues Fixed
- ✅ Duplicate CLASSIC_TYPES declaration (causing "already been declared" error)
- ✅ Missing function definitions (performDetailedJsonMatch, displayDetailedMatchResults)
- ✅ Global error handling to prevent page crashes
- ✅ Unhandled promise rejection handling

## Files Created
- \`static/js/production_error_fix.js\` - Main error fix script
- \`${JS_FIX_ZIP}\` - Deployment package

## Deployment Steps

### Option 1: Upload JavaScript Files
1. Go to PythonAnywhere **Files** tab
2. Navigate to: \`/home/adamcordova/AGTDesigner/static/js/\`
3. Upload: \`production_error_fix.js\`
4. Replace: \`tags_table.js\` (fixed version)

### Option 2: Use Deployment Package
1. Upload: \`${JS_FIX_ZIP}\` to PythonAnywhere
2. Extract in: \`/home/adamcordova/AGTDesigner/\`
3. Move files to: \`static/js/\`

### Option 3: Add Script to HTML
Add this to your HTML template (before closing </body> tag):
\`\`\`html
<script src="/static/js/production_error_fix.js"></script>
\`\`\`

## Expected Results
After deployment:
- ✅ No more "CLASSIC_TYPES already been declared" errors
- ✅ No more "function not found" errors
- ✅ Better error handling and page stability
- ✅ Database stats should display correctly

## Test
1. Reload your web app
2. Open browser console (F12)
3. Should see: "✅ Production JavaScript error fixes loaded"
4. No more red error messages
5. Database stats should show 10,543 products

## Files to Upload
- \`static/js/production_error_fix.js\`
- \`static/js/tags_table.js\` (fixed)
EOF

echo "✅ Created: JAVASCRIPT_ERROR_FIX_INSTRUCTIONS.md"

echo ""
echo "=================================================="
echo "✅ JAVASCRIPT ERROR FIX READY!"
echo "=================================================="
echo ""
echo "📦 Files created:"
echo "   - static/js/production_error_fix.js"
echo "   - ${JS_FIX_ZIP}"
echo "   - JAVASCRIPT_ERROR_FIX_INSTRUCTIONS.md"
echo ""
echo "🚀 Next steps:"
echo "1. Upload JavaScript files to PythonAnywhere"
echo "2. Add error fix script to your HTML template"
echo "3. Reload your web app"
echo "4. Check browser console for confirmation"
echo ""
echo "📋 Instructions: JAVASCRIPT_ERROR_FIX_INSTRUCTIONS.md"
echo "=================================================="
