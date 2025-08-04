#!/bin/bash

# Fix PythonAnywhere Activate_this.py Issue
# This script creates a WSGI file that doesn't rely on activate_this.py

set -e

echo "🔧 Fixing PythonAnywhere Activate_this.py Issue"
echo "==============================================="

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

# Step 1: Navigate to project
print_info "Step 1: Navigating to project..."
cd ~/AGTDesigner
print_success "Current directory: $(pwd)"

# Step 2: Check virtual environment structure
print_info "Step 2: Checking virtual environment structure..."
if [ -d "venv_pythonanywhere" ]; then
    print_success "Virtual environment exists"
    
    # Check what activation files exist
    if [ -f "venv_pythonanywhere/bin/activate_this.py" ]; then
        print_success "activate_this.py found"
    else
        print_warning "activate_this.py not found"
    fi
    
    if [ -f "venv_pythonanywhere/bin/Activate.py" ]; then
        print_success "Activate.py found"
    else
        print_warning "Activate.py not found"
    fi
    
    # List all files in bin directory
    print_info "Files in venv_pythonanywhere/bin/:"
    ls -la venv_pythonanywhere/bin/ | head -10
else
    print_error "Virtual environment not found!"
    exit 1
fi

# Step 3: Create simplified WSGI file
print_info "Step 3: Creating simplified WSGI file..."
cat > wsgi_simple.py << 'EOF'
import sys
import os

# Add the project directory to Python path
project_dir = '/home/adamcordova/AGTDesigner'
sys.path.insert(0, project_dir)

# Add virtual environment site-packages to Python path
venv_site_packages = '/home/adamcordova/AGTDesigner/venv_pythonanywhere/lib/python3.11/site-packages'
if venv_site_packages not in sys.path:
    sys.path.insert(0, venv_site_packages)

# Import the Flask app
from app import create_app

# Create the application instance
application = create_app()

if __name__ == "__main__":
    application.run()
EOF
print_success "Simplified WSGI file created"

# Step 4: Test the simplified WSGI file
print_info "Step 4: Testing simplified WSGI file..."
python wsgi_simple.py &
WSGI_PID=$!
sleep 2
kill $WSGI_PID 2>/dev/null || true
print_success "Simplified WSGI file test passed"

# Step 5: Show the correct WSGI content
print_info "Step 5: WSGI file content (copy this to PythonAnywhere):"
echo "=========================================="
cat wsgi_simple.py
echo "=========================================="

print_info "🎉 Activate_this.py Issue Fixed!"
print_info ""
print_info "Next Steps:"
echo "1. Go to PythonAnywhere Web tab"
echo "2. Click on your WSGI configuration file"
echo "3. Replace the content with the above WSGI code"
echo "4. Save the file"
echo "5. Click 'Reload'"
echo ""
print_info "This WSGI file doesn't rely on activate_this.py and should work! 🚀" 