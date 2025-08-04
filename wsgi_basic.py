#!/usr/bin/env python3

import sys
import os

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Set environment variables
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = 'False'

# Create the most basic Flask app possible
from flask import Flask

def create_basic_app():
    app = Flask(__name__)
    
    @app.route('/')
    def index():
        return "AGT Label Maker - Basic Version"
    
    @app.route('/test')
    def test():
        return "Test route working"
    
    @app.route('/health')
    def health():
        return "Healthy"
    
    return app

# Create the application
application = create_basic_app()

if __name__ == "__main__":
    application.run() 