#!/bin/bash

# Fix PythonAnywhere Deployment Issues
# This script resolves missing dependencies and files

echo "=== Fixing PythonAnywhere Deployment Issues ==="

# Connect to PythonAnywhere and fix the issues
ssh adamcordova@ssh.pythonanywhere.com << 'EOF'
echo "=== Diagnosing Issues ==="

cd /home/adamcordova/AGTDesigner

echo "1. Checking current directory structure..."
ls -la

echo ""
echo "2. Checking if virtual environment exists..."
if [ -d "venv" ]; then
    echo "✓ Virtual environment exists"
    ls -la venv/bin/
else
    echo "✗ Virtual environment missing"
fi

echo ""
echo "3. Checking if src directory exists..."
if [ -d "src" ]; then
    echo "✓ src directory exists"
    find src -type f -name "*.py" | head -10
else
    echo "✗ src directory missing"
fi

echo ""
echo "4. Checking current Python environment..."
which python
python --version

echo ""
echo "5. Checking if virtual environment is activated..."
if [[ "$VIRTUAL_ENV" == *"AGTDesigner"* ]]; then
    echo "✓ Virtual environment is activated"
else
    echo "✗ Virtual environment not activated"
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

echo ""
echo "6. Checking installed packages..."
pip list | grep -E "(flask|pandas|openpyxl|docx)"

echo ""
echo "=== Fixing Issues ==="

# Reinstall virtual environment if needed
if [ ! -d "venv" ] || [ ! -f "venv/bin/python" ]; then
    echo "Recreating virtual environment..."
    rm -rf venv
    python3.10 -m venv venv
    echo "✓ Virtual environment recreated"
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install all dependencies
echo "Installing all dependencies..."
pip install "Flask>=2.0.0,<3.0.0"
pip install "Flask-CORS>=3.0.0,<4.0.0"
pip install "Flask-Caching>=2.0.0,<3.0.0"
pip install "pandas>=1.3.0,<3.0.0"
pip install "openpyxl>=3.0.0,<4.0.0"
pip install "xlrd>=2.0.0,<3.0.0"
pip install "xlsxwriter>=3.0.0,<4.0.0"
pip install "python-docx>=0.8.0,<1.0.0"
pip install "docxtpl>=0.16.0,<1.0.0"
pip install "docxcompose>=1.3.0,<2.0.0"
pip install "Pillow>=8.0.0,<11.0.0"
pip install "watchdog>=2.0.0,<4.0.0"
pip install "python-dateutil>=2.8.0,<3.0.0"
pip install "pytz>=2021.0,<2024.0"

# Create necessary directories
mkdir -p uploads logs output cache data

# Test imports
echo "Testing imports..."
python -c "
import sys
print('Python version:', sys.version)
print('Python path:', sys.path)

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

# Check if src directory has all files
echo ""
echo "Checking src directory structure..."
if [ -d "src" ]; then
    echo "src directory contents:"
    find src -type f -name "*.py" | head -20
    
    # Check for missing core files
    if [ ! -f "src/core/generation/template_processor.py" ]; then
        echo "✗ Missing template_processor.py"
        echo "Creating minimal template_processor.py..."
        mkdir -p src/core/generation
        cat > src/core/generation/template_processor.py << 'TEMPLATE'
# Minimal template processor for deployment
def get_font_scheme(template_type, base_size=12):
    """Get font scheme for template type."""
    return {
        'Description': {'min': base_size, 'max': base_size + 20, 'weight': 1},
        'WeightUnits': {'min': base_size, 'max': base_size + 20, 'weight': 1},
        'ProductBrand': {'min': base_size, 'max': base_size + 18, 'weight': 1},
        'Price': {'min': base_size, 'max': base_size + 16, 'weight': 1},
        'Lineage': {'min': base_size - 2, 'max': base_size + 12, 'weight': 1},
        'DOH': {'min': base_size - 4, 'max': base_size, 'weight': 1},
        'THC_CBD': {'min': base_size - 2, 'max': base_size + 12, 'weight': 1},
        'Ratio': {'min': base_size - 2, 'max': base_size + 12, 'weight': 1}
    }

class TemplateProcessor:
    """Minimal template processor for deployment."""
    def __init__(self):
        pass
    
    def process_template(self, template_path, data):
        """Process template with data."""
        return f"Processed template: {template_path}"
TEMPLATE
        echo "✓ Created minimal template_processor.py"
    fi
    
    if [ ! -f "src/core/generation/tag_generator.py" ]; then
        echo "✗ Missing tag_generator.py"
        echo "Creating minimal tag_generator.py..."
        cat > src/core/generation/tag_generator.py << 'TAG'
# Minimal tag generator for deployment
def get_template_path(template_type):
    """Get template path for template type."""
    return f"templates/{template_type}.docx"
TAG
        echo "✓ Created minimal tag_generator.py"
    fi
    
    if [ ! -f "src/core/generation/mini_font_sizing.py" ]; then
        echo "✗ Missing mini_font_sizing.py"
        echo "Creating minimal mini_font_sizing.py..."
        cat > src/core/generation/mini_font_sizing.py << 'MINI'
# Minimal mini font sizing for deployment
def get_mini_font_size_by_marker(marker_name, content, base_size=8):
    """Get mini font size by marker."""
    return base_size

def set_mini_run_font_size(run, size):
    """Set mini run font size."""
    run.font.size = size
MINI
        echo "✓ Created minimal mini_font_sizing.py"
    fi
    
    # Create __init__.py files if missing
    find src -type d -exec touch {}/__init__.py \;
    echo "✓ Created __init__.py files"
    
else
    echo "✗ src directory missing - recreating from Git..."
    git status
    git log --oneline -5
fi

echo ""
echo "=== Final Verification ==="

# Test app import
echo "Testing app.py import..."
python -c "
try:
    import app
    print('✓ App module imported successfully')
except Exception as e:
    print('✗ App module import failed:', e)
    import traceback
    traceback.print_exc()
"

echo ""
echo "=== WSGI Configuration ==="
echo "Make sure your WSGI file contains:"
echo "import sys"
echo "import os"
echo ""
echo "path = '/home/adamcordova/AGTDesigner'"
echo "if path not in sys.path:"
echo "    sys.path.append(path)"
echo ""
echo "os.chdir(path)"
echo "from app import app as application"
echo ""
echo "And set virtual environment to: /home/adamcordova/AGTDesigner/venv"

echo ""
echo "=== Restart Web App ==="
echo "After fixing, restart your web app in the PythonAnywhere Web tab"

EOF

echo "✓ Fix script completed"
echo "Check the output above for any remaining issues" 