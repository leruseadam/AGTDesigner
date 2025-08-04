#!/usr/bin/env python3
"""
Specialized WSGI file for PythonAnywhere deployment.
Handles BlockingIOError, import issues, and provides detailed error reporting.
"""

import sys
import os
import time
from datetime import datetime

# CRITICAL: Prevent BlockingIOError by setting unbuffered output
os.environ['PYTHONUNBUFFERED'] = '1'

# Force stdout/stderr to be unbuffered
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)

# Set production environment
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = 'False'

# Get project directory
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Simple logging function that won't cause BlockingIOError
def safe_log(message):
    """Safe logging that won't cause BlockingIOError."""
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {message}", flush=True)
    except:
        pass

safe_log("🚀 Starting Label Maker WSGI initialization...")

# Try to activate virtual environment
def try_activate_venv():
    """Try to activate virtual environment with multiple fallbacks."""
    venv_locations = [
        os.path.join(project_dir, 'venv_pythonanywhere'),
        os.path.join(project_dir, 'venv'),
        os.path.join(os.path.expanduser('~'), 'AGTDesigner', 'venv_pythonanywhere'),
        os.path.join(os.path.expanduser('~'), 'AGTDesigner', 'venv')
    ]
    
    for venv_path in venv_locations:
        activate_script = os.path.join(venv_path, 'bin', 'activate_this.py')
        if os.path.exists(activate_script):
            try:
                with open(activate_script) as file_:
                    exec(file_.read(), dict(__file__=activate_script))
                safe_log(f"✅ Virtual environment activated: {venv_path}")
                return True
            except Exception as e:
                safe_log(f"⚠️  Failed to activate {venv_path}: {e}")
                continue
    
    safe_log("⚠️  No virtual environment found, using system Python")
    return False

# Activate virtual environment
try_activate_venv()

# Import dependencies with error handling
def safe_import(module_name, package_name=None):
    """Safely import a module with detailed error reporting."""
    try:
        if package_name:
            module = __import__(package_name, fromlist=[module_name])
        else:
            module = __import__(module_name)
        safe_log(f"✅ Successfully imported {module_name}")
        return module
    except ImportError as e:
        safe_log(f"❌ Failed to import {module_name}: {e}")
        return None
    except Exception as e:
        safe_log(f"❌ Unexpected error importing {module_name}: {e}")
        return None

# Try to import Flask first
flask_module = safe_import('flask')
if not flask_module:
    safe_log("❌ Flask not available - creating minimal error app")
    # Create minimal error application
    class MinimalFlask:
        def __init__(self):
            self.config = {}
            self.secret_key = 'error-key'
        
        def route(self, path):
            def decorator(f):
                return f
            return decorator
    
    application = MinimalFlask()
    
    @application.route('/')
    def error_page():
        return """
        <html>
        <head><title>Label Maker - Flask Not Available</title></head>
        <body>
        <h1>Label Maker Application Error</h1>
        <p>Flask is not available. Please install dependencies:</p>
        <pre>pip install -r requirements_production.txt</pre>
        <p>Time: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
        </body>
        </html>
        """, 500
else:
    # Flask is available, try to create the real application
    try:
        safe_log("📦 Attempting to import app module...")
        
        # Import the app module
        from app import create_app
        
        safe_log("📦 Creating Flask application...")
        
        # Create the application
        application = create_app()
        
        # Configure for production
        application.config['DEBUG'] = False
        application.config['TESTING'] = False
        application.config['PROPAGATE_EXCEPTIONS'] = True
        
        # Set production secret key
        if not application.secret_key or application.secret_key == 'dev':
            application.secret_key = os.environ.get('SECRET_KEY', 'label-maker-production-key-2024')
        
        safe_log("✅ Label Maker application created successfully!")
        
    except ImportError as e:
        safe_log(f"❌ Import error in app module: {e}")
        
        # Create error application
        from flask import Flask
        application = Flask(__name__)
        
        @application.route('/')
        def import_error_page():
            return f"""
            <html>
            <head><title>Label Maker - Import Error</title></head>
            <body>
            <h1>Label Maker Application Error</h1>
            <p>Failed to import application module.</p>
            <p>Error: {str(e)}</p>
            <p>Please check that all dependencies are installed:</p>
            <pre>pip install -r requirements_production.txt</pre>
            <p>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </body>
            </html>
            """, 500
            
    except Exception as e:
        safe_log(f"❌ Unexpected error creating application: {e}")
        
        # Create error application
        from flask import Flask
        application = Flask(__name__)
        
        @application.route('/')
        def unexpected_error_page():
            return f"""
            <html>
            <head><title>Label Maker - Unexpected Error</title></head>
            <body>
            <h1>Label Maker Application Error</h1>
            <p>An unexpected error occurred while creating the application.</p>
            <p>Error: {str(e)}</p>
            <p>Please check the PythonAnywhere error logs for more details.</p>
            <p>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </body>
            </html>
            """, 500

safe_log("🎉 WSGI file loaded successfully!")

if __name__ == "__main__":
    try:
        application.run(host='0.0.0.0', port=5000, debug=False)
    except Exception as e:
        safe_log(f"❌ Failed to run application: {e}")
