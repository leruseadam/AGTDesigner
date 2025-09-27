#!/usr/bin/env python3
"""
WSGI configuration for PythonAnywhere deployment
Fixed directory path and added performance optimizations
"""

import sys
import os
import logging

# Add the project directory to the Python path
project_dir = '/home/adamcordova/AGTDesigner'  # Fixed: Correct directory name
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

# Add user site-packages for --user installed packages
import site
user_site = site.getusersitepackages()
if user_site not in sys.path:
    sys.path.insert(0, user_site)

# Verify directory exists before changing to it
if os.path.exists(project_dir):
    os.chdir(project_dir)
else:
    # Log error but continue - let Python path handle imports
    print(f"Warning: Directory {project_dir} not found")

# Set environment variables for PythonAnywhere
os.environ['PYTHONANYWHERE_SITE'] = 'True'
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = 'False'

# Configure logging to reduce verbosity
logging.basicConfig(level=logging.ERROR)
for logger_name in ['werkzeug', 'urllib3', 'requests', 'pandas', 'openpyxl']:
    logging.getLogger(logger_name).setLevel(logging.ERROR)

try:
    # Import the Flask app
    from app import app as application
    
    # Production configuration
    application.config.update(
        DEBUG=False,
        TESTING=False,
        TEMPLATES_AUTO_RELOAD=False,
        SEND_FILE_MAX_AGE_DEFAULT=31536000,  # 1 year cache for static files
        MAX_CONTENT_LENGTH=50 * 1024 * 1024,  # 50MB max file size
    )
    
except ImportError as e:
    print(f"Error importing Flask app: {e}")
    print(f"Python path: {sys.path}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Directory contents: {os.listdir('.')}")
    raise

if __name__ == "__main__":
    application.run(debug=False)