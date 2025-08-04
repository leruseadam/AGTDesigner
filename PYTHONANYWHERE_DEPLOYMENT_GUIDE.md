# PythonAnywhere Deployment Guide for Label Maker

## 🚀 Quick Deployment (5 minutes)

### Step 1: Access PythonAnywhere
1. Go to [www.pythonanywhere.com](https://www.pythonanywhere.com)
2. Log into your account
3. Click on **Consoles** tab
4. Start a new **Bash console**

### Step 2: Run the Deployment Script
```bash
# Download and run the deployment script
curl -sSL https://raw.githubusercontent.com/leruseadam/AGTDesigner/main/deploy_pythonanywhere_complete.sh | bash
```

### Step 3: Configure Web App
1. Go to **Web** tab in PythonAnywhere
2. Click **Add a new web app**
3. Choose **Manual configuration**
4. Python version: **3.11**

### Step 4: Set Configuration
- **Source code**: `/home/yourusername/AGTDesigner`
- **Working directory**: `/home/yourusername/AGTDesigner`
- **WSGI configuration file**: `/var/www/yourusername_pythonanywhere_com_wsgi.py`
- **Virtual environment**: `/home/yourusername/AGTDesigner/venv_pythonanywhere`

### Step 5: Update WSGI File
Replace the content of the WSGI file with:
```python
import sys
import os

# Add the project directory to Python path
project_dir = '/home/yourusername/AGTDesigner'
sys.path.insert(0, project_dir)

# Activate virtual environment
activate_this = '/home/yourusername/AGTDesigner/venv_pythonanywhere/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

# Set environment variables
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = 'False'

# Import the Flask app
from app import create_app

# Create the application instance
application = create_app()

if __name__ == "__main__":
    application.run()
```

### Step 6: Reload Application
Click the **Reload** button in the Web tab.

## 📋 Detailed Step-by-Step Guide

### Prerequisites
- PythonAnywhere account (free or paid)
- Git access to the repository

### Manual Setup (if automated script fails)

#### Step 1: Clone Repository
```bash
cd ~
git clone https://github.com/leruseadam/AGTDesigner.git
cd AGTDesigner
```

#### Step 2: Create Virtual Environment
```bash
python3.11 -m venv venv_pythonanywhere
source venv_pythonanywhere/bin/activate
```

#### Step 3: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements_pythonanywhere.txt
pip install flask-caching python-dotenv gunicorn
```

#### Step 4: Test Application
```bash
python -c "from app import create_app; print('✅ Application ready!')"
```

#### Step 5: Create WSGI File
```bash
cat > wsgi.py << 'EOF'
import sys
import os

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Activate virtual environment
activate_this = os.path.join(project_dir, 'venv_pythonanywhere', 'bin', 'activate_this.py')
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

# Import the Flask app
from app import create_app

# Create the application instance
application = create_app()

if __name__ == "__main__":
    application.run()
EOF
```

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. Import Errors
**Problem**: `ModuleNotFoundError` or import failures
**Solution**:
```bash
# Check if virtual environment is activated
which python
# Should show: /home/yourusername/AGTDesigner/venv_pythonanywhere/bin/python

# Reinstall dependencies
source venv_pythonanywhere/bin/activate
pip install -r requirements_pythonanywhere.txt
```

#### 2. Database Issues
**Problem**: Database not found or corrupted
**Solution**:
```bash
# Check if database exists
ls -la product_database.db

# If missing, the app will create a default one
python -c "from app import create_app; app = create_app()"
```

#### 3. WSGI Configuration Errors
**Problem**: WSGI file syntax errors
**Solution**:
```bash
# Test WSGI file syntax
python -m py_compile wsgi.py

# Check WSGI file content
cat wsgi.py
```

#### 4. Permission Issues
**Problem**: Permission denied errors
**Solution**:
```bash
# Set proper permissions
chmod 755 /home/yourusername/AGTDesigner
chmod 644 /home/yourusername/AGTDesigner/*.py
```

#### 5. Virtual Environment Issues
**Problem**: Virtual environment not found or corrupted
**Solution**:
```bash
# Recreate virtual environment
rm -rf venv_pythonanywhere
python3.11 -m venv venv_pythonanywhere
source venv_pythonanywhere/bin/activate
pip install -r requirements_pythonanywhere.txt
```

### Error Logs
Check error logs in PythonAnywhere:
1. Go to **Web** tab
2. Click on your web app
3. Check **Error log** section
4. Look for specific error messages

### Debugging Commands
```bash
# Test application import
python -c "from app import create_app; print('Import successful')"

# Test database loading
python -c "from app import create_app; app = create_app(); print('Database loaded')"

# Test WSGI configuration
python -c "import wsgi; print('WSGI OK')"

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Check installed packages
pip list
```

## 📊 Verification Commands

### Pre-Deployment Checks
```bash
# Verify virtual environment
which python
python --version

# Verify dependencies
pip list | grep -E "(flask|pandas|openpyxl)"

# Verify application
python -c "from app import create_app; print('✅ Ready for deployment')"
```

### Post-Deployment Verification
```bash
# Test the deployed application
curl -s https://yourusername.pythonanywhere.com/api/health

# Check application status
python verify_deployment.py
```

## 🔄 Maintenance

### Updating the Application
```bash
cd ~/AGTDesigner
git pull origin main
source venv_pythonanywhere/bin/activate
pip install -r requirements_pythonanywhere.txt
# Go to Web tab and click Reload
```

### Restarting the Application
```bash
cd ~/AGTDesigner
./restart_app.sh
# Or manually go to Web tab and click Reload
```

### Monitoring
- Check error logs regularly
- Monitor application performance
- Verify database integrity

## 📞 Support

If you encounter issues:
1. Check the error logs in PythonAnywhere Web tab
2. Run the verification script: `python verify_deployment.py`
3. Check this troubleshooting guide
4. Verify all dependencies are installed correctly

## 🎉 Success Indicators

Your deployment is successful when:
- ✅ Application loads without errors
- ✅ Database loads successfully (2,433+ records)
- ✅ Health endpoint responds: `{"status": "healthy", "records": 2433}`
- ✅ Main page loads correctly
- ✅ All features work as expected

---

**🎉 Congratulations! Your Label Maker is now deployed on PythonAnywhere!** 