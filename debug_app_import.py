#!/usr/bin/env python3
"""
Debug script for app import issues
"""

def print_debug_commands():
    """Print debug commands to run in PythonAnywhere console."""
    
    print("🔍 Debug App Import Issues")
    print("=" * 40)
    print()
    
    print("📋 STEP 1: Test Basic Imports")
    print("-" * 30)
    print("Run these commands in PythonAnywhere console:")
    print()
    print("python -c 'import flask; print(\"Flask: OK\")'")
    print("python -c 'import flask_cors; print(\"flask_cors: OK\")'")
    print("python -c 'import pandas; print(\"pandas: OK\")'")
    print()
    
    print("📋 STEP 2: Test App Import Step by Step")
    print("-" * 30)
    print("cd /home/adamcordova/AGTDesigner")
    print("python -c 'import sys; print(\"Python path:\", sys.path[:3])'")
    print("python -c 'import os; print(\"Current dir:\", os.getcwd())'")
    print("python -c 'import os; print(\"Files in dir:\", os.listdir(\".\")[:5])'")
    print()
    
    print("📋 STEP 3: Test App Import with Error Details")
    print("-" * 30)
    print("python -c '")
    print("try:")
    print("    from app import app")
    print("    print(\"App imported successfully\")")
    print("except Exception as e:")
    print("    print(f\"Error: {e}\")")
    print("    import traceback")
    print("    traceback.print_exc()")
    print("'")
    print()
    
    print("📋 STEP 4: Check App.py File")
    print("-" * 30)
    print("head -20 app.py")
    print("grep -n \"from flask_cors\" app.py")
    print("grep -n \"import\" app.py | head -10")
    print()

def get_minimal_test_app():
    """Return a minimal test app to verify Flask works."""
    
    return '''#!/usr/bin/env python3
"""
Minimal test app to verify Flask works
"""

from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello, Flask is working!'

if __name__ == '__main__':
    app.run()
'''

def get_debug_wsgi_content():
    """Return debug WSGI content with detailed error reporting."""
    
    return '''#!/usr/bin/env python3
"""
Debug WSGI configuration with detailed error reporting
"""

import sys
import os
import traceback

print("WSGI: Starting debug configuration...")

# Add project path
project_dir = '/home/adamcordova/AGTDesigner'
print(f"WSGI: Project directory: {project_dir}")
print(f"WSGI: Directory exists: {os.path.exists(project_dir)}")

sys.path.insert(0, project_dir)
print(f"WSGI: Python path: {sys.path[:3]}")

# Test basic imports
try:
    print("WSGI: Testing basic imports...")
    import flask
    print("WSGI: Flask imported successfully")
    
    import flask_cors
    print("WSGI: flask_cors imported successfully")
    
except ImportError as e:
    print(f"WSGI: Basic import error - {e}")
    traceback.print_exc()

# Try to import app
try:
    print("WSGI: Attempting to import app...")
    from app import app
    application = app
    print("WSGI: App imported successfully")
    
except ImportError as e:
    print(f"WSGI: App import error - {e}")
    traceback.print_exc()
    
    # Create fallback app
    print("WSGI: Creating fallback Flask app...")
    from flask import Flask
    application = Flask(__name__)
    application.config['DEBUG'] = False
    
except Exception as e:
    print(f"WSGI: Other error - {e}")
    traceback.print_exc()
    raise

print("WSGI: Configuration complete")
'''

def main():
    """Main function."""
    
    print_debug_commands()
    
    print("📄 MINIMAL TEST APP (save as test_app.py):")
    print("=" * 40)
    print(get_minimal_test_app())
    print()
    
    print("📄 DEBUG WSGI CONTENT:")
    print("=" * 40)
    print(get_debug_wsgi_content())
    print()
    
    print("💡 Next Steps:")
    print("1. Run the debug commands above")
    print("2. Check what specific error you get")
    print("3. Try the minimal test app")
    print("4. Use the debug WSGI content")
    print()
    
    print("🔍 Common Issues:")
    print("- Syntax error in app.py")
    print("- Missing import in app.py")
    print("- Circular import issue")
    print("- File permission problem")
    print("- Python path issue")

if __name__ == "__main__":
    main() 