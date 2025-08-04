#!/bin/bash

# PythonAnywhere Python 3.13 Fix Script
# Run this in your PythonAnywhere bash console

echo "=== Fixing Python 3.13 Compatibility Issues ==="

# Step 1: Navigate to project
cd ~/AGTDesigner

# Step 2: Update core packages
echo "Updating pip, setuptools, and wheel..."
pip install --upgrade pip setuptools wheel

# Step 3: Try Python 3.10 requirements first
echo "Installing Python 3.10 compatible requirements..."
if pip install -r requirements_pythonanywhere_py310.txt; then
    echo "✅ Python 3.10 requirements installed successfully"
else
    echo "⚠️  Python 3.10 requirements failed, trying minimal requirements..."
    if pip install -r requirements_pythonanywhere_py313_minimal.txt; then
        echo "✅ Minimal requirements installed successfully"
    else
        echo "❌ Both failed. Consider switching to Python 3.10 in Web tab."
        exit 1
    fi
fi

# Step 4: Pull latest changes
echo "Pulling latest changes from GitHub..."
git pull origin main

# Step 5: Clear cache
echo "Clearing cache..."
rm -rf __pycache__
rm -rf src/__pycache__
rm -rf src/core/__pycache__
rm -rf src/core/data/__pycache__
rm -rf src/core/generation/__pycache__

# Step 6: Set permissions
echo "Setting permissions..."
chmod -R 755 .
chmod -R 755 uploads output cache logs static

echo ""
echo "=== Fix Complete ==="
echo "Next steps:"
echo "1. Go to PythonAnywhere Web tab"
echo "2. Click 'Reload' for your web app"
echo "3. If still having issues, consider switching to Python 3.10"
echo ""
echo "If you need to switch to Python 3.10:"
echo "1. Go to Web tab"
echo "2. Click 'Edit' next to your web app"
echo "3. Change Python version to 3.10"
echo "4. Save and reload" 