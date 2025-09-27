#!/usr/bin/env python3
"""
WSGI configuration for PythonAnywhere deployment
"""

import sys
import os

# Add the project directory to the Python path
project_dir = '/home/adamcordova/labelMaker_fresh'  # Updated to correct folder name
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

# Change to the project directory
os.chdir(project_dir)

# Import the Flask app
from app import app as application

if __name__ == "__main__":
    application.run()