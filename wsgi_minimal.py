#!/usr/bin/env python3
"""
Ultra-minimal WSGI file for PythonAnywhere.
No print statements, no logging, just the bare minimum to work.
"""

import sys
import os

# Set environment variables
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = 'False'
os.environ['PYTHONUNBUFFERED'] = '1'

# Add project directory to path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Try to activate virtual environment silently
try:
    venv_path = os.path.join(project_dir, 'venv_pythonanywhere')
    activate_script = os.path.join(venv_path, 'bin', 'activate_this.py')
    if os.path.exists(activate_script):
        with open(activate_script) as file_:
            exec(file_.read(), dict(__file__=activate_script))
except:
    pass

# Create application with minimal error handling
try:
    from app import create_app
    application = create_app()
    application.config['DEBUG'] = False
    application.config['TESTING'] = False
except:
    # Fallback to minimal Flask app
    from flask import Flask
    application = Flask(__name__)
    @application.route('/')
    def error():
        return '<h1>Application Error</h1><p>Please check the logs.</p>', 500 