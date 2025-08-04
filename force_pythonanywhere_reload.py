#!/usr/bin/env python3
"""
Force PythonAnywhere reload and diagnostic script.
This will help identify why the WSGI changes aren't taking effect.
"""

import os
import sys
import time

def create_force_reload_wsgi():
    """Create a WSGI file that forces a reload and shows diagnostic info."""
    
    wsgi_content = f'''#!/usr/bin/env python3
"""
Force reload WSGI for PythonAnywhere.
This file includes a timestamp to force reloading.
"""

import sys
import os
import time

# Force reload by including timestamp
TIMESTAMP = {int(time.time())}
print(f"=== WSGI RELOAD FORCED - TIMESTAMP: {{TIMESTAMP}} ===")
print(f"Current time: {{time.strftime('%Y-%m-%d %H:%M:%S')}}")
print(f"Python version: {{sys.version}}")
print(f"Python executable: {{sys.executable}}")
print(f"Current working directory: {{os.getcwd()}}")
print(f"sys.path: {{sys.path[:3]}}...")

# Add project directory
project_dir = '/home/adamcordova/AGTDesigner'
print(f"Checking project directory: {{project_dir}}")

if os.path.exists(project_dir):
    print(f"✓ Project directory exists")
    if project_dir not in sys.path:
        sys.path.insert(0, project_dir)
        print(f"  Added to sys.path")
    else:
        print(f"  Already in sys.path")
else:
    print(f"✗ Project directory does not exist")

# Check if app.py exists
app_path = os.path.join(project_dir, 'app.py')
if os.path.exists(app_path):
    print(f"✓ app.py exists at {{app_path}}")
else:
    print(f"✗ app.py does not exist at {{app_path}}")

# Try to import Flask
try:
    import flask
    print(f"✓ Flask version: {{flask.__version__}}")
except ImportError as e:
    print(f"✗ Flask import error: {{e}}")

# Try to import the app
try:
    from app import create_app
    print("✓ Successfully imported create_app")
    application = create_app()
    print("✓ Successfully created application")
except ImportError as e:
    print(f"✗ Import error: {{e}}")
    # Create a minimal fallback app
    from flask import Flask
    application = Flask(__name__)
    
    @application.route('/')
    def error():
        return f"""
        <h1>WSGI Diagnostic Page - Timestamp: {{TIMESTAMP}}</h1>
        <p>Import error: {{e}}</p>
        <p>Python version: {{sys.version}}</p>
        <p>Python executable: {{sys.executable}}</p>
        <p>Current directory: {{os.getcwd()}}</p>
        <p>Project directory: {{project_dir}}</p>
        <p>app.py exists: {{os.path.exists(app_path)}}</p>
        <p>sys.path: {{sys.path}}</p>
        """, 500
except Exception as e:
    print(f"✗ Unexpected error: {{e}}")
    # Create a minimal fallback app
    from flask import Flask
    application = Flask(__name__)
    
    @application.route('/')
    def error():
        return f"""
        <h1>WSGI Error Page - Timestamp: {{TIMESTAMP}}</h1>
        <p>Unexpected error: {{e}}</p>
        <p>Python version: {{sys.version}}</p>
        <p>Python executable: {{sys.executable}}</p>
        <p>Current directory: {{os.getcwd()}}</p>
        <p>Project directory: {{project_dir}}</p>
        """, 500

print(f"=== WSGI Setup Complete - Timestamp: {{TIMESTAMP}} ===")

if __name__ == "__main__":
    application.run()
'''
    
    with open('force_reload_wsgi.py', 'w') as f:
        f.write(wsgi_content)
    
    print("✓ Created force_reload_wsgi.py")
    print(f"Timestamp: {int(time.time())}")
    return wsgi_content

def create_minimal_test_wsgi():
    """Create a minimal test WSGI that should definitely work."""
    
    wsgi_content = f'''#!/usr/bin/env python3
import sys
import os
import time

# Force reload with timestamp
TIMESTAMP = {int(time.time())}
print(f"MINIMAL WSGI LOADED - TIMESTAMP: {{TIMESTAMP}}")

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Try to create a simple Flask app
try:
    from flask import Flask
    application = Flask(__name__)
    
    @application.route('/')
    def hello():
        return f"Hello from minimal WSGI! Timestamp: {{TIMESTAMP}}"
    
    print("✓ Minimal Flask app created")
except Exception as e:
    print(f"✗ Error creating minimal app: {{e}}")
    # Create a dummy application
    class DummyApp:
        def __call__(self, environ, start_response):
            status = '200 OK'
            response_headers = [('Content-type', 'text/plain')]
            start_response(status, response_headers)
            return [f"Error: {{e}} - Timestamp: {{TIMESTAMP}}".encode()]
    
    application = DummyApp()

if __name__ == "__main__":
    application.run()
'''
    
    with open('minimal_test_wsgi.py', 'w') as f:
        f.write(wsgi_content)
    
    print("✓ Created minimal_test_wsgi.py")
    print(f"Timestamp: {int(time.time())}")
    return wsgi_content

def main():
    """Main function to create force reload WSGI files."""
    print("Creating force reload WSGI files...")
    print("=" * 50)
    
    # Create the force reload WSGI
    force_reload_content = create_force_reload_wsgi()
    
    # Create minimal test WSGI
    minimal_content = create_minimal_test_wsgi()
    
    print("\n=== INSTRUCTIONS ===")
    print("1. Go to PythonAnywhere dashboard")
    print("2. Navigate to Web tab")
    print("3. Click on your web app")
    print("4. Go to WSGI configuration file")
    print("5. DELETE EVERYTHING in the current file")
    print("6. Copy and paste the force_reload_wsgi.py content")
    print("7. SAVE the file")
    print("8. Go back to main web app page")
    print("9. Click RELOAD")
    print("10. Wait 30 seconds")
    print("11. Check the Error log")
    print("12. If no change, try the minimal_test_wsgi.py content")
    
    print("\n=== FORCE RELOAD WSGI CONTENT ===")
    print("Copy this entire content to PythonAnywhere:")
    print("-" * 50)
    print(force_reload_content)
    print("-" * 50)
    
    print("\n=== MINIMAL TEST WSGI CONTENT ===")
    print("If the above doesn't work, try this:")
    print("-" * 50)
    print(minimal_content)
    print("-" * 50)

if __name__ == "__main__":
    main() 