#!/usr/bin/env python3
"""
Optimized WSGI entry point for Label Maker web server deployment.
"""

import sys
import os

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Set web server environment variables
os.environ['WEB_SERVER_MODE'] = 'True'
os.environ['DEVELOPMENT_MODE'] = 'False'
os.environ['DISABLE_DEFAULT_FILE_LOADING'] = 'True'

# Import the Flask app from app.py
from app import app

# For web servers, we need to expose the app object
application = app

if __name__ == "__main__":
    app.run()
