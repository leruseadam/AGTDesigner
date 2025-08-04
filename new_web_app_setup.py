#!/usr/bin/env python3
"""
New Web App Setup Guide
This will help you create a completely new web app to bypass the caching issue.
"""

import time

def create_new_web_app_guide():
    """Create a guide for setting up a new web app."""
    
    timestamp = int(time.time())
    
    print("=== NEW WEB APP SETUP GUIDE ===")
    print(f"Timestamp: {timestamp}")
    print()
    
    print("=== STEP-BY-STEP INSTRUCTIONS ===")
    print("1. Go to PythonAnywhere dashboard")
    print("2. Navigate to Web tab")
    print("3. Click 'Add a new web app'")
    print("4. Choose 'Manual configuration'")
    print("5. Choose 'Python 3.11'")
    print("6. Set Source code to: /home/adamcordova/AGTDesigner")
    print("7. Set Working directory to: /home/adamcordova/AGTDesigner")
    print("8. Click 'Next'")
    print("9. Use this minimal WSGI:")
    print()
    
    minimal_wsgi = f'''import sys
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
    
    print(minimal_wsgi)
    print()
    
    print("=== ALTERNATIVE: EVEN SIMPLER WSGI ===")
    print("If the above doesn't work, try this:")
    print()
    
    simpler_wsgi = f'''import sys
import os
sys.path.insert(0, '/home/adamcordova/AGTDesigner')
from app import create_app
application = create_app()'''
    
    print(simpler_wsgi)
    print()
    
    print("=== WHAT TO EXPECT ===")
    print("After setting up the new web app:")
    print("1. You should see 'NEW WEB APP WSGI - TIMESTAMP: {timestamp}' in error logs")
    print("2. Either 'SUCCESS: App loaded' or a specific error message")
    print("3. Your website should either work or show a specific error")
    print()
    
    print("=== IF THE NEW WEB APP ALSO FAILS ===")
    print("If you still get errors:")
    print("1. Check that your project directory exists: /home/adamcordova/AGTDesigner")
    print("2. Check that app.py exists in that directory")
    print("3. Check that app.py has a create_app() function")
    print("4. Install missing dependencies in your virtual environment")
    print()
    
    print("=== DEPENDENCIES TO CHECK ===")
    print("Make sure these are installed in your PythonAnywhere virtual environment:")
    print("- flask")
    print("- pandas")
    print("- python-docx")
    print("- docxtpl")
    print("- openpyxl")
    print("- Pillow")
    print("- flask-cors")
    print("- flask-caching")
    print()
    
    print("=== INSTALL DEPENDENCIES ===")
    print("If dependencies are missing:")
    print("1. Go to Consoles tab in PythonAnywhere")
    print("2. Start a new console")
    print("3. Activate your virtual environment:")
    print("   workon your-virtual-environment-name")
    print("4. Install dependencies:")
    print("   pip install flask pandas python-docx docxtpl openpyxl Pillow flask-cors flask-caching")
    
    return minimal_wsgi, simpler_wsgi

if __name__ == "__main__":
    create_new_web_app_guide() 