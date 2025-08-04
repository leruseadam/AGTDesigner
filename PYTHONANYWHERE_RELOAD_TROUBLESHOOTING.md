# PythonAnywhere Reload Troubleshooting

## The Problem
You're changing the WSGI file but the error log isn't updating, suggesting PythonAnywhere isn't actually reloading the file.

## Possible Causes and Solutions

### 1. PythonAnywhere Caching Issue
**Symptoms:** Changes to WSGI file don't appear in error logs
**Solution:** 
- Wait 2-3 minutes after saving
- Try accessing your website directly (not just checking logs)
- Check if the website actually changes

### 2. Wrong WSGI File Location
**Symptoms:** Changes don't take effect
**Solution:**
- Make sure you're editing the correct WSGI file
- In PythonAnywhere Web tab, verify you're editing the WSGI file for the right web app
- Check the file path shown in the editor

### 3. Syntax Error Preventing Reload
**Symptoms:** Old errors persist
**Solution:**
- Use the minimal test WSGI first to verify reloading works
- Check for any syntax errors in your WSGI file
- Make sure there are no shell script commands

### 4. PythonAnywhere Server Issues
**Symptoms:** No response from reload button
**Solution:**
- Try reloading multiple times
- Wait 5-10 minutes between attempts
- Check PythonAnywhere status page

## Step-by-Step Diagnostic Process

### Step 1: Test with Minimal WSGI
Use this minimal WSGI to test if reloading works at all:

```python
#!/usr/bin/env python3
import sys
import os
import time

# Force reload with timestamp
TIMESTAMP = 1754283094
print(f"MINIMAL WSGI LOADED - TIMESTAMP: {TIMESTAMP}")

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Try to create a simple Flask app
try:
    from flask import Flask
    application = Flask(__name__)
    
    @application.route('/')
    def hello():
        return f"Hello from minimal WSGI! Timestamp: {TIMESTAMP}"
    
    print("✓ Minimal Flask app created")
except Exception as e:
    print(f"✗ Error creating minimal app: {e}")
    # Create a dummy application
    class DummyApp:
        def __call__(self, environ, start_response):
            status = '200 OK'
            response_headers = [('Content-type', 'text/plain')]
            start_response(status, response_headers)
            return [f"Error: {e} - Timestamp: {TIMESTAMP}".encode()]
    
    application = DummyApp()

if __name__ == "__main__":
    application.run()
```

### Step 2: Check Website Response
After saving and reloading:
1. Visit your website directly (e.g., www.agtpricetags.com)
2. Check if you see the timestamp message
3. If you see the timestamp, reloading is working
4. If you don't see the timestamp, there's a reload issue

### Step 3: Force Reload with Diagnostic WSGI
If the minimal WSGI works, try the diagnostic version:

```python
#!/usr/bin/env python3
"""
Force reload WSGI for PythonAnywhere.
This file includes a timestamp to force reloading.
"""

import sys
import os
import time

# Force reload by including timestamp
TIMESTAMP = 1754283094
print(f"=== WSGI RELOAD FORCED - TIMESTAMP: {TIMESTAMP} ===")
print(f"Current time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print(f"Current working directory: {os.getcwd()}")
print(f"sys.path: {sys.path[:3]}...")

# Add project directory
project_dir = '/home/adamcordova/AGTDesigner'
print(f"Checking project directory: {project_dir}")

if os.path.exists(project_dir):
    print(f"✓ Project directory exists")
    if project_dir not in sys.path:
        sys.path.insert(0, project_dir)
        print(f"  Added to sys.path")
    else:
        print(f"  Already in sys.path")
else:
    print(f"✗ Project directory does not exist")

# Check if app.py exists
app_path = os.path.join(project_dir, 'app.py')
if os.path.exists(app_path):
    print(f"✓ app.py exists at {app_path}")
else:
    print(f"✗ app.py does not exist at {app_path}")

# Try to import Flask
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
        <h1>WSGI Diagnostic Page - Timestamp: {TIMESTAMP}</h1>
        <p>Import error: {e}</p>
        <p>Python version: {sys.version}</p>
        <p>Python executable: {sys.executable}</p>
        <p>Current directory: {os.getcwd()}</p>
        <p>Project directory: {project_dir}</p>
        <p>app.py exists: {os.path.exists(app_path)}</p>
        <p>sys.path: {sys.path}</p>
        """, 500
except Exception as e:
    print(f"✗ Unexpected error: {e}")
    # Create a minimal fallback app
    from flask import Flask
    application = Flask(__name__)
    
    @application.route('/')
    def error():
        return f"""
        <h1>WSGI Error Page - Timestamp: {TIMESTAMP}</h1>
        <p>Unexpected error: {e}</p>
        <p>Python version: {sys.version}</p>
        <p>Python executable: {sys.executable}</p>
        <p>Current directory: {os.getcwd()}</p>
        <p>Project directory: {project_dir}</p>
        """, 500

print(f"=== WSGI Setup Complete - Timestamp: {TIMESTAMP} ===")

if __name__ == "__main__":
    application.run()
```

### Step 4: Alternative Reload Methods
If the reload button isn't working:

1. **Try multiple reloads:** Click reload 3-4 times
2. **Wait longer:** Wait 5-10 minutes between attempts
3. **Check PythonAnywhere status:** Visit status.pythonanywhere.com
4. **Try a different browser:** Sometimes browser caching interferes
5. **Clear browser cache:** Clear cache and cookies for PythonAnywhere

### Step 5: Emergency Solutions
If nothing works:

1. **Create a new web app:**
   - Go to Web tab
   - Click "Add a new web app"
   - Choose "Manual configuration"
   - Choose Python 3.11
   - Set source code to your project directory
   - Use the minimal WSGI

2. **Contact PythonAnywhere support:**
   - If reloading completely fails
   - If you can't access the WSGI file
   - If the web app disappears

## What to Look For

### In Error Logs:
- **Timestamp messages:** Should show current timestamp
- **Python version:** Should match your PythonAnywhere version
- **Directory information:** Should show correct paths
- **Import errors:** Should show specific import issues

### In Website Response:
- **Timestamp in page:** Should show current timestamp
- **Error messages:** Should show specific error details
- **Working page:** Should load your actual application

## Common Issues and Fixes

### Issue: "No module named 'flask'"
**Fix:** Install Flask in your virtual environment
```bash
pip install flask
```

### Issue: "No module named 'app'"
**Fix:** Check your project path and make sure app.py exists

### Issue: "Permission denied"
**Fix:** Check file permissions on PythonAnywhere

### Issue: "Syntax error"
**Fix:** Make sure there are no shell script commands in the WSGI file

## Next Steps
1. Try the minimal WSGI first
2. Check if the website actually changes
3. Look for timestamp messages in error logs
4. If minimal WSGI works, try the diagnostic version
5. If nothing works, consider creating a new web app

The key is to verify that reloading is actually working before trying to fix the specific application issues. 