#!/usr/bin/env python3
"""
WSGI entry point for the Label Maker application.
Optimized for PythonAnywhere deployment with error handling and performance optimizations.
"""

import sys
import os
import logging
from datetime import datetime

# Disable stdout/stderr buffering to prevent BlockingIOError
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

# Get the current directory (project root)
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Add virtual environment to Python path - use the correct path that's working
venv_path = os.path.join(project_dir, 'venv_pythonanywhere')
venv_site_packages = os.path.join(venv_path, 'lib', 'python3.11', 'site-packages')

if os.path.exists(venv_site_packages):
    sys.path.insert(0, venv_site_packages)
else:
    # Continue without virtual environment
    pass

# Set environment variables
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = 'False'

# Configure basic logging to prevent BlockingIOError
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Suppress verbose logging that can cause issues
logging.getLogger('werkzeug').setLevel(logging.ERROR)
logging.getLogger('urllib3').setLevel(logging.ERROR)
logging.getLogger('requests').setLevel(logging.ERROR)
logging.getLogger('PIL').setLevel(logging.ERROR)

# Import the Flask app directly - more reliable than create_app()
try:
    from app import app
    application = app
except ImportError as e:
    # Fallback to create_app if direct import fails
    try:
        from app import create_app
        application = create_app()
    except ImportError as fallback_error:
        raise

# Configure for production
application.config['DEBUG'] = False
application.config['TESTING'] = False
application.config['PROPAGATE_EXCEPTIONS'] = True

# Set production secret key if not already set
if not application.secret_key or application.secret_key == 'dev':
    application.secret_key = os.environ.get('SECRET_KEY', 'label-maker-production-key-2024')

# Application created successfully

# WSGI application entry point
if __name__ == "__main__":
    application.run() 