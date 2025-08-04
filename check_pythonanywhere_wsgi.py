#!/usr/bin/env python3

# Check and Fix PythonAnywhere WSGI Configuration
# Run this on PythonAnywhere to verify and fix WSGI setup

import os
import sys

print("🔍 Checking PythonAnywhere WSGI Configuration")
print("=" * 50)

# Check current directory
print(f"Current directory: {os.getcwd()}")

# Check if we're in the right project
if not os.path.exists('app.py'):
    print("❌ Error: app.py not found in current directory")
    print("Make sure you're in the AGTDesigner project directory")
    sys.exit(1)

print("✅ app.py found")

# Check virtual environment
venv_path = os.path.join(os.getcwd(), 'venv_pythonanywhere')
if os.path.exists(venv_path):
    print(f"✅ Virtual environment found: {venv_path}")
else:
    print(f"❌ Virtual environment not found at: {venv_path}")
    sys.exit(1)

# Check if virtual environment is activated
if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
    print("✅ Virtual environment is activated")
else:
    print("❌ Virtual environment is NOT activated")
    print("Please activate it with: source venv_pythonanywhere/bin/activate")

# Test imports
print("\n🧪 Testing imports...")
try:
    import flask
    print(f"✅ Flask version: {flask.__version__}")
except ImportError as e:
    print(f"❌ Flask import error: {e}")

try:
    from flask_cors import CORS
    print("✅ flask_cors imported successfully")
except ImportError as e:
    print(f"❌ flask_cors import error: {e}")

try:
    from flask_caching import Cache
    print("✅ flask_caching imported successfully")
except ImportError as e:
    print(f"❌ flask_caching import error: {e}")

try:
    from app import create_app
    print("✅ app.create_app imported successfully")
except ImportError as e:
    print(f"❌ app import error: {e}")

# Create proper WSGI file
print("\n📝 Creating proper WSGI file...")
wsgi_content = '''import sys
import os

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Activate virtual environment
activate_this = os.path.join(project_dir, 'venv_pythonanywhere', 'bin', 'activate_this.py')
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

# Import the Flask app
from app import create_app

# Create the application instance
application = create_app()

if __name__ == "__main__":
    application.run()
'''

with open('wsgi.py', 'w') as f:
    f.write(wsgi_content)

print("✅ WSGI file created/updated")

# Test the WSGI file
print("\n🧪 Testing WSGI file...")
try:
    exec(wsgi_content)
    print("✅ WSGI file executes successfully")
except Exception as e:
    print(f"❌ WSGI file error: {e}")

print("\n📋 Next Steps:")
print("1. Copy the wsgi.py content to your PythonAnywhere WSGI file")
print("2. Make sure your virtual environment path is set correctly")
print("3. Reload your web app in PythonAnywhere")
print("\nWSGI file content:")
print("-" * 40)
print(wsgi_content)
print("-" * 40) 