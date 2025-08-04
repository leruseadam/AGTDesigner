# PythonAnywhere Virtual Environment Setup Guide

## 🚀 Quick Setup (5 minutes)

### Option 1: Automated Setup (Recommended)

1. **Log into PythonAnywhere**
   - Go to [www.pythonanywhere.com](https://www.pythonanywhere.com)
   - Log into your account

2. **Open a Bash Console**
   - Click on **Consoles** tab
   - Start a new **Bash console**

3. **Run the Setup Script**
   ```bash
   # Download and run the setup script
   curl -sSL https://raw.githubusercontent.com/leruseadam/AGTDesigner/main/pythonanywhere_venv_setup.sh | bash
   ```

### Option 2: Manual Setup

Follow these steps if you prefer to set up manually:

## 📋 Step-by-Step Manual Setup

### Step 1: Access PythonAnywhere
1. Go to [www.pythonanywhere.com](https://www.pythonanywhere.com)
2. Log into your account
3. Click on **Consoles** tab
4. Start a new **Bash console**

### Step 2: Navigate to Home Directory
```bash
cd ~
pwd
# Should show: /home/yourusername
```

### Step 3: Clone Your Repository
```bash
# Clone the repository
git clone https://github.com/leruseadam/AGTDesigner.git
cd AGTDesigner

# Verify the clone
ls -la
```

### Step 4: Create Virtual Environment
```bash
# Create virtual environment with Python 3.11
python3.11 -m venv venv_pythonanywhere

# Verify the virtual environment was created
ls -la venv_pythonanywhere/
```

### Step 5: Activate Virtual Environment
```bash
# Activate the virtual environment
source venv_pythonanywhere/bin/activate

# Verify activation (should show venv_pythonanywhere in prompt)
which python
# Should show: /home/yourusername/AGTDesigner/venv_pythonanywhere/bin/python
```

### Step 6: Upgrade Pip
```bash
# Upgrade pip to latest version
pip install --upgrade pip
```

### Step 7: Install Dependencies
```bash
# Install all dependencies from requirements file
pip install -r requirements_pythonanywhere.txt

# Install additional dependencies
pip install flask-caching python-dotenv gunicorn
```

### Step 8: Test the Application
```bash
# Test that everything works
python -c "from app import create_app; print('✅ Application ready!')"
```

### Step 9: Create WSGI Configuration
```bash
# Create WSGI configuration file
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

#### 2. Virtual Environment Issues
```bash
# Recreate virtual environment if needed
rm -rf venv_pythonanywhere
python3.11 -m venv venv_pythonanywhere
source venv_pythonanywhere/bin/activate
pip install -r requirements_pythonanywhere.txt
```

#### 3. Permission Issues
```bash
# Set proper permissions
chmod 755 /home/yourusername/AGTDesigner
chmod 644 /home/yourusername/AGTDesigner/*.py
```

#### 4. WSGI Configuration Issues
```bash
# Check WSGI file syntax
python -m py_compile wsgi.py

# Test WSGI file
python wsgi.py
```

## 📊 Verification Commands

### Check Virtual Environment
```bash
# Verify virtual environment is active
which python
# Should show: /home/yourusername/AGTDesigner/venv_pythonanywhere/bin/python

# Check Python version
python --version
# Should show: Python 3.11.x
```

### Check Dependencies
```bash
# List installed packages
pip list

# Check specific packages
python -c "import flask, pandas, openpyxl; print('✅ All key packages available')"
```

### Test Application
```bash
# Test application import
python -c "from app import create_app; print('✅ App imports successfully')"

# Test database loading
python -c "from app import create_app; app = create_app(); print('✅ Database loaded')"
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

## 🔗 Your Application URL
Once deployed, your application will be available at:
```
https://yourusername.pythonanywhere.com
```

## 📞 Support
If you encounter issues:
1. Check the error logs in PythonAnywhere Web tab
2. Verify all dependencies are installed
3. Ensure the virtual environment is activated
4. Make sure the WSGI file is correctly configured

---

**🎉 Congratulations! Your Label Maker virtual environment is now set up on PythonAnywhere!** 