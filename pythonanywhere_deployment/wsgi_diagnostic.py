#!/usr/bin/env python3
"""
Diagnostic WSGI file for PythonAnywhere.
Helps identify the root cause of OSError and other issues.
"""

import sys
import os

# Force unbuffered output
os.environ['PYTHONUNBUFFERED'] = '1'

# Basic Flask app for diagnostics
from flask import Flask
application = Flask(__name__)

@application.route('/')
def index():
    return "Label Maker - Diagnostic Mode", 200

@application.route('/health')
def health():
    return "OK", 200

@application.route('/debug')
def debug():
    """Debug endpoint to check system status"""
    info = {
        'python_version': sys.version,
        'python_path': sys.path,
        'current_dir': os.getcwd(),
        'file_dir': os.path.dirname(os.path.abspath(__file__)),
        'env_vars': {
            'PYTHONANYWHERE': os.environ.get('PYTHONANYWHERE', 'Not set'),
            'FLASK_ENV': os.environ.get('FLASK_ENV', 'Not set'),
            'PYTHONUNBUFFERED': os.environ.get('PYTHONUNBUFFERED', 'Not set')
        }
    }
    return str(info), 200

@application.route('/test-import')
def test_import():
    """Test importing the main app"""
    try:
        from app import create_app
        return "App import successful", 200
    except Exception as e:
        return f"App import failed: {str(e)}", 500

@application.route('/test-files')
def test_files():
    """Test file system access"""
    try:
        project_dir = os.path.dirname(os.path.abspath(__file__))
        files = os.listdir(project_dir)
        return f"Files in directory: {files[:10]}", 200
    except Exception as e:
        return f"File system error: {str(e)}", 500

# Basic configuration
application.config['DEBUG'] = False
application.config['TESTING'] = False
application.config['PROPAGATE_EXCEPTIONS'] = True
application.secret_key = 'diagnostic-key-2024'

if __name__ == "__main__":
    application.run() 