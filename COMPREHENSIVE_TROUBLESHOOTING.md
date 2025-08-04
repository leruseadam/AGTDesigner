# 🔧 Comprehensive BlockingIOError Troubleshooting Guide

## 🚨 **The Problem**
You're getting `BlockingIOError: [Errno 11] write could not complete without blocking` on lines 19 and 106 of your WSGI file.

## 🎯 **Root Cause**
The error occurs because your WSGI file has `print()` statements that are trying to write to stdout/stderr, but the output stream is blocked or buffered.

## 📋 **All Possible Solutions**

### **Solution 1: Replace WSGI Content (IMMEDIATE FIX)**
**Status: ⭐ RECOMMENDED - Most Likely to Work**

Replace your entire WSGI file content with:
```python
import sys
import os

os.environ['PYTHONUNBUFFERED'] = '1'
os.environ['FLASK_ENV'] = 'production'

sys.path.insert(0, '/home/adamcordova/AGTDesigner')

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

### **Solution 2: Environment Variables Only**
**Status: 🔧 TRY IF SOLUTION 1 DOESN'T WORK**

Add these to the top of your existing WSGI file:
```python
import os
import sys

# Prevent BlockingIOError
os.environ['PYTHONUNBUFFERED'] = '1'
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = 'False'

# Force unbuffered output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)
```

### **Solution 3: Output Redirection**
**Status: 🔧 ALTERNATIVE APPROACH**

Add this to your WSGI file:
```python
import sys
import io

class UnbufferedStream:
    def __init__(self, stream):
        self.stream = stream
    
    def write(self, data):
        self.stream.write(data)
        self.stream.flush()
    
    def __getattr__(self, attr):
        return getattr(self.stream, attr)

# Apply unbuffered streams
sys.stdout = UnbufferedStream(sys.stdout)
sys.stderr = UnbufferedStream(sys.stderr)
```

### **Solution 4: PythonAnywhere-Specific Configuration**
**Status: 🔧 PYTHONANYWHERE OPTIMIZED**

Use this specialized configuration:
```python
import sys
import os

# PythonAnywhere environment setup
os.environ['PYTHONANYWHERE_SITE'] = 'True'
os.environ['PYTHONUNBUFFERED'] = '1'
os.environ['FLASK_ENV'] = 'production'

# Disable all output during startup
class NullWriter:
    def write(self, text):
        pass
    def flush(self):
        pass

# Temporarily suppress output during import
original_stdout = sys.stdout
original_stderr = sys.stderr
sys.stdout = NullWriter()
sys.stderr = NullWriter()

try:
    sys.path.insert(0, '/home/adamcordova/AGTDesigner')
    from app import create_app
    application = create_app()
    application.config['DEBUG'] = False
finally:
    sys.stdout = original_stdout
    sys.stderr = original_stderr
```

### **Solution 5: Web Server Configuration Changes**
**Status: ⚙️ SERVER-LEVEL FIX**

In PythonAnywhere Web tab:
1. **Python version**: Change to 3.11
2. **Working directory**: `/home/adamcordova/AGTDesigner`
3. **Virtual environment**: `/home/adamcordova/AGTDesigner/venv_pythonanywhere`
4. **Environment variables**:
   - `PYTHONUNBUFFERED=1`
   - `FLASK_ENV=production`
   - `FLASK_DEBUG=False`

### **Solution 6: Alternative WSGI Structure**
**Status: 🔧 STRUCTURAL APPROACH**

Use this alternative structure:
```python
import sys
import os

def create_wsgi_app():
    """Create the WSGI application without any output."""
    os.environ['PYTHONUNBUFFERED'] = '1'
    os.environ['FLASK_ENV'] = 'production'
    
    sys.path.insert(0, '/home/adamcordova/AGTDesigner')
    
    try:
        from app import create_app
        app = create_app()
        app.config['DEBUG'] = False
        return app
    except:
        from flask import Flask
        app = Flask(__name__)
        @app.route('/')
        def error():
            return '<h1>Error</h1>', 500
        return app

# Create the application
application = create_wsgi_app()
```

### **Solution 7: Logging Configuration**
**Status: 🔧 LOGGING-LEVEL FIX**

Add this to suppress all logging:
```python
import logging

# Configure logging to prevent BlockingIOError
logging.basicConfig(
    level=logging.ERROR,
    format='%(levelname)s: %(message)s',
    handlers=[logging.NullHandler()]
)

# Suppress all logging
logging.getLogger().setLevel(logging.CRITICAL)
logging.getLogger('werkzeug').setLevel(logging.CRITICAL)
logging.getLogger('urllib3').setLevel(logging.CRITICAL)
```

## 🚀 **Recommended Action Plan**

### **Step 1: Try Solution 1 (Immediate)**
1. Go to PythonAnywhere Web tab
2. Click on WSGI configuration file
3. **DELETE ALL CONTENT**
4. Paste the Solution 1 code
5. Save and reload

### **Step 2: If Solution 1 Fails**
1. Try Solution 2 (Environment Variables)
2. If that fails, try Solution 4 (PythonAnywhere-Specific)

### **Step 3: Server Configuration**
1. Apply Solution 5 (Web Server Configuration)
2. Ensure Python version is 3.11
3. Set correct working directory and virtual environment

### **Step 4: Advanced Fixes**
1. Try Solution 6 (Alternative Structure)
2. If still failing, try Solution 7 (Logging Configuration)

## 🔍 **Diagnostic Steps**

### **Check Current WSGI File**
1. Look for any `print()` statements
2. Look for any logging statements
3. Check for any output during import

### **Check PythonAnywhere Settings**
1. Verify Python version (should be 3.11)
2. Check working directory path
3. Verify virtual environment path
4. Check environment variables

### **Test Each Solution**
1. Apply one solution at a time
2. Reload the web app after each change
3. Check error logs for improvement
4. Move to next solution if current one fails

## 📊 **Success Indicators**

After applying any solution, you should see:
- ✅ No more BlockingIOError messages
- ✅ Clean error logs
- ✅ Application loads (or shows real import errors)
- ✅ No buffering issues

## 🆘 **If All Solutions Fail**

If none of these solutions work:
1. **Check PythonAnywhere status** - There might be server issues
2. **Contact PythonAnywhere support** - The issue might be platform-specific
3. **Try a different Python version** - Some versions have different buffering behavior
4. **Check for conflicting processes** - Other processes might be blocking output

---

**Start with Solution 1 (Replace WSGI Content) as it's the most likely to resolve the issue immediately.** 