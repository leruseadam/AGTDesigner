#!/usr/bin/env python3

import sys
import os
import traceback

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Set environment variables
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = 'False'

# Create a basic Flask app with error handling
try:
    from flask import Flask
    
    def create_error_handler_app():
        app = Flask(__name__)
        
        @app.route('/')
        def index():
            return "AGT Label Maker - Error Handler Version"
        
        @app.route('/test')
        def test():
            return "Test route working"
        
        @app.route('/error')
        def show_error():
            return f"Error info: Python {sys.version}, Path: {project_dir}"
        
        return app
    
    application = create_error_handler_app()
    
except Exception as e:
    # If Flask import fails, create a minimal WSGI app
    class MinimalApp:
        def __init__(self):
            self.status = '200 OK'
            self.headers = [('Content-type', 'text/html')]
        
        def __call__(self, environ, start_response):
            start_response(self.status, self.headers)
            error_info = f"""
            <h1>AGT Label Maker - Error Mode</h1>
            <h2>Error: {str(e)}</h2>
            <h3>Python Version: {sys.version}</h3>
            <h3>Project Directory: {project_dir}</h3>
            <h3>Python Path: {sys.path[:3]}</h3>
            <pre>{traceback.format_exc()}</pre>
            """
            return [error_info.encode('utf-8')]
    
    application = MinimalApp()

if __name__ == "__main__":
    if hasattr(application, 'run'):
        application.run()
    else:
        print("Minimal app created") 