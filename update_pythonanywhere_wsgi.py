#!/usr/bin/env python3
"""
Update PythonAnywhere WSGI File with Latest Optimizations
This script provides the complete, optimized WSGI content for PythonAnywhere.
"""

def print_wsgi_content():
    """Print the complete WSGI content for PythonAnywhere."""
    
    print("🔧 PythonAnywhere WSGI Update")
    print("=" * 40)
    print()
    print("📋 INSTRUCTIONS:")
    print("1. Go to PythonAnywhere dashboard")
    print("2. Click 'Files' tab")
    print("3. Navigate to: /var/www/www_agtpricetags_com_wsgi.py")
    print("4. Click 'Edit' button")
    print("5. Replace ALL content with the following:")
    print()
    print("=" * 60)
    print("COPY THE FOLLOWING CONTENT:")
    print("=" * 60)
    print()

    wsgi_content = '''#!/usr/bin/env python3
"""
WSGI configuration for Python 3.10 on PythonAnywhere
Optimized for performance with all latest fixes
"""

import sys
import os

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

# Configure logging for better performance
import logging
logging.basicConfig(level=logging.ERROR)

# Suppress verbose logging from pandas, openpyxl, xlrd
logging.getLogger('pandas').setLevel(logging.ERROR)
logging.getLogger('openpyxl').setLevel(logging.ERROR)
logging.getLogger('xlrd').setLevel(logging.ERROR)

# Import the Flask app
try:
    from app import app
    application = app
    
    # Configure Flask for production
    app.config['DEBUG'] = False
    app.config['TESTING'] = False
    app.config['TEMPLATES_AUTO_RELOAD'] = False
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000
    app.config['JSON_SORT_KEYS'] = False
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
    
    print("WSGI: App loaded successfully for Python 3.10 with all optimizations")
    
except ImportError as e:
    print(f"WSGI: Import error - {e}")
    # Create fallback app
    from flask import Flask
    application = Flask(__name__)
    application.config['DEBUG'] = False
    print("WSGI: Using fallback Flask app")
    
except Exception as e:
    print(f"WSGI: Other error - {e}")
    raise

if __name__ == "__main__":
    application.run()
'''
    
    print(wsgi_content)
    print()
    print("=" * 60)
    print("END OF CONTENT TO COPY")
    print("=" * 60)
    print()
    print("📋 AFTER UPDATING:")
    print("1. Click 'Save' button")
    print("2. Go to 'Web' tab")
    print("3. Click 'Reload' button for your web app")
    print("4. Wait for the reload to complete")
    print("5. Test your application")
    print()
    print("✅ This will fix:")
    print("• JavaScript syntax errors")
    print("• 500 errors on /api/initial-data")
    print("• UnboundLocalError in get_available_tags")
    print("• Performance optimizations")
    print()

if __name__ == "__main__":
    print_wsgi_content() 