#!/usr/bin/env python3
"""
Simple test WSGI file for debugging PythonAnywhere deployment
"""

import sys
import os

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

print(f"🔍 Project directory: {project_dir}")
print(f"🔍 Python path: {sys.path[:3]}")

# Try to add virtual environment to Python path
venv_paths = [
    os.path.join(project_dir, 'venv_pythonanywhere'),
    os.path.join(os.path.expanduser('~'), 'AGTDesigner', 'venv_pythonanywhere'),
    os.path.join(os.path.expanduser('~'), 'venv_pythonanywhere'),
    '/var/www/venv_pythonanywhere',
]

venv_found = False
for venv_path in venv_paths:
    venv_site_packages = os.path.join(venv_path, 'lib', 'python3.11', 'site-packages')
    if os.path.exists(venv_site_packages):
        sys.path.insert(0, venv_site_packages)
        print(f"✅ Virtual environment site-packages added: {venv_site_packages}")
        venv_found = True
        break

if not venv_found:
    print("⚠️  Virtual environment site-packages not found in common locations:")
    for venv_path in venv_paths:
        venv_site_packages = os.path.join(venv_path, 'lib', 'python3.11', 'site-packages')
        print(f"   - {venv_site_packages}")
    print("Continuing without virtual environment...")

# Set environment variables
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = 'False'

# Test basic Flask import
try:
    from flask import Flask
    print("✅ Flask imported successfully")
except ImportError as e:
    print(f"❌ Error importing Flask: {e}")
    raise

# Test app import
try:
    from app import create_app
    print("✅ Successfully imported Flask app")
except ImportError as e:
    print(f"❌ Error importing Flask app: {e}")
    print("Available packages:")
    for path in sys.path:
        print(f"  - {path}")
    raise

# Create a simple test application
def simple_app(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'text/html; charset=utf-8')]
    start_response(status, headers)
    
    html = f"""
    <html>
    <head><title>Test Page</title></head>
    <body>
        <h1>✅ PythonAnywhere Test Page</h1>
        <p>Project directory: {project_dir}</p>
        <p>Python path: {sys.path[:3]}</p>
        <p>Virtual environment found: {venv_found}</p>
        <p>Flask imported: ✅</p>
        <p>App imported: ✅</p>
        <hr>
        <p><a href="/app">Try the main application</a></p>
    </body>
    </html>
    """
    return [html.encode('utf-8')]

# Create the application instance
try:
    application = create_app()
    print("✅ Application created successfully")
except Exception as e:
    print(f"❌ Error creating application: {e}")
    print("Falling back to simple test app")
    application = simple_app

if __name__ == "__main__":
    print("🚀 Starting test server...")
    application.run(debug=True) 