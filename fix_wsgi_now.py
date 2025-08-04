#!/usr/bin/env python3
"""
Generate the exact WSGI content to fix BlockingIOError.
Copy the output and paste it into your PythonAnywhere WSGI file.
"""

def generate_wsgi_content():
    """Generate the minimal WSGI content that will fix BlockingIOError."""
    
    wsgi_content = '''import sys
import os

os.environ['PYTHONUNBUFFERED'] = '1'
os.environ['FLASK_ENV'] = 'production'

sys.path.insert(0, '/home/adamcordova/AGTDesigner')

try:
    from app import create_app
    application = create_app()
    application.config['DEBUG'] = False
except:
    from flask import Flask
    application = Flask(__name__)
    @application.route('/')
    def error():
        return '<h1>Error</h1>', 500'''
    
    print("=" * 80)
    print("COPY THIS EXACT CONTENT INTO YOUR PYTHONANYWHERE WSGI FILE:")
    print("=" * 80)
    print()
    print(wsgi_content)
    print()
    print("=" * 80)
    print("STEPS TO FIX:")
    print("1. Go to PythonAnywhere Web tab")
    print("2. Click on your WSGI configuration file")
    print("3. DELETE ALL EXISTING CONTENT")
    print("4. Paste the content above")
    print("5. Save the file")
    print("6. Go back to Web tab and click Reload")
    print("=" * 80)

if __name__ == "__main__":
    generate_wsgi_content() 