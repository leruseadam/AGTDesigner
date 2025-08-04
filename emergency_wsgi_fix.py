#!/usr/bin/env python3
"""
Emergency WSGI fix for PythonAnywhere.
This is a minimal, bulletproof WSGI file that should work regardless of the environment.
"""

import sys
import os

# Print diagnostic information
print("=== WSGI Diagnostic Information ===")
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print(f"Current working directory: {os.getcwd()}")
print(f"sys.path: {sys.path[:5]}...")  # Show first 5 entries

# Add multiple possible project paths
possible_paths = [
    '/home/adamcordova/AGTDesigner',
    '/home/adamcordova/labelMaker_ newgui BACKUP 6.24 copy 17',
    '/home/adamcordova/AGTDesigner/labelMaker_ newgui BACKUP 6.24 copy 17',
    os.path.dirname(os.path.abspath(__file__))
]

for path in possible_paths:
    if os.path.exists(path):
        print(f"✓ Found project directory: {path}")
        if path not in sys.path:
            sys.path.insert(0, path)
            print(f"  Added to sys.path")
    else:
        print(f"✗ Path not found: {path}")

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
        <p>sys.path: {sys.path}</p>
        """, 500

if __name__ == "__main__":
    application.run() 