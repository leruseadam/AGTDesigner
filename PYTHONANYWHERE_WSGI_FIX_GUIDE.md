# PythonAnywhere WSGI Fix Guide

## The Problem
Your PythonAnywhere WSGI file is trying to execute shell script syntax as Python code, causing a syntax error:
```
SyntaxError: invalid syntax
File "/var/www/www_agtpricetags_com_wsgi.py", line 11
exec(file_.read(), dict(__file__=activate_this))
```

## The Root Cause
The WSGI file contains code that tries to execute a virtual environment activation script (which is a shell script) as Python code. This is causing the `deactivate () {` syntax error.

## Step-by-Step Fix

### 1. Access Your PythonAnywhere Dashboard
- Go to [www.pythonanywhere.com](https://www.pythonanywhere.com)
- Log in to your account
- Navigate to the **Web** tab

### 2. Open Your Web App Configuration
- Click on your web app (likely `www.agtpricetags.com`)
- Look for the **WSGI configuration file** section
- Click to edit the WSGI file

### 3. Replace the Entire WSGI File Content
**DELETE EVERYTHING** in the current WSGI file and replace it with this clean code:

```python
#!/usr/bin/env python3
"""
Clean WSGI entry point for the Label Maker application.
This file is used by PythonAnywhere to serve the Flask application.
"""

import sys
import os

# Add the project directory to Python path
project_dir = '/home/adamcordova/AGTDesigner'
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

# Add virtual environment site-packages to Python path
venv_site_packages = '/home/adamcordova/AGTDesigner/venv_pythonanywhere/lib/python3.11/site-packages'
if os.path.exists(venv_site_packages) and venv_site_packages not in sys.path:
    sys.path.insert(0, venv_site_packages)

# Set environment variables for the virtual environment
os.environ['VIRTUAL_ENV'] = '/home/adamcordova/AGTDesigner/venv_pythonanywhere'
os.environ['PATH'] = '/home/adamcordova/AGTDesigner/venv_pythonanywhere/bin:' + os.environ.get('PATH', '')

# Import the Flask app
try:
    from app import create_app
    # Create the application instance
    application = create_app()
except ImportError as e:
    print(f"Import error: {e}")
    # Fallback - create a simple error application
    from flask import Flask
    application = Flask(__name__)
    @application.route('/')
    def error():
        return f"Import error: {e}", 500

if __name__ == "__main__":
    application.run()
```

### 4. Save the File
- Click **Save** to save the changes

### 5. Reload Your Web App
- Go back to the main web app configuration page
- Click the **Reload** button for your web app

### 6. Check the Error Logs
- If there are still issues, check the **Error log** section
- Look for any new error messages

## What This Fix Does

1. **Removes shell script execution** - No more `exec(file_.read())` calls
2. **Uses pure Python** - Only Python syntax, no bash commands
3. **Properly sets up paths** - Adds your project and virtual environment to Python path
4. **Handles import errors gracefully** - Shows helpful error messages if imports fail
5. **Sets environment variables** - Properly configures the virtual environment

## Alternative: Use the Simple Version
If the above doesn't work, try this even simpler version:

```python
import sys
import os

# Add the project directory to Python path
sys.path.insert(0, '/home/adamcordova/AGTDesigner')

# Import the Flask app
from app import create_app

# Create the application instance
application = create_app()

if __name__ == "__main__":
    application.run()
```

## Troubleshooting

### If you still get errors:
1. Check that your project path is correct (`/home/adamcordova/AGTDesigner`)
2. Verify your virtual environment path exists
3. Make sure your `app.py` file has a `create_app()` function
4. Check the error logs for specific import errors

### Common issues:
- **Wrong project path**: Update the `project_dir` variable
- **Missing virtual environment**: Remove the venv-related lines
- **Missing create_app function**: Make sure your `app.py` exports this function

## Files Created for Reference
- `clean_pythonanywhere_wsgi.py` - The clean WSGI file
- `diagnose_pythonanywhere_wsgi.py` - Diagnostic script
- `pythonanywhere_wsgi_fixed.py` - Previous fix attempt 