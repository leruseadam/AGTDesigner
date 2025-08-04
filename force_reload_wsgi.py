#!/usr/bin/env python3
"""
Force reload WSGI for PythonAnywhere.
This file includes a timestamp to force reloading.
"""

import sys
import os
import time

# Force reload by including timestamp
TIMESTAMP = 1754283094
print(f"=== WSGI RELOAD FORCED - TIMESTAMP: {TIMESTAMP} ===")
print(f"Current time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print(f"Current working directory: {os.getcwd()}")
print(f"sys.path: {sys.path[:3]}...")

# Add project directory
project_dir = '/home/adamcordova/AGTDesigner'
print(f"Checking project directory: {project_dir}")

if os.path.exists(project_dir):
    print(f"✓ Project directory exists")
    if project_dir not in sys.path:
        sys.path.insert(0, project_dir)
        print(f"  Added to sys.path")
    else:
        print(f"  Already in sys.path")
else:
    print(f"✗ Project directory does not exist")

# Check if app.py exists
app_path = os.path.join(project_dir, 'app.py')
if os.path.exists(app_path):
    print(f"✓ app.py exists at {app_path}")
else:
    print(f"✗ app.py does not exist at {app_path}")

# Try to import Flask
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
        <h1>WSGI Diagnostic Page - Timestamp: {TIMESTAMP}</h1>
        <p>Import error: {e}</p>
        <p>Python version: {sys.version}</p>
        <p>Python executable: {sys.executable}</p>
        <p>Current directory: {os.getcwd()}</p>
        <p>Project directory: {project_dir}</p>
        <p>app.py exists: {os.path.exists(app_path)}</p>
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
        <h1>WSGI Error Page - Timestamp: {TIMESTAMP}</h1>
        <p>Unexpected error: {e}</p>
        <p>Python version: {sys.version}</p>
        <p>Python executable: {sys.executable}</p>
        <p>Current directory: {os.getcwd()}</p>
        <p>Project directory: {project_dir}</p>
        """, 500

print(f"=== WSGI Setup Complete - Timestamp: {TIMESTAMP} ===")

if __name__ == "__main__":
    application.run()
