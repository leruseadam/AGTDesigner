#!/bin/bash

# PythonAnywhere Diagnostic Script
# Run this to identify and fix deployment issues

set -e

echo "🔍 PythonAnywhere Diagnostic Tool"
echo "================================"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️ $1${NC}"; }

# Check current directory
print_info "Current directory: $(pwd)"

# Check if we're in the right project
if [ ! -f "app.py" ]; then
    print_error "app.py not found! Make sure you're in the AGTDesigner directory"
    exit 1
fi
print_success "app.py found"

# Check virtual environment
if [ ! -d "venv_pythonanywhere" ]; then
    print_error "Virtual environment not found!"
    print_info "Creating virtual environment..."
    python3.11 -m venv venv_pythonanywhere
    print_success "Virtual environment created"
else
    print_success "Virtual environment exists"
fi

# Activate virtual environment
print_info "Activating virtual environment..."
source venv_pythonanywhere/bin/activate
print_success "Virtual environment activated"

# Check Python path
print_info "Python path: $(which python)"
print_info "Python version: $(python --version)"

# Test imports
print_info "Testing imports..."
python -c "
try:
    import flask
    print('✅ Flask imported')
except ImportError as e:
    print(f'❌ Flask error: {e}')

try:
    from flask_cors import CORS
    print('✅ flask_cors imported')
except ImportError as e:
    print(f'❌ flask_cors error: {e}')

try:
    from flask_caching import Cache
    print('✅ flask_caching imported')
except ImportError as e:
    print(f'❌ flask_caching error: {e}')

try:
    from app import create_app
    print('✅ app imported')
except ImportError as e:
    print(f'❌ app error: {e}')
"

# Check WSGI file
print_info "Checking WSGI file..."
if [ -f "wsgi.py" ]; then
    print_success "wsgi.py exists"
    echo "WSGI file content:"
    cat wsgi.py
else
    print_warning "wsgi.py not found, creating one..."
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
    print_success "wsgi.py created"
fi

# Check PythonAnywhere specific settings
print_info "PythonAnywhere Configuration:"
echo "Virtual environment path: /home/adamcordova/AGTDesigner/venv_pythonanywhere"
echo "Source code: /home/adamcordova/AGTDesigner"
echo "Working directory: /home/adamcordova/AGTDesigner"

# Test the application
print_info "Testing application..."
python -c "
try:
    from app import create_app
    app = create_app()
    print('✅ Application created successfully')
except Exception as e:
    print(f'❌ Application error: {e}')
"

print_info "Diagnostic complete!"
print_info "Next steps:"
echo "1. Go to PythonAnywhere Web tab"
echo "2. Set virtual environment to: /home/adamcordova/AGTDesigner/venv_pythonanywhere"
echo "3. Copy the wsgi.py content to your WSGI file"
echo "4. Reload your web app" 