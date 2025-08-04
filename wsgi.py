#!/usr/bin/env python3
"""
WSGI entry point for the Label Maker application.
Optimized for PythonAnywhere deployment with error handling and performance optimizations.
"""

import sys
import os
import logging
from datetime import datetime

# Disable stdout/stderr buffering to prevent BlockingIOError
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

# Set environment variables for production
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = 'False'
os.environ['PYTHONUNBUFFERED'] = '1'

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

# Configure basic logging to prevent BlockingIOError
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Suppress verbose logging that can cause issues
logging.getLogger('werkzeug').setLevel(logging.ERROR)
logging.getLogger('urllib3').setLevel(logging.ERROR)
logging.getLogger('requests').setLevel(logging.ERROR)
logging.getLogger('PIL').setLevel(logging.ERROR)

def activate_virtual_environment():
    """Activate virtual environment if it exists."""
    try:
        # Try multiple possible virtual environment paths
        venv_paths = [
            os.path.join(project_dir, 'venv_pythonanywhere'),
            os.path.join(project_dir, 'venv'),
            os.path.join(os.path.dirname(project_dir), 'venv_pythonanywhere'),
            os.path.join(os.path.dirname(project_dir), 'venv')
        ]
        
        for venv_path in venv_paths:
            activate_script = os.path.join(venv_path, 'bin', 'activate_this.py')
            if os.path.exists(activate_script):
                with open(activate_script) as file_:
                    exec(file_.read(), dict(__file__=activate_script))
                print(f"✅ Virtual environment activated: {venv_path}")
                return True
        
        print("⚠️  No virtual environment found, using system Python")
        return False
    except Exception as e:
        print(f"⚠️  Virtual environment activation failed: {e}")
        return False

def create_application():
    """Create and configure the Flask application with error handling."""
    try:
        # Activate virtual environment first
        activate_virtual_environment()
        
        # Import the Flask app
        from app import create_app
        
        # Create the application instance
        app = create_app()
        
        # Configure for production
        app.config['DEBUG'] = False
        app.config['TESTING'] = False
        app.config['PROPAGATE_EXCEPTIONS'] = True
        
        # Set production secret key if not already set
        if not app.secret_key or app.secret_key == 'dev':
            app.secret_key = os.environ.get('SECRET_KEY', 'label-maker-production-key-2024')
        
        print(f"✅ Label Maker application created successfully at {datetime.now()}")
        return app
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure all dependencies are installed:")
        print("   pip install -r requirements_production.txt")
        raise
    except Exception as e:
        print(f"❌ Application creation failed: {e}")
        import traceback
        traceback.print_exc()
        raise

# Create the application instance
try:
    application = create_application()
except Exception as e:
    print(f"❌ Failed to create application: {e}")
    # Create a minimal error application
    from flask import Flask
    application = Flask(__name__)
    
    @application.route('/')
    def error_page():
        return f"""
        <html>
        <head><title>Label Maker - Error</title></head>
        <body>
        <h1>Label Maker Application Error</h1>
        <p>The application failed to start properly.</p>
        <p>Error: {str(e)}</p>
        <p>Please check the PythonAnywhere error logs for more details.</p>
        <p>Time: {datetime.now()}</p>
        </body>
        </html>
        """, 500

# WSGI application entry point
if __name__ == "__main__":
    try:
        application.run(host='0.0.0.0', port=5000, debug=False)
    except Exception as e:
        print(f"❌ Failed to run application: {e}") 