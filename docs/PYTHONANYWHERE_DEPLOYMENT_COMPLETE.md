# 🚀 Complete PythonAnywhere Deployment Guide

## Overview
This guide will walk you through deploying your Label Maker Flask application to PythonAnywhere, including all dependency installation steps.

## Prerequisites
- PythonAnywhere account (free tier works for testing)
- Your application files uploaded to PythonAnywhere

## Step-by-Step Deployment

### 1. 📂 Upload Your Code

**Option A: Via Files Tab**
1. Go to PythonAnywhere Dashboard → Files
2. Create a new folder: `labelmaker`
3. Upload all your project files (avoid uploading `__pycache__` folders)

**Option B: Via Git (Recommended)**
```bash
# In PythonAnywhere Bash console
git clone https://github.com/leruseadam/AGTDesigner2.git labelmaker
cd labelmaker
```

### 2. 🐍 Create Virtual Environment

In PythonAnywhere Bash console:
```bash
# Create virtual environment
python3.10 -m venv ~/labelmaker-venv

# Activate it
source ~/labelmaker-venv/bin/activate

# Verify activation
which python
# Should show: /home/yourusername/labelmaker-venv/bin/python
```

### 3. 📦 Install Dependencies

**Method 1: Using the Installation Script (Recommended)**
```bash
# Make sure you're in the labelmaker directory
cd ~/labelmaker

# Make the script executable
chmod +x install_pythonanywhere.sh

# Run the installation script
./install_pythonanywhere.sh
```

**Method 2: Manual Installation**
```bash
# Activate virtual environment
source ~/labelmaker-venv/bin/activate

# Upgrade pip first
pip install --upgrade pip setuptools wheel

# Try requirements files in order
pip install -r requirements_web.txt
# If that fails, try:
pip install -r requirements_pythonanywhere.txt
# If that fails, try:
pip install -r requirements_minimal.txt
```

**Method 3: Individual Package Installation**
If requirements files fail, install packages individually:
```bash
# Core Flask packages
pip install Flask==3.0.2 Werkzeug==3.0.1 Jinja2==3.1.3

# Data processing
pip install pandas==2.2.1 numpy==1.26.4

# Document processing
pip install python-docx==1.1.0 docxtpl==0.16.7 openpyxl==3.1.2

# Image processing
pip install Pillow==10.2.0

# Others
pip install python-dateutil==2.8.2 watchdog>=2.1.6
```

### 4. 🌐 Create Web App

1. Go to **Web** tab in PythonAnywhere dashboard
2. Click **"Add a new web app"**
3. Choose **"Manual configuration"**
4. Select **Python 3.10**
5. Click **"Next"**

### 5. ⚙️ Configure Web App Settings

In the Web tab, configure:

**Code section:**
- **Source code**: `/home/yourusername/labelmaker`
- **Working directory**: `/home/yourusername/labelmaker`

**Virtualenv section:**
- **Path**: `/home/yourusername/labelmaker-venv`

**WSGI configuration file:**
- Click on the WSGI file link
- Replace content with your `wsgi.py` file content

**Static files:**
- **URL**: `/static/`
- **Directory**: `/home/yourusername/labelmaker/static/`

### 6. 📝 Environment Variables

In the Web tab → Environment variables section, add:
- `DEVELOPMENT_MODE` = `false`
- `FLASK_ENV` = `production`
- `SECRET_KEY` = `your-secure-secret-key-here`

### 7. 🗂️ Create Necessary Directories

```bash
cd ~/labelmaker
mkdir -p uploads output cache logs static/css static/js static/img templates
chmod -R 755 uploads output cache logs static
```

### 8. 🔄 Deploy and Test

1. Click **"Reload"** button in the Web tab
2. Visit your app at `https://yourusername.pythonanywhere.com`
3. Check for any errors in the error log (accessible via Web tab)

## 🔧 Troubleshooting

### Common Issues and Solutions

**1. Import Errors**
- Check that all dependencies are installed in the virtual environment
- Verify WSGI file path is correct
- Ensure working directory is set correctly

**2. Static Files Not Loading**
- Verify static files mapping in Web tab
- Check that static files exist in the correct directory
- Ensure proper permissions: `chmod -R 755 static/`

**3. Database Issues**
- Make sure database file has correct permissions
- Check that database directory exists and is writable

**4. Package Installation Failures**
- Try using older versions from `requirements_pythonanywhere.txt`
- Use `--no-build-isolation` flag for problematic packages
- Check PythonAnywhere system packages that might conflict

### Debugging Commands

```bash
# Check installed packages
pip list

# Test imports
python -c "import flask; print('Flask version:', flask.__version__)"
python -c "import pandas; print('Pandas version:', pandas.__version__)"
python -c "import docx; print('python-docx available')"

# Check file permissions
ls -la ~/labelmaker/

# View error logs
tail -f ~/labelmaker/logs/error.log  # if you have logging set up
```

## 🎯 Post-Deployment Checklist

- [ ] Virtual environment created and activated
- [ ] All dependencies installed successfully
- [ ] Web app configured with correct paths
- [ ] WSGI file updated and working
- [ ] Static files mapping configured
- [ ] Environment variables set
- [ ] Necessary directories created with correct permissions
- [ ] App loads without errors
- [ ] File upload functionality works
- [ ] Document generation works
- [ ] All features tested

## 📞 Support

If you encounter issues:
1. Check the error logs in PythonAnywhere Web tab
2. Verify all paths in the Web configuration
3. Test package imports in the bash console
4. Consult PythonAnywhere help documentation

## 🔄 Updates and Maintenance

To update your app:
1. Upload new files or `git pull` changes
2. Activate virtual environment
3. Install any new dependencies
4. Click "Reload" in Web tab

Remember: PythonAnywhere free accounts have some limitations, but they're perfect for testing and small applications!
