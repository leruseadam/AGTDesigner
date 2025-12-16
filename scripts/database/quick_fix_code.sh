#!/bin/bash
# Quick fix to update code on PythonAnywhere

echo "🚀 Updating code to remove \$25 defaults..."

cd ~/AGTDesigner

echo "📥 Fetching latest changes..."
git fetch origin

echo "🔄 Resetting to latest code..."
git reset --hard origin/main

echo "🧹 Cleaning untracked files..."
git clean -fd

echo "✅ Code updated! Now reload the web app."
echo ""
echo "Next steps:"
echo "1. Go to PythonAnywhere Web tab"
echo "2. Click 'Reload' for www.agtpricetags.com"
echo "3. Wait 15-20 seconds"
echo ""
echo "Current commit:"
git log --oneline -1
