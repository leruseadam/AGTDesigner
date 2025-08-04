# PythonAnywhere WSGI Path Fix

## 🚨 **URGENT: WSGI Virtual Environment Path Error**

Your PythonAnywhere WSGI file is looking for the virtual environment in the wrong location:
- **❌ Wrong path**: `/var/www/venv_pythonanywhere/bin/activate_this.py`
- **✅ Correct path**: `/home/adamcordova/AGTDesigner/venv_pythonanywhere/bin/activate_this.py`

## 🔧 **Quick Fix (2 minutes)**

### **Step 1: Go to PythonAnywhere Web Tab**
1. Log into PythonAnywhere
2. Click on **Web** tab
3. Click on your WSGI configuration file (usually `/var/www/www_agtpricetags_com_wsgi.py`)

### **Step 2: Replace WSGI Content**
Replace the entire content with this:

```python
import sys
import os

# Add the project directory to Python path
project_dir = '/home/adamcordova/AGTDesigner'
sys.path.insert(0, project_dir)

# Activate virtual environment with correct path
activate_this = '/home/adamcordova/AGTDesigner/venv_pythonanywhere/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

# Import the Flask app
from app import create_app

# Create the application instance
application = create_app()

if __name__ == "__main__":
    application.run()
```

### **Step 3: Save and Reload**
1. **Save the file**
2. **Click "Reload"** in the Web tab
3. **Check error logs** - should be clean now

## 🎯 **What This Fixes**

- ✅ **Correct virtual environment path**
- ✅ **Proper project directory path**
- ✅ **Working Flask application import**
- ✅ **No more FileNotFoundError**

## 🚀 **Automated Fix (Alternative)**

If you prefer to run a script:

```bash
curl -sSL https://raw.githubusercontent.com/leruseadam/AGTDesigner/main/fix_pythonanywhere_wsgi_path.sh | bash
```

## 📋 **Verification**

After applying the fix:
1. **Check error logs** in PythonAnywhere Web tab
2. **Should see no more FileNotFoundError**
3. **Your website should load properly**

---

**🎉 This should fix the WSGI path error immediately!** 