#!/bin/bash
# PythonAnywhere Deployment Script for Label Maker
# This script sets up the complete environment on PythonAnywhere

set -e  # Exit on any error

echo "🚀 Starting Label Maker deployment on PythonAnywhere..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Get current directory
PROJECT_DIR=$(pwd)
print_status "Project directory: $PROJECT_DIR"

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    print_error "app.py not found. Please run this script from the Label Maker project directory."
    exit 1
fi

# Step 1: Create virtual environment
print_status "Creating virtual environment..."
if [ -d "venv_pythonanywhere" ]; then
    print_warning "Virtual environment already exists. Removing old one..."
    rm -rf venv_pythonanywhere
fi

python3.11 -m venv venv_pythonanywhere
print_success "Virtual environment created"

# Step 2: Activate virtual environment
print_status "Activating virtual environment..."
source venv_pythonanywhere/bin/activate

# Step 3: Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Step 4: Install dependencies
print_status "Installing dependencies..."
if [ -f "requirements_production.txt" ]; then
    pip install -r requirements_production.txt
else
    print_warning "requirements_production.txt not found, installing basic dependencies..."
    pip install Flask pandas openpyxl python-docx docxtpl Pillow flask-cors python-dotenv
fi

# Step 5: Install additional production dependencies
print_status "Installing additional production dependencies..."
pip install flask-caching gunicorn

# Step 6: Test the application
print_status "Testing application import..."
python -c "from app import create_app; print('✅ Application imports successfully')"

# Step 7: Create optimized WSGI file
print_status "Creating optimized WSGI file..."
cat > wsgi_optimized.py << 'EOF'
#!/usr/bin/env python3
"""
Optimized WSGI file for PythonAnywhere deployment.
Handles BlockingIOError and provides detailed error reporting.
"""

import sys
import os
from datetime import datetime

# Prevent BlockingIOError
os.environ['PYTHONUNBUFFERED'] = '1'

# Set production environment
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = 'False'

# Add project directory to path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

def safe_log(message):
    """Safe logging that won't cause BlockingIOError."""
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {message}", flush=True)
    except:
        pass

safe_log("🚀 Starting Label Maker WSGI...")

# Activate virtual environment
venv_path = os.path.join(project_dir, 'venv_pythonanywhere')
activate_script = os.path.join(venv_path, 'bin', 'activate_this.py')
if os.path.exists(activate_script):
    with open(activate_script) as file_:
        exec(file_.read(), dict(__file__=activate_script))
    safe_log("✅ Virtual environment activated")

# Create application
try:
    from app import create_app
    application = create_app()
    application.config['DEBUG'] = False
    application.config['TESTING'] = False
    safe_log("✅ Application created successfully")
except Exception as e:
    safe_log(f"❌ Error creating application: {e}")
    from flask import Flask
    application = Flask(__name__)
    @application.route('/')
    def error_page():
        return f"<h1>Error: {str(e)}</h1>", 500

safe_log("🎉 WSGI ready!")
EOF

print_success "Optimized WSGI file created"

# Step 8: Create deployment instructions
print_status "Creating deployment instructions..."
cat > PYTHONANYWHERE_SETUP.md << 'EOF'
# PythonAnywhere Deployment Instructions

## Web App Configuration

1. Go to **Web** tab in PythonAnywhere
2. Click **Add a new web app**
3. Choose **Manual configuration**
4. Python version: **3.11**

## Configure Source Code
- **Source code**: `/home/yourusername/AGTDesigner`
- **Working directory**: `/home/yourusername/AGTDesigner`
- **WSGI configuration file**: `/var/www/yourusername_pythonanywhere_com_wsgi.py`

## Update WSGI File
Replace the content of the WSGI file with the content from `wsgi_optimized.py`

## Configure Virtual Environment
- **Virtual environment**: `/home/yourusername/AGTDesigner/venv_pythonanywhere`

## Environment Variables
Add these to your WSGI file:
```python
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = 'False'
os.environ['PYTHONUNBUFFERED'] = '1'
```

## Reload Web App
Click **Reload** button in the Web tab.

## Your Application URL
Your application will be available at:
```
https://yourusername.pythonanywhere.com
```
EOF

print_success "Deployment instructions created"

# Step 9: Create a test script
print_status "Creating test script..."
cat > test_deployment.py << 'EOF'
#!/usr/bin/env python3
"""
Test script to verify deployment is working correctly.
"""

import sys
import os

# Add project directory to path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

def test_imports():
    """Test all critical imports."""
    print("Testing imports...")
    
    try:
        import flask
        print("✅ Flask imported successfully")
    except ImportError as e:
        print(f"❌ Flask import failed: {e}")
        return False
    
    try:
        import pandas
        print("✅ Pandas imported successfully")
    except ImportError as e:
        print(f"❌ Pandas import failed: {e}")
        return False
    
    try:
        import openpyxl
        print("✅ OpenPyXL imported successfully")
    except ImportError as e:
        print(f"❌ OpenPyXL import failed: {e}")
        return False
    
    try:
        from docx import Document
        print("✅ python-docx imported successfully")
    except ImportError as e:
        print(f"❌ python-docx import failed: {e}")
        return False
    
    return True

def test_app_creation():
    """Test Flask app creation."""
    print("\nTesting app creation...")
    
    try:
        from app import create_app
        app = create_app()
        print("✅ Flask app created successfully")
        return True
    except Exception as e:
        print(f"❌ Flask app creation failed: {e}")
        return False

def test_wsgi():
    """Test WSGI file."""
    print("\nTesting WSGI file...")
    
    try:
        exec(open('wsgi_optimized.py').read())
        print("✅ WSGI file executed successfully")
        return True
    except Exception as e:
        print(f"❌ WSGI file execution failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Running deployment tests...\n")
    
    success = True
    success &= test_imports()
    success &= test_app_creation()
    success &= test_wsgi()
    
    if success:
        print("\n🎉 All tests passed! Deployment is ready.")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        sys.exit(1)
EOF

print_success "Test script created"

# Step 10: Run tests
print_status "Running deployment tests..."
python test_deployment.py

print_success "Deployment completed successfully!"
print_status ""
print_status "Next steps:"
print_status "1. Go to PythonAnywhere Web tab"
print_status "2. Configure your web app to use this directory"
print_status "3. Set the WSGI file to use wsgi_optimized.py"
print_status "4. Set the virtual environment to venv_pythonanywhere"
print_status "5. Reload the web app"
print_status ""
print_status "See PYTHONANYWHERE_SETUP.md for detailed instructions." 