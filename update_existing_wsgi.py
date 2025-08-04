#!/usr/bin/env python3
"""
Script to update the existing PythonAnywhere WSGI file with performance optimizations
"""

def print_update_instructions():
    """Print instructions for updating the existing WSGI file."""
    
    print("🔧 Update Existing WSGI File - Performance Optimization")
    print("=" * 60)
    print()
    
    print("📋 STEP 1: Access the WSGI File in PythonAnywhere")
    print("-" * 50)
    print("1. Log into your PythonAnywhere account")
    print("2. Go to the 'Files' tab")
    print("3. Navigate to: /var/www/")
    print("4. Find and click on: www_agtpricetags_com_wsgi.py")
    print("5. Click 'Edit' to open the file")
    print()
    
    print("📋 STEP 2: Replace the File Content")
    print("-" * 50)
    print("1. Select all content in the file (Ctrl+A)")
    print("2. Delete all existing content")
    print("3. Copy and paste the optimized content below")
    print("4. Click 'Save'")
    print()
    
    print("📋 STEP 3: Reload the Web App")
    print("-" * 50)
    print("1. Go to the 'Web' tab")
    print("2. Click 'Reload' for your web app")
    print("3. Wait for the reload to complete")
    print("4. Check the error logs for performance improvement")
    print()

def get_wsgi_content():
    """Return the optimized WSGI content."""
    
    return '''#!/usr/bin/env python3
"""
PythonAnywhere WSGI configuration - Optimized for Performance
Fixed for use with /var/www/www_agtpricetags_com_wsgi.py path
"""

import os
import sys
import logging

# Add the project directory to Python path
# Use the actual project location on PythonAnywhere
project_dir = '/home/adamcordova/AGTDesigner'
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

# Set environment variables for PythonAnywhere
os.environ['PYTHONANYWHERE_SITE'] = 'True'
os.environ['PYTHONANYWHERE_DOMAIN'] = 'www.agtpricetags.com'

# Performance optimization: Disable default file loading during startup
os.environ['DISABLE_DEFAULT_FILE_LOADING'] = 'True'
os.environ['LAZY_LOADING_ENABLED'] = 'True'

# Configure logging for PythonAnywhere - Reduce verbosity for better performance
try:
    logging.basicConfig(
        level=logging.ERROR,  # Changed from WARNING to ERROR for better performance
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('/home/adamcordova/pythonanywhere.log')
        ]
    )
except (OSError, PermissionError):
    # Fallback to console-only logging if file logging fails
    logging.basicConfig(
        level=logging.ERROR,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )

# Suppress verbose logging from all libraries
logging.getLogger('werkzeug').setLevel(logging.ERROR)
logging.getLogger('urllib3').setLevel(logging.ERROR)
logging.getLogger('requests').setLevel(logging.ERROR)
logging.getLogger('pandas').setLevel(logging.ERROR)
logging.getLogger('openpyxl').setLevel(logging.ERROR)
logging.getLogger('xlrd').setLevel(logging.ERROR)

# Import and configure the Flask app with lazy loading
try:
    from app import app
    
    # Configure Flask for PythonAnywhere with performance optimizations
    app.config['DEBUG'] = False
    app.config['TESTING'] = False
    app.config['TEMPLATES_AUTO_RELOAD'] = False
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000
    
    # Additional performance optimizations
    app.config['JSON_SORT_KEYS'] = False  # Disable JSON sorting for better performance
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False  # Disable pretty printing
    
    # Set the application
    application = app
    
    # Log successful startup
    logging.info("WSGI application loaded successfully with performance optimizations")
    
except ImportError as e:
    logging.error(f"Failed to import Flask app: {e}")
    raise
except Exception as e:
    logging.error(f"Error configuring Flask app: {e}")
    raise

if __name__ == "__main__":
    application.run()
'''

def save_wsgi_content_to_file():
    """Save the WSGI content to a local file for easy copying."""
    
    content = get_wsgi_content()
    filename = "wsgi_content_for_pythonanywhere.py"
    
    with open(filename, 'w') as f:
        f.write(content)
    
    print(f"✅ WSGI content saved to: {filename}")
    print("📋 You can copy this file content to PythonAnywhere")
    print()

def main():
    """Main function."""
    
    print_update_instructions()
    
    print("📄 OPTIMIZED WSGI CONTENT (copy this to PythonAnywhere):")
    print("=" * 60)
    print()
    print(get_wsgi_content())
    print()
    print("=" * 60)
    
    print("❓ Would you like to save this content to a local file? (y/n): ", end="")
    response = input().lower().strip()
    
    if response in ['y', 'yes']:
        save_wsgi_content_to_file()
    
    print("✅ Instructions complete!")
    print("📝 Follow the steps above to update your existing WSGI file.")
    print("🚀 After updating, your app should start in under 10 seconds!")

if __name__ == "__main__":
    main() 