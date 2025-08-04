#!/usr/bin/env python3
"""
Final, bulletproof WSGI file for PythonAnywhere.
This should work regardless of the environment setup.
"""

import sys
import os

# Print diagnostic information to error logs
print("=== WSGI Startup Diagnostic ===")
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print(f"Current working directory: {os.getcwd()}")

# Add the project directory to Python path
project_dir = '/home/adamcordova/AGTDesigner'
if os.path.exists(project_dir):
    print(f"✓ Found project directory: {project_dir}")
    if project_dir not in sys.path:
        sys.path.insert(0, project_dir)
        print(f"  Added to sys.path")
else:
    print(f"✗ Project directory not found: {project_dir}")

# Try to import Flask first
try:
    import flask
    print(f"✓ Flask version: {flask.__version__}")
except ImportError as e:
    print(f"✗ Flask import error: {e}")

# Try to import the app
try:
    from app import create_app
    print("✓ Successfully imported create_app")
    application = create_app()
    print("✓ Successfully created application")
except ImportError as e:
    print(f"✗ Import error: {e}")
    # Create a minimal fallback app
    from flask import Flask
    application = Flask(__name__)
    
    @application.route('/')
    def error():
        return f"""
        <h1>WSGI Diagnostic Page</h1>
        <p>Import error: {e}</p>
        <p>Python version: {sys.version}</p>
        <p>Python executable: {sys.executable}</p>
        <p>Current directory: {os.getcwd()}</p>
        <p>Project directory: {project_dir}</p>
        <p>sys.path: {sys.path}</p>
        """, 500
except Exception as e:
    print(f"✗ Unexpected error: {e}")
    # Create a minimal fallback app
    from flask import Flask
    application = Flask(__name__)
    
    @application.route('/')
    def error():
        return f"""
        <h1>WSGI Error Page</h1>
        <p>Unexpected error: {e}</p>
        <p>Python version: {sys.version}</p>
        <p>Python executable: {sys.executable}</p>
        <p>Current directory: {os.getcwd()}</p>
        <p>Project directory: {project_dir}</p>
        """, 500

print("=== WSGI Setup Complete ===")

if __name__ == "__main__":
    application.run() 