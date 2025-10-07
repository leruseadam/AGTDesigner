#!/bin/bash

# PythonAnywhere Emergency Database Fix
# ====================================
# Run this in your PythonAnywhere Bash console

echo "🚨 PythonAnywhere Emergency Database Fix"
echo "======================================="

# Navigate to your project directory
cd ~/AGTDesigner

echo "📁 Current directory: $(pwd)"

# Run the emergency database fix
echo "🔧 Creating emergency working database..."
python3 emergency_database_fix.py

echo ""
echo "🎉 Emergency database fix complete!"
echo ""
echo "📋 Next steps:"
echo "1. Go to your PythonAnywhere Web tab"
echo "2. Click 'Reload' to restart your web app"
echo "3. Visit your site - should show 10 products"
echo ""
echo "🔗 Your app: https://$(whoami).pythonanywhere.com"
echo ""
echo "💡 To get your full 8,000+ product database:"
echo "   1. Download a clean database from your local machine"
echo "   2. Upload it to PythonAnywhere Files tab"
echo "   3. Rename it to 'product_database_AGT_Bothell.db'"
echo "   4. Run: python3 rebuild_database_clean.py"
echo "   5. Reload your web app"
