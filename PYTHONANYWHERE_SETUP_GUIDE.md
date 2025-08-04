# PythonAnywhere Setup Guide for Label Maker

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)
1. Log into your PythonAnywhere account
2. Open a Bash console
3. Run the automated setup script:
```bash
curl -sSL https://raw.githubusercontent.com/leruseadam/AGTDesigner/restored-working-version/quick_setup_pythonanywhere.sh | bash
```

### Option 2: Manual Setup
Follow the step-by-step instructions below.

## 📋 Prerequisites
- PythonAnywhere account (free or paid)
- Git access to your repository
- Basic knowledge of PythonAnywhere interface

## 🔧 Step-by-Step Setup

### 1. Access PythonAnywhere
1. Go to [www.pythonanywhere.com](https://www.pythonanywhere.com)
2. Log into your account
3. Click on "Consoles" tab
4. Start a new Bash console

### 2. Clone Your Repository
```bash
# Create project directory
mkdir ~/labelMaker
cd ~/labelMaker

# Clone the repository
git clone -b restored-working-version https://github.com/leruseadam/AGTDesigner.git .
```

### 3. Set Up Virtual Environment
```bash
# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### 4. Install Dependencies
```bash
# Install from requirements file
pip install -r requirements_pythonanywhere.txt
```

### 5. Create Project Structure
```bash
# Create necessary directories
mkdir -p static/uploads
mkdir -p logs
mkdir -p data

# Set up database
python setup_database.py
```

### 6. Configure Web App

#### 6.1 Create Web App
1. Go to "Web" tab in PythonAnywhere dashboard
2. Click "Add a new web app"
3. Choose "Manual configuration"
4. Select Python 3.11
5. Click "Next"

#### 6.2 Configure Source Code
- **Source code**: `/home/yourusername/labelMaker`
- **Working directory**: `/home/yourusername/labelMaker`
- **WSGI configuration file**: `/var/www/yourusername_pythonanywhere_com_wsgi.py`

#### 6.3 Edit WSGI File
Click on the WSGI configuration file link and replace the content with:

```python
import sys
import os

# Add the project directory to Python path
project_dir = '/home/yourusername/labelMaker'
sys.path.insert(0, project_dir)

# Set environment variables
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = 'False'

# Import and create the Flask app
from app import create_app
application = create_app()
```

**Important**: Replace `yourusername` with your actual PythonAnywhere username.

#### 6.4 Configure Static Files
In the Web app configuration:
- **Static URL**: `/static/`
- **Static Directory**: `/home/yourusername/labelMaker/static`

#### 6.5 Set Environment Variables
Add these environment variables in the Web app configuration:
```
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
DATABASE_PATH=/home/yourusername/labelMaker/data/product_database.db
UPLOAD_FOLDER=/home/yourusername/labelMaker/static/uploads
LOG_LEVEL=INFO
```

### 7. Test Your Setup
```bash
# Run the test script
python test_deployment.py
```

### 8. Reload Web App
1. Go back to the Web tab
2. Click "Reload" button
3. Wait for the reload to complete

## 🧪 Testing Your Deployment

### 1. Check Web App Status
- Go to your PythonAnywhere URL
- You should see your Label Maker application

### 2. Test File Upload
- Try uploading an Excel file
- Check that the file is processed correctly

### 3. Test Label Generation
- Generate a test label
- Verify the PDF is created and downloaded

### 4. Check Error Logs
If something doesn't work:
1. Go to Web tab
2. Click on "Error log" link
3. Look for any error messages

## 🔧 Troubleshooting

### Common Issues

#### 1. Import Errors
**Problem**: ModuleNotFoundError when starting the app
**Solution**: 
```bash
# Make sure you're in the virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements_pythonanywhere.txt
```

#### 2. Permission Errors
**Problem**: Cannot write to database or upload files
**Solution**:
```bash
# Set proper permissions
chmod 755 ~/labelMaker
chmod 755 ~/labelMaker/data
chmod 755 ~/labelMaker/static/uploads
```

#### 3. WSGI Configuration Errors
**Problem**: 500 Internal Server Error
**Solution**:
1. Check the error log in PythonAnywhere Web tab
2. Verify the WSGI file path is correct
3. Make sure all imports work in the virtual environment

#### 4. Static Files Not Loading
**Problem**: CSS/JS files not loading
**Solution**:
1. Verify static file configuration in Web tab
2. Check that static files exist in the correct directory
3. Clear browser cache

### Debugging Commands

```bash
# Test Flask app locally
cd ~/labelMaker
source venv/bin/activate
python app.py

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Test imports
python -c "from app import create_app; print('App created successfully')"

# Check file permissions
ls -la ~/labelMaker/
ls -la ~/labelMaker/data/
ls -la ~/labelMaker/static/
```

## 📝 Maintenance

### Updating Your App
```bash
cd ~/labelMaker
git pull origin restored-working-version
source venv/bin/activate
pip install -r requirements_pythonanywhere.txt
# Reload web app in PythonAnywhere dashboard
```

### Monitoring Logs
```bash
# Check application logs
tail -f ~/labelMaker/logs/app.log

# Check PythonAnywhere error logs
# (Access via Web tab in dashboard)
```

### Backup Database
```bash
# Create backup of database
cp ~/labelMaker/data/product_database.db ~/labelMaker/data/product_database.db.backup
```

## 🆘 Getting Help

If you encounter issues:

1. **Check the error logs** in PythonAnywhere Web tab
2. **Run the test script**: `python test_deployment.py`
3. **Verify your configuration** matches the guide above
4. **Check file permissions** and paths
5. **Contact support** if the issue persists

## 📊 Performance Tips

1. **Use the paid plan** for better performance
2. **Optimize database queries** for large datasets
3. **Use static file caching** for better load times
4. **Monitor memory usage** in PythonAnywhere dashboard
5. **Regularly clean up** uploaded files

## 🔗 Useful Links

- [PythonAnywhere Documentation](https://help.pythonanywhere.com/)
- [Flask Deployment Guide](https://flask.palletsprojects.com/en/2.3.x/deploying/)
- [Your GitHub Repository](https://github.com/leruseadam/AGTDesigner)

---

**Note**: This guide assumes you're using the `restored-working-version` branch. If you're using a different branch, update the git clone command accordingly. 