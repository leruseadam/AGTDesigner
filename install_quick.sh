#!/bin/bash

# Quick dependency installation for PythonAnywhere
# Run this script if the main installation script fails

echo "=== Quick Dependency Installation ==="
echo "This script installs only the most essential packages"
echo ""

# Check virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "❌ No virtual environment detected!"
    echo "Please run: source ~/labelmaker-venv/bin/activate"
    exit 1
fi

echo "✅ Virtual environment: $VIRTUAL_ENV"

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install core packages one by one
echo "Installing core Flask packages..."
pip install Flask==2.3.3 || pip install Flask
pip install Werkzeug==2.3.7 || pip install Werkzeug
pip install Jinja2==3.1.2 || pip install Jinja2

echo "Installing data processing packages..."
pip install numpy==1.24.3 || pip install numpy
pip install pandas==2.0.3 || pip install pandas

echo "Installing document processing packages..."
pip install python-docx==0.8.11 || pip install python-docx
pip install openpyxl==3.1.2 || pip install openpyxl

echo "Installing image processing..."
pip install Pillow==9.5.0 || pip install Pillow

echo "Installing other dependencies..."
pip install python-dateutil==2.8.2 || pip install python-dateutil
pip install docxtpl==0.16.7 || pip install docxtpl

echo ""
echo "=== Testing imports ==="
python -c "import flask; print('✅ Flask:', flask.__version__)" || echo "❌ Flask failed"
python -c "import pandas; print('✅ Pandas:', pandas.__version__)" || echo "❌ Pandas failed"
python -c "import numpy; print('✅ NumPy:', numpy.__version__)" || echo "❌ NumPy failed"
python -c "import docx; print('✅ python-docx available')" || echo "❌ python-docx failed"
python -c "from PIL import Image; print('✅ Pillow available')" || echo "❌ Pillow failed"

echo ""
echo "=== Installation complete ==="
echo "If any packages failed, try installing them individually:"
echo "pip install package_name"
