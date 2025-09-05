#!/bin/bash
# Update PythonAnywhere deployment script

echo "🚀 Updating PythonAnywhere deployment..."

# Step 1: Pull latest changes
echo "📥 Pulling latest changes..."
git pull

# Step 2: Install missing dependencies
echo "📦 Installing missing dependencies..."
source venv_pythonanywhere_fresh/bin/activate
pip install flask-caching

# Step 3: Update WSGI file with fixed version
echo "🔧 Updating WSGI file..."
cat > /var/www/www_agtpricetags_com_wsgi.py << 'EOF'
#!/usr/bin/env python3
"""
PythonAnywhere WSGI configuration - Fixed for directory path issues
This fixes the chdir() errors and logging issues
"""

import os
import sys
import logging

# Fix the directory path issue
project_dir = '/home/adamcordova/labelMaker_fresh'

# Verify directory exists, fallback to current directory
if not os.path.exists(project_dir):
    project_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"⚠️  Project directory not found, using current directory: {project_dir}")

# Add the project directory to Python path
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

# Set environment variables for PythonAnywhere
os.environ['PYTHONANYWHERE_SITE'] = 'True'
os.environ['PYTHONANYWHERE_DOMAIN'] = 'www.agtpricetags.com'
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = 'False'

# Configure logging to prevent "Message too long" errors
logging.basicConfig(
    level=logging.ERROR,  # Only show errors to reduce log size
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

# Suppress verbose logging from all libraries
logging.getLogger('werkzeug').setLevel(logging.ERROR)
logging.getLogger('urllib3').setLevel(logging.ERROR)
logging.getLogger('requests').setLevel(logging.ERROR)
logging.getLogger('pandas').setLevel(logging.ERROR)
logging.getLogger('openpyxl').setLevel(logging.ERROR)
logging.getLogger('xlrd').setLevel(logging.ERROR)

# Import and configure the Flask app
try:
    from app import app
    
    # Configure Flask for PythonAnywhere
    app.config['DEBUG'] = False
    app.config['TESTING'] = False
    app.config['TEMPLATES_AUTO_RELOAD'] = False
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000
    
    # Set the application
    application = app
    
    # Log successful startup
    logging.info("WSGI application loaded successfully")
    
except ImportError as e:
    logging.error(f"Failed to import Flask app: {e}")
    raise
except Exception as e:
    logging.error(f"Error configuring Flask app: {e}")
    raise

if __name__ == "__main__":
    application.run()
EOF

echo "✅ WSGI file updated!"

# Step 4: Restart web app
echo "🔄 Please restart your web app in PythonAnywhere Web tab"
echo "✅ Update complete!"