#!/usr/bin/env python3
"""
Minimal WSGI entry point for PythonAnywhere deployment.
Designed to handle all common PythonAnywhere issues.
"""

import sys
import os

# CRITICAL: Force unbuffered output to prevent BlockingIOError
os.environ['PYTHONUNBUFFERED'] = '1'

# Get the current directory
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Set environment variables
os.environ['PYTHONANYWHERE'] = 'true'
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = 'False'

# Ensure required directories exist
uploads_dir = os.path.join(project_dir, 'uploads')
os.makedirs(uploads_dir, exist_ok=True)

logs_dir = os.path.join(project_dir, 'logs')
os.makedirs(logs_dir, exist_ok=True)

# Try to import and create the application
try:
    from app import create_app
    application = create_app()
    
    # Configure for production
    application.config['DEBUG'] = False
    application.config['TESTING'] = False
    application.config['PROPAGATE_EXCEPTIONS'] = True
    
    # Set secret key
    if not application.secret_key or application.secret_key == 'dev':
        application.secret_key = 'label-maker-production-key-2024'
        
except Exception as e:
    # If anything fails, create a minimal error app
    from flask import Flask
    application = Flask(__name__)
    
    @application.route('/')
    def error_page():
        return f"Application Error: {str(e)}", 500
    
    @application.route('/health')
    def health_check():
        return "Error: Application failed to start", 500

# WSGI application
if __name__ == "__main__":
    application.run() 