#!/usr/bin/env python3
"""
WSGI entry point for the Label Maker application.
This file is used by PythonAnywhere to serve the Flask application.
"""

import sys
import os

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Import the Flask app
from app import create_app

# Create the application instance
application = create_app()

if __name__ == "__main__":
    application.run() 