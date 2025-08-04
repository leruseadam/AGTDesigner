#!/usr/bin/env python3
"""
Most basic WSGI file for PythonAnywhere.
No file operations, no logging, no buffering issues.
"""

import sys
import os

# Force unbuffered output
os.environ['PYTHONUNBUFFERED'] = '1'

# Add project to path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Set environment variables
os.environ['PYTHONANYWHERE'] = 'true'
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = 'False'

# Create basic Flask app
from flask import Flask
application = Flask(__name__)

@application.route('/')
def index():
    return "Label Maker - Basic Version", 200

@application.route('/health')
def health():
    return "OK", 200

@application.route('/test')
def test():
    return "Test endpoint working", 200

# Basic configuration
application.config['DEBUG'] = False
application.config['TESTING'] = False
application.config['PROPAGATE_EXCEPTIONS'] = True
application.secret_key = 'basic-key-2024'

if __name__ == "__main__":
    application.run() 