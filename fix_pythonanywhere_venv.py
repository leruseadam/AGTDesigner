#!/usr/bin/env python3
"""
Script to fix virtual environment and dependencies on PythonAnywhere
"""

def print_venv_fix_instructions():
    """Print instructions for fixing virtual environment issues."""
    
    print("🔧 Fix PythonAnywhere Virtual Environment & Dependencies")
    print("=" * 60)
    print()
    
    print("📋 STEP 1: Check Your Virtual Environment")
    print("-" * 50)
    print("1. In PythonAnywhere console, run:")
    print("   which python")
    print("   which pip")
    print("   echo $VIRTUAL_ENV")
    print()
    
    print("📋 STEP 2: Install Dependencies in Virtual Environment")
    print("-" * 50)
    print("Make sure you're in your virtual environment, then run:")
    print()
    print("   # Method 1: Direct pip install")
    print("   pip install flask-cors")
    print("   pip install pandas openpyxl xlrd python-docx flask-session requests watchdog")
    print()
    print("   # Method 2: Using python -m pip")
    print("   python -m pip install flask-cors")
    print("   python -m pip install pandas openpyxl xlrd python-docx flask-session requests watchdog")
    print()
    
    print("📋 STEP 3: Alternative - Install System-Wide")
    print("-" * 50)
    print("If virtual environment doesn't work, try system-wide install:")
    print("   pip3 install flask-cors")
    print("   pip3 install pandas openpyxl xlrd python-docx flask-session requests watchdog")
    print()
    
    print("📋 STEP 4: Check PythonAnywhere Web App Settings")
    print("-" * 50)
    print("1. Go to 'Web' tab in PythonAnywhere")
    print("2. Click on your web app")
    print("3. Check 'Code' section")
    print("4. Look for 'Python version' setting")
    print("5. Make sure it matches your virtual environment")
    print()

def get_venv_activation_script():
    """Return virtual environment activation script."""
    
    return '''#!/bin/bash
# Activate virtual environment and install dependencies

echo "Current Python: $(which python)"
echo "Current pip: $(which pip)"
echo "Virtual env: $VIRTUAL_ENV"

# Activate virtual environment (if not already activated)
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Activating virtual environment..."
    source /home/adamcordova/venv/bin/activate
    echo "Virtual env activated: $VIRTUAL_ENV"
fi

# Install dependencies
echo "Installing dependencies..."
python -m pip install --upgrade pip
python -m pip install flask-cors==4.0.0
python -m pip install pandas==2.0.3
python -m pip install openpyxl==3.1.2
python -m pip install xlrd==2.0.1
python -m pip install python-docx==0.8.11
python -m pip install flask-session==0.5.0
python -m pip install requests==2.31.0
python -m pip install watchdog==3.0.0

echo "Testing installations..."
python -c "import flask_cors; print('flask_cors: OK')"
python -c "import pandas; print('pandas: OK')"
python -c "from app import app; print('app: OK')"

echo "Installation complete!"
'''

def get_alternative_wsgi_content():
    """Return alternative WSGI content that doesn't require flask_cors."""
    
    return '''#!/usr/bin/env python3
"""
Alternative WSGI configuration without flask_cors dependency
"""

import sys
import os

# Add project path
sys.path.insert(0, '/home/adamcordova/AGTDesigner')

# Set environment variables
os.environ['PYTHONANYWHERE_SITE'] = 'True'
os.environ['DISABLE_DEFAULT_FILE_LOADING'] = 'True'
os.environ['LAZY_LOADING_ENABLED'] = 'True'

try:
    # Try to import app without flask_cors
    from app import app
    
    # Remove CORS if it's causing issues
    if hasattr(app, 'config'):
        app.config['DEBUG'] = False
        app.config['TESTING'] = False
    
    application = app
    print("WSGI: App loaded successfully")
    
except ImportError as e:
    print(f"WSGI: Import error - {e}")
    # Create a minimal fallback app
    from flask import Flask
    application = Flask(__name__)
    application.config['DEBUG'] = False
    print("WSGI: Using fallback Flask app")
    
except Exception as e:
    print(f"WSGI: Other error - {e}")
    raise
'''

def get_app_modification_instructions():
    """Return instructions for temporarily modifying app.py."""
    
    return '''# TEMPORARY FIX: Modify app.py to handle missing flask_cors

# In your app.py file, replace this line:
# from flask_cors import CORS

# With this conditional import:
try:
    from flask_cors import CORS
    cors_enabled = True
except ImportError:
    print("Warning: flask_cors not available, CORS disabled")
    cors_enabled = False

# Then modify the CORS initialization:
if cors_enabled:
    CORS(app)
else:
    print("CORS disabled due to missing flask_cors module")
'''

def main():
    """Main function."""
    
    print_venv_fix_instructions()
    
    print("📄 VIRTUAL ENVIRONMENT ACTIVATION SCRIPT:")
    print("=" * 50)
    print(get_venv_activation_script())
    print()
    
    print("📄 ALTERNATIVE WSGI CONTENT (if dependencies fail):")
    print("=" * 50)
    print(get_alternative_wsgi_content())
    print()
    
    print("📄 TEMPORARY APP.PY MODIFICATION:")
    print("=" * 50)
    print(get_app_modification_instructions())
    print()
    
    print("💡 Quick Fix Options:")
    print("1. Try: python -m pip install flask-cors")
    print("2. Try: pip3 install flask-cors (system-wide)")
    print("3. Temporarily modify app.py to handle missing flask_cors")
    print("4. Use the alternative WSGI content above")
    print()
    
    print("🔍 Debug Commands:")
    print("   which python")
    print("   which pip")
    print("   python --version")
    print("   pip list | grep flask")

if __name__ == "__main__":
    main() 