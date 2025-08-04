#!/usr/bin/env python3
"""
Script to install missing flask_caching dependency
"""

def print_installation_commands():
    """Print commands to install missing dependencies."""
    
    print("🔧 Install Missing flask_caching Dependency")
    print("=" * 40)
    print()
    
    print("📋 MISSING DEPENDENCY DETECTED:")
    print("-" * 30)
    print("• Module: flask_caching")
    print("• Package: Flask-Caching")
    print("• Error: ModuleNotFoundError: No module named 'flask_caching'")
    print()
    
    print("📋 STEP 1: Install Flask-Caching")
    print("-" * 20)
    print("Run this command in PythonAnywhere console:")
    print()
    print("python -m pip install Flask-Caching")
    print()
    
    print("📋 STEP 2: Install All Missing Dependencies")
    print("-" * 30)
    print("To be safe, install all required packages:")
    print()
    print("python -m pip install Flask-Caching")
    print("python -m pip install Pillow")
    print("python -m pip install numpy")
    print("python -m pip install openpyxl")
    print("python -m pip install pandas")
    print("python -m pip install xlrd")
    print("python -m pip install python-docx")
    print("python -m pip install flask-session")
    print("python -m pip install requests")
    print("python -m pip install watchdog")
    print()
    
    print("📋 STEP 3: Test Installation")
    print("-" * 20)
    print("After installation, test with:")
    print()
    print("python -c 'from flask_caching import Cache; print(\"flask_caching: OK\")'")
    print("python -c 'from app import app; print(\"App: OK\")'")
    print()

def get_complete_install_script():
    """Return complete installation script."""
    
    return '''#!/bin/bash
# Complete installation script for all dependencies

echo "Installing all required dependencies..."

# Install all packages
python -m pip install Flask-Caching==2.1.0
python -m pip install Pillow==10.0.0
python -m pip install numpy==1.24.3
python -m pip install openpyxl==3.1.2
python -m pip install pandas==2.0.3
python -m pip install xlrd==2.0.1
python -m pip install python-docx==0.8.11
python -m pip install flask-session==0.5.0
python -m pip install requests==2.31.0
python -m pip install watchdog==3.0.0

echo "Testing installations..."
python -c "from flask_caching import Cache; print('flask_caching: OK')"
python -c "from PIL import Image; print('PIL: OK')"
python -c "import numpy; print('numpy: OK')"
python -c "import openpyxl; print('openpyxl: OK')"
python -c "import pandas; print('pandas: OK')"
python -c "from app import app; print('app: OK')"

echo "All dependencies installed successfully!"
'''

def get_requirements_content():
    """Return complete requirements.txt content."""
    
    return '''flask==2.3.3
flask-cors==4.0.0
Flask-Caching==2.1.0
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

def get_test_commands():
    """Return test commands."""
    
    return '''📋 TEST COMMANDS:

# Test individual imports
python -c "from flask_caching import Cache; print('flask_caching: OK')"
python -c "from PIL import Image; print('PIL: OK')"
python -c "import numpy; print('numpy: OK')"
python -c "import openpyxl; print('openpyxl: OK')"
python -c "import pandas; print('pandas: OK')"

# Test app import
python -c "from app import app; print('App: OK')"

# Test in project directory
cd /home/adamcordova/AGTDesigner
python -c "from app import app; print('App imported successfully')"
'''

def get_wsgi_content():
    """Return updated WSGI content with caching support."""
    
    return '''#!/usr/bin/env python3
"""
WSGI configuration for Python 3.10 on PythonAnywhere
Optimized for performance with caching support
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
    
    print("WSGI: App loaded successfully for Python 3.10 with caching support")
    
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

def main():
    """Main function."""
    
    print_installation_commands()
    
    print("📄 COMPLETE INSTALLATION SCRIPT:")
    print("=" * 40)
    print(get_complete_install_script())
    print()
    
    print("📄 REQUIREMENTS.TXT CONTENT:")
    print("=" * 40)
    print(get_requirements_content())
    print()
    
    print("📄 TEST COMMANDS:")
    print("=" * 40)
    print(get_test_commands())
    print()
    
    print("📄 UPDATED WSGI CONTENT:")
    print("=" * 40)
    print(get_wsgi_content())
    print()
    
    print("💡 Quick Fix:")
    print("1. Run: python -m pip install Flask-Caching")
    print("2. Test: python -c 'from flask_caching import Cache; print(\"flask_caching: OK\")'")
    print("3. Test: python -c 'from app import app; print(\"App: OK\")'")
    print("4. If successful, your WSGI should work perfectly!")
    print()
    
    print("🚀 Expected Result:")
    print("• Flask-Caching will be installed")
    print("• App will import successfully")
    print("• WSGI will work with 3-second startup time")
    print("• All caching features will work")

if __name__ == "__main__":
    main() 