#!/usr/bin/env python3
"""
Diagnostic script for WSGI issues on PythonAnywhere
"""

def print_diagnostic_steps():
    """Print diagnostic steps to identify the issue."""
    
    print("🔍 WSGI Issue Diagnosis Guide")
    print("=" * 50)
    print()
    
    print("📋 STEP 1: Check PythonAnywhere Error Logs")
    print("-" * 40)
    print("1. Go to PythonAnywhere dashboard")
    print("2. Click 'Web' tab")
    print("3. Click on your web app")
    print("4. Click 'Error log' button")
    print("5. Look for specific error messages")
    print("6. Copy any error messages you see")
    print()
    
    print("📋 STEP 2: Check File Paths")
    print("-" * 40)
    print("1. Go to 'Files' tab in PythonAnywhere")
    print("2. Navigate to: /home/adamcordova/AGTDesigner/")
    print("3. Verify these files exist:")
    print("   - app.py")
    print("   - src/ directory")
    print("   - All required Python files")
    print()
    
    print("📋 STEP 3: Test Simple WSGI Configuration")
    print("-" * 40)
    print("1. Edit the WSGI file: /var/www/www_agtpricetags_com_wsgi.py")
    print("2. Replace with this minimal content:")
    print()
    print("import sys")
    print("sys.path.insert(0, '/home/adamcordova/AGTDesigner')")
    print("from app import app")
    print("application = app")
    print()
    print("3. Save and reload")
    print()
    
    print("📋 STEP 4: Check Python Version")
    print("-" * 40)
    print("1. Go to 'Consoles' tab in PythonAnywhere")
    print("2. Start a new console")
    print("3. Run: python --version")
    print("4. Run: python -c 'import sys; print(sys.path)'")
    print("5. Run: python -c 'import os; print(os.getcwd())'")
    print()

def get_minimal_wsgi_content():
    """Return minimal WSGI content for testing."""
    
    return '''import sys
sys.path.insert(0, '/home/adamcordova/AGTDesigner')

try:
    from app import app
    application = app
    print("WSGI: App loaded successfully")
except Exception as e:
    print(f"WSGI: Error loading app - {e}")
    raise
'''

def get_debug_wsgi_content():
    """Return debug WSGI content with more logging."""
    
    return '''import sys
import os

print("WSGI: Starting configuration...")

# Add project path
project_dir = '/home/adamcordova/AGTDesigner'
print(f"WSGI: Project directory: {project_dir}")
print(f"WSGI: Directory exists: {os.path.exists(project_dir)}")

sys.path.insert(0, project_dir)
print(f"WSGI: Python path: {sys.path[:3]}")

# Set environment variables
os.environ['PYTHONANYWHERE_SITE'] = 'True'
os.environ['DISABLE_DEFAULT_FILE_LOADING'] = 'True'
os.environ['LAZY_LOADING_ENABLED'] = 'True'

print("WSGI: Environment variables set")

try:
    print("WSGI: Attempting to import app...")
    from app import app
    application = app
    print("WSGI: App imported successfully")
except ImportError as e:
    print(f"WSGI: Import error - {e}")
    raise
except Exception as e:
    print(f"WSGI: Other error - {e}")
    raise
'''

def main():
    """Main diagnostic function."""
    
    print_diagnostic_steps()
    
    print("📄 MINIMAL WSGI CONTENT (for testing):")
    print("=" * 50)
    print(get_minimal_wsgi_content())
    print()
    
    print("📄 DEBUG WSGI CONTENT (with logging):")
    print("=" * 50)
    print(get_debug_wsgi_content())
    print()
    
    print("❓ What specific error are you seeing?")
    print("Please share:")
    print("1. Error messages from PythonAnywhere logs")
    print("2. Whether the app loads at all")
    print("3. Any specific import errors")
    print()
    
    print("💡 Common Issues:")
    print("- Wrong project directory path")
    print("- Missing required files")
    print("- Python version mismatch")
    print("- Import path issues")
    print("- Permission problems")

if __name__ == "__main__":
    main() 