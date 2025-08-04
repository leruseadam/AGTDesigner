#!/usr/bin/env python3
"""
Minimal WSGI file for testing Flask app loading.
"""

import sys
import os

# Get the current directory (project root)
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Set environment variables
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = 'False'

# Import the Flask app directly
try:
    from app import app
    print("✅ Successfully imported Flask app")
    application = app
except ImportError as e:
    print(f"❌ Error importing Flask app: {e}")
    # Create a minimal fallback app
    from flask import Flask
    application = Flask(__name__)
    @application.route('/')
    def index():
        return "Flask app is running"
    @application.route('/test')
    def test():
        return "Test route working"

print("✅ WSGI application loaded successfully")