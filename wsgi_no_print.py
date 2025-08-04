#!/usr/bin/env python3

import sys
import os

# Get the current directory
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Set environment variables
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = 'False'

# Create Flask app with NO print statements
from flask import Flask

def create_no_print_app():
    app = Flask(__name__)
    
    @app.route('/')
    def index():
        return "AGT Label Maker - No Print Version"
    
    @app.route('/test')
    def test():
        return "Test route working"
    
    @app.route('/load-real-app')
    def load_real_app():
        try:
            from app import app as real_app
            return "Real app imported successfully!"
        except ImportError as e:
            return f"Import error: {str(e)}"
        except Exception as e:
            return f"Other error: {str(e)}"
    
    @app.route('/load-create-app')
    def load_create_app():
        try:
            from app import create_app
            real_app = create_app()
            return "create_app() worked successfully!"
        except ImportError as e:
            return f"Import error: {str(e)}"
        except Exception as e:
            return f"Other error: {str(e)}"
    
    @app.route('/debug')
    def debug():
        info = f"""
        <h1>Debug Information</h1>
        <p><strong>Python Version:</strong> {sys.version}</p>
        <p><strong>Project Directory:</strong> {project_dir}</p>
        <p><strong>Python Path:</strong> {sys.path[:3]}</p>
        <p><strong>Environment:</strong> FLASK_ENV={os.environ.get('FLASK_ENV')}, FLASK_DEBUG={os.environ.get('FLASK_DEBUG')}</p>
        """
        return info
    
    return app

# Create the application silently
application = create_no_print_app() 