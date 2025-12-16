#!/bin/bash
# Fix API 500 errors by deploying the updated app.py

echo "🔧 FIXING API 500 ERRORS"
echo "========================="

echo "📝 Changes made:"
echo "  ✅ Added pandas import to /api/database-vendor-stats"
echo "  ✅ Added pandas import to /api/database-analytics"
echo ""

# Create a zip file with the fixed app.py
ZIP_FILE="api_fixes_$(date +%Y%m%d_%H%M%S).zip"

echo "📦 Creating deployment package..."
zip -r "$ZIP_FILE" app.py

echo "✅ Created: $ZIP_FILE"
echo ""

echo "📋 DEPLOYMENT INSTRUCTIONS:"
echo "1. Upload $ZIP_FILE to PythonAnywhere"
echo "2. Extract it in your home directory:"
echo "   unzip $ZIP_FILE"
echo "3. Copy the fixed app.py to your web app:"
echo "   cp app.py /home/yourusername/mysite/"
echo "4. Reload your web app in PythonAnywhere Web tab"
echo "5. Wait 30-60 seconds"
echo "6. Test the endpoints:"
echo "   - https://www.agtpricetags.com/api/database-analytics"
echo "   - https://www.agtpricetags.com/api/database-vendor-stats"
echo ""

echo "🧪 Or run the test script locally:"
echo "python3 test_api_endpoints.py"
echo ""

echo "=================================="
echo "🎯 The 500 errors should now be fixed!"
echo "=================================="
