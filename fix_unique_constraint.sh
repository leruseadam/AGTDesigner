#!/bin/bash

# PythonAnywhere Database UNIQUE Constraint Fix
# ============================================
# Run this in your PythonAnywhere Bash console

echo "🚀 PythonAnywhere Database UNIQUE Constraint Fix"
echo "==============================================="

# Navigate to your project directory
cd ~/AGTDesigner

echo "📁 Current directory: $(pwd)"

# Run the fixed restoration script
echo "🔧 Running fixed database restoration..."
python3 restore_database_fixed.py

echo ""
echo "🎉 Database constraint fix complete!"
echo ""
echo "📋 Next steps:"
echo "1. Go to your PythonAnywhere Web tab"
echo "2. Click 'Reload' to restart your web app"
echo "3. Visit your site to verify it's working"
echo ""
echo "🔗 Your app: https://$(whoami).pythonanywhere.com"
echo ""
echo "💡 If you still have issues:"
echo "   python3 fix_corrupted_database.py"
echo "   Then reload your web app"
