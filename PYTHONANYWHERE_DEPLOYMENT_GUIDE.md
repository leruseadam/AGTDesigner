# PythonAnywhere Deployment Guide for Label Maker

## 🚀 Quick Setup (5 minutes)

### Step 1: Log into PythonAnywhere
1. Go to [www.pythonanywhere.com](https://www.pythonanywhere.com)
2. Log into your account
3. Click on **Consoles** tab
4. Start a new **Bash console**

### Step 2: Clone Your Repository
```bash
# Clone the repository
git clone https://github.com/leruseadam/AGTDesigner.git
cd AGTDesigner

# Switch to the working branch
git checkout main
```

### Step 3: Create PythonAnywhere Virtual Environment
```bash
# Create virtual environment with Python 3.11
python3.11 -m venv venv_pythonanywhere

# Activate the virtual environment
source venv_pythonanywhere/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install all dependencies
pip install -r requirements_pythonanywhere.txt

# Install additional dependencies
pip install flask-caching python-dotenv gunicorn
```

### Step 4: Test the Application
```bash
# Test that everything works
python -c "from app import create_app; print('✅ App ready for deployment!')"
```

## 🌐 Web App Configuration

### Step 1: Create Web App
1. Go to **Web** tab in PythonAnywhere
2. Click **Add a new web app**
3. Choose **Manual configuration**
4. Python version: **3.11**

### Step 2: Configure Source Code
- **Source code**: `/home/yourusername/AGTDesigner`
- **Working directory**: `/home/yourusername/AGTDesigner`
- **WSGI configuration file**: `/var/www/yourusername_pythonanywhere_com_wsgi.py`

### Step 3: Update WSGI File
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

# Import the Flask app
from app import create_app

# Create the application instance
application = create_app()

if __name__ == "__main__":
    application.run()
```

### Step 4: Configure Virtual Environment
- **Virtual environment**: `/home/yourusername/AGTDesigner/venv_pythonanywhere`

### Step 5: Set Environment Variables
Add these to your WSGI file or create a `.env` file:
```python
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = 'False'
```

## 📁 File Structure
```
/home/yourusername/AGTDesigner/
├── app.py                          # Main application
├── wsgi.py                         # WSGI entry point
├── requirements_pythonanywhere.txt  # Dependencies
├── venv_pythonanywhere/           # Virtual environment
├── src/                           # Source code
├── templates/                     # HTML templates
├── static/                        # CSS, JS, images
└── product_database.db           # Database file
```

## 🔧 Troubleshooting

### Common Issues:

#### 1. Import Errors
```bash
# Make sure you're in the correct directory
cd /home/yourusername/AGTDesigner

# Activate virtual environment
source venv_pythonanywhere/bin/activate

# Check Python path
python -c "import sys; print(sys.path)"
```

#### 2. Database Issues
```bash
# Check if database file exists
ls -la product_database.db

# If missing, the app will create it automatically
```

#### 3. Permission Issues
```bash
# Set proper permissions
chmod 755 /home/yourusername/AGTDesigner
chmod 644 /home/yourusername/AGTDesigner/*.py
```

#### 4. Virtual Environment Issues
```bash
# Recreate virtual environment if needed
rm -rf venv_pythonanywhere
python3.11 -m venv venv_pythonanywhere
source venv_pythonanywhere/bin/activate
pip install -r requirements_pythonanywhere.txt
```

## 🚀 Deployment Commands

### Complete Setup Script
```bash
#!/bin/bash
# Run this in PythonAnywhere Bash console

echo "🚀 Setting up Label Maker on PythonAnywhere..."

# Clone repository
git clone https://github.com/leruseadam/AGTDesigner.git
cd AGTDesigner

# Create virtual environment
python3.11 -m venv venv_pythonanywhere
source venv_pythonanywhere/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements_pythonanywhere.txt
pip install flask-caching python-dotenv gunicorn

# Test application
python -c "from app import create_app; print('✅ Setup complete!')"

echo "🎉 Label Maker is ready for deployment!"
```

## 📊 Monitoring

### Check Application Status
```bash
# Check if app is running
ps aux | grep python

# Check logs
tail -f /var/log/yourusername_pythonanywhere_com.error.log
```

### Restart Application
1. Go to **Web** tab
2. Click **Reload** button
3. Check for any error messages

## 🔗 Your Application URL
Once deployed, your application will be available at:
```
https://yourusername.pythonanywhere.com
```

## 📞 Support
If you encounter issues:
1. Check the error logs in PythonAnywhere
2. Verify all dependencies are installed
3. Ensure the virtual environment is activated
4. Make sure the WSGI file is correctly configured

---

**🎉 Congratulations! Your Label Maker application is now deployed on PythonAnywhere!** 