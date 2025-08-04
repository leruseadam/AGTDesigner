#!/bin/bash

# Check PythonAnywhere Deployment Status
# This script diagnoses the current state of your deployment

echo "=== Checking PythonAnywhere Deployment Status ==="

# Connect to PythonAnywhere and check status
ssh adamcordova@ssh.pythonanywhere.com << 'EOF'
echo "=== PythonAnywhere Status Check ==="

cd /home/adamcordova/AGTDesigner

echo "1. Current directory and files:"
pwd
ls -la

echo ""
echo "2. Virtual environment status:"
if [ -d "venv" ]; then
    echo "✓ Virtual environment exists"
    ls -la venv/bin/python*
    echo "Python version in venv:"
    venv/bin/python --version
else
    echo "✗ Virtual environment missing"
fi

echo ""
echo "3. Source files check:"
if [ -d "src" ]; then
    echo "✓ src directory exists"
    echo "src structure:"
    find src -type f -name "*.py" | head -15
    
    echo ""
    echo "Checking specific files:"
    [ -f "src/core/generation/template_processor.py" ] && echo "✓ template_processor.py exists" || echo "✗ template_processor.py missing"
    [ -f "src/core/generation/tag_generator.py" ] && echo "✓ tag_generator.py exists" || echo "✗ tag_generator.py missing"
    [ -f "src/core/generation/mini_font_sizing.py" ] && echo "✓ mini_font_sizing.py exists" || echo "✗ mini_font_sizing.py missing"
    [ -f "src/__init__.py" ] && echo "✓ src/__init__.py exists" || echo "✗ src/__init__.py missing"
    [ -f "src/core/__init__.py" ] && echo "✓ src/core/__init__.py exists" || echo "✗ src/core/__init__.py missing"
    [ -f "src/core/generation/__init__.py" ] && echo "✓ src/core/generation/__init__.py exists" || echo "✗ src/core/generation/__init__.py missing"
else
    echo "✗ src directory missing"
fi

echo ""
echo "4. Python path and imports test:"
source venv/bin/activate
python -c "
import sys
print('Python version:', sys.version)
print('Python executable:', sys.executable)
print('Python path:')
for path in sys.path:
    print(f'  {path}')

print('\\nTesting imports:')
try:
    import pandas
    print('✓ pandas imported successfully')
except ImportError as e:
    print('✗ pandas import failed:', e)

try:
    import flask
    print('✓ flask imported successfully')
except ImportError as e:
    print('✗ flask import failed:', e)

try:
    import openpyxl
    print('✓ openpyxl imported successfully')
except ImportError as e:
    print('✗ openpyxl import failed:', e)
"

echo ""
echo "5. Testing app.py import:"
python -c "
import sys
sys.path.insert(0, '/home/adamcordova/AGTDesigner')

try:
    import app
    print('✓ app.py imported successfully')
except Exception as e:
    print('✗ app.py import failed:', e)
    import traceback
    traceback.print_exc()
"

echo ""
echo "6. Git status:"
git status
git log --oneline -3

echo ""
echo "7. WSGI file check:"
if [ -f "/var/www/adamcordova_pythonanywhere_com_wsgi.py" ]; then
    echo "✓ WSGI file exists"
    echo "WSGI file content:"
    cat /var/www/adamcordova_pythonanywhere_com_wsgi.py
else
    echo "✗ WSGI file missing"
fi

echo ""
echo "=== Summary ==="
echo "Virtual environment: /home/adamcordova/AGTDesigner/venv"
echo "Working directory: /home/adamcordova/AGTDesigner"
echo "Python version: $(venv/bin/python --version)"
echo "Dependencies installed: $(venv/bin/pip list | grep -E '(flask|pandas|openpyxl)' | wc -l) packages"

EOF

echo "✓ Status check completed"
echo "Check the output above to identify the specific issues" 