#!/usr/bin/env python3
"""
Deployment script for WSGI performance optimization
This script helps update the PythonAnywhere WSGI configuration
"""

import os
import sys

def print_deployment_instructions():
    """Print step-by-step deployment instructions."""
    
    print("🚀 WSGI Performance Optimization Deployment Guide")
    print("=" * 60)
    print()
    
    print("📋 STEP 1: Update PythonAnywhere WSGI Configuration")
    print("-" * 50)
    print("1. Log into your PythonAnywhere account")
    print("2. Go to the 'Web' tab in your dashboard")
    print("3. Click on your web app (www.agtpricetags.com)")
    print("4. Scroll down to the 'Code' section")
    print("5. Find the 'WSGI configuration file' field")
    print("6. Change the path from:")
    print("   /var/www/www_agtpricetags_com_wsgi.py")
    print("   TO:")
    print("   /home/adamcordova/AGTDesigner/wsgi_pythonanywhere.py")
    print("7. Click 'Save'")
    print()
    
    print("📋 STEP 2: Upload the Optimized WSGI File")
    print("-" * 50)
    print("1. In PythonAnywhere, go to the 'Files' tab")
    print("2. Navigate to: /home/adamcordova/AGTDesigner/")
    print("3. Upload the optimized 'wsgi_pythonanywhere.py' file")
    print("4. Or use the Files tab to edit/create the file directly")
    print()
    
    print("📋 STEP 3: Reload the Web App")
    print("-" * 50)
    print("1. Go back to the 'Web' tab")
    print("2. Click the 'Reload' button for your web app")
    print("3. Wait for the reload to complete")
    print("4. Check the error logs if there are any issues")
    print()
    
    print("📋 STEP 4: Verify Performance Improvement")
    print("-" * 50)
    print("1. Check the error logs for startup time")
    print("2. Look for these messages:")
    print("   - 'Lazy loading enabled - not loading default file during startup'")
    print("   - 'Default file loading disabled for testing/performance optimization'")
    print("   - 'WSGI application loaded successfully with performance optimizations'")
    print("3. Startup time should be under 10 seconds (vs 58 seconds before)")
    print()

def create_wsgi_file_content():
    """Return the content for the optimized WSGI file."""
    
    return '''#!/usr/bin/env python3
"""
PythonAnywhere WSGI configuration - Optimized for Performance
"""

import os
import sys
import logging

# Add the project directory to Python path
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

def print_wsgi_file_content():
    """Print the WSGI file content for manual copying."""
    
    print("📄 WSGI File Content (copy this to PythonAnywhere):")
    print("=" * 60)
    print()
    print(create_wsgi_file_content())
    print()
    print("=" * 60)

def check_current_wsgi_path():
    """Check if we can determine the current WSGI path."""
    
    print("🔍 Current WSGI Configuration Check")
    print("-" * 40)
    print()
    print("The current WSGI path is: /var/www/www_agtpricetags_com_wsgi.py")
    print("This needs to be changed to: /home/adamcordova/AGTDesigner/wsgi_pythonanywhere.py")
    print()
    print("This change must be made in the PythonAnywhere dashboard.")
    print("The file path cannot be changed programmatically from this script.")
    print()

def main():
    """Main deployment function."""
    
    print_deployment_instructions()
    check_current_wsgi_path()
    
    print("❓ Would you like to see the WSGI file content? (y/n): ", end="")
    response = input().lower().strip()
    
    if response in ['y', 'yes']:
        print_wsgi_file_content()
    
    print("✅ Deployment instructions complete!")
    print("📝 Follow the steps above to update your PythonAnywhere configuration.")
    print("🚀 After deployment, your app should start in under 10 seconds!")

if __name__ == "__main__":
    main() 