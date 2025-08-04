#!/bin/bash

# Fix Missing Dependencies on PythonAnywhere
# Run this script on PythonAnywhere to install missing dependencies

set -e

echo "🔧 Fixing Missing Dependencies on PythonAnywhere"
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Step 1: Navigate to project directory
print_status "Step 1: Navigating to project directory..."
cd ~/AGTDesigner
print_success "Current directory: $(pwd)"

# Step 2: Activate virtual environment
print_status "Step 2: Activating virtual environment..."
if [ -d "venv_pythonanywhere" ]; then
    source venv_pythonanywhere/bin/activate
    print_success "Virtual environment activated"
else
    print_warning "Virtual environment not found, creating new one..."
    python3.11 -m venv venv_pythonanywhere
    source venv_pythonanywhere/bin/activate
    print_success "New virtual environment created and activated"
fi

# Step 3: Upgrade pip
print_status "Step 3: Upgrading pip..."
pip install --upgrade pip
print_success "Pip upgraded"

# Step 4: Install missing dependencies
print_status "Step 4: Installing missing dependencies..."
pip install flask-cors
pip install flask-caching
pip install python-dotenv
pip install gunicorn
pip install werkzeug
pip install jinja2
pip install pandas
pip install numpy
pip install openpyxl
pip install python-docx
pip install pillow
print_success "Core dependencies installed"

# Step 5: Install additional dependencies that might be needed
print_status "Step 5: Installing additional dependencies..."
pip install docxtpl
pip install xlrd
pip install xlsxwriter
pip install requests
pip install beautifulsoup4
pip install lxml
print_success "Additional dependencies installed"

# Step 6: Test the application
print_status "Step 6: Testing application imports..."
python -c "
try:
    from flask import Flask
    from flask_cors import CORS
    from flask_caching import Cache
    from app import create_app
    print('✅ All imports successful!')
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
"
print_success "Application test passed!"

# Step 7: Update WSGI file if needed
print_status "Step 7: Checking WSGI configuration..."
if [ -f "wsgi.py" ]; then
    print_success "WSGI file exists"
else
    print_warning "Creating WSGI file..."
    cat > wsgi.py << 'EOF'
import sys
import os

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Activate virtual environment
activate_this = os.path.join(project_dir, 'venv_pythonanywhere', 'bin', 'activate_this.py')
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

# Import the Flask app
from app import create_app

# Create the application instance
application = create_app()

if __name__ == "__main__":
    application.run()
EOF
    print_success "WSGI file created"
fi

# Step 8: Create a requirements file for future reference
print_status "Step 8: Creating updated requirements file..."
pip freeze > requirements_pythonanywhere_fixed.txt
print_success "Requirements file updated"

# Step 9: Set permissions
print_status "Step 9: Setting permissions..."
chmod 755 venv_pythonanywhere
chmod 644 *.py
print_success "Permissions set"

# Final status
echo ""
echo "🎉 Missing Dependencies Fixed!"
echo "=============================="
echo ""
echo "📦 Dependencies installed:"
echo "   - flask-cors"
echo "   - flask-caching"
echo "   - python-dotenv"
echo "   - gunicorn"
echo "   - All other required packages"
echo ""
echo "🐍 Virtual environment: venv_pythonanywhere"
echo "✅ Application test: PASSED"
echo ""
echo "Next Steps:"
echo "1. Go to PythonAnywhere Web tab"
echo "2. Reload your web app"
echo "3. Check for any remaining errors"
echo ""
echo "Your application should now work! 🚀" 