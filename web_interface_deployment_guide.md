# PythonAnywhere Web Interface Deployment Guide

Since SSH authentication is having issues, here's how to deploy using the PythonAnywhere web interface:

## Step 1: Prepare Your Project Archive

First, create a clean archive of your current project:

```bash
# Create project archive
tar --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' --exclude='.DS_Store' \
    --exclude='node_modules' --exclude='.venv' --exclude='venv' \
    -czf labelMaker_web_deploy.tar.gz .
```

## Step 2: Access PythonAnywhere Web Interface

1. Go to https://www.pythonanywhere.com
2. Log in to your account (adamcordova)
3. Navigate to the **Files** tab

## Step 3: Upload and Extract Project

1. **Navigate to your home directory:**
   - In the Files tab, click on `/home/adamcordova/`

2. **Backup existing project (if it exists):**
   - If you see an `AGTDesigner` folder, right-click it and rename it to `AGTDesigner_backup_$(date)`

3. **Upload your project:**
   - Click "Upload a file" button
   - Select the `labelMaker_web_deploy.tar.gz` file you created
   - Wait for upload to complete

4. **Extract the project:**
   - Go to the **Consoles** tab
   - Click "Bash" to open a new console
   - Run these commands:

```bash
# Navigate to home directory
cd /home/adamcordova

# Create fresh directory
mkdir AGTDesigner
cd AGTDesigner

# Extract the uploaded archive
tar -xzf ../labelMaker_web_deploy.tar.gz

# Remove the archive
rm ../labelMaker_web_deploy.tar.gz
```

## Step 4: Set Up Python Environment

In the same Bash console, run:

```bash
# Check available Python versions
echo "Available Python versions:"
python3.10 --version 2>/dev/null && echo "✓ Python 3.10 available" || echo "✗ Python 3.10 not available"
python3.9 --version 2>/dev/null && echo "✓ Python 3.9 available" || echo "✗ Python 3.9 not available"
python3.8 --version 2>/dev/null && echo "✓ Python 3.8 available" || echo "✗ Python 3.8 not available"
python3 --version 2>/dev/null && echo "✓ Default Python 3 available" || echo "✗ Default Python 3 not available"

# Determine which Python to use
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

# Create virtual environment
$PYTHON_CMD -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies (Python 3.10 compatible versions)
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

# Create necessary directories
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

echo "✓ Python environment setup complete!"
```

## Step 5: Configure Web App

1. **Go to the Web tab** in PythonAnywhere dashboard
2. **Click on your web app** (adamcordova.pythonanywhere.com)
3. **Update the WSGI configuration file:**

Click on the WSGI configuration file and update it to:

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

4. **Set the working directory:**
   - In the Web app configuration, set the working directory to: `/home/adamcordova/AGTDesigner`

5. **Set the virtual environment:**
   - Set the virtual environment to: `/home/adamcordova/AGTDesigner/venv`

## Step 6: Restart Web App

1. **Click the "Reload" button** in the Web tab
2. **Wait for the reload to complete** (usually takes 30-60 seconds)

## Step 7: Verify Deployment

1. **Check your web app:** https://adamcordova.pythonanywhere.com
2. **Check the error logs** if there are issues:
   - In the Web tab, click "Log files" → "Error log"

## Troubleshooting

### If the web app shows errors:
1. **Check the error log** in the Web tab
2. **Verify Python version:**
   ```bash
   cd /home/adamcordova/AGTDesigner
   source venv/bin/activate
   python --version
   ```
3. **Test imports manually:**
   ```bash
   cd /home/adamcordova/AGTDesigner
   source venv/bin/activate
   python -c "import flask; print('Flask works')"
   ```

### If dependencies fail to install:
1. **Try installing one by one:**
   ```bash
   pip install Flask
   pip install pandas
   pip install openpyxl
   # ... continue with others
   ```

### If the web app doesn't load:
1. **Check the WSGI file** is correctly configured
2. **Verify the working directory** is set correctly
3. **Make sure the virtual environment** is set correctly
4. **Check the error logs** for specific error messages

## Final Verification

After deployment, verify these files exist:
- ✅ `/home/adamcordova/AGTDesigner/app.py`
- ✅ `/home/adamcordova/AGTDesigner/src/core/data/excel_processor.py`
- ✅ `/home/adamcordova/AGTDesigner/venv/bin/python`
- ✅ `/home/adamcordova/AGTDesigner/uploads/` (directory)
- ✅ `/home/adamcordova/AGTDesigner/logs/` (directory)

Your application should be available at:
**https://adamcordova.pythonanywhere.com**

## Quick Commands for Console

If you need to run commands in the PythonAnywhere console:

```bash
# Navigate to project
cd /home/adamcordova/AGTDesigner

# Activate virtual environment
source venv/bin/activate

# Check Python version
python --version

# Test imports
python -c "import flask, pandas, openpyxl; print('All imports successful')"

# Check file structure
ls -la
``` 