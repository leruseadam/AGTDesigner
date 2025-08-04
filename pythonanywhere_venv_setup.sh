#!/bin/bash

# PythonAnywhere Virtual Environment Setup Script
# Run this script on PythonAnywhere to set up your Label Maker project

set -e  # Exit on any error

echo "🚀 Setting up Label Maker Virtual Environment on PythonAnywhere"
echo "================================================================"

# Configuration
PYTHON_VERSION="3.11"
PROJECT_NAME="AGTDesigner"
GITHUB_REPO="https://github.com/leruseadam/AGTDesigner.git"
BRANCH="main"

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

# Check if we're on PythonAnywhere
if [[ "$HOSTNAME" == *"pythonanywhere"* ]]; then
    print_success "Detected PythonAnywhere environment"
else
    print_warning "This script is designed for PythonAnywhere"
fi

# Step 1: Navigate to home directory
print_status "Step 1: Setting up project directory..."
cd ~
print_success "Current directory: $(pwd)"

# Step 2: Clone or update repository
if [ -d "$PROJECT_NAME" ]; then
    print_status "Step 2: Updating existing repository..."
    cd $PROJECT_NAME
    git fetch origin
    git checkout $BRANCH
    git pull origin $BRANCH
    print_success "Repository updated successfully"
else
    print_status "Step 2: Cloning repository..."
    git clone -b $BRANCH $GITHUB_REPO
    cd $PROJECT_NAME
    print_success "Repository cloned successfully"
fi

# Step 3: Create virtual environment
print_status "Step 3: Creating virtual environment..."
if [ -d "venv_pythonanywhere" ]; then
    print_warning "Virtual environment already exists. Removing old one..."
    rm -rf venv_pythonanywhere
fi

python3.11 -m venv venv_pythonanywhere
print_success "Virtual environment created: venv_pythonanywhere"

# Step 4: Activate virtual environment
print_status "Step 4: Activating virtual environment..."
source venv_pythonanywhere/bin/activate
print_success "Virtual environment activated"

# Step 5: Upgrade pip
print_status "Step 5: Upgrading pip..."
pip install --upgrade pip
print_success "Pip upgraded successfully"

# Step 6: Install dependencies
print_status "Step 6: Installing dependencies..."
if [ -f "requirements_pythonanywhere.txt" ]; then
    pip install -r requirements_pythonanywhere.txt
    print_success "Dependencies installed from requirements_pythonanywhere.txt"
else
    print_warning "requirements_pythonanywhere.txt not found, installing basic dependencies..."
    pip install flask flask-cors werkzeug jinja2 pandas numpy openpyxl python-docx pillow gunicorn python-dotenv
    print_success "Basic dependencies installed"
fi

# Step 7: Install additional dependencies
print_status "Step 7: Installing additional dependencies..."
pip install flask-caching python-dotenv gunicorn
print_success "Additional dependencies installed"

# Step 8: Test the application
print_status "Step 8: Testing application..."
python -c "from app import create_app; print('✅ Application imports successfully!')"
print_success "Application test passed!"

# Step 9: Create WSGI configuration
print_status "Step 9: Creating WSGI configuration..."
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
print_success "WSGI configuration created"

# Step 10: Set permissions
print_status "Step 10: Setting permissions..."
chmod 755 venv_pythonanywhere
chmod 644 *.py
print_success "Permissions set"

# Step 11: Create deployment summary
print_status "Step 11: Creating deployment summary..."
cat > PYTHONANYWHERE_DEPLOYMENT_SUMMARY.md << 'EOF'
# PythonAnywhere Deployment Summary

## ✅ Setup Complete!

### Project Details:
- **Repository**: https://github.com/leruseadam/AGTDesigner.git
- **Branch**: main
- **Virtual Environment**: venv_pythonanywhere
- **Python Version**: 3.11

### Next Steps:

1. **Configure Web App on PythonAnywhere:**
   - Go to Web tab
   - Add new web app
   - Choose Manual configuration
   - Python version: 3.11

2. **Set Source Code:**
   - Source code: `/home/yourusername/AGTDesigner`
   - Working directory: `/home/yourusername/AGTDesigner`

3. **Configure WSGI:**
   - WSGI file: `/var/www/yourusername_pythonanywhere_com_wsgi.py`
   - Use the wsgi.py file created in this directory

4. **Set Virtual Environment:**
   - Virtual environment: `/home/yourusername/AGTDesigner/venv_pythonanywhere`

5. **Reload Web App:**
   - Click Reload button
   - Check for any errors

### Your Application URL:
https://yourusername.pythonanywhere.com

### Troubleshooting:
- Check error logs in PythonAnywhere Web tab
- Verify virtual environment is activated
- Ensure all dependencies are installed
EOF
print_success "Deployment summary created"

# Final status
echo ""
echo "🎉 PythonAnywhere Virtual Environment Setup Complete!"
echo "=================================================="
echo ""
echo "📁 Project Location: $(pwd)"
echo "🐍 Virtual Environment: venv_pythonanywhere"
echo "📦 Dependencies: Installed and tested"
echo "🔧 WSGI Configuration: Created"
echo ""
echo "Next Steps:"
echo "1. Go to PythonAnywhere Web tab"
echo "2. Configure your web app"
echo "3. Set the virtual environment path"
echo "4. Reload your web app"
echo ""
echo "Your application is ready for deployment! 🚀" 