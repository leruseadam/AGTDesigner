#!/bin/bash

# PythonAnywhere Quick Fix - Show Full Database
# =============================================
# Run this in your PythonAnywhere Bash console

echo "🚀 PythonAnywhere Database Quick Fix"
echo "===================================="

# Navigate to your project directory
cd ~/AGTDesigner

echo "📁 Current directory: $(pwd)"

# Run the database fix
echo "🔧 Fixing database display..."
python3 fix_pythonanywhere_full_database.py

echo ""
echo "🎉 Database fix complete!"
echo ""
echo "📋 Next steps:"
echo "1. Go to your PythonAnywhere Web tab"
echo "2. Click 'Reload' to restart your web app"
echo "3. Visit your site - should now show 5,000+ products"
echo ""
echo "🔗 Your app: https://$(whoami).pythonanywhere.com"
echo ""
echo "⚠️  If still showing 5 products:"
echo "   python3 disable_default_loading.py"
echo "   Then reload your web app again"
