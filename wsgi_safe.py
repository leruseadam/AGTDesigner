#!/usr/bin/env python3
"""
Safe WSGI file that tries to import the real app but falls back gracefully.
"""

import sys
import os

# Get the current directory
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Set environment variables
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = 'False'

# Try to import the real app
try:
    from app import app
    application = app
    print("✅ Successfully imported real Flask app")
except Exception as e:
    print(f"❌ Failed to import real app: {e}")
    
    # Fallback to minimal app
    from flask import Flask
    application = Flask(__name__)
    
    @application.route('/')
    def index():
        return "AGT Label Maker (Fallback Mode) - Real app failed to load"
    
    @application.route('/test')
    def test():
        return "Test route working (fallback)"
    
    @application.route('/health')
    def health():
        return "Healthy (fallback)"
    
    @application.route('/api/status')
    def api_status():
        return {"status": "fallback", "message": "Using fallback app"}

if __name__ == "__main__":
    application.run() 