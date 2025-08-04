#!/usr/bin/env python3
"""
WSGI entry point for the Label Maker application.
Optimized for PythonAnywhere deployment with robust error handling.
"""

import sys
import os
import logging
from datetime import datetime

# CRITICAL: Disable stdout/stderr buffering to prevent BlockingIOError
import io
import os

# Force unbuffered output
os.environ['PYTHONUNBUFFERED'] = '1'

# Replace stdout/stderr with unbuffered versions
sys.stdout = io.TextIOWrapper(
    sys.stdout.buffer, 
    encoding='utf-8', 
    errors='replace', 
    line_buffering=True,
    write_through=True
)
sys.stderr = io.TextIOWrapper(
    sys.stderr.buffer, 
    encoding='utf-8', 
    errors='replace', 
    line_buffering=True,
    write_through=True
)

# Get the current directory (project root)
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Add virtual environment to Python path (if it exists)
venv_path = os.path.join(project_dir, 'venv_pythonanywhere')
venv_site_packages = os.path.join(venv_path, 'lib', 'python3.11', 'site-packages')

if os.path.exists(venv_site_packages):
    sys.path.insert(0, venv_site_packages)
    # Use logging instead of print to avoid buffering issues
    logging.info(f"Virtual environment site-packages added: {venv_site_packages}")
else:
    logging.warning(f"Virtual environment site-packages not found at: {venv_site_packages}")

# Set environment variables for PythonAnywhere
os.environ['PYTHONANYWHERE'] = 'true'
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = 'False'

# Configure basic logging with file handler to avoid stdout issues
log_dir = os.path.join(project_dir, 'logs')
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'wsgi.log')),
        logging.StreamHandler(sys.stdout)
    ]
)

# Suppress verbose logging
logging.getLogger('werkzeug').setLevel(logging.ERROR)
logging.getLogger('urllib3').setLevel(logging.ERROR)
logging.getLogger('requests').setLevel(logging.ERROR)
logging.getLogger('PIL').setLevel(logging.ERROR)

# Ensure uploads directory exists with proper permissions
uploads_dir = os.path.join(project_dir, 'uploads')
os.makedirs(uploads_dir, mode=0o755, exist_ok=True)
try:
    os.chmod(uploads_dir, 0o755)
    logging.info(f"Uploads directory configured: {uploads_dir}")
except Exception as e:
    logging.warning(f"Could not set uploads directory permissions: {e}")

# Import the Flask app with error handling
try:
    from app import create_app
    logging.info("Successfully imported Flask app")
except ImportError as e:
    logging.error(f"Error importing Flask app: {e}")
    # Create a minimal error application
    from flask import Flask
    error_app = Flask(__name__)
    @error_app.route('/')
    def error_page():
        return f"Import Error: {str(e)}", 500
    application = error_app
else:
    # Create the application instance with error handling
    try:
        application = create_app()
        logging.info("Application created successfully")
        
        # Configure for production
        application.config['DEBUG'] = False
        application.config['TESTING'] = False
        application.config['PROPAGATE_EXCEPTIONS'] = True
        
        # Set production secret key
        if not application.secret_key or application.secret_key == 'dev':
            application.secret_key = os.environ.get('SECRET_KEY', 'label-maker-production-key-2024')
        
        logging.info(f"Label Maker application created successfully at {datetime.now()}")
        
    except Exception as e:
        logging.error(f"Error creating application: {e}")
        # Create a minimal error application
        from flask import Flask
        error_app = Flask(__name__)
        @error_app.route('/')
        def error_page():
            return f"Application Creation Error: {str(e)}", 500
        application = error_app

# WSGI application entry point
if __name__ == "__main__":
    application.run() 