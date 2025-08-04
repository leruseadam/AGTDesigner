#!/usr/bin/env python3
"""
Clean working WSGI for PythonAnywhere.
This file is properly formatted with correct indentation.
"""

import sys
import os
import time

# Force reload with unique ID
UNIQUE_ID = 1754283450
TIMESTAMP = int(time.time())

print(f"CLEAN WSGI LOADED - ID: {UNIQUE_ID} - TIMESTAMP: {TIMESTAMP}")
print(f"File: {__file__}")
print(f"Directory: {os.getcwd()}")

# Add project directory
project_dir = '/home/adamcordova/AGTDesigner'
sys.path.insert(0, project_dir)

# Try to import the app
try:
    from app import create_app
    application = create_app()
    print(f"✓ SUCCESS: App loaded - ID: {UNIQUE_ID}")
except Exception as e:
    print(f"✗ ERROR: {e} - ID: {UNIQUE_ID}")
    from flask import Flask
    application = Flask(__name__)
    
    @application.route('/')
    def error():
        return f"""
        <h1>Clean WSGI - ID: {UNIQUE_ID}</h1>
        <p>Timestamp: {TIMESTAMP}</p>
        <p>Error: {e}</p>
        <p>File: {__file__}</p>
        <p>Directory: {os.getcwd()}</p>
        """, 500

if __name__ == "__main__":
    application.run() 