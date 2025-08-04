#!/usr/bin/env python3
"""
Simplest possible WSGI file for PythonAnywhere.
No imports, no print statements, no buffering issues.
"""

import sys
import os

# Force unbuffered output
os.environ['PYTHONUNBUFFERED'] = '1'

# Add project to path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Create minimal Flask app
from flask import Flask
application = Flask(__name__)

@application.route('/')
def index():
    return "Label Maker - Loading...", 200

@application.route('/health')
def health():
    return "OK", 200

# Configure for production
application.config['DEBUG'] = False
application.config['TESTING'] = False
application.config['PROPAGATE_EXCEPTIONS'] = True
application.secret_key = 'label-maker-production-key-2024'

if __name__ == "__main__":
    application.run() 