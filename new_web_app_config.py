#!/usr/bin/env python3
"""
New Web App Configuration Guide
"""

import time

def create_new_web_app_config():
    """Create a configuration guide for the new web app."""
    
    timestamp = int(time.time())
    
    print("=== NEW WEB APP CONFIGURATION ===")
    print(f"Timestamp: {timestamp}")
    print()
    
    print("=== STEP 1: BASIC CONFIGURATION ===")
    print("1. Go to Web tab")
    print("2. Click on your NEW web app")
    print("3. Set these configurations:")
    print("   - Source code: /home/adamcordova/AGTDesigner")
    print("   - Working directory: /home/adamcordova/AGTDesigner")
    print("   - Python version: 3.11")
    print()
    
    print("=== STEP 2: VIRTUAL ENVIRONMENT ===")
    print("1. Look for 'Virtual environment' section")
    print("2. Set it to: /home/adamcordova/AGTDesigner/venv_pythonanywhere")
    print("3. If that doesn't exist, create it first:")
    print("   - Go to Consoles tab")
    print("   - Start a new Bash console")
    print("   - Run: cd /home/adamcordova/AGTDesigner")
    print("   - Run: python3 -m venv venv_pythonanywhere")
    print("   - Run: source venv_pythonanywhere/bin/activate")
    print("   - Run: pip install flask pandas python-docx docxtpl openpyxl Pillow flask-cors flask-caching")
    print()
    
    print("=== STEP 3: WSGI CONFIGURATION ===")
    print("Use this WSGI file:")
    print("-" * 50)
    
    wsgi_content = f'''#!/usr/bin/env python3
import sys
import os
import time

# New web app timestamp
TIMESTAMP = {timestamp}
print(f"NEW WEB APP WSGI - TIMESTAMP: {{TIMESTAMP}}")

# Add project directory
sys.path.insert(0, '/home/adamcordova/AGTDesigner')

# Try to import the app
try:
    from app import create_app
    application = create_app()
    print(f"SUCCESS: App loaded at {{TIMESTAMP}}")
except Exception as e:
    print(f"ERROR: {{e}} at {{TIMESTAMP}}")
    from flask import Flask
    application = Flask(__name__)
    
    @application.route('/')
    def error():
        return f"Error: {{e}} - Timestamp: {{TIMESTAMP}}", 500

if __name__ == "__main__":
    application.run()'''
    
    print(wsgi_content)
    print("-" * 50)
    print()
    
    print("=== STEP 4: ALTERNATIVE SIMPLE WSGI ===")
    print("If the above doesn't work, try this:")
    print("-" * 50)
    simple_wsgi = f'''import sys
import os
sys.path.insert(0, '/home/adamcordova/AGTDesigner')
from app import create_app
application = create_app()'''
    print(simple_wsgi)
    print("-" * 50)
    print()
    
    print("=== STEP 5: SAVE AND RELOAD ===")
    print("1. Save the WSGI file")
    print("2. Go back to main web app page")
    print("3. Click RELOAD")
    print("4. Wait 2-3 minutes")
    print("5. Check error logs")
    print()
    
    print("=== STEP 6: WHAT TO LOOK FOR ===")
    print("In error logs, you should see:")
    print(f"- 'NEW WEB APP WSGI - TIMESTAMP: {timestamp}'")
    print("- Either 'SUCCESS: App loaded' or specific error message")
    print()
    
    print("=== STEP 7: TROUBLESHOOTING ===")
    print("If you get import errors:")
    print("1. Check that app.py exists in /home/adamcordova/AGTDesigner/")
    print("2. Check that app.py has create_app() function")
    print("3. Install missing dependencies in virtual environment")
    print("4. Make sure virtual environment is configured in web app settings")
    print()
    
    print("=== STEP 8: DEPENDENCIES TO INSTALL ===")
    print("In your virtual environment, install:")
    print("- flask")
    print("- pandas")
    print("- python-docx")
    print("- docxtpl")
    print("- openpyxl")
    print("- Pillow")
    print("- flask-cors")
    print("- flask-caching")
    print()
    
    print("=== QUICK COMMANDS ===")
    print("Copy and paste these in your console:")
    print()
    print("# Create virtual environment")
    print("cd /home/adamcordova/AGTDesigner")
    print("python3 -m venv venv_pythonanywhere")
    print("source venv_pythonanywhere/bin/activate")
    print()
    print("# Install dependencies")
    print("pip install flask pandas python-docx docxtpl openpyxl Pillow flask-cors flask-caching")
    print()
    print("# Verify installation")
    print("pip list")
    print("python -c 'import flask; print(flask.__version__)'")
    
    return wsgi_content, simple_wsgi

if __name__ == "__main__":
    create_new_web_app_config() 