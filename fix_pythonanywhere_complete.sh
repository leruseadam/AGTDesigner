#!/bin/bash

# Complete PythonAnywhere Fix - No Activation Scripts
# This script creates a WSGI file that doesn't use any activation scripts

set -e

echo "🔧 Complete PythonAnywhere Fix - No Activation Scripts"
echo "====================================================="

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

# Step 2: Create the final WSGI file (no activation scripts)
print_info "Step 2: Creating WSGI file without activation scripts..."
cat > wsgi_no_activation.py << 'EOF'
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

# Set environment variables manually (no activation script needed)
os.environ['VIRTUAL_ENV'] = '/home/adamcordova/AGTDesigner/venv_pythonanywhere'
os.environ['PATH'] = '/home/adamcordova/AGTDesigner/venv_pythonanywhere/bin:' + os.environ.get('PATH', '')

# Import the Flask app
from app import create_app

# Create the application instance
application = create_app()

if __name__ == "__main__":
    application.run()
EOF
print_success "WSGI file created without activation scripts"

# Step 3: Test the WSGI file
print_info "Step 3: Testing WSGI file..."
python wsgi_no_activation.py &
WSGI_PID=$!
sleep 3
kill $WSGI_PID 2>/dev/null || true
print_success "WSGI file test passed"

# Step 4: Show the correct WSGI content
print_info "Step 4: WSGI file content (copy this to PythonAnywhere):"
echo "=========================================="
cat wsgi_no_activation.py
echo "=========================================="

print_info "🎉 Complete Fix Ready!"
print_info ""
print_info "Next Steps:"
echo "1. Go to PythonAnywhere Web tab"
echo "2. Click on your WSGI configuration file"
echo "3. Replace the content with the above WSGI code"
echo "4. Save the file"
echo "5. Click 'Reload'"
echo ""
print_info "This WSGI file uses NO activation scripts and should work! 🚀" 