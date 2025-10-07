#!/bin/bash

# PythonAnywhere Database Quick Fix
# =================================
# Run this in your PythonAnywhere Bash console

echo "🚀 PythonAnywhere Database Quick Fix"
echo "===================================="

# Navigate to your project directory
cd ~/AGTDesigner

echo "📁 Current directory: $(pwd)"

# Create uploads directory if it doesn't exist
mkdir -p uploads
echo "✅ Uploads directory ready"

# Set proper permissions
chmod 755 uploads
echo "✅ Permissions set"

# Run the PythonAnywhere database troubleshooter
echo "🔧 Running database diagnostics..."
python3 pythonanywhere_database_troubleshooter.py

echo ""
echo "🎉 Database fix complete!"
echo ""
echo "📋 If you still have issues:"
echo "1. Check the error log in your Web tab"
echo "2. Try reloading your web app"
echo "3. Upload a small Excel file to test"
echo ""
echo "🔗 Your app should be available at:"
echo "https://$(whoami).pythonanywhere.com"
