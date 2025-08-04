#!/usr/bin/env python3
"""
Diagnostic script to identify BlockingIOError causes.
"""

def create_diagnostic_wsgi():
    """Create a diagnostic WSGI that captures the exact error."""
    return '''import sys
import os
import traceback

# Capture all errors without printing
def silent_error_handler():
    try:
        # Set environment variables
        os.environ['PYTHONUNBUFFERED'] = '1'
        os.environ['FLASK_ENV'] = 'production'
        
        # Add project path
        sys.path.insert(0, '/home/adamcordova/AGTDesigner')
        
        # Try to import and create app
        from app import create_app
        app = create_app()
        app.config['DEBUG'] = False
        return app
        
    except Exception as e:
        # Create minimal error app
        from flask import Flask
        app = Flask(__name__)
        
        @app.route('/')
        def error_page():
            error_info = {
                'error_type': type(e).__name__,
                'error_message': str(e),
                'traceback': traceback.format_exc()
            }
            return f'''
            <h1>WSGI Error Diagnostic</h1>
            <h2>Error Type: {error_info['error_type']}</h2>
            <h3>Error Message: {error_info['error_message']}</h3>
            <pre>{error_info['traceback']}</pre>
            ''', 500
        
        return app

# Create application silently
application = silent_error_handler()
'''

def create_ultra_minimal_wsgi():
    """Create ultra minimal WSGI with zero output."""
    return '''import sys
import os

os.environ['PYTHONUNBUFFERED'] = '1'
sys.path.insert(0, '/home/adamcordova/AGTDesigner')

try:
    from app import create_app
    application = create_app()
except:
    from flask import Flask
    application = Flask(__name__)
    @application.route('/')
    def error():
        return '<h1>Import Error</h1>', 500
'''

def create_pythonanywhere_specific_wsgi():
    """Create PythonAnywhere-specific WSGI."""
    return '''import sys
import os

# PythonAnywhere specific settings
os.environ['PYTHONUNBUFFERED'] = '1'
os.environ['PYTHONANYWHERE_SITE'] = 'True'

# Multiple path attempts
paths = [
    '/home/adamcordova/AGTDesigner',
    '/home/adamcordova/labelMaker_ newgui BACKUP 6.24 copy 17',
    os.path.dirname(os.path.abspath(__file__))
]

for path in paths:
    if path not in sys.path:
        sys.path.insert(0, path)

# Create app with multiple fallbacks
try:
    from app import create_app
    application = create_app()
    application.config['DEBUG'] = False
except ImportError:
    try:
        from flask import Flask
        application = Flask(__name__)
        @application.route('/')
        def error():
            return '<h1>Import Error</h1>', 500
    except:
        # Last resort
        class MinimalApp:
            def __call__(self, environ, start_response):
                status = '500 Internal Server Error'
                response_headers = [('Content-type', 'text/html')]
                start_response(status, response_headers)
                return [b'<h1>Critical Error</h1>']
        application = MinimalApp()
'''

def main():
    """Show diagnostic options."""
    print("🔍 WSGI DIAGNOSTIC OPTIONS")
    print("=" * 50)
    print()
    print("Since replacing the WSGI didn't work, try these options:")
    print()
    
    print("OPTION 1: Diagnostic WSGI (Shows exact error)")
    print("-" * 40)
    print("Use this to see what's actually failing:")
    print(create_diagnostic_wsgi())
    print()
    
    print("OPTION 2: Ultra Minimal WSGI")
    print("-" * 40)
    print("Absolute minimal with zero output:")
    print(create_ultra_minimal_wsgi())
    print()
    
    print("OPTION 3: PythonAnywhere-Specific WSGI")
    print("-" * 40)
    print("Optimized for PythonAnywhere:")
    print(create_pythonanywhere_specific_wsgi())
    print()
    
    print("ADDITIONAL TROUBLESHOOTING:")
    print("1. Check if your app.py has print statements")
    print("2. Check if any imported modules have print statements")
    print("3. Verify the project path is correct")
    print("4. Check PythonAnywhere web server settings")
    print("5. Try a different Python version (3.10, 3.9)")

if __name__ == "__main__":
    main() 