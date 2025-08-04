#!/usr/bin/env python3
"""
VERIFICATION WSGI - UNIQUE ID: 1754283391
This will help us verify which WSGI file PythonAnywhere is actually using.
"""

import sys
import os
import time

# Unique identifier to verify this file is being used
UNIQUE_ID = 1754283391
TIMESTAMP = 1754283391

print(f"VERIFICATION WSGI LOADED - ID: {UNIQUE_ID} - TIMESTAMP: {TIMESTAMP}")
print(f"File path: {__file__}")
print(f"Current directory: {os.getcwd()}")

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
        <h1>Verification WSGI - ID: {UNIQUE_ID}</h1>
        <p>Timestamp: {TIMESTAMP}</p>
        <p>Error: {e}</p>
        <p>File: {__file__}</p>
        <p>Directory: {os.getcwd()}</p>
        """, 500

if __name__ == "__main__":
    application.run()
