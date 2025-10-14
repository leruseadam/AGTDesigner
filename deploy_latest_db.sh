#!/bin/bash
# Quick database deployment to PythonAnywhere

echo "🚀 DEPLOYING LATEST DATABASE TO PYTHONANYWHERE"
echo "=============================================="

# Find the most recent database zip
LATEST_DB=$(ls -t *database*.zip | head -1)
echo "📁 Latest database file: $LATEST_DB"

if [ -z "$LATEST_DB" ]; then
    echo "❌ No database zip files found!"
    exit 1
fi

echo "📊 File info:"
ls -lh "$LATEST_DB"

echo ""
echo "🎯 DEPLOYMENT STEPS:"
echo "==================="
echo ""
echo "1️⃣  UPLOAD TO PYTHONANYWHERE:"
echo "   • Go to https://www.pythonanywhere.com"
echo "   • Click 'Files' tab"
echo "   • Navigate to: /home/adamcordova/AGTDesigner"
echo "   • Click 'Upload a file'"
echo "   • Select: $LATEST_DB"
echo "   • Wait for upload to complete"
echo ""
echo "2️⃣  EXTRACT ON PYTHONANYWHERE:"
echo "   Open a Bash console and run:"
echo ""
echo "   cd ~/AGTDesigner"
echo "   ls -lh $LATEST_DB"
echo "   mkdir -p uploads/backups_old"
echo "   mv uploads/product_database_AGT_Bothell.db uploads/backups_old/corrupted_\$(date +%Y%m%d).db 2>/dev/null"
echo "   unzip -o $LATEST_DB"
echo "   mv product_database_AGT_Bothell.db uploads/"
echo "   sqlite3 uploads/product_database_AGT_Bothell.db \"PRAGMA integrity_check;\""
echo ""
echo "3️⃣  RELOAD WEB APP:"
echo "   • Go to 'Web' tab"
echo "   • Click 'Reload' button"
echo "   • Wait 15-20 seconds"
echo ""
echo "4️⃣  TEST:"
echo "   • Visit https://www.agtpricetags.com"
echo "   • Check that TOTAL PRODUCTS shows correct count"
echo ""

echo "✅ Ready to deploy: $LATEST_DB"
echo "📁 File size: $(ls -lh "$LATEST_DB" | awk '{print $5}')"
echo "📅 Created: $(stat -f "%Sm" "$LATEST_DB")"
