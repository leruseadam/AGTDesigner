#!/bin/bash

# PythonAnywhere Installation Script - Fixed for Pillow Issue
# This script handles the Pillow build issue by using pre-built wheels

echo "=== PythonAnywhere Package Installation (Pillow Fix) ==="

# Check virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "❌ ERROR: Not in virtual environment!"
    echo "Please run: source ~/.virtualenvs/myflaskapp-env/bin/activate"
    exit 1
fi

echo "✅ Virtual environment: $VIRTUAL_ENV"

# Clear pip cache to avoid cached broken packages
echo "Clearing pip cache..."
pip cache purge

# Upgrade pip and setuptools
echo "Upgrading pip, setuptools, and wheel..."
pip install --upgrade pip setuptools wheel

# Install packages in order of dependency
echo ""
echo "Installing packages in dependency order..."

# Install core dependencies first
echo "1. Installing core Flask dependencies..."
pip install --no-cache-dir Flask==2.3.3 Werkzeug==2.3.7 Jinja2==3.1.2 itsdangerous==2.1.2 click==8.1.7 MarkupSafe==2.1.3

# Install numpy first (required by pandas)
echo "2. Installing numpy..."
pip install --no-cache-dir numpy==1.24.3

# Install pandas
echo "3. Installing pandas..."
pip install --no-cache-dir pandas==2.0.3

# Install other data processing libraries
echo "4. Installing other data processing libraries..."
pip install --no-cache-dir python-dateutil==2.8.2
pip install --no-cache-dir python-docx==0.8.11
pip install --no-cache-dir openpyxl==3.1.2

# Install Pillow with specific flags to avoid build issues
echo "5. Installing Pillow (with build fix)..."
pip install --no-cache-dir --only-binary=all Pillow==9.5.0

# Install remaining packages
echo "6. Installing remaining packages..."
pip install --no-cache-dir docxtpl==0.16.7
pip install --no-cache-dir watchdog==3.0.0

# Try to install docxcompose (may fail, but not critical)
echo "7. Installing docxcompose (optional, may fail)..."
pip install --no-cache-dir docxcompose==1.4.0 || echo "⚠️  docxcompose failed - continuing without it"

echo ""
echo "=== Installation Complete ==="
echo ""
echo "Verifying installations..."
python -c "import flask; print('✅ Flask:', flask.__version__)" 2>/dev/null || echo "❌ Flask failed"
python -c "import numpy; print('✅ numpy:', numpy.__version__)" 2>/dev/null || echo "❌ numpy failed"
python -c "import pandas; print('✅ pandas:', pandas.__version__)" 2>/dev/null || echo "❌ pandas failed"
python -c "import PIL; print('✅ Pillow:', PIL.__version__)" 2>/dev/null || echo "❌ Pillow failed"
python -c "import docx; print('✅ python-docx available')" 2>/dev/null || echo "❌ python-docx failed"
python -c "import openpyxl; print('✅ openpyxl available')" 2>/dev/null || echo "❌ openpyxl failed"

echo ""
echo "=== Next Steps ==="
echo "1. Restart your web app in PythonAnywhere Web tab"
echo "2. Check the error log for any remaining import issues"
echo "3. If you still get import errors, check your WSGI configuration"
