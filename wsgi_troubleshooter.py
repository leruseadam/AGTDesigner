#!/usr/bin/env python3
"""
WSGI Troubleshooter - Find the real cause of BlockingIOError
"""

def option_1_ultra_minimal():
    """Ultra minimal WSGI with zero output."""
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

def option_2_pythonanywhere_specific():
    """PythonAnywhere-specific WSGI."""
    return '''import sys
import os

os.environ['PYTHONUNBUFFERED'] = '1'
os.environ['PYTHONANYWHERE_SITE'] = 'True'

paths = [
    '/home/adamcordova/AGTDesigner',
    '/home/adamcordova/labelMaker_ newgui BACKUP 6.24 copy 17',
    os.path.dirname(os.path.abspath(__file__))
]

for path in paths:
    if path not in sys.path:
        sys.path.insert(0, path)

try:
    from app import create_app
    application = create_app()
    application.config['DEBUG'] = False
except ImportError:
    from flask import Flask
    application = Flask(__name__)
    @application.route('/')
    def error():
        return '<h1>Import Error</h1>', 500
'''

def option_3_complete_silence():
    """Complete silence - no imports, no output."""
    return '''import sys
import os

os.environ['PYTHONUNBUFFERED'] = '1'

class SilentApp:
    def __call__(self, environ, start_response):
        status = '200 OK'
        response_headers = [('Content-type', 'text/html')]
        start_response(status, response_headers)
        return [b'<h1>Silent App Working</h1>']

application = SilentApp()
'''

def main():
    """Show troubleshooting options."""
    print("🔧 WSGI TROUBLESHOOTER")
    print("=" * 50)
    print()
    print("Since the WSGI replacement didn't work, the issue might be:")
    print("1. Your app.py has print statements")
    print("2. Imported modules have print statements")
    print("3. Wrong project path")
    print("4. PythonAnywhere server issues")
    print()
    
    print("Try these WSGI options in order:")
    print()
    
    print("OPTION 1: Ultra Minimal")
    print("-" * 30)
    print(option_1_ultra_minimal())
    print()
    
    print("OPTION 2: PythonAnywhere-Specific")
    print("-" * 30)
    print(option_2_pythonanywhere_specific())
    print()
    
    print("OPTION 3: Complete Silence (Test)")
    print("-" * 30)
    print(option_3_complete_silence())
    print()
    
    print("DIAGNOSTIC STEPS:")
    print("1. Try Option 3 first - if it works, the issue is in your app")
    print("2. If Option 3 fails, it's a PythonAnywhere server issue")
    print("3. Check your app.py for any print() statements")
    print("4. Check PythonAnywhere web server settings")
    print("5. Try changing Python version to 3.10 or 3.9")

if __name__ == "__main__":
    main() 