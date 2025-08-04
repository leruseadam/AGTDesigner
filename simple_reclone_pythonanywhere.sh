#!/bin/bash

# Simple Re-clone to PythonAnywhere
# Non-interactive deployment script
# Compatible with Python 3.10

set -e

echo "=== Simple Re-clone to PythonAnywhere (Python 3.10 Compatible) ==="

# Configuration
PYTHONANYWHERE_USER="adamcordova"
REMOTE_DIR="/home/$PYTHONANYWHERE_USER/AGTDesigner"

echo "1. Creating project archive..."
tar --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' --exclude='.DS_Store' \
    --exclude='node_modules' --exclude='.venv' --exclude='venv' \
    -czf /tmp/labelMaker_simple.tar.gz .

echo "2. Uploading to PythonAnywhere..."
scp /tmp/labelMaker_simple.tar.gz "$PYTHONANYWHERE_USER@ssh.pythonanywhere.com:/tmp/"

echo "3. Deploying on PythonAnywhere..."
ssh -o BatchMode=yes "$PYTHONANYWHERE_USER@ssh.pythonanywhere.com" << 'EOF'
echo "=== Deploying Project (Python 3.10 Compatible) ==="

# Backup existing project
cd /home/adamcordova
if [ -d "AGTDesigner" ]; then
    mv AGTDesigner AGTDesigner_backup_$(date +%Y%m%d_%H%M%S)
fi

# Create fresh directory and extract
mkdir -p AGTDesigner
cd AGTDesigner
tar -xzf /tmp/labelMaker_simple.tar.gz
rm /tmp/labelMaker_simple.tar.gz

# Check available Python versions
echo "Available Python versions:"
python3.10 --version 2>/dev/null && echo "✓ Python 3.10 available" || echo "✗ Python 3.10 not available"
python3.9 --version 2>/dev/null && echo "✓ Python 3.9 available" || echo "✗ Python 3.9 not available"
python3.8 --version 2>/dev/null && echo "✓ Python 3.8 available" || echo "✗ Python 3.8 not available"
python3 --version 2>/dev/null && echo "✓ Default Python 3 available" || echo "✗ Default Python 3 not available"

# Determine which Python to use (prefer 3.10, fallback to others)
PYTHON_CMD="python3"
if command -v python3.10 &> /dev/null; then
    PYTHON_CMD="python3.10"
    echo "Using Python 3.10"
elif command -v python3.9 &> /dev/null; then
    PYTHON_CMD="python3.9"
    echo "Using Python 3.9"
elif command -v python3.8 &> /dev/null; then
    PYTHON_CMD="python3.8"
    echo "Using Python 3.8"
else
    PYTHON_CMD="python3"
    echo "Using default Python 3"
fi

echo "Selected Python: $PYTHON_CMD"
$PYTHON_CMD --version

# Create virtual environment with selected Python
echo "Creating virtual environment with $PYTHON_CMD..."
$PYTHON_CMD -m venv venv

# Install dependencies
echo "Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip

# Install core dependencies (compatible with Python 3.10)
echo "Installing Flask and core dependencies..."
pip install "Flask>=2.0.0,<3.0.0"
pip install "Flask-CORS>=3.0.0,<4.0.0"
pip install "Flask-Caching>=2.0.0,<3.0.0"

echo "Installing data processing dependencies..."
pip install "pandas>=1.3.0,<3.0.0"
pip install "openpyxl>=3.0.0,<4.0.0"
pip install "xlrd>=2.0.0,<3.0.0"
pip install "xlsxwriter>=3.0.0,<4.0.0"

echo "Installing document processing dependencies..."
pip install "python-docx>=0.8.0,<1.0.0"
pip install "docxtpl>=0.16.0,<1.0.0"
pip install "docxcompose>=1.3.0,<2.0.0"

echo "Installing image processing dependencies..."
pip install "Pillow>=8.0.0,<11.0.0"

echo "Installing additional dependencies..."
pip install "watchdog>=2.0.0,<4.0.0"
pip install "python-dateutil>=2.8.0,<3.0.0"
pip install "pytz>=2021.0,<2024.0"

# Create directories
echo "Creating necessary directories..."
mkdir -p uploads logs output cache data
chmod 755 uploads logs output cache data

# Test imports
echo "Testing imports..."
python -c "
import sys
print('Python version:', sys.version)

try:
    import flask
    print('✓ Flask imported successfully')
except ImportError as e:
    print('✗ Flask import failed:', e)

try:
    import pandas
    print('✓ Pandas imported successfully')
except ImportError as e:
    print('✗ Pandas import failed:', e)

try:
    import openpyxl
    print('✓ OpenPyXL imported successfully')
except ImportError as e:
    print('✗ OpenPyXL import failed:', e)

try:
    from docx import Document
    print('✓ Python-docx imported successfully')
except ImportError as e:
    print('✗ Python-docx import failed:', e)
"

# Restart web app
echo "Restarting web app..."
touch /var/www/adamcordova_pythonanywhere_com_wsgi.py

echo "✓ Deployment complete!"
echo "Your app will be available at: https://adamcordova.pythonanywhere.com"
echo "Python version used: $($PYTHON_CMD --version)"
EOF

# Clean up
rm -f /tmp/labelMaker_simple.tar.gz

echo "✓ Re-clone complete!"
echo "Your application should be available at: https://adamcordova.pythonanywhere.com"
echo "Python 3.10 compatible deployment completed!" 