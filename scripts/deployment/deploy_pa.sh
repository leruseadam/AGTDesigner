#!/bin/bash
# PythonAnywhere Deployment Script - NO STASH VERSION
# This script forces a clean pull without needing to stash

echo "🚀 Deploying to PythonAnywhere..."

# Try common PythonAnywhere directories
if [ -d "/home/adamcordova/AGTDesigner" ]; then
    cd /home/adamcordova/AGTDesigner || exit 1
elif [ -d "~/AGTDesigner" ]; then
    cd ~/AGTDesigner || exit 1
elif [ -d "." ]; then
    echo "Using current directory: $(pwd)"
else
    echo "Error: Could not find project directory"
    exit 1
fi

# Fetch latest changes
echo "Fetching latest changes..."
git fetch origin

# Hard reset to remote (discards local changes)
echo "Resetting to latest code..."
git reset --hard origin/main

# Clean up any untracked files
echo "Cleaning untracked files..."
git clean -fd

echo "✅ Deployment complete!"
echo ""
echo "Next steps:"
echo "1. Go to PythonAnywhere Web tab"
echo "2. Click 'Reload www.agtpricetags.com'"
