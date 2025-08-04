#!/bin/bash

# Complete PythonAnywhere Deployment Script for Label Maker
# This script handles the full deployment process

set -e  # Exit on any error

echo "🚀 Starting complete PythonAnywhere deployment for Label Maker..."

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

# Step 1: Navigate to home directory
print_status "Step 1: Navigating to home directory..."
cd ~
print_success "Current directory: $(pwd)"

# Step 2: Clone or update repository
if [ -d "AGTDesigner" ]; then
    print_status "Step 2: Updating existing repository..."
    cd AGTDesigner
    git pull origin main
    print_success "Repository updated successfully"
else
    print_status "Step 2: Cloning repository..."
    git clone https://github.com/leruseadam/AGTDesigner.git
    cd AGTDesigner
    print_success "Repository cloned successfully"
fi

# Step 3: Remove existing virtual environment if it exists
if [ -d "venv_pythonanywhere" ]; then
    print_status "Step 3: Removing existing virtual environment..."
    rm -rf venv_pythonanywhere
    print_success "Old virtual environment removed"
fi

# Step 4: Create new virtual environment
print_status "Step 4: Creating new virtual environment..."
python3.11 -m venv venv_pythonanywhere
print_success "Virtual environment created"

# Step 5: Activate virtual environment
print_status "Step 5: Activating virtual environment..."
source venv_pythonanywhere/bin/activate
print_success "Virtual environment activated: $(which python)"

# Step 6: Upgrade pip
print_status "Step 6: Upgrading pip..."
pip install --upgrade pip
print_success "Pip upgraded"

# Step 7: Install dependencies
print_status "Step 7: Installing dependencies..."
if [ -f "requirements_pythonanywhere.txt" ]; then
    pip install -r requirements_pythonanywhere.txt
else
    print_warning "requirements_pythonanywhere.txt not found, installing from requirements.txt"
    pip install -r requirements.txt
fi

# Install additional dependencies
print_status "Installing additional dependencies..."
pip install flask-caching python-dotenv gunicorn
print_success "All dependencies installed"

# Step 8: Test application import
print_status "Step 8: Testing application import..."
python -c "from app import create_app; print('✅ Application imports successfully')"
print_success "Application import test passed"

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

# Step 10: Test WSGI file
print_status "Step 10: Testing WSGI file..."
python -m py_compile wsgi.py
print_success "WSGI file syntax is correct"

# Step 11: Create .env file for production settings
print_status "Step 11: Creating production environment file..."
cat > .env << 'EOF'
FLASK_ENV=production
FLASK_DEBUG=False
EOF
print_success "Production environment file created"

# Step 12: Test database loading
print_status "Step 12: Testing database loading..."
python -c "from app import create_app; app = create_app(); print('✅ Database loaded successfully')"
print_success "Database loading test passed"

# Step 13: Set proper permissions
print_status "Step 13: Setting proper permissions..."
chmod 755 .
chmod 644 *.py
chmod 644 .env
print_success "Permissions set correctly"

# Step 14: Create deployment verification script
print_status "Step 14: Creating deployment verification script..."
cat > verify_deployment.py << 'EOF'
#!/usr/bin/env python3
"""
Deployment verification script for PythonAnywhere
"""

import sys
import os

def test_imports():
    """Test all critical imports"""
    try:
        from app import create_app
        print("✅ App import successful")
        return True
    except Exception as e:
        print(f"❌ App import failed: {e}")
        return False

def test_database():
    """Test database loading"""
    try:
        from app import create_app
        app = create_app()
        print("✅ Database loading successful")
        return True
    except Exception as e:
        print(f"❌ Database loading failed: {e}")
        return False

def test_wsgi():
    """Test WSGI configuration"""
    try:
        import wsgi
        print("✅ WSGI configuration successful")
        return True
    except Exception as e:
        print(f"❌ WSGI configuration failed: {e}")
        return False

def main():
    print("🔍 Verifying deployment...")
    
    tests = [
        test_imports,
        test_database,
        test_wsgi
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Deployment verification successful!")
        return 0
    else:
        print("❌ Deployment verification failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
EOF
print_success "Deployment verification script created"

# Step 15: Run verification
print_status "Step 15: Running deployment verification..."
python verify_deployment.py
print_success "Deployment verification completed"

# Step 16: Create restart script
print_status "Step 16: Creating restart script..."
cat > restart_app.sh << 'EOF'
#!/bin/bash
# Restart script for PythonAnywhere web app

echo "🔄 Restarting Label Maker application..."

# Navigate to project directory
cd ~/AGTDesigner

# Activate virtual environment
source venv_pythonanywhere/bin/activate

# Test application
python verify_deployment.py

if [ $? -eq 0 ]; then
    echo "✅ Application ready for restart"
    echo "📝 Please go to PythonAnywhere Web tab and click 'Reload'"
else
    echo "❌ Application verification failed"
    exit 1
fi
EOF

chmod +x restart_app.sh
print_success "Restart script created"

# Final summary
echo ""
echo "🎉 DEPLOYMENT COMPLETE!"
echo "========================"
echo ""
echo "📁 Project location: ~/AGTDesigner"
echo "🐍 Virtual environment: ~/AGTDesigner/venv_pythonanywhere"
echo "🔧 WSGI file: ~/AGTDesigner/wsgi.py"
echo ""
echo "📋 Next steps:"
echo "1. Go to PythonAnywhere Web tab"
echo "2. Create a new web app (Manual configuration)"
echo "3. Set source code to: /home/yourusername/AGTDesigner"
echo "4. Set working directory to: /home/yourusername/AGTDesigner"
echo "5. Set WSGI file to: /var/www/yourusername_pythonanywhere_com_wsgi.py"
echo "6. Set virtual environment to: /home/yourusername/AGTDesigner/venv_pythonanywhere"
echo "7. Update the WSGI file content with the provided configuration"
echo "8. Click 'Reload' to start the application"
echo ""
echo "🔗 Your application will be available at:"
echo "   https://yourusername.pythonanywhere.com"
echo ""
echo "🔄 To restart the app later, run:"
echo "   ./restart_app.sh"
echo ""
print_success "Deployment script completed successfully!" 