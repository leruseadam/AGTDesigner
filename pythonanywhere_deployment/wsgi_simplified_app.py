#!/usr/bin/env python3
"""
WSGI file for simplified app deployment on PythonAnywhere.
"""

import sys
import os

# Force unbuffered output
os.environ['PYTHONUNBUFFERED'] = '1'

# Add project directory to path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Set environment variables
os.environ['PYTHONANYWHERE'] = 'true'
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = 'False'

try:
    # Import the simplified app
    from app_simplified import application
    print("Simplified app imported successfully")
except ImportError as e:
    print(f"Import error: {e}")
    # Fallback to basic Flask app
    from flask import Flask
    application = Flask(__name__)
    
    @application.route('/')
    def index():
        return "Label Maker - Fallback Mode", 200
    
    @application.route('/health')
    def health():
        return "OK", 200
    
    application.config['DEBUG'] = False
    application.config['TESTING'] = False
    application.config['PROPAGATE_EXCEPTIONS'] = True
    application.secret_key = 'fallback-key-2024'

if __name__ == "__main__":
    application.run() 