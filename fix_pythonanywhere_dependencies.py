#!/usr/bin/env python3
"""
Script to fix missing dependencies on PythonAnywhere
"""

def print_installation_instructions():
    """Print instructions for installing missing dependencies."""
    
    print("🔧 Fix Missing Dependencies on PythonAnywhere")
    print("=" * 50)
    print()
    
    print("📋 STEP 1: Install Missing Dependencies")
    print("-" * 40)
    print("1. Go to PythonAnywhere dashboard")
    print("2. Click 'Consoles' tab")
    print("3. Start a new console")
    print("4. Run these commands:")
    print()
    print("   pip install flask-cors")
    print("   pip install pandas")
    print("   pip install openpyxl")
    print("   pip install xlrd")
    print("   pip install python-docx")
    print("   pip install flask-session")
    print("   pip install requests")
    print("   pip install watchdog")
    print()
    
    print("📋 STEP 2: Verify Installation")
    print("-" * 40)
    print("After installation, test with:")
    print("   python -c 'import flask_cors; print(\"flask_cors installed\")'")
    print("   python -c 'from app import app; print(\"App imported successfully\")'")
    print()
    
    print("📋 STEP 3: Update WSGI File")
    print("-" * 40)
    print("Once dependencies are installed, update your WSGI file with:")
    print()
    print("import sys")
    print("sys.path.insert(0, '/home/adamcordova/AGTDesigner')")
    print("from app import app")
    print("application = app")
    print()

def get_requirements_content():
    """Return the requirements.txt content."""
    
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

def get_install_script():
    """Return a bash script to install dependencies."""
    
    return '''#!/bin/bash
# Install dependencies on PythonAnywhere

echo "Installing dependencies..."

# Activate virtual environment (if using one)
# source /home/adamcordova/venv/bin/activate

# Install required packages
pip install flask-cors==4.0.0
pip install pandas==2.0.3
pip install openpyxl==3.1.2
pip install xlrd==2.0.1
pip install python-docx==0.8.11
pip install flask-session==0.5.0
pip install requests==2.31.0
pip install watchdog==3.0.0
pip install numpy==1.24.3
pip install Pillow==10.0.0

echo "Dependencies installed successfully!"

# Test imports
echo "Testing imports..."
python -c "import flask_cors; print('flask_cors: OK')"
python -c "import pandas; print('pandas: OK')"
python -c "import openpyxl; print('openpyxl: OK')"
python -c "from app import app; print('app: OK')"

echo "All tests passed!"
'''

def main():
    """Main function."""
    
    print_installation_instructions()
    
    print("📄 REQUIREMENTS.TXT CONTENT:")
    print("=" * 40)
    print(get_requirements_content())
    print()
    
    print("📄 INSTALL SCRIPT:")
    print("=" * 40)
    print(get_install_script())
    print()
    
    print("💡 Alternative: Use requirements.txt")
    print("1. Create requirements.txt file in PythonAnywhere")
    print("2. Copy the requirements content above")
    print("3. Run: pip install -r requirements.txt")
    print()
    
    print("✅ After installing dependencies:")
    print("1. Test the app import again")
    print("2. Update your WSGI file")
    print("3. Reload your web app")

if __name__ == "__main__":
    main() 