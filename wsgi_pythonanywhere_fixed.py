#!/usr/bin/env python3
"""
PythonAnywhere WSGI configuration - Optimized for Performance
Fixed for use with /var/www/www_agtpricetags_com_wsgi.py path
"""

import os
import sys
import logging

# Add the project directory to Python path
# Use the actual project location on PythonAnywhere
project_dir = '/home/adamcordova/AGTDesigner'
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

# Set environment variables for PythonAnywhere
os.environ['PYTHONANYWHERE_SITE'] = 'True'
os.environ['PYTHONANYWHERE_DOMAIN'] = 'www.agtpricetags.com'

# Performance optimization: Disable default file loading during startup
os.environ['DISABLE_DEFAULT_FILE_LOADING'] = 'True'
os.environ['LAZY_LOADING_ENABLED'] = 'True'

# Configure logging for PythonAnywhere - Reduce verbosity for better performance
try:
    logging.basicConfig(
        level=logging.ERROR,  # Changed from WARNING to ERROR for better performance
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('/home/adamcordova/pythonanywhere.log')
        ]
    )
except (OSError, PermissionError):
    # Fallback to console-only logging if file logging fails
    logging.basicConfig(
        level=logging.ERROR,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )

# Suppress verbose logging from all libraries
logging.getLogger('werkzeug').setLevel(logging.ERROR)
logging.getLogger('urllib3').setLevel(logging.ERROR)
logging.getLogger('requests').setLevel(logging.ERROR)
logging.getLogger('pandas').setLevel(logging.ERROR)
logging.getLogger('openpyxl').setLevel(logging.ERROR)
logging.getLogger('xlrd').setLevel(logging.ERROR)

# Import and configure the Flask app with lazy loading
try:
    from app import app
    
    # Configure Flask for PythonAnywhere with performance optimizations
    app.config['DEBUG'] = False
    app.config['TESTING'] = False
    app.config['TEMPLATES_AUTO_RELOAD'] = False
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000
    
    # Additional performance optimizations
    app.config['JSON_SORT_KEYS'] = False  # Disable JSON sorting for better performance
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False  # Disable pretty printing
    
    # Set the application
    application = app
    
    # Log successful startup
    logging.info("WSGI application loaded successfully with performance optimizations")
    
except ImportError as e:
    logging.error(f"Failed to import Flask app: {e}")
    raise
except Exception as e:
    logging.error(f"Error configuring Flask app: {e}")
    raise

if __name__ == "__main__":
    application.run() 