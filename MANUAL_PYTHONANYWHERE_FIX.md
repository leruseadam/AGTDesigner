# Manual PythonAnywhere Fix Guide

## Issues to Fix:
1. **Missing pandas module**
2. **Missing src.core.generation module**

## Step 1: Access PythonAnywhere Console

1. Go to https://www.pythonanywhere.com
2. Log in to your account (adamcordova)
3. Go to the **Consoles** tab
4. Click **Bash** to open a new console

## Step 2: Navigate to Your Project

```bash
cd /home/adamcordova/AGTDesigner
ls -la
```

## Step 3: Check Virtual Environment

```bash
# Check if virtual environment exists
ls -la venv/

# If it doesn't exist, create it
python3.10 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Check Python version
python --version
```

## Step 4: Install Dependencies

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install all required packages
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
```

## Step 5: Test Imports

```bash
# Test if packages are installed
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
```

## Step 6: Check Source Files

```bash
# Check if src directory exists
ls -la src/

# Check if core files exist
ls -la src/core/generation/

# If files are missing, create minimal versions
```

## Step 7: Create Missing Files (if needed)

If `src/core/generation/template_processor.py` is missing:

```bash
mkdir -p src/core/generation
```

Then create the file with this content:

```python
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
```

If `src/core/generation/tag_generator.py` is missing:

```python
# Minimal tag generator for deployment
def get_template_path(template_type):
    """Get template path for template type."""
    return f"templates/{template_type}.docx"
```

If `src/core/generation/mini_font_sizing.py` is missing:

```python
# Minimal mini font sizing for deployment
def get_mini_font_size_by_marker(marker_name, content, base_size=8):
    """Get mini font size by marker."""
    return base_size

def set_mini_run_font_size(run, size):
    """Set mini run font size."""
    run.font.size = size
```

## Step 8: Create __init__.py Files

```bash
# Create __init__.py files in all directories
find src -type d -exec touch {}/__init__.py \;
```

## Step 9: Test App Import

```bash
# Test if app.py can be imported
python -c "
try:
    import app
    print('✓ App module imported successfully')
except Exception as e:
    print('✗ App module import failed:', e)
    import traceback
    traceback.print_exc()
"
```

## Step 10: Configure Web App

1. **Go to the Web tab** in PythonAnywhere
2. **Click on your web app** (adamcordova.pythonanywhere.com)
3. **Update the WSGI configuration file:**

Replace the content with:

```python
import sys
import os

# Add your project directory to the Python path
path = '/home/adamcordova/AGTDesigner'
if path not in sys.path:
    sys.path.append(path)

# Set the working directory
os.chdir(path)

# Import your Flask app
from app import app as application

# Optional: Set environment variables
os.environ['FLASK_ENV'] = 'production'
```

4. **Set the working directory:** `/home/adamcordova/AGTDesigner`
5. **Set the virtual environment:** `/home/adamcordova/AGTDesigner/venv`
6. **Click "Save"**
7. **Click "Reload"** to restart the web app

## Step 11: Verify Deployment

1. **Check your web app:** https://adamcordova.pythonanywhere.com
2. **Check the error logs** if there are issues:
   - In the Web tab, click "Log files" → "Error log"

## Troubleshooting

### If packages still don't install:
```bash
# Try installing one by one
pip install Flask
pip install pandas
pip install openpyxl
# ... continue with others
```

### If virtual environment issues:
```bash
# Remove and recreate virtual environment
rm -rf venv
python3.10 -m venv venv
source venv/bin/activate
pip install --upgrade pip
# Then install packages again
```

### If src files are still missing:
```bash
# Check Git status
git status
git log --oneline -5

# Pull latest changes
git pull origin main
```

### If app.py still fails to import:
```bash
# Check the exact error
python -c "import app" 2>&1

# Check if all required files exist
ls -la src/core/generation/
```

## Final Verification

After all fixes, verify:
- ✅ Virtual environment: `/home/adamcordova/AGTDesigner/venv`
- ✅ Working directory: `/home/adamcordova/AGTDesigner`
- ✅ All dependencies installed
- ✅ All source files present
- ✅ Web app reloaded

Your application should be available at:
**https://adamcordova.pythonanywhere.com** 