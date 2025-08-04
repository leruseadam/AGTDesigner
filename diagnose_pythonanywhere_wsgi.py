#!/usr/bin/env python3
"""
Diagnostic script to help identify WSGI issues on PythonAnywhere.
"""

import os
import sys

def check_wsgi_file():
    """Check if the WSGI file exists and what it contains."""
    wsgi_path = '/var/www/www_agtpricetags_com_wsgi.py'
    
    print("=== PythonAnywhere WSGI Diagnostic ===")
    print(f"Checking WSGI file: {wsgi_path}")
    
    if os.path.exists(wsgi_path):
        print("✓ WSGI file exists")
        try:
            with open(wsgi_path, 'r') as f:
                content = f.read()
                print(f"✓ WSGI file is readable ({len(content)} characters)")
                
                # Check for problematic patterns
                if 'exec(file_.read()' in content:
                    print("⚠️  PROBLEM: Found 'exec(file_.read()' - this is trying to execute shell scripts!")
                if 'activate_this' in content:
                    print("⚠️  PROBLEM: Found 'activate_this' - this is shell script activation!")
                if 'deactivate ()' in content:
                    print("⚠️  PROBLEM: Found 'deactivate ()' - this is shell script syntax!")
                if '#!/bin/bash' in content:
                    print("⚠️  PROBLEM: Found bash shebang - this is a shell script!")
                
                # Show first few lines
                lines = content.split('\n')
                print(f"\nFirst 10 lines of WSGI file:")
                for i, line in enumerate(lines[:10]):
                    print(f"{i+1:2d}: {line}")
                    
                if len(lines) > 10:
                    print(f"... and {len(lines) - 10} more lines")
                    
        except Exception as e:
            print(f"✗ Error reading WSGI file: {e}")
    else:
        print("✗ WSGI file does not exist")
    
    print("\n=== Recommended Fix ===")
    print("Replace the entire WSGI file content with:")
    print("=" * 50)
    
    clean_wsgi = '''#!/usr/bin/env python3
"""
Clean WSGI entry point for the Label Maker application.
This file is used by PythonAnywhere to serve the Flask application.
"""

import sys
import os

# Add the project directory to Python path
project_dir = '/home/adamcordova/AGTDesigner'
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

# Add virtual environment site-packages to Python path
venv_site_packages = '/home/adamcordova/AGTDesigner/venv_pythonanywhere/lib/python3.11/site-packages'
if os.path.exists(venv_site_packages) and venv_site_packages not in sys.path:
    sys.path.insert(0, venv_site_packages)

# Set environment variables for the virtual environment
os.environ['VIRTUAL_ENV'] = '/home/adamcordova/AGTDesigner/venv_pythonanywhere'
os.environ['PATH'] = '/home/adamcordova/AGTDesigner/venv_pythonanywhere/bin:' + os.environ.get('PATH', '')

# Import the Flask app
try:
    from app import create_app
    # Create the application instance
    application = create_app()
except ImportError as e:
    print(f"Import error: {e}")
    # Fallback - create a simple error application
    from flask import Flask
    application = Flask(__name__)
    @application.route('/')
    def error():
        return f"Import error: {e}", 500

if __name__ == "__main__":
    application.run()'''
    
    print(clean_wsgi)
    print("=" * 50)

if __name__ == "__main__":
    check_wsgi_file() 