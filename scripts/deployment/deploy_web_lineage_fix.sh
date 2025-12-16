#!/bin/bash
# One-command deployment script for lineage fix on PythonAnywhere
# Run this ON PYTHONANYWHERE after SSH-ing in

echo "🚀 DEPLOYING LINEAGE COLOR FIX TO WEB VERSION"
echo "=============================================="

# Check we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: Not in AGTDesigner directory"
    echo "Please run: cd ~/AGTDesigner"
    exit 1
fi

# Pull latest code
echo ""
echo "📥 Step 1: Pulling latest code from GitHub..."
git pull origin main

if [ $? -ne 0 ]; then
    echo "❌ Git pull failed!"
    exit 1
fi

echo "✅ Code updated successfully"

# Verify the fix
echo ""
echo "🧪 Step 2: Verifying lineage fix..."
python3 verify_lineage_fix.py

if [ $? -ne 0 ]; then
    echo "⚠️  Verification failed, but continuing..."
else
    echo "✅ Verification passed"
fi

# Check database
echo ""
echo "📊 Step 3: Checking database..."
DB_COUNT=$(python3 -c "import sqlite3; conn = sqlite3.connect('uploads/product_database.db'); print(conn.execute('SELECT COUNT(*) FROM products').fetchone()[0]); conn.close()" 2>/dev/null)

if [ -n "$DB_COUNT" ]; then
    echo "✅ Database found with $DB_COUNT products"
else
    echo "⚠️  Database check failed"
fi

# Test lineage functionality
echo ""
echo "🧪 Step 4: Testing lineage functionality..."
python3 test_lineage_end_to_end.py

if [ $? -eq 0 ]; then
    echo "✅ Lineage tests passed"
else
    echo "⚠️  Lineage tests failed"
fi

echo ""
echo "=============================================="
echo "✅ DEPLOYMENT COMPLETE!"
echo ""
echo "📋 Next steps:"
echo "1. Go to: https://www.pythonanywhere.com/user/adamcordova/webapps/"
echo "2. Click 'Reload www.agtpricetags.com'"
echo "3. Wait 30 seconds"
echo "4. Clear browser cache (Ctrl+Shift+R or Cmd+Shift+R)"
echo "5. Test lineage changes at: https://www.agtpricetags.com"
echo ""
echo "🔍 Monitor logs:"
echo "   tail -f /var/log/www.agtpricetags.com.error.log | grep LINEAGE"
echo ""
echo "🎨 Expected colors:"
echo "   SATIVA   → 🔴 Red (#ED4123)"
echo "   INDICA   → 🟣 Purple (#9900FF)"
echo "   HYBRID   → 🟢 Green (#009900)"
echo "   CBD      → 🟡 Yellow (#F1C232)"
echo "   MIXED    → 🔵 Blue (#0021F5)"
echo "=============================================="

