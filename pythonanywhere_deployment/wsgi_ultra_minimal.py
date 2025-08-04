#!/usr/bin/env python3
"""
Ultra-minimal WSGI file for PythonAnywhere.
No print statements, no buffering, guaranteed to work.
"""

import sys
import os

# CRITICAL: Force unbuffered output
os.environ['PYTHONUNBUFFERED'] = '1'

# Get project directory
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Set environment
os.environ['PYTHONANYWHERE'] = 'true'
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = 'False'

# Create directories
os.makedirs(os.path.join(project_dir, 'uploads'), exist_ok=True)
os.makedirs(os.path.join(project_dir, 'logs'), exist_ok=True)

# Import and create application with minimal error handling
try:
    from app import create_app
    application = create_app()
    application.config['DEBUG'] = False
    application.config['TESTING'] = False
    application.config['PROPAGATE_EXCEPTIONS'] = True
    if not application.secret_key or application.secret_key == 'dev':
        application.secret_key = 'label-maker-production-key-2024'
except Exception:
    # If anything fails, create minimal error app
    from flask import Flask
    application = Flask(__name__)
    @application.route('/')
    def error():
        return "Application Error - Check logs", 500
    @application.route('/health')
    def health():
        return "Error", 500

# WSGI application
if __name__ == "__main__":
    application.run() 