# Manual PythonAnywhere Deployment Guide (Python 3.10 Compatible)

## Option 1: Automated Deployment (Recommended)

Run the simple deployment script:
```bash
./simple_reclone_pythonanywhere.sh
```

## Option 2: Manual Deployment Steps

If the automated script doesn't work, follow these manual steps:

### Step 1: Prepare Your Local Project
```bash
# Create a clean archive of your project
tar --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' --exclude='.DS_Store' \
    --exclude='node_modules' --exclude='.venv' --exclude='venv' \
    -czf labelMaker_deploy.tar.gz .
```

### Step 2: Upload to PythonAnywhere
```bash
# Upload the archive
scp labelMaker_deploy.tar.gz adamcordova@ssh.pythonanywhere.com:/tmp/
```

### Step 3: Deploy on PythonAnywhere
SSH into PythonAnywhere:
```bash
ssh adamcordova@ssh.pythonanywhere.com
```

Then run these commands:
```bash
# Navigate to home directory
cd /home/adamcordova

# Backup existing project
if [ -d "AGTDesigner" ]; then
    mv AGTDesigner AGTDesigner_backup_$(date +%Y%m%d_%H%M%S)
fi

# Create fresh directory
mkdir AGTDesigner
cd AGTDesigner

# Extract project
tar -xzf /tmp/labelMaker_deploy.tar.gz
rm /tmp/labelMaker_deploy.tar.gz

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

# Restart web app
touch /var/www/adamcordova_pythonanywhere_com_wsgi.py

echo "Deployment complete!"
echo "Python version used: $($PYTHON_CMD --version)"
```

### Step 4: Verify Deployment
```bash
# Check if everything is working
cd /home/adamcordova/AGTDesigner
source venv/bin/activate

# Test imports
python -c "import flask; import pandas; import openpyxl; print('All imports successful')"

# Check file structure
ls -la
```

## Option 3: Using PythonAnywhere Web Interface

1. Go to https://www.pythonanywhere.com
2. Log in to your account
3. Go to the "Files" tab
4. Navigate to `/home/adamcordova/`
5. Delete the existing `AGTDesigner` folder
6. Upload your project files manually
7. Go to the "Consoles" tab
8. Open a Bash console
9. Run the deployment commands from Step 3 above

## Python Version Compatibility

### Python 3.10 Features
- ✅ Full compatibility with all dependencies
- ✅ Better performance than older versions
- ✅ Enhanced error messages and debugging
- ✅ Improved type hints support

### Fallback Versions
If Python 3.10 is not available on PythonAnywhere:
- **Python 3.9**: Full compatibility
- **Python 3.8**: Full compatibility  
- **Python 3.7**: Limited compatibility (not recommended)

## Troubleshooting

### If you get permission errors:
```bash
chmod -R 755 /home/adamcordova/AGTDesigner
```

### If the web app doesn't restart:
```bash
# Go to PythonAnywhere dashboard
# Click on "Web" tab
# Click "Reload" button
```

### If imports fail:
```bash
# Check Python version
python3.10 --version
python3.9 --version
python3.8 --version
python3 --version

# Reinstall virtual environment with specific Python version
rm -rf venv
python3.10 -m venv venv  # or python3.9, python3.8, python3
source venv/bin/activate
pip install --upgrade pip

# Install dependencies with version constraints
pip install "Flask>=2.0.0,<3.0.0"
pip install "pandas>=1.3.0,<3.0.0"
pip install "openpyxl>=3.0.0,<4.0.0"
# ... (continue with other dependencies)
```

### If you get Python version conflicts:
```bash
# Check which Python is being used
which python
python --version

# Make sure you're using the correct Python in virtual environment
source venv/bin/activate
which python
python --version
```

### Check logs:
```bash
# View application logs
tail -f /var/log/adamcordova.pythonanywhere_com.error.log

# Check PythonAnywhere error logs
tail -f /var/log/adamcordova.pythonanywhere_com.access.log
```

## Final Verification

Your application should be available at:
**https://adamcordova.pythonanywhere.com**

If you see any errors, check:
1. The PythonAnywhere error logs
2. That all dependencies are installed with correct versions
3. That the virtual environment is activated
4. That the WSGI file is properly configured
5. That you're using a compatible Python version (3.8, 3.9, or 3.10)

## Key Files to Verify

After deployment, these files should exist:
- ✅ `/home/adamcordova/AGTDesigner/app.py`
- ✅ `/home/adamcordova/AGTDesigner/src/core/data/excel_processor.py`
- ✅ `/home/adamcordova/AGTDesigner/venv/bin/python` (correct Python version)
- ✅ `/home/adamcordova/AGTDesigner/uploads/` (directory)
- ✅ `/home/adamcordova/AGTDesigner/logs/` (directory)

## Python Version Check

To verify the Python version being used:
```bash
cd /home/adamcordova/AGTDesigner
source venv/bin/activate
python --version
```

This should show Python 3.10.x, 3.9.x, or 3.8.x depending on what's available on PythonAnywhere. 