#!/usr/bin/env python3
"""
Clean WSGI entry point for the Label Maker application.
This file is used by PythonAnywhere to serve the Flask application.
"""

import sys
import os

# Add the project directory to Python path
project_dir = '/home/adamcordova/AGTDesigner'
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

# Add virtual environment site-packages to Python path
venv_site_packages = '/home/adamcordova/AGTDesigner/venv_pythonanywhere/lib/python3.11/site-packages'
if os.path.exists(venv_site_packages) and venv_site_packages not in sys.path:
    sys.path.insert(0, venv_site_packages)

# Set environment variables for the virtual environment
os.environ['VIRTUAL_ENV'] = '/home/adamcordova/AGTDesigner/venv_pythonanywhere'
os.environ['PATH'] = '/home/adamcordova/AGTDesigner/venv_pythonanywhere/bin:' + os.environ.get('PATH', '')

# Import the Flask app
try:
    from app import create_app
    # Create the application instance
    application = create_app()
except ImportError as e:
    print(f"Import error: {e}")
    # Fallback - create a simple error application
    from flask import Flask
    application = Flask(__name__)
    @application.route('/')
    def error():
        return f"Import error: {e}", 500

if __name__ == "__main__":
    application.run() 