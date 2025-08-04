#!/bin/bash

echo "🚀 PythonAnywhere WSGI Configuration Fix"
echo "========================================"

# Check if we're on PythonAnywhere
if [[ "$HOSTNAME" == *"pythonanywhere"* ]]; then
    echo "✅ Running on PythonAnywhere"
else
    echo "⚠️  This script is designed for PythonAnywhere"
    echo "   You can still run it, but results may vary"
fi

# Get current directory
CURRENT_DIR=$(pwd)
echo "📁 Current directory: $CURRENT_DIR"

# Check if we're in the right place
if [ ! -f "app.py" ]; then
    echo "❌ app.py not found in current directory"
    echo "   Please navigate to your project directory first"
    exit 1
fi

echo "✅ Found app.py - this looks like the project directory"

# Run the Python deployment script
echo ""
echo "🔧 Running WSGI configuration fix..."
python3 deploy_pythonanywhere_fix.py

echo ""
echo "📋 Manual Steps Required:"
echo "1. Go to PythonAnywhere Web tab"
echo "2. Click on your web app"
echo "3. In the 'Code' section:"
echo "   - Set 'Source code' to: $CURRENT_DIR"
echo "   - Set 'Working directory' to: $CURRENT_DIR"
echo "4. In the 'WSGI configuration file' section:"
echo "   - Click on the WSGI file link"
echo "   - Replace the content with the generated wsgi.py content"
echo "5. In the 'Virtual environment' section:"
echo "   - Set the path to your virtual environment (if you have one)"
echo "6. Click 'Reload' button"
echo ""
echo "🔗 Your app should then be available at your PythonAnywhere URL" 