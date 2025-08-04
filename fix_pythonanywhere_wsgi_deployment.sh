#!/bin/bash

echo "Fixing PythonAnywhere WSGI file..."

# Create the corrected WSGI content
cat > /tmp/wsgi_fixed.py << 'EOF'
import sys
import os

# Add the project directory to Python path
project_dir = '/home/adamcordova/AGTDesigner'
sys.path.insert(0, project_dir)

# Add virtual environment site-packages to Python path
venv_site_packages = '/home/adamcordova/AGTDesigner/venv_pythonanywhere/lib/python3.11/site-packages'
if os.path.exists(venv_site_packages) and venv_site_packages not in sys.path:
    sys.path.insert(0, venv_site_packages)

# Set environment variables for the virtual environment
os.environ['VIRTUAL_ENV'] = '/home/adamcordova/AGTDesigner/venv_pythonanywhere'
os.environ['PATH'] = '/home/adamcordova/AGTDesigner/venv_pythonanywhere/bin:' + os.environ.get('PATH', '')

# Import the Flask app
from app import create_app

# Create the application instance
application = create_app()

if __name__ == "__main__":
    application.run()
EOF

echo "WSGI file content created. Please copy this content to your PythonAnywhere WSGI file:"
echo ""
cat /tmp/wsgi_fixed.py
echo ""
echo "Steps to fix:"
echo "1. Go to your PythonAnywhere dashboard"
echo "2. Navigate to the Web tab"
echo "3. Click on your web app"
echo "4. Go to the WSGI configuration file"
echo "5. Replace the entire content with the above code"
echo "6. Save the file"
echo "7. Reload your web app"
echo ""
echo "The error was caused by trying to execute shell script syntax as Python code."
echo "This corrected version properly handles the virtual environment setup." 