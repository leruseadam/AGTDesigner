#!/bin/bash

# PythonAnywhere Corrupted Database Fix
# ====================================
# Run this in your PythonAnywhere Bash console

echo "🚀 PythonAnywhere Corrupted Database Fix"
echo "========================================"

# Navigate to your project directory
cd ~/AGTDesigner

echo "📁 Current directory: $(pwd)"

# Run the corrupted database fix
echo "🔧 Fixing corrupted database..."
python3 fix_corrupted_database.py

echo ""
echo "🎉 Database corruption fix complete!"
echo ""
echo "📋 Next steps:"
echo "1. Go to your PythonAnywhere Web tab"
echo "2. Click 'Reload' to restart your web app"
echo "3. Visit your site to verify it's working"
echo ""
echo "🔗 Your app: https://$(whoami).pythonanywhere.com"
echo ""
echo "💡 If you need the full 5,000+ products:"
echo "   1. Upload product_database_compressed.sql.gz"
echo "   2. Run: python3 populate_pythonanywhere_database.py"
echo "   3. Reload your web app"
