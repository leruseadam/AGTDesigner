#!/usr/bin/env python3
"""
EMERGENCY WSGI OVERRIDE
This will force PythonAnywhere to use the correct WSGI file.
"""

import sys
import os
import time

# Force reload with unique timestamp
TIMESTAMP = int(time.time())
print(f"EMERGENCY WSGI OVERRIDE - TIMESTAMP: {TIMESTAMP}")

# Add project directory
project_dir = '/home/adamcordova/AGTDesigner'
sys.path.insert(0, project_dir)

# Try to import the app
try:
    from app import create_app
    application = create_app()
    print(f"✓ SUCCESS: App loaded with timestamp {TIMESTAMP}")
except Exception as e:
    print(f"✗ ERROR: {e}")
    from flask import Flask
    application = Flask(__name__)
    
    @application.route('/')
    def error():
        return f"EMERGENCY WSGI - Timestamp: {TIMESTAMP} - Error: {e}", 500

if __name__ == "__main__":
    application.run() 