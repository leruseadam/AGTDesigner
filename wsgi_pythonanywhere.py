#!/usr/bin/env python3
"""
WSGI configuration for Python 3.10 on PythonAnywhere
Optimized for performance
"""

import sys
import os

# Add the project directory to Python path
project_dir = '/home/adamcordova/AGTDesigner'
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

# Set environment variables for PythonAnywhere
os.environ['PYTHONANYWHERE_SITE'] = 'True'
os.environ['PYTHONANYWHERE_DOMAIN'] = 'www.agtpricetags.com'

# Performance optimization: Disable default file loading during startup
os.environ['DISABLE_DEFAULT_FILE_LOADING'] = 'True'
os.environ['LAZY_LOADING_ENABLED'] = 'True'

# Configure logging for better performance
import logging
logging.basicConfig(level=logging.ERROR)

# Import the Flask app
try:
    from app import app
    application = app
    
    # Configure Flask for production
    app.config['DEBUG'] = False
    app.config['TESTING'] = False
    app.config['TEMPLATES_AUTO_RELOAD'] = False
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000
    
    print("WSGI: App loaded successfully for Python 3.10")
    
except ImportError as e:
    print(f"WSGI: Import error - {e}")
    # Create fallback app
    from flask import Flask
    application = Flask(__name__)
    application.config['DEBUG'] = False
    print("WSGI: Using fallback Flask app")
    
except Exception as e:
    print(f"WSGI: Other error - {e}")
    raise

if __name__ == "__main__":
    application.run()
