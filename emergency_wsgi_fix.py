#!/usr/bin/env python3
"""
EMERGENCY WSGI FIX
This script outputs the exact content to replace your WSGI file.
"""

def get_emergency_wsgi_content():
    """Return the emergency WSGI content."""
    return '''import sys
import os

# Set environment variables silently
os.environ['PYTHONUNBUFFERED'] = '1'
os.environ['FLASK_ENV'] = 'production'

# Add project path silently
sys.path.insert(0, '/home/adamcordova/AGTDesigner')

# Create application silently
try:
    from app import create_app
    application = create_app()
    application.config['DEBUG'] = False
except:
    from flask import Flask
    application = Flask(__name__)
    @application.route('/')
    def error():
        return '<h1>Error</h1>', 500
'''

def main():
    """Display the emergency fix."""
    print("🚨 EMERGENCY WSGI FIX 🚨")
    print("=" * 50)
    print()
    print("Your WSGI file has print statements causing BlockingIOError!")
    print("Replace your ENTIRE WSGI file content with this:")
    print()
    print("-" * 50)
    print(get_emergency_wsgi_content())
    print("-" * 50)
    print()
    print("STEPS TO FIX:")
    print("1. Go to PythonAnywhere Web tab")
    print("2. Click on your WSGI configuration file")
    print("3. SELECT ALL (Ctrl+A) and DELETE everything")
    print("4. Paste the content above")
    print("5. Save the file")
    print("6. Go back to Web tab and click 'Reload'")
    print()
    print("This will eliminate ALL print statements that cause BlockingIOError!")

if __name__ == "__main__":
    main() 