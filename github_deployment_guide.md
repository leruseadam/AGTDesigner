# GitHub Deployment to PythonAnywhere Guide

This guide will help you deploy your project to PythonAnywhere using GitHub, which is more reliable than SSH or web uploads.

## Step 1: Prepare Your Local Repository

First, let's check if your project is already a Git repository and prepare it for GitHub:

```bash
# Check if this is already a Git repository
git status

# If not a Git repository, initialize it
if [ ! -d ".git" ]; then
    git init
    echo "Git repository initialized"
fi

# Add all files (excluding sensitive data)
git add .

# Create initial commit
git commit -m "Initial commit - Label Maker project"

# Check if you have a remote repository
git remote -v
```

## Step 2: Create GitHub Repository

1. **Go to GitHub:** https://github.com
2. **Create a new repository:**
   - Click "New repository"
   - Name: `labelMaker` (or your preferred name)
   - Description: "Label Maker - Excel processing and document generation"
   - Make it **Public** (easier for PythonAnywhere)
   - **Don't** initialize with README (we'll push existing code)
   - Click "Create repository"

3. **Add GitHub as remote and push:**
```bash
# Add GitHub as remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/labelMaker.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Step 3: Deploy to PythonAnywhere via GitHub

### Option A: Using PythonAnywhere Web Interface

1. **Go to PythonAnywhere:** https://www.pythonanywhere.com
2. **Log in** to your account (adamcordova)
3. **Go to the Consoles tab**
4. **Open a Bash console**

### Option B: Using SSH (if working)

```bash
ssh adamcordova@ssh.pythonanywhere.com
```

## Step 4: Clone from GitHub on PythonAnywhere

In the PythonAnywhere console, run:

```bash
# Navigate to home directory
cd /home/adamcordova

# Backup existing project if it exists
if [ -d "AGTDesigner" ]; then
    mv AGTDesigner AGTDesigner_backup_$(date +%Y%m%d_%H%M%S)
    echo "Existing project backed up"
fi

# Clone from GitHub (replace YOUR_USERNAME with your GitHub username)
git clone https://github.com/YOUR_USERNAME/labelMaker.git AGTDesigner

# Navigate to project
cd AGTDesigner

# Check what we cloned
ls -la
```

## Step 5: Set Up Python Environment

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

## Step 6: Configure Web App

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

## Step 7: Restart Web App

1. **Click the "Reload" button** in the Web tab
2. **Wait for the reload to complete** (usually takes 30-60 seconds)

## Step 8: Verify Deployment

1. **Check your web app:** https://adamcordova.pythonanywhere.com
2. **Check the error logs** if there are issues:
   - In the Web tab, click "Log files" → "Error log"

## Step 9: Set Up Git for Future Updates

To make future updates easier, set up Git on PythonAnywhere:

```bash
# Configure Git (replace with your details)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Test Git access
git status
```

## Future Updates

To update your PythonAnywhere deployment in the future:

### On Your Local Machine:
```bash
# Make your changes
git add .
git commit -m "Update description"
git push origin main
```

### On PythonAnywhere:
```bash
cd /home/adamcordova/AGTDesigner
git pull origin main

# Restart the web app
touch /var/www/adamcordova_pythonanywhere_com_wsgi.py
```

## Troubleshooting

### If Git clone fails:
```bash
# Try with HTTPS
git clone https://github.com/YOUR_USERNAME/labelMaker.git AGTDesigner

# Or try with SSH (if you have SSH keys set up)
git clone git@github.com:YOUR_USERNAME/labelMaker.git AGTDesigner
```

### If dependencies fail to install:
```bash
# Try installing one by one
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

## Benefits of GitHub Deployment

✅ **Version Control** - Track all changes
✅ **Easy Updates** - Just push to GitHub and pull on PythonAnywhere
✅ **Backup** - Your code is safely stored on GitHub
✅ **Collaboration** - Easy to share and collaborate
✅ **Reliability** - No SSH or upload issues
✅ **Rollback** - Easy to revert to previous versions

## Final Verification

After deployment, verify these files exist:
- ✅ `/home/adamcordova/AGTDesigner/app.py`
- ✅ `/home/adamcordova/AGTDesigner/src/core/data/excel_processor.py`
- ✅ `/home/adamcordova/AGTDesigner/venv/bin/python`
- ✅ `/home/adamcordova/AGTDesigner/.git/` (Git repository)
- ✅ `/home/adamcordova/AGTDesigner/uploads/` (directory)
- ✅ `/home/adamcordova/AGTDesigner/logs/` (directory)

Your application should be available at:
**https://adamcordova.pythonanywhere.com** 