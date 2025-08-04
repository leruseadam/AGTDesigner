#!/usr/bin/env python3
"""
Simple test WSGI file for debugging PythonAnywhere deployment
"""

import sys
import os

print("🔍 === PYTHONANYWHERE WSGI DEBUG ===")
print(f"🔍 Current working directory: {os.getcwd()}")
print(f"🔍 Script location: {os.path.abspath(__file__)}")
print(f"🔍 Python executable: {sys.executable}")
print(f"🔍 Python version: {sys.version}")

# Add the correct project directory to Python path
project_dir = '/home/adamcordova/AGTDesigner'
print(f"🔍 Adding project directory: {project_dir}")

if os.path.exists(project_dir):
    sys.path.insert(0, project_dir)
    print(f"✅ Project directory exists and added to path")
else:
    print(f"❌ Project directory does not exist: {project_dir}")

# Try to add virtual environment to Python path
venv_path = os.path.join(project_dir, 'venv_pythonanywhere')
venv_site_packages = os.path.join(venv_path, 'lib', 'python3.11', 'site-packages')

if os.path.exists(venv_site_packages):
    sys.path.insert(0, venv_site_packages)
    print(f"✅ Virtual environment site-packages added: {venv_site_packages}")
else:
    print(f"⚠️  Virtual environment site-packages not found at: {venv_site_packages}")

print(f"🔍 Python path: {sys.path[:3]}")

# Try to import Flask
try:
    import flask
    print(f"✅ Flask imported successfully: {flask.__version__}")
except ImportError as e:
    print(f"❌ Flask import failed: {e}")

# Try to import the app
try:
    from app import create_app
    print("✅ Successfully imported Flask app")
    
    # Create the application instance
    application = create_app()
    print("✅ Application created successfully")
    
except ImportError as e:
    print(f"❌ Error importing Flask app: {e}")
    print("Available packages:")
    for path in sys.path[:5]:
        print(f"  - {path}")
    # Create a simple fallback application
    from flask import Flask
    application = Flask(__name__)
    
    @application.route('/')
    def hello():
        return f"""
        <h1>PythonAnywhere Debug Page</h1>
        <p>Project directory: {project_dir}</p>
        <p>Virtual environment: {venv_path}</p>
        <p>Python path: {sys.path[:3]}</p>
        <p>Flask version: {flask.__version__ if 'flask' in sys.modules else 'Not imported'}</p>
        <p>Error: {e}</p>
        """
    
except Exception as e:
    print(f"❌ Error creating application: {e}")
    # Create a simple fallback application
    from flask import Flask
    application = Flask(__name__)
    
    @application.route('/')
    def hello():
        return f"""
        <h1>PythonAnywhere Debug Page</h1>
        <p>Project directory: {project_dir}</p>
        <p>Virtual environment: {venv_path}</p>
        <p>Python path: {sys.path[:3]}</p>
        <p>Error: {e}</p>
        """

print("🎉 WSGI file loaded successfully!")

if __name__ == "__main__":
    application.run() 