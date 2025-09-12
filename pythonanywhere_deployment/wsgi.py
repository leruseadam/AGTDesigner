#!/usr/bin/env python3
"""
WSGI configuration for PythonAnywhere
"""

import sys
import os

# Add the app directory to Python path
path = '/home/AGTDesigner/pythonanywhere_deployment'
if path not in sys.path:
    sys.path.append(path)

# Change to the app directory
os.chdir(path)

# Import the Flask app
from app import app as application

if __name__ == "__main__":
    application.run()
