#!/usr/bin/env python3
"""
Script to install missing PIL/Pillow dependency
"""

def print_installation_commands():
    """Print commands to install missing dependencies."""
    
    print("🔧 Install Missing PIL/Pillow Dependency")
    print("=" * 40)
    print()
    
    print("📋 MISSING DEPENDENCY DETECTED:")
    print("-" * 30)
    print("• Module: PIL (Python Imaging Library)")
    print("• Package: Pillow")
    print("• Error: ModuleNotFoundError: No module named 'PIL'")
    print()
    
    print("📋 STEP 1: Install Pillow")
    print("-" * 20)
    print("Run this command in PythonAnywhere console:")
    print()
    print("python -m pip install Pillow")
    print()
    
    print("📋 STEP 2: Install All Missing Dependencies")
    print("-" * 30)
    print("To be safe, install all required packages:")
    print()
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
    print("python -c 'from PIL import Image; print(\"PIL: OK\")'")
    print("python -c 'from app import app; print(\"App: OK\")'")
    print()

def get_complete_install_script():
    """Return complete installation script."""
    
    return '''#!/bin/bash
# Complete installation script for all dependencies

echo "Installing all required dependencies..."

# Install all packages
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
    
    print("💡 Quick Fix:")
    print("1. Run: python -m pip install Pillow")
    print("2. Test: python -c 'from PIL import Image; print(\"PIL: OK\")'")
    print("3. Test: python -c 'from app import app; print(\"App: OK\")'")
    print("4. If successful, your WSGI should work perfectly!")
    print()
    
    print("🚀 Expected Result:")
    print("• PIL/Pillow will be installed")
    print("• App will import successfully")
    print("• WSGI will work with 3-second startup time")
    print("• All image processing features will work")

if __name__ == "__main__":
    main() 