#!/usr/bin/env python3
"""
Script to install missing dependencies on PythonAnywhere
"""

def print_installation_commands():
    """Print the exact commands to run."""
    
    print("🔧 Install Missing Dependencies on PythonAnywhere")
    print("=" * 50)
    print()
    
    print("📋 STEP 1: Install Missing Packages")
    print("-" * 40)
    print("Run these commands in your PythonAnywhere console:")
    print()
    print("pip install openpyxl")
    print("pip install pandas")
    print("pip install xlrd")
    print("pip install python-docx")
    print("pip install flask-session")
    print("pip install requests")
    print("pip install watchdog")
    print()
    
    print("📋 STEP 2: Verify Installation")
    print("-" * 40)
    print("After installation, test with:")
    print("python -c 'import openpyxl; print(\"openpyxl: OK\")'")
    print("python -c 'import pandas; print(\"pandas: OK\")'")
    print("python -c 'from app import app; print(\"App imported successfully\")'")
    print()
    
    print("📋 STEP 3: Test App Import")
    print("-" * 40)
    print("cd /home/adamcordova/AGTDesigner")
    print("python -c 'from app import app; print(\"App works!\")'")
    print()

def get_quick_install_script():
    """Return a quick install script."""
    
    return '''#!/bin/bash
# Quick install script for PythonAnywhere

echo "Installing missing dependencies..."

# Install all required packages
pip install openpyxl==3.1.2
pip install pandas==2.0.3
pip install xlrd==2.0.1
pip install python-docx==0.8.11
pip install flask-session==0.5.0
pip install requests==2.31.0
pip install watchdog==3.0.0

echo "Testing installations..."
python -c "import openpyxl; print('openpyxl: OK')"
python -c "import pandas; print('pandas: OK')"
python -c "from app import app; print('app: OK')"

echo "Installation complete!"
'''

def get_requirements_content():
    """Return requirements.txt content."""
    
    return '''flask==2.3.3
flask-cors==4.0.0
pandas==2.0.3
openpyxl==3.1.2
xlrd==2.0.1
python-docx==0.8.11
flask-session==0.5.0
requests==2.31.0
watchdog==3.0.0
numpy==1.24.3
Pillow==10.0.0
'''

def get_working_wsgi_content():
    """Return working WSGI content after dependencies are installed."""
    
    return '''#!/usr/bin/env python3
"""
Working WSGI configuration after dependencies are installed
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
    
    print_installation_commands()
    
    print("📄 QUICK INSTALL SCRIPT:")
    print("=" * 40)
    print(get_quick_install_script())
    print()
    
    print("📄 REQUIREMENTS.TXT CONTENT:")
    print("=" * 40)
    print(get_requirements_content())
    print()
    
    print("📄 WORKING WSGI CONTENT (after dependencies installed):")
    print("=" * 40)
    print(get_working_wsgi_content())
    print()
    
    print("💡 Quick Fix:")
    print("1. Run: pip install openpyxl")
    print("2. Test: python -c 'import openpyxl; print(\"OK\")'")
    print("3. Test: python -c 'from app import app; print(\"App works\")'")
    print("4. Update WSGI file with the working content above")
    print("5. Reload your web app")
    print()
    
    print("🚀 Expected Result:")
    print("- openpyxl will be installed")
    print("- App will import successfully")
    print("- WSGI will work properly")
    print("- Your web app will start normally")

if __name__ == "__main__":
    main() 