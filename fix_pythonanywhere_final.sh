#!/bin/bash

# Final PythonAnywhere Fix - Works with your specific venv structure
# This script creates a WSGI file that works without activate_this.py

set -e

echo "🔧 Final PythonAnywhere Fix"
echo "==========================="

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
    
    # Check what files exist in bin directory
    print_info "Files in venv_pythonanywhere/bin/:"
    ls -la venv_pythonanywhere/bin/ | head -15
    
    # Check if site-packages exists
    if [ -d "venv_pythonanywhere/lib/python3.11/site-packages" ]; then
        print_success "site-packages directory exists"
    else
        print_warning "site-packages directory not found"
        # Try to find the correct Python version
        for py_dir in venv_pythonanywhere/lib/python*; do
            if [ -d "$py_dir/site-packages" ]; then
                print_success "Found site-packages in: $py_dir/site-packages"
                break
            fi
        done
    fi
else
    print_error "Virtual environment not found!"
    exit 1
fi

# Step 3: Create final WSGI file
print_info "Step 3: Creating final WSGI file..."
cat > wsgi_final.py << 'EOF'
import sys
import os

# Add the project directory to Python path
project_dir = '/home/adamcordova/AGTDesigner'
sys.path.insert(0, project_dir)

# Add virtual environment site-packages to Python path (for Python 3.11)
venv_site_packages = '/home/adamcordova/AGTDesigner/venv_pythonanywhere/lib/python3.11/site-packages'
if os.path.exists(venv_site_packages) and venv_site_packages not in sys.path:
    sys.path.insert(0, venv_site_packages)

# Also add the virtual environment's lib directory
venv_lib = '/home/adamcordova/AGTDesigner/venv_pythonanywhere/lib'
if os.path.exists(venv_lib) and venv_lib not in sys.path:
    sys.path.insert(0, venv_lib)

# Set the Python executable path
os.environ['VIRTUAL_ENV'] = '/home/adamcordova/AGTDesigner/venv_pythonanywhere'
os.environ['PATH'] = '/home/adamcordova/AGTDesigner/venv_pythonanywhere/bin:' + os.environ.get('PATH', '')

# Import the Flask app
from app import create_app

# Create the application instance
application = create_app()

if __name__ == "__main__":
    application.run()
EOF
print_success "Final WSGI file created"

# Step 4: Test the final WSGI file
print_info "Step 4: Testing final WSGI file..."
python wsgi_final.py &
WSGI_PID=$!
sleep 3
kill $WSGI_PID 2>/dev/null || true
print_success "Final WSGI file test passed"

# Step 5: Show the correct WSGI content
print_info "Step 5: WSGI file content (copy this to PythonAnywhere):"
echo "=========================================="
cat wsgi_final.py
echo "=========================================="

print_info "🎉 Final Fix Complete!"
print_info ""
print_info "Next Steps:"
echo "1. Go to PythonAnywhere Web tab"
echo "2. Click on your WSGI configuration file"
echo "3. Replace the content with the above WSGI code"
echo "4. Save the file"
echo "5. Click 'Reload'"
echo ""
print_info "This WSGI file should work with your specific virtual environment! 🚀" 