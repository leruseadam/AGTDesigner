#!/usr/bin/env python3
"""
Create a working WSGI file for PythonAnywhere
"""

def create_working_wsgi():
    """Create a simple, working WSGI file"""
    
    wsgi_content = '''import sys
import os

# Set environment variables
os.environ['PYTHONUNBUFFERED'] = '1'
os.environ['FLASK_ENV'] = 'production'

# Add the app directory to Python path
project_dir = '/home/AGTDesigner/pythonanywhere_deployment'
sys.path.insert(0, project_dir)

# Change to the app directory
os.chdir(project_dir)

try:
    # Try to import the Flask app
    from app import app as application
    application.config['DEBUG'] = False
except Exception as e:
    # If that fails, create a simple error app
    from flask import Flask
    application = Flask(__name__)
    
    @application.route('/')
    def error():
        return f'<h1>App Error</h1><p>Error: {str(e)}</p>', 500
    
    @application.route('/health')
    def health():
        return 'OK', 200
'''
    
    # Write to both locations
    with open('pythonanywhere_deployment/wsgi.py', 'w') as f:
        f.write(wsgi_content)
    
    with open('wsgi_simple.py', 'w') as f:
        f.write(wsgi_content)
    
    print("✅ Created working WSGI file")
    print("📋 Files created:")
    print("  - pythonanywhere_deployment/wsgi.py")
    print("  - wsgi_simple.py")
    print("📋 This WSGI file will:")
    print("  - Handle import errors gracefully")
    print("  - Show error messages if the app fails to load")
    print("  - Work even if there are dependency issues")

if __name__ == "__main__":
    create_working_wsgi()
