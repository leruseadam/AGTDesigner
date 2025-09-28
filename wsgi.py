#!/usr/bin/env python3.11
"""
Clean WSGI configuration for PythonAnywhere
Simple, direct deployment without web_deployment directory
"""

import os
import sys

# Add project directory to Python path
project_dir = '/home/adamcordova/AGTDesigner'
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

# Add user site-packages
import site
user_site = site.getusersitepackages()
if user_site and user_site not in sys.path:
    sys.path.insert(0, user_site)

# Set environment variables
os.environ['PYTHONANYWHERE_SITE'] = 'True'
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = 'False'

# Import and configure Flask app
from app import app as application

# Production settings
application.config.update(
    DEBUG=False,
    TESTING=False,
    TEMPLATES_AUTO_RELOAD=False
)

# For direct execution
if __name__ == "__main__":
    application.run(debug=False)