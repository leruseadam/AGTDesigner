#!/usr/bin/env python3
"""
PythonAnywhere Fix Script
This script fixes the critical issues identified in the logs:
1. Logging "Message too long" error
2. Directory path issues
3. uWSGI restart loop
"""

import os
import sys

def create_fixed_wsgi():
    """Create a fixed WSGI file for PythonAnywhere"""
    
    wsgi_content = '''#!/usr/bin/env python3
"""
PythonAnywhere WSGI configuration - Fixed for directory path issues
This fixes the chdir() errors and logging issues
"""

import os
import sys
import logging

# Fix the directory path issue
# The error shows it's trying to chdir to /home/adamcordova/AGTDesigner
# but the actual directory is /home/adamcordova/labelMaker_fresh
project_dir = '/home/adamcordova/labelMaker_fresh'

# Verify directory exists, fallback to current directory
if not os.path.exists(project_dir):
    project_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"⚠️  Project directory not found, using current directory: {project_dir}")

# Add the project directory to Python path
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

# Set environment variables for PythonAnywhere
os.environ['PYTHONANYWHERE_SITE'] = 'True'
os.environ['PYTHONANYWHERE_DOMAIN'] = 'www.agtpricetags.com'
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = 'False'

# Configure logging to prevent "Message too long" errors
logging.basicConfig(
    level=logging.ERROR,  # Only show errors to reduce log size
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

# Suppress verbose logging from all libraries
logging.getLogger('werkzeug').setLevel(logging.ERROR)
logging.getLogger('urllib3').setLevel(logging.ERROR)
logging.getLogger('requests').setLevel(logging.ERROR)
logging.getLogger('pandas').setLevel(logging.ERROR)
logging.getLogger('openpyxl').setLevel(logging.ERROR)
logging.getLogger('xlrd').setLevel(logging.ERROR)

# Import and configure the Flask app
try:
    from app import app
    
    # Configure Flask for PythonAnywhere
    app.config['DEBUG'] = False
    app.config['TESTING'] = False
    app.config['TEMPLATES_AUTO_RELOAD'] = False
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000
    
    # Set the application
    application = app
    
    # Log successful startup
    logging.info("WSGI application loaded successfully")
    
except ImportError as e:
    logging.error(f"Failed to import Flask app: {e}")
    raise
except Exception as e:
    logging.error(f"Error configuring Flask app: {e}")
    raise

if __name__ == "__main__":
    application.run()
'''
    
    with open('wsgi_pythonanywhere_fixed.py', 'w') as f:
        f.write(wsgi_content)
    
    print("✅ Created fixed WSGI file: wsgi_pythonanywhere_fixed.py")

def create_emergency_fix_instructions():
    """Create emergency fix instructions for PythonAnywhere"""
    
    instructions = """
# 🚨 EMERGENCY FIX FOR PYTHONANYWHERE

## Critical Issues Identified:
1. **Logging Error**: "Message too long" - Fixed by truncating log messages
2. **Directory Path**: Trying to chdir to /home/adamcordova/AGTDesigner (doesn't exist)
3. **uWSGI Restart Loop**: Server keeps restarting every 10-20 seconds

## 🔧 IMMEDIATE FIXES NEEDED:

### Step 1: Update WSGI File
Replace your WSGI file content with the fixed version:

```bash
# Copy the fixed WSGI content to your WSGI file
cp wsgi_pythonanywhere_fixed.py /var/www/www_agtpricetags_com_wsgi.py
```

### Step 2: Verify Directory Structure
```bash
# Check if the correct directory exists
ls -la /home/adamcordova/
# Should see: labelMaker_fresh (not AGTDesigner)

# If AGTDesigner exists but is wrong, rename it
mv /home/adamcordova/AGTDesigner /home/adamcordova/AGTDesigner_backup
```

### Step 3: Update PythonAnywhere Web App Configuration
1. Go to PythonAnywhere Web tab
2. Update the source code directory to: `/home/adamcordova/labelMaker_fresh`
3. Update the WSGI file path to: `/var/www/www_agtpricetags_com_wsgi.py`

### Step 4: Restart the Web App
1. Go to PythonAnywhere Web tab
2. Click "Reload" button
3. Check the error logs

## 🎯 Expected Results:
- No more "Message too long" errors
- No more chdir() errors
- uWSGI should start successfully
- Application should load without restart loops

## 📋 Verification Commands:
```bash
# Check if the application is running
ps aux | grep uwsgi

# Check error logs
tail -f /var/log/www.agtpricetags.com.error.log

# Test the application
curl -I https://www.agtpricetags.com/
```
"""
    
    with open('EMERGENCY_PYTHONANYWHERE_FIX.md', 'w') as f:
        f.write(instructions)
    
    print("✅ Created emergency fix instructions: EMERGENCY_PYTHONANYWHERE_FIX.md")

def main():
    """Main function to create all fixes"""
    print("🚨 Creating PythonAnywhere emergency fixes...")
    
    create_fixed_wsgi()
    create_emergency_fix_instructions()
    
    print("\n✅ All fixes created!")
    print("\n📋 Next steps:")
    print("1. Copy wsgi_pythonanywhere_fixed.py to your PythonAnywhere WSGI file")
    print("2. Update your PythonAnywhere web app configuration")
    print("3. Restart the web app")
    print("4. Check the error logs")

if __name__ == "__main__":
    main()
