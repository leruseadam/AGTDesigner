#!/usr/bin/env python3
"""
Simple WSGI configuration for PythonAnywhere
This version is designed to work with the existing setup
"""

import os
import sys

# Add the project directory to Python path
project_dir = '/home/adamcordova/AGTDesigner'
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

# Set environment variables
os.environ['PYTHONANYWHERE_SITE'] = 'True'
os.environ['PYTHONANYWHERE_DOMAIN'] = 'www.agtpricetags.com'

# Disable default file loading for performance
os.environ['DISABLE_DEFAULT_FILE_LOADING'] = 'True'
os.environ['LAZY_LOADING_ENABLED'] = 'True'

# Simple logging configuration
import logging
logging.basicConfig(level=logging.ERROR)

# Import the Flask app
try:
    from app import app
    application = app
    
    # Basic Flask configuration
    app.config['DEBUG'] = False
    app.config['TESTING'] = False
    
    print("WSGI: Flask app imported successfully")
    
except ImportError as e:
    print(f"WSGI: Import error - {e}")
    raise
except Exception as e:
    print(f"WSGI: Configuration error - {e}")
    raise

if __name__ == "__main__":
    application.run() 