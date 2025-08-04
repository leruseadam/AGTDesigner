#!/bin/bash

echo "🚀 PYTHONANYWHERE CODE UPDATE SCRIPT"
echo "===================================="
echo ""

echo "📍 Current directory: $(pwd)"
echo "📁 Checking if project directory exists..."

if [ ! -d "AGTDesigner" ]; then
    echo "❌ Project directory not found!"
    echo "   Please make sure you're in the correct directory"
    echo "   Expected: AGTDesigner directory"
    exit 1
fi

cd AGTDesigner
echo "📂 Changed to project directory: $(pwd)"
echo ""

echo "🔄 Fetching latest changes from remote..."
git fetch origin

echo "📊 Current status:"
git status --short

echo ""
echo "🔄 Pulling latest code from main branch..."
git pull origin main

echo ""
echo "📊 Status after pull:"
git status --short

echo ""
echo "🏷️  Latest commit:"
git log --oneline -1

echo ""
echo "✅ Code update completed!"
echo ""
echo "🔄 Reloading PythonAnywhere web app..."
touch /var/www/www_agtpricetags_com_wsgi.py

echo "✅ Web app reloaded!"
echo ""
echo "🌐 Your app should now be updated at:"
echo "   https://www.agtpricetags.com"
echo ""
echo "📝 If you encounter any issues:"
echo "   1. Check the error logs in PythonAnywhere"
echo "   2. Verify all dependencies are installed"
echo "   3. Check the WSGI configuration"
echo ""
echo "🎉 Deployment complete!" 