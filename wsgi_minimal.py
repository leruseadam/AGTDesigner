#!/usr/bin/env python3
"""
Ultra-minimal WSGI file that should definitely work.
"""

import sys
import os

# Get the current directory
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Set environment variables
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = 'False'

# Create a minimal Flask app that will definitely work
from flask import Flask

application = Flask(__name__)

@application.route('/')
def index():
    return "AGT Label Maker is running!"

@application.route('/test')
def test():
    return "Test route working"

@application.route('/health')
def health():
    return "Healthy"

@application.route('/api/status')
def api_status():
    return {"status": "ok", "message": "API is working"}

if __name__ == "__main__":
    application.run() 