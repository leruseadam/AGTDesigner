#!/usr/bin/env python3
"""
Comprehensive PythonAnywhere troubleshooting script.
This will help diagnose and fix the WSGI issues.
"""

import os
import sys
import subprocess

def check_local_environment():
    """Check the local environment to understand the project structure."""
    print("=== Local Environment Check ===")
    print(f"Current directory: {os.getcwd()}")
    print(f"Python version: {sys.version}")
    
    # Check if app.py exists
    if os.path.exists('app.py'):
        print("✓ app.py exists")
        with open('app.py', 'r') as f:
            content = f.read()
            if 'def create_app():' in content:
                print("✓ create_app() function found in app.py")
            else:
                print("✗ create_app() function NOT found in app.py")
    else:
        print("✗ app.py does not exist")
    
    # Check project structure
    print("\n=== Project Structure ===")
    for item in os.listdir('.'):
        if os.path.isdir(item):
            print(f"📁 {item}/")
        else:
            print(f"📄 {item}")

def generate_wsgi_options():
    """Generate different WSGI file options."""
    print("\n=== WSGI File Options ===")
    
    # Option 1: Simple
    print("\n--- Option 1: Simple WSGI ---")
    simple_wsgi = '''import sys
import os

# Add the project directory to Python path
sys.path.insert(0, '/home/adamcordova/AGTDesigner')

# Import the Flask app
from app import create_app

# Create the application instance
application = create_app()

if __name__ == "__main__":
    application.run()'''
    print(simple_wsgi)
    
    # Option 2: Diagnostic
    print("\n--- Option 2: Diagnostic WSGI ---")
    diagnostic_wsgi = '''#!/usr/bin/env python3
import sys
import os

# Print diagnostic information
print("=== WSGI Diagnostic ===")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")

# Add project directory
project_dir = '/home/adamcordova/AGTDesigner'
if os.path.exists(project_dir):
    print(f"✓ Found project directory: {project_dir}")
    sys.path.insert(0, project_dir)
else:
    print(f"✗ Project directory not found: {project_dir}")

# Try to import
try:
    from app import create_app
    print("✓ Successfully imported create_app")
    application = create_app()
    print("✓ Successfully created application")
except Exception as e:
    print(f"✗ Error: {e}")
    from flask import Flask
    application = Flask(__name__)
    @application.route('/')
    def error():
        return f"Error: {e}", 500

if __name__ == "__main__":
    application.run()'''
    print(diagnostic_wsgi)
    
    # Option 3: Bulletproof
    print("\n--- Option 3: Bulletproof WSGI ---")
    bulletproof_wsgi = '''#!/usr/bin/env python3
import sys
import os

# Add multiple possible paths
possible_paths = [
    '/home/adamcordova/AGTDesigner',
    '/home/adamcordova/AGTDesigner/labelMaker_ newgui BACKUP 6.24 copy 17',
    os.path.dirname(os.path.abspath(__file__))
]

for path in possible_paths:
    if os.path.exists(path):
        sys.path.insert(0, path)
        break

# Try to create app
try:
    from app import create_app
    application = create_app()
except Exception as e:
    from flask import Flask
    application = Flask(__name__)
    @application.route('/')
    def error():
        return f"Error: {e}", 500

if __name__ == "__main__":
    application.run()'''
    print(bulletproof_wsgi)

def create_wsgi_files():
    """Create the WSGI files locally for easy copying."""
    print("\n=== Creating WSGI Files ===")
    
    # Create simple WSGI
    with open('wsgi_simple.py', 'w') as f:
        f.write('''import sys
import os

# Add the project directory to Python path
sys.path.insert(0, '/home/adamcordova/AGTDesigner')

# Import the Flask app
from app import create_app

# Create the application instance
application = create_app()

if __name__ == "__main__":
    application.run()''')
    print("✓ Created wsgi_simple.py")
    
    # Create diagnostic WSGI
    with open('wsgi_diagnostic.py', 'w') as f:
        f.write('''#!/usr/bin/env python3
import sys
import os

# Print diagnostic information
print("=== WSGI Diagnostic ===")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")

# Add project directory
project_dir = '/home/adamcordova/AGTDesigner'
if os.path.exists(project_dir):
    print(f"✓ Found project directory: {project_dir}")
    sys.path.insert(0, project_dir)
else:
    print(f"✗ Project directory not found: {project_dir}")

# Try to import
try:
    from app import create_app
    print("✓ Successfully imported create_app")
    application = create_app()
    print("✓ Successfully created application")
except Exception as e:
    print(f"✗ Error: {e}")
    from flask import Flask
    application = Flask(__name__)
    @application.route('/')
    def error():
        return f"Error: {e}", 500

if __name__ == "__main__":
    application.run()''')
    print("✓ Created wsgi_diagnostic.py")
    
    # Create bulletproof WSGI
    with open('wsgi_bulletproof.py', 'w') as f:
        f.write('''#!/usr/bin/env python3
import sys
import os

# Add multiple possible paths
possible_paths = [
    '/home/adamcordova/AGTDesigner',
    '/home/adamcordova/AGTDesigner/labelMaker_ newgui BACKUP 6.24 copy 17',
    os.path.dirname(os.path.abspath(__file__))
]

for path in possible_paths:
    if os.path.exists(path):
        sys.path.insert(0, path)
        break

# Try to create app
try:
    from app import create_app
    application = create_app()
except Exception as e:
    from flask import Flask
    application = Flask(__name__)
    @application.route('/')
    def error():
        return f"Error: {e}", 500

if __name__ == "__main__":
    application.run()''')
    print("✓ Created wsgi_bulletproof.py")

def main():
    """Main troubleshooting function."""
    print("PythonAnywhere WSGI Troubleshooting")
    print("=" * 50)
    
    check_local_environment()
    generate_wsgi_options()
    create_wsgi_files()
    
    print("\n=== Next Steps ===")
    print("1. Go to your PythonAnywhere dashboard")
    print("2. Navigate to the Web tab")
    print("3. Click on your web app")
    print("4. Go to the WSGI configuration file")
    print("5. Replace the entire content with one of the options above")
    print("6. Start with wsgi_simple.py content")
    print("7. If that doesn't work, try wsgi_diagnostic.py")
    print("8. If still not working, try wsgi_bulletproof.py")
    print("9. Save the file and reload your web app")
    print("10. Check the error logs for diagnostic information")

if __name__ == "__main__":
    main() 