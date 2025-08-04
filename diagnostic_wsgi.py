#!/usr/bin/env python3
"""
Diagnostic WSGI file to identify Flask app loading issues.
"""

import sys
import os
import traceback

# Get the current directory (project root)
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

print(f"🔍 Diagnostic WSGI starting...")
print(f"📁 Project directory: {project_dir}")
print(f"🐍 Python version: {sys.version}")
print(f"📦 Python path: {sys.path[:3]}...")

# Set environment variables
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = 'False'

# Test basic imports
try:
    import flask
    print(f"✅ Flask imported successfully: {flask.__version__}")
except ImportError as e:
    print(f"❌ Flask import failed: {e}")

try:
    from flask import Flask
    print("✅ Flask.Flask imported successfully")
except ImportError as e:
    print(f"❌ Flask.Flask import failed: {e}")

# Try to import the app
try:
    print("🔄 Attempting to import app...")
    from app import app
    print("✅ Successfully imported Flask app directly")
    application = app
    print("✅ Application assigned successfully")
except ImportError as e:
    print(f"❌ Direct app import failed: {e}")
    print(f"📋 Full traceback: {traceback.format_exc()}")
    
    # Try create_app as fallback
    try:
        print("🔄 Attempting create_app fallback...")
        from app import create_app
        application = create_app()
        print("✅ create_app fallback successful")
    except Exception as fallback_error:
        print(f"❌ create_app fallback failed: {fallback_error}")
        print(f"📋 Full traceback: {traceback.format_exc()}")
        
        # Create minimal app
        print("🔄 Creating minimal Flask app...")
        from flask import Flask
        application = Flask(__name__)
        
        @application.route('/')
        def index():
            return "Minimal Flask app is running"
        
        @application.route('/test')
        def test():
            return "Test route working"
        
        @application.route('/debug')
        def debug():
            return f"Debug info: Python {sys.version}, Flask {flask.__version__}"
        
        print("✅ Minimal Flask app created")

print("✅ Diagnostic WSGI completed") 