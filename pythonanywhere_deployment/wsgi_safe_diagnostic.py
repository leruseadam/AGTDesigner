#!/usr/bin/env python3
"""
Safe diagnostic WSGI file for PythonAnywhere.
Doesn't import main app on startup to avoid crashes.
"""

import sys
import os

# Force unbuffered output
os.environ['PYTHONUNBUFFERED'] = '1'

# Add project to path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Set environment variables
os.environ['PYTHONANYWHERE'] = 'true'
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = 'False'

# Create basic Flask app
from flask import Flask
application = Flask(__name__)

@application.route('/')
def index():
    return "Label Maker - Safe Diagnostic Mode", 200

@application.route('/health')
def health():
    return "OK", 200

@application.route('/debug')
def debug():
    """Debug endpoint to check system status"""
    try:
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
    except Exception as e:
        return f"Debug error: {str(e)}", 500

@application.route('/test-import')
def test_import():
    """Test importing the main app"""
    try:
        # Test basic imports first
        import flask
        result = f"Flask import: OK\n"
        
        # Test app import
        try:
            from app import create_app
            result += "App import: SUCCESS"
            return result, 200
        except ImportError as e:
            result += f"App import: FAILED - {str(e)}"
            return result, 500
        except Exception as e:
            result += f"App import: ERROR - {str(e)}"
            return result, 500
    except Exception as e:
        return f"Test import failed: {str(e)}", 500

@application.route('/test-files')
def test_files():
    """Test file system access"""
    try:
        project_dir = os.path.dirname(os.path.abspath(__file__))
        files = os.listdir(project_dir)
        return f"Files in directory: {files[:10]}", 200
    except Exception as e:
        return f"File system error: {str(e)}", 500

@application.route('/test-simple')
def test_simple():
    """Simple test endpoint"""
    return "Simple test working", 200

# Basic configuration
application.config['DEBUG'] = False
application.config['TESTING'] = False
application.config['PROPAGATE_EXCEPTIONS'] = True
application.secret_key = 'safe-diagnostic-key-2024'

if __name__ == "__main__":
    application.run() 