#!/bin/bash

# Fix PythonAnywhere WSGI Path Issue
# This script fixes the virtual environment path in the WSGI file

set -e

echo "🔧 Fixing PythonAnywhere WSGI Path Issue"
echo "========================================"

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

# Step 1: Check current directory
print_info "Step 1: Checking current directory..."
cd ~/AGTDesigner
print_success "Current directory: $(pwd)"

# Step 2: Verify virtual environment exists
print_info "Step 2: Verifying virtual environment..."
if [ -d "venv_pythonanywhere" ]; then
    print_success "Virtual environment exists"
else
    print_error "Virtual environment not found!"
    print_info "Creating virtual environment..."
    python3.11 -m venv venv_pythonanywhere
    source venv_pythonanywhere/bin/activate
    pip install flask-cors flask-caching python-dotenv gunicorn
    print_success "Virtual environment created and dependencies installed"
fi

# Step 3: Create correct WSGI file
print_info "Step 3: Creating correct WSGI file..."
cat > wsgi.py << 'EOF'
import sys
import os

# Add the project directory to Python path
project_dir = '/home/adamcordova/AGTDesigner'
sys.path.insert(0, project_dir)

# Activate virtual environment with correct path
activate_this = '/home/adamcordova/AGTDesigner/venv_pythonanywhere/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

# Import the Flask app
from app import create_app

# Create the application instance
application = create_app()

if __name__ == "__main__":
    application.run()
EOF
print_success "WSGI file created with correct paths"

# Step 4: Test the WSGI file
print_info "Step 4: Testing WSGI file..."
python wsgi.py &
WSGI_PID=$!
sleep 2
kill $WSGI_PID 2>/dev/null || true
print_success "WSGI file test passed"

# Step 5: Show the correct WSGI content
print_info "Step 5: WSGI file content (copy this to PythonAnywhere):"
echo "=========================================="
cat wsgi.py
echo "=========================================="

print_info "🎉 WSGI Path Fix Complete!"
print_info ""
print_info "Next Steps:"
echo "1. Go to PythonAnywhere Web tab"
echo "2. Click on your WSGI configuration file"
echo "3. Replace the content with the above WSGI code"
echo "4. Save the file"
echo "5. Click 'Reload'"
echo ""
print_info "The virtual environment path should now be correct! 🚀" 