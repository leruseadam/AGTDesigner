#!/usr/bin/env python3
"""
WSGI entry point for the Label Maker application.
This file is used by PythonAnywhere to serve the Flask application.
"""

import sys
import os

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Set production environment variables
os.environ.setdefault('DEVELOPMENT_MODE', 'false')
os.environ.setdefault('FLASK_ENV', 'production')

# Import the Flask app from app.py
try:
    from app import app
    # For PythonAnywhere, we need to expose the app object
    application = app
except ImportError as e:
    # Log the error for debugging
    print(f"Error importing app: {e}")
    raise

if __name__ == "__main__":
    app.run() 