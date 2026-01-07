#!/usr/bin/env python3
"""
PythonAnywhere WSGI configuration - Enhanced for production deployment
Updated after database recovery and optimization
"""

import os
import sys
import logging

# Project directory configuration for PythonAnywhere
project_dir = '/home/adamcordova/AGTDesigner'

# Verify directory exists and add to Python path
if os.path.exists(project_dir):
    if project_dir not in sys.path:
        sys.path.insert(0, project_dir)
    os.chdir(project_dir)
else:
    # Fallback to current directory if project_dir doesn't exist
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    logging.error(f"Project directory {project_dir} not found, using {current_dir}")

# Set environment variables for PythonAnywhere optimization
os.environ['PYTHONANYWHERE_SITE'] = 'True'
os.environ['PYTHONANYWHERE_DOMAIN'] = 'pythonanywhere.com'
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = 'False'

# CRITICAL PERFORMANCE OPTIMIZATIONS for PythonAnywhere
os.environ['FORCE_FAST_LOAD'] = 'True'  # Always use fast database queries
os.environ['DISABLE_STARTUP_FILE_LOADING'] = 'True'  # Skip heavy Excel parsing on startup
os.environ['MAX_MEMORY_MB'] = '450'  # Allow more memory before cleanup
os.environ['CACHE_SIZE_LIMIT'] = '100'  # Increase cache size for better hit rates
os.environ['BATCH_SIZE_LIMIT'] = '500'  # Larger batches for faster processing

# Configure logging to prevent verbose output and "Message too long" errors
logging.basicConfig(
    level=logging.ERROR,
    format='%(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

# Suppress verbose logging from libraries
for logger_name in ['werkzeug', 'urllib3', 'requests', 'pandas', 'openpyxl', 'xlrd']:
    logging.getLogger(logger_name).setLevel(logging.ERROR)

try:
    # Import the Flask application
    from app import app as application
    
    # Production configuration optimized for PythonAnywhere
    application.config.update(
        DEBUG=False,
        TESTING=False,
        TEMPLATES_AUTO_RELOAD=False,
        SEND_FILE_MAX_AGE_DEFAULT=31536000,  # 1 year cache for static files
        MAX_CONTENT_LENGTH=50 * 1024 * 1024,  # 50MB max file size
        # Performance optimizations
        JSON_SORT_KEYS=False,  # Don't sort JSON keys (faster)
        JSONIFY_PRETTYPRINT_REGULAR=False,  # Compact JSON (faster)
    )
    
    logging.info("WSGI application loaded successfully with recovered database")
    
except ImportError as e:
    logging.error(f"Failed to import Flask app: {e}")
    logging.error(f"Python path: {sys.path}")
    logging.error(f"Current working directory: {os.getcwd()}")
    if os.path.exists('.'):
        logging.error(f"Directory contents: {os.listdir('.')}")
    raise
except Exception as e:
    logging.error(f"Error configuring Flask app: {e}")
    raise

# For direct execution
if __name__ == "__main__":
    application.run(debug=False)