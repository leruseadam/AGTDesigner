# PythonAnywhere BlockingIOError Fix Guide

## 🚨 **IMMEDIATE FIX** - Replace Your WSGI File

The BlockingIOError is caused by print statements in your current WSGI file. Here's how to fix it:

### Step 1: Go to PythonAnywhere Web Tab
1. Log into PythonAnywhere
2. Click on **Web** tab
3. Find your web app (www.agtpricetags.com)
4. Click on the **WSGI configuration file** link

### Step 2: Replace the WSGI Content
**DELETE ALL CONTENT** in the WSGI file and replace it with this:

```python
# +++++++++++ FLASK +++++++++++
# The WSGI configuration file for the Label Maker application
# This file should be placed in /var/www/yourusername_pythonanywhere_com_wsgi.py

import sys
import os

# Set environment variables to prevent BlockingIOError
os.environ['PYTHONUNBUFFERED'] = '1'
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = 'False'

# Add the project directory to Python path
project_dir = '/home/adamcordova/AGTDesigner'
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

# Try to activate virtual environment silently
try:
    venv_path = os.path.join(project_dir, 'venv_pythonanywhere')
    activate_script = os.path.join(venv_path, 'bin', 'activate_this.py')
    if os.path.exists(activate_script):
        with open(activate_script) as file_:
            exec(file_.read(), dict(__file__=activate_script))
except:
    pass

# Create the Flask application
try:
    from app import create_app
    application = create_app()
    application.config['DEBUG'] = False
    application.config['TESTING'] = False
except Exception as e:
    # Fallback to minimal Flask app if import fails
    from flask import Flask
    application = Flask(__name__)
    @application.route('/')
    def error():
        return f'<h1>Application Error</h1><p>Import failed: {str(e)}</p>', 500
```

### Step 3: Save and Reload
1. Click **Save** button
2. Go back to the **Web** tab
3. Click **Reload** button

## 🔧 **Alternative: Use the Minimal WSGI File**

If the above doesn't work, use the ultra-minimal version:

```python
import sys
import os

os.environ['PYTHONUNBUFFERED'] = '1'
os.environ['FLASK_ENV'] = 'production'

project_dir = '/home/adamcordova/AGTDesigner'
sys.path.insert(0, project_dir)

try:
    venv_path = os.path.join(project_dir, 'venv_pythonanywhere')
    activate_script = os.path.join(venv_path, 'bin', 'activate_this.py')
    if os.path.exists(activate_script):
        with open(activate_script) as file_:
            exec(file_.read(), dict(__file__=activate_script))
except:
    pass

try:
    from app import create_app
    application = create_app()
    application.config['DEBUG'] = False
except:
    from flask import Flask
    application = Flask(__name__)
    @application.route('/')
    def error():
        return '<h1>Error</h1>', 500
```

## 🐛 **What Causes BlockingIOError?**

The error occurs because:
1. **Print statements** in WSGI files can cause buffering issues
2. **Logging** can block the output stream
3. **Environment variables** not set correctly
4. **Virtual environment** activation issues

## ✅ **Why This Fix Works**

1. **No print statements** - Eliminates the main cause
2. **PYTHONUNBUFFERED=1** - Prevents output buffering
3. **Silent virtual environment activation** - No output during activation
4. **Minimal error handling** - Graceful fallbacks without logging
5. **Production settings** - Optimized for deployment

## 🚀 **After the Fix**

Once you've replaced the WSGI content:

1. **Check the error logs** - They should be much cleaner
2. **Test your application** - Visit your domain
3. **Monitor for new errors** - The BlockingIOError should be gone

## 📞 **If Still Having Issues**

If you still get errors after this fix:

1. **Check virtual environment path** - Make sure `venv_pythonanywhere` exists
2. **Verify project directory** - Ensure `/home/adamcordova/AGTDesigner` is correct
3. **Check dependencies** - Make sure all packages are installed
4. **Look at error logs** - They should now show the real import errors

## 🎯 **Expected Result**

After applying this fix, you should see:
- ✅ No more BlockingIOError messages
- ✅ Clean error logs
- ✅ Application loads properly (or shows specific import errors)
- ✅ Faster WSGI startup

---

**This fix specifically addresses the BlockingIOError you're experiencing and should resolve the issue immediately.** 