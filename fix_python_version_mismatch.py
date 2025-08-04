#!/usr/bin/env python3
"""
Script to fix Python version mismatch on PythonAnywhere
"""

def print_version_mismatch_info():
    """Print information about the Python version mismatch."""
    
    print("🔧 Python Version Mismatch Issue")
    print("=" * 40)
    print()
    
    print("📋 PROBLEM IDENTIFIED:")
    print("-" * 30)
    print("• openpyxl is installed for Python 3.11")
    print("• Your app is running on Python 3.13")
    print("• This causes import errors")
    print()
    
    print("📋 SOLUTION: Install for Correct Python Version")
    print("-" * 40)
    print("Run these commands in PythonAnywhere console:")
    print()
    print("python -m pip install openpyxl")
    print("python -m pip install pandas")
    print("python -m pip install xlrd")
    print("python -m pip install python-docx")
    print("python -m pip install flask-session")
    print("python -m pip install requests")
    print("python -m pip install watchdog")
    print()

def get_version_check_commands():
    """Return commands to check Python versions."""
    
    return '''📋 CHECK PYTHON VERSIONS:
python --version
which python
python -c "import sys; print(sys.version)"
python -c "import sys; print(sys.executable)"

📋 CHECK PACKAGE LOCATIONS:
python -c "import openpyxl; print(openpyxl.__file__)"
python -c "import pandas; print(pandas.__file__)"
python -c "import flask; print(flask.__file__)"
'''

def get_fix_commands():
    """Return commands to fix the version mismatch."""
    
    return '''📋 FIX COMMANDS:

# Method 1: Use python -m pip (recommended)
python -m pip install openpyxl
python -m pip install pandas
python -m pip install xlrd
python -m pip install python-docx
python -m pip install flask-session
python -m pip install requests
python -m pip install watchdog

# Method 2: Force reinstall for current Python version
python -m pip install --force-reinstall openpyxl
python -m pip install --force-reinstall pandas

# Method 3: Check what's installed for current Python
python -m pip list | grep openpyxl
python -m pip list | grep pandas
'''

def get_test_commands():
    """Return test commands after fixing."""
    
    return '''📋 TEST AFTER FIXING:

# Test imports
python -c "import openpyxl; print('openpyxl: OK')"
python -c "import pandas; print('pandas: OK')"
python -c "from app import app; print('App: OK')"

# Test app import
cd /home/adamcordova/AGTDesigner
python -c "from app import app; print('App imported successfully')"
'''

def get_wsgi_content():
    """Return working WSGI content."""
    
    return '''#!/usr/bin/env python3
"""
Working WSGI configuration for Python 3.13
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

# Import the Flask app
from app import app
application = app

# Configure Flask for production
app.config['DEBUG'] = False
app.config['TESTING'] = False

if __name__ == "__main__":
    application.run()
'''

def main():
    """Main function."""
    
    print_version_mismatch_info()
    
    print("📄 VERSION CHECK COMMANDS:")
    print("=" * 40)
    print(get_version_check_commands())
    print()
    
    print("📄 FIX COMMANDS:")
    print("=" * 40)
    print(get_fix_commands())
    print()
    
    print("📄 TEST COMMANDS:")
    print("=" * 40)
    print(get_test_commands())
    print()
    
    print("📄 WORKING WSGI CONTENT:")
    print("=" * 40)
    print(get_wsgi_content())
    print()
    
    print("💡 Quick Fix Steps:")
    print("1. Run: python -m pip install openpyxl")
    print("2. Test: python -c 'import openpyxl; print(\"OK\")'")
    print("3. Test: python -c 'from app import app; print(\"App works\")'")
    print("4. Update WSGI file")
    print("5. Reload web app")
    print()
    
    print("🚀 Expected Result:")
    print("- Packages will be installed for Python 3.13")
    print("- App will import successfully")
    print("- WSGI will work properly")
    print("- Your web app will start normally")

if __name__ == "__main__":
    main() 