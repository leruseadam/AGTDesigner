#!/bin/bash

# PythonAnywhere SQL Corruption Fix
# ================================
# Run this in your PythonAnywhere Bash console

echo "🚀 PythonAnywhere SQL Corruption Fix"
echo "===================================="

# Navigate to your project directory
cd ~/AGTDesigner

echo "📁 Current directory: $(pwd)"

# Run the clean database rebuild
echo "🔧 Rebuilding database from clean source..."
python3 rebuild_database_clean.py

echo ""
echo "🎉 SQL corruption fix complete!"
echo ""
echo "📋 Next steps:"
echo "1. Go to your PythonAnywhere Web tab"
echo "2. Click 'Reload' to restart your web app"
echo "3. Visit your site to verify it's working"
echo ""
echo "🔗 Your app: https://$(whoami).pythonanywhere.com"
echo ""
echo "💡 This fix rebuilds the database cleanly from AGT Bothell source"
echo "   instead of using the corrupted SQL dump"
