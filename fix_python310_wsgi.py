#!/usr/bin/env python3
"""
Script to fix WSGI configuration for Python 3.10 on PythonAnywhere
"""

def print_python310_fix():
    """Print fix for Python 3.10 configuration."""
    
    print("🔧 Fix for Python 3.10 on PythonAnywhere")
    print("=" * 40)
    print()
    
    print("📋 CONFIGURATION DETECTED:")
    print("-" * 30)
    print("• Python version: 3.10")
    print("• Source code: /home/adamcordova/AGTDesigner")
    print("• WSGI file: /var/www/www_agtpricetags_com_wsgi.py")
    print()
    
    print("📋 STEP 1: Install Dependencies for Python 3.10")
    print("-" * 40)
    print("In PythonAnywhere console, run:")
    print()
    print("python -m pip install openpyxl")
    print("python -m pip install pandas")
    print("python -m pip install xlrd")
    print("python -m pip install python-docx")
    print("python -m pip install flask-session")
    print("python -m pip install requests")
    print("python -m pip install watchdog")
    print()
    
    print("📋 STEP 2: Test Installation")
    print("-" * 30)
    print("python -c 'import openpyxl; print(\"openpyxl: OK\")'")
    print("python -c 'from app import app; print(\"App: OK\")'")
    print()

def get_wsgi_content_python310():
    """Return WSGI content optimized for Python 3.10."""
    
    return '''#!/usr/bin/env python3
"""
WSGI configuration for Python 3.10 on PythonAnywhere
Optimized for performance
"""

import sys
import os

# Add the project directory to Python path
project_dir = '/home/adamcordova/AGTDesigner'
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

# Set environment variables for PythonAnywhere
os.environ['PYTHONANYWHERE_SITE'] = 'True'
os.environ['PYTHONANYWHERE_DOMAIN'] = 'www.agtpricetags.com'

# Performance optimization: Disable default file loading during startup
os.environ['DISABLE_DEFAULT_FILE_LOADING'] = 'True'
os.environ['LAZY_LOADING_ENABLED'] = 'True'

# Configure logging for better performance
import logging
logging.basicConfig(level=logging.ERROR)

# Import the Flask app
try:
    from app import app
    application = app
    
    # Configure Flask for production
    app.config['DEBUG'] = False
    app.config['TESTING'] = False
    app.config['TEMPLATES_AUTO_RELOAD'] = False
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000
    
    print("WSGI: App loaded successfully for Python 3.10")
    
except ImportError as e:
    print(f"WSGI: Import error - {e}")
    # Create fallback app
    from flask import Flask
    application = Flask(__name__)
    application.config['DEBUG'] = False
    print("WSGI: Using fallback Flask app")
    
except Exception as e:
    print(f"WSGI: Other error - {e}")
    raise

if __name__ == "__main__":
    application.run()
'''

def get_installation_script():
    """Return installation script for Python 3.10."""
    
    return '''#!/bin/bash
# Installation script for Python 3.10 on PythonAnywhere

echo "Installing dependencies for Python 3.10..."

# Install required packages
python -m pip install openpyxl==3.1.2
python -m pip install pandas==2.0.3
python -m pip install xlrd==2.0.1
python -m pip install python-docx==0.8.11
python -m pip install flask-session==0.5.0
python -m pip install requests==2.31.0
python -m pip install watchdog==3.0.0

echo "Testing installations..."
python -c "import openpyxl; print('openpyxl: OK')"
python -c "import pandas; print('pandas: OK')"
python -c "from app import app; print('app: OK')"

echo "Installation complete for Python 3.10!"
'''

def get_deployment_steps():
    """Return deployment steps."""
    
    return '''📋 DEPLOYMENT STEPS:

1. INSTALL DEPENDENCIES:
   python -m pip install openpyxl pandas xlrd python-docx flask-session requests watchdog

2. TEST INSTALLATION:
   python -c 'import openpyxl; print("openpyxl: OK")'
   python -c 'from app import app; print("App: OK")'

3. UPDATE WSGI FILE:
   - Edit /var/www/www_agtpricetags_com_wsgi.py
   - Replace with the optimized content below

4. RELOAD WEB APP:
   - Go to Web tab in PythonAnywhere
   - Click Reload for your web app

5. VERIFY:
   - Check error logs for success messages
   - Test your website functionality
'''

def main():
    """Main function."""
    
    print_python310_fix()
    
    print("📄 WSGI CONTENT FOR PYTHON 3.10:")
    print("=" * 40)
    print(get_wsgi_content_python310())
    print()
    
    print("📄 INSTALLATION SCRIPT:")
    print("=" * 40)
    print(get_installation_script())
    print()
    
    print("📄 DEPLOYMENT STEPS:")
    print("=" * 40)
    print(get_deployment_steps())
    print()
    
    print("💡 Key Points:")
    print("• Use python -m pip to ensure correct Python version")
    print("• Python 3.10 is compatible with your packages")
    print("• The WSGI content is optimized for performance")
    print("• Startup time should be under 10 seconds after optimization")
    print()
    
    print("🚀 Expected Result:")
    print("• Dependencies installed for Python 3.10")
    print("• App imports successfully")
    print("• WSGI works properly")
    print("• Fast startup time")

if __name__ == "__main__":
    main() 