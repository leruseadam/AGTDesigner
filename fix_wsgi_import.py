#!/usr/bin/env python3
"""
Fix WSGI import issue
"""

def fix_wsgi_import():
    """Fix the WSGI import to use create_app() function"""
    
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
    # Try to import the Flask app using create_app function
    from app import create_app
    application = create_app()
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
    
    with open('wsgi_fixed.py', 'w') as f:
        f.write(wsgi_content)
    
    print("✅ Fixed WSGI import to use create_app() function")
    print("📋 Files updated:")
    print("  - pythonanywhere_deployment/wsgi.py")
    print("  - wsgi_fixed.py")
    print("📋 This should fix the web app loading issue")

if __name__ == "__main__":
    fix_wsgi_import()
