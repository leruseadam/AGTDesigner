# EMERGENCY PythonAnywhere WSGI Fix

## The Problem
Your PythonAnywhere WSGI file is still trying to execute shell script syntax, causing persistent syntax errors.

## Emergency Fix Options

### Option 1: Use the Diagnostic WSGI (Recommended)
Replace your WSGI file with this diagnostic version that will show us exactly what's wrong:

```python
#!/usr/bin/env python3
"""
Emergency WSGI fix for PythonAnywhere.
This is a minimal, bulletproof WSGI file that should work regardless of the environment.
"""

import sys
import os

# Print diagnostic information
print("=== WSGI Diagnostic Information ===")
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print(f"Current working directory: {os.getcwd()}")
print(f"sys.path: {sys.path[:5]}...")  # Show first 5 entries

# Add multiple possible project paths
possible_paths = [
    '/home/adamcordova/AGTDesigner',
    '/home/adamcordova/labelMaker_ newgui BACKUP 6.24 copy 17',
    '/home/adamcordova/AGTDesigner/labelMaker_ newgui BACKUP 6.24 copy 17',
    os.path.dirname(os.path.abspath(__file__))
]

for path in possible_paths:
    if os.path.exists(path):
        print(f"✓ Found project directory: {path}")
        if path not in sys.path:
            sys.path.insert(0, path)
            print(f"  Added to sys.path")
    else:
        print(f"✗ Path not found: {path}")

# Try to import Flask first
try:
    import flask
    print(f"✓ Flask version: {flask.__version__}")
except ImportError as e:
    print(f"✗ Flask import error: {e}")

# Try to import the app
try:
    from app import create_app
    print("✓ Successfully imported create_app")
    application = create_app()
    print("✓ Successfully created application")
except ImportError as e:
    print(f"✗ Import error: {e}")
    # Create a minimal fallback app
    from flask import Flask
    application = Flask(__name__)
    
    @application.route('/')
    def error():
        return f"""
        <h1>WSGI Diagnostic Page</h1>
        <p>Import error: {e}</p>
        <p>Python version: {sys.version}</p>
        <p>Python executable: {sys.executable}</p>
        <p>Current directory: {os.getcwd()}</p>
        <p>sys.path: {sys.path}</p>
        """, 500

if __name__ == "__main__":
    application.run()
```

### Option 2: Ultra-Simple WSGI
If Option 1 doesn't work, try this minimal version:

```python
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Try to import and create app
try:
    from app import create_app
    application = create_app()
except Exception as e:
    from flask import Flask
    application = Flask(__name__)
    @application.route('/')
    def error():
        return f"Error: {e}", 500
```

### Option 3: Check Your Project Structure
1. Go to your PythonAnywhere **Files** tab
2. Navigate to your project directory
3. Check if `app.py` exists
4. Check if `app.py` has a `create_app()` function

### Option 4: Create a New Web App
If all else fails:
1. Go to **Web** tab in PythonAnywhere
2. Click **Add a new web app**
3. Choose **Manual configuration**
4. Choose **Python 3.11**
5. Set the **Source code** to your project directory
6. Set the **Working directory** to your project directory
7. Use this simple WSGI:

```python
import sys
import os
sys.path.insert(0, '/home/adamcordova/AGTDesigner')
from app import create_app
application = create_app()
```

## Step-by-Step Instructions

### 1. Access PythonAnywhere
- Go to [www.pythonanywhere.com](https://www.pythonanywhere.com)
- Log in to your account

### 2. Check Your Project Structure
- Go to **Files** tab
- Navigate to `/home/adamcordova/AGTDesigner`
- Verify that `app.py` exists
- Check that `app.py` contains a `create_app()` function

### 3. Fix the WSGI File
- Go to **Web** tab
- Click on your web app
- Find the **WSGI configuration file**
- **DELETE EVERYTHING** in the current file
- Paste one of the options above (start with Option 1)
- **Save** the file

### 4. Reload and Check
- Click **Reload** for your web app
- Check the **Error log** for new messages
- Visit your website to see if it works

### 5. If Still Not Working
- Check the **Error log** for specific error messages
- Try the different WSGI options above
- Consider creating a new web app (Option 4)

## What to Look For

### In Error Logs:
- Import errors (missing modules)
- Path errors (wrong directory)
- Syntax errors (still shell script code)
- Permission errors

### In Your Project:
- Does `app.py` exist?
- Does `app.py` have `create_app()` function?
- Are all dependencies installed in your virtual environment?

## Emergency Contact
If none of these work, we may need to:
1. Check your exact project structure on PythonAnywhere
2. Verify your virtual environment setup
3. Reinstall dependencies
4. Create a completely new web app

The diagnostic WSGI (Option 1) will show us exactly what's wrong and help us fix it. 