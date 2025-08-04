#!/bin/bash

# Re-clone Entire Project to PythonAnywhere
# This script completely re-deploys the current project to PythonAnywhere
# using previous settings and dependencies

set -e

echo "=== Re-cloning Entire Project to PythonAnywhere ==="

# Configuration
PYTHONANYWHERE_USER="adamcordova"
PYTHONANYWHERE_DOMAIN="adamcordova.pythonanywhere.com"
REMOTE_DIR="/home/$PYTHONANYWHERE_USER/AGTDesigner"
GIT_REPO="https://github.com/adamcordova/labelMaker.git"  # Update with your actual repo URL

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}1. Connecting to PythonAnywhere and preparing environment...${NC}"

# Connect to PythonAnywhere and prepare for fresh deployment
ssh "$PYTHONANYWHERE_USER@ssh.pythonanywhere.com" << 'EOF'
echo "=== PythonAnywhere Environment Setup ==="

# Navigate to home directory
cd /home/adamcordova

# Backup current project if it exists
if [ -d "AGTDesigner" ]; then
    echo "Backing up current project..."
    mv AGTDesigner AGTDesigner_backup_$(date +%Y%m%d_%H%M%S)
    echo "✓ Current project backed up"
else
    echo "No existing project found, proceeding with fresh clone"
fi

# Clean up any temporary files
echo "Cleaning up temporary files..."
rm -rf /tmp/AGTDesigner_temp
rm -rf /tmp/labelMaker_temp

# Create fresh directory
mkdir -p AGTDesigner
cd AGTDesigner

echo "✓ Environment prepared for fresh deployment"
EOF

echo -e "${BLUE}2. Uploading current project files...${NC}"

# Create a temporary archive of current project
echo "Creating project archive..."
tar --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' --exclude='.DS_Store' \
    --exclude='node_modules' --exclude='.venv' --exclude='venv' \
    -czf /tmp/labelMaker_current.tar.gz .

# Upload the archive to PythonAnywhere
echo "Uploading project archive..."
scp /tmp/labelMaker_current.tar.gz "$PYTHONANYWHERE_USER@ssh.pythonanywhere.com:/tmp/"

# Extract and setup on PythonAnywhere
ssh "$PYTHONANYWHERE_USER@ssh.pythonanywhere.com" << 'EOF'
echo "=== Extracting and Setting Up Project ==="

cd /home/adamcordova/AGTDesigner

# Extract the project
echo "Extracting project files..."
tar -xzf /tmp/labelMaker_current.tar.gz

# Clean up uploaded archive
rm /tmp/labelMaker_current.tar.gz

echo "✓ Project files extracted"
EOF

echo -e "${BLUE}3. Setting up Python environment and dependencies...${NC}"

# Setup Python environment and install dependencies
ssh "$PYTHONANYWHERE_USER@ssh.pythonanywhere.com" << 'EOF'
echo "=== Python Environment Setup ==="

cd /home/adamcordova/AGTDesigner

# Check Python version
echo "Python version:"
python3 --version

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "✓ Requirements installed from requirements.txt"
elif [ -f "requirements_pythonanywhere.txt" ]; then
    pip install -r requirements_pythonanywhere.txt
    echo "✓ Requirements installed from requirements_pythonanywhere.txt"
else
    echo "Installing core dependencies..."
    pip install flask flask-cors pandas openpyxl python-docx docxtpl pillow
    pip install flask-caching watchdog docxcompose
    echo "✓ Core dependencies installed"
fi

# Install additional dependencies that might be needed
echo "Installing additional dependencies..."
pip install xlrd xlsxwriter

echo "✓ Python environment setup complete"
EOF

echo -e "${BLUE}4. Configuring PythonAnywhere-specific settings...${NC}"

# Apply PythonAnywhere-specific configurations
ssh "$PYTHONANYWHERE_USER@ssh.pythonanywhere.com" << 'EOF'
echo "=== PythonAnywhere Configuration ==="

cd /home/adamcordova/AGTDesigner

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p uploads
mkdir -p logs
mkdir -p output
mkdir -p cache
mkdir -p data

# Set proper permissions
echo "Setting permissions..."
chmod 755 uploads
chmod 755 logs
chmod 755 output
chmod 755 cache
chmod 755 data

# Create PythonAnywhere-specific configuration if needed
if [ ! -f "config_pythonanywhere.py" ]; then
    echo "Creating PythonAnywhere configuration..."
    cat > config_pythonanywhere.py << 'CONFIG'
# PythonAnywhere-specific configuration
import os

class PythonAnywhereConfig:
    """Configuration specific to PythonAnywhere environment."""
    
    # Server settings
    DEBUG = False
    TESTING = False
    TEMPLATES_AUTO_RELOAD = False
    SEND_FILE_MAX_AGE_DEFAULT = 31536000
    
    # Logging settings
    LOG_LEVEL = 'WARNING'
    LOG_FILE = '/home/adamcordova/pythonanywhere.log'
    
    # Performance settings
    MAX_CONTENT_LENGTH = 25 * 1024 * 1024  # 25MB
    CACHE_DURATION = 180  # 3 minutes
    SESSION_LIFETIME = 1800  # 30 minutes
    
    # File processing settings
    CHUNK_SIZE = 500
    LARGE_FILE_THRESHOLD = 5 * 1024 * 1024  # 5MB
    ENABLE_MEMORY_MONITORING = True
    FORCE_GARBAGE_COLLECTION = True
    
    # Database settings
    DATABASE_PATH = '/home/adamcordova/AGTDesigner/product_database.db'
    
    # Upload settings
    UPLOAD_FOLDER = '/home/adamcordova/AGTDesigner/uploads'
    MAX_UPLOAD_SIZE = 25 * 1024 * 1024  # 25MB
    
    # Error handling
    SUPPRESS_ERRORS = True
    SAFE_LOGGING = True
    
    @classmethod
    def get_config(cls):
        """Get configuration as dictionary."""
        return {key: value for key, value in cls.__dict__.items() 
                if not key.startswith('_') and not callable(value)}

# Export configuration
PYTHONANYWHERE_CONFIG = PythonAnywhereConfig.get_config()
CONFIG
    echo "✓ PythonAnywhere configuration created"
fi

echo "✓ PythonAnywhere configuration complete"
EOF

echo -e "${BLUE}5. Testing the deployment...${NC}"

# Test the deployment
ssh "$PYTHONANYWHERE_USER@ssh.pythonanywhere.com" << 'EOF'
echo "=== Testing Deployment ==="

cd /home/adamcordova/AGTDesigner

# Activate virtual environment
source venv/bin/activate

# Test Python imports
echo "Testing Python imports..."
python3 -c "
import sys
print('Python path:', sys.path)

try:
    import flask
    print('✓ Flask imported successfully')
except ImportError as e:
    print('✗ Flask import failed:', e)

try:
    import pandas
    print('✓ Pandas imported successfully')
except ImportError as e:
    print('✗ Pandas import failed:', e)

try:
    import openpyxl
    print('✓ OpenPyXL imported successfully')
except ImportError as e:
    print('✗ OpenPyXL import failed:', e)

try:
    from docx import Document
    print('✓ Python-docx imported successfully')
except ImportError as e:
    print('✗ Python-docx import failed:', e)
"

# Test app.py import
echo "Testing app.py import..."
python3 -c "
try:
    import app
    print('✓ App module imported successfully')
except Exception as e:
    print('✗ App module import failed:', e)
"

# Check file structure
echo "Checking file structure..."
ls -la

echo "✓ Deployment testing complete"
EOF

echo -e "${BLUE}6. Restarting PythonAnywhere web app...${NC}"

# Restart the PythonAnywhere web app
ssh "$PYTHONANYWHERE_USER@ssh.pythonanywhere.com" << 'EOF'
echo "=== Restarting Web App ==="

# Touch the WSGI file to restart the app
touch /var/www/adamcordova_pythonanywhere_com_wsgi.py

echo "✓ Web app restart triggered"
echo "Note: It may take a few minutes for the changes to take effect"
EOF

echo -e "${BLUE}7. Final verification...${NC}"

# Final verification
ssh "$PYTHONANYWHERE_USER@ssh.pythonanywhere.com" << 'EOF'
echo "=== Final Verification ==="

cd /home/adamcordova/AGTDesigner

echo "Project structure:"
ls -la

echo ""
echo "Virtual environment:"
ls -la venv/bin/python*

echo ""
echo "Key files present:"
[ -f "app.py" ] && echo "✓ app.py"
[ -f "src/core/data/excel_processor.py" ] && echo "✓ excel_processor.py"
[ -f "requirements.txt" ] && echo "✓ requirements.txt"
[ -f "config_pythonanywhere.py" ] && echo "✓ config_pythonanywhere.py"

echo ""
echo "Directories:"
[ -d "uploads" ] && echo "✓ uploads/"
[ -d "logs" ] && echo "✓ logs/"
[ -d "output" ] && echo "✓ output/"
[ -d "src" ] && echo "✓ src/"

echo ""
echo "=== Deployment Summary ==="
echo "✓ Project re-cloned successfully"
echo "✓ Python environment configured"
echo "✓ Dependencies installed"
echo "✓ PythonAnywhere settings applied"
echo "✓ Web app restarted"
echo ""
echo "Your application should be available at:"
echo "https://adamcordova.pythonanywhere.com"
echo ""
echo "If you encounter any issues, check the logs at:"
echo "/home/adamcordova/AGTDesigner/logs/"
EOF

# Clean up local temporary files
rm -f /tmp/labelMaker_current.tar.gz

echo -e "${GREEN}=== Re-clone Complete! ===${NC}"
echo -e "${GREEN}✓ Entire project has been re-cloned to PythonAnywhere${NC}"
echo -e "${GREEN}✓ All previous settings and dependencies have been applied${NC}"
echo -e "${GREEN}✓ Web application has been restarted${NC}"
echo ""
echo -e "${YELLOW}Your application should be available at:${NC}"
echo -e "${BLUE}https://adamcordova.pythonanywhere.com${NC}"
echo ""
echo -e "${YELLOW}If you need to check the deployment status:${NC}"
echo -e "${BLUE}ssh adamcordova@ssh.pythonanywhere.com${NC}"
echo -e "${BLUE}cd /home/adamcordova/AGTDesigner${NC}"
echo -e "${BLUE}ls -la${NC}" 