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

# Try to activate virtual environment if it exists
venv_path = os.path.join(project_dir, 'venv_pythonanywhere')
activate_this = os.path.join(venv_path, 'bin', 'activate_this.py')

if os.path.exists(activate_this):
    with open(activate_this) as file_:
        exec(file_.read(), dict(__file__=activate_this))
    print(f"✅ Virtual environment activated: {venv_path}")
else:
    print(f"⚠️  Virtual environment not found at: {venv_path}")
    print("Continuing without virtual environment activation...")

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

# Import the Flask app
try:
    from app import create_app
    print("✅ Flask app imported successfully")
except ImportError as e:
    print(f"❌ Error importing Flask app: {e}")
    raise

# Create the application instance
application = create_app()

# Configure for production
application.config['DEBUG'] = False
application.config['TESTING'] = False
application.config['PROPAGATE_EXCEPTIONS'] = True

# Set production secret key if not already set
if not application.secret_key or application.secret_key == 'dev':
    application.secret_key = os.environ.get('SECRET_KEY', 'label-maker-production-key-2024')

print(f"✅ Label Maker application created successfully at {datetime.now()}")

# WSGI application entry point
if __name__ == "__main__":
    try:
        application.run()
    except Exception as e:
        print(f"❌ Failed to run application: {e}") 