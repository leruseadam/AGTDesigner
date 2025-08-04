#!/usr/bin/env python3
"""
WSGI file with no print statements to avoid BlockingIOError.
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

# Create basic Flask app without any print statements
from flask import Flask
application = Flask(__name__)

@application.route('/')
def index():
    return "Label Maker - No Print Mode", 200

@application.route('/health')
def health():
    return "OK", 200

@application.route('/test')
def test():
    return "Test endpoint working", 200

@application.route('/api/status')
def api_status():
    return {
        'status': 'running',
        'environment': 'production',
        'python_version': sys.version
    }, 200

# Basic configuration
application.config['DEBUG'] = False
application.config['TESTING'] = False
application.config['PROPAGATE_EXCEPTIONS'] = True
application.secret_key = 'no-print-key-2024'

if __name__ == "__main__":
    application.run() 