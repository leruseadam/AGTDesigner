#!/bin/bash

# PythonAnywhere Deployment Script for Label Maker
# This script sets up your project on PythonAnywhere

set -e  # Exit on any error

echo "🚀 Starting PythonAnywhere deployment..."

# Configuration
PYTHON_VERSION="3.11"
PROJECT_NAME="labelMaker"
GITHUB_REPO="https://github.com/leruseadam/AGTDesigner.git"
BRANCH="restored-working-version"

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
if [[ "$USER" == *"pythonanywhere"* ]]; then
    print_status "Detected PythonAnywhere environment"
    PYTHONANYWHERE=true
else
    print_warning "Not on PythonAnywhere - this script is designed for PythonAnywhere deployment"
    PYTHONANYWHERE=false
fi

# Create project directory
print_status "Setting up project directory..."
mkdir -p ~/labelMaker
cd ~/labelMaker

# Clone or update repository
if [ -d ".git" ]; then
    print_status "Updating existing repository..."
    git fetch origin
    git checkout $BRANCH
    git pull origin $BRANCH
else
    print_status "Cloning repository..."
    git clone -b $BRANCH $GITHUB_REPO .
fi

print_success "Repository setup complete"

# Create virtual environment
print_status "Setting up virtual environment..."
if [ ! -d "venv" ]; then
    python$PYTHON_VERSION -m venv venv
    print_success "Virtual environment created"
else
    print_status "Virtual environment already exists"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install requirements
print_status "Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_success "Dependencies installed"
else
    print_warning "No requirements.txt found - installing common dependencies..."
    pip install flask pandas openpyxl python-docx pillow
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p static/uploads
mkdir -p logs
mkdir -p data

# Set up environment variables
print_status "Setting up environment variables..."
cat > .env << EOF
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
DATABASE_PATH=./data/product_database.db
UPLOAD_FOLDER=./static/uploads
LOG_LEVEL=INFO
EOF

print_success "Environment variables configured"

# Create WSGI file for PythonAnywhere
print_status "Creating WSGI configuration..."
cat > wsgi.py << 'EOF'
import sys
import os

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Import and create the Flask app
from app import create_app
application = create_app()

if __name__ == "__main__":
    application.run()
EOF

print_success "WSGI file created"

# Create startup script
print_status "Creating startup script..."
cat > start_app.sh << 'EOF'
#!/bin/bash
cd ~/labelMaker
source venv/bin/activate
python app.py
EOF

chmod +x start_app.sh

# Create database initialization script
print_status "Creating database setup script..."
cat > setup_database.py << 'EOF'
#!/usr/bin/env python3
"""
Database setup script for Label Maker
"""
import os
import sqlite3
from pathlib import Path

def setup_database():
    """Initialize the database with required tables"""
    db_path = Path("./data/product_database.db")
    db_path.parent.mkdir(exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create products table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            price REAL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully")

if __name__ == "__main__":
    setup_database()
EOF

# Create PythonAnywhere specific configuration
print_status "Creating PythonAnywhere configuration..."
cat > pythonanywhere_config.py << 'EOF'
"""
PythonAnywhere specific configuration
"""
import os

# PythonAnywhere specific settings
class PythonAnywhereConfig:
    # Static files configuration
    STATIC_FOLDER = '/home/yourusername/labelMaker/static'
    UPLOAD_FOLDER = '/home/yourusername/labelMaker/static/uploads'
    
    # Database configuration
    DATABASE_PATH = '/home/yourusername/labelMaker/data/product_database.db'
    
    # Logging configuration
    LOG_FOLDER = '/home/yourusername/labelMaker/logs'
    
    # Security settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Flask settings
    DEBUG = False
    TESTING = False
    
    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}

# Update this with your actual PythonAnywhere username
PYTHONANYWHERE_USERNAME = "yourusername"  # Replace with your actual username
EOF

print_success "PythonAnywhere configuration created"

# Create deployment checklist
print_status "Creating deployment checklist..."
cat > DEPLOYMENT_CHECKLIST.md << 'EOF'
# PythonAnywhere Deployment Checklist

## ✅ Completed Steps
- [x] Repository cloned/updated
- [x] Virtual environment created
- [x] Dependencies installed
- [x] Environment variables configured
- [x] WSGI file created
- [x] Database setup script created

## 🔧 Manual Steps Required

### 1. Update PythonAnywhere Configuration
Edit `pythonanywhere_config.py` and replace `yourusername` with your actual PythonAnywhere username.

### 2. Set up Web App on PythonAnywhere
1. Go to PythonAnywhere Dashboard
2. Click "Web" tab
3. Click "Add a new web app"
4. Choose "Manual configuration"
5. Select Python 3.11
6. Set source code to: `/home/yourusername/labelMaker`
7. Set working directory to: `/home/yourusername/labelMaker`
8. Set WSGI configuration file to: `/var/www/yourusername_pythonanywhere_com_wsgi.py`

### 3. Configure WSGI File
Edit the WSGI file in PythonAnywhere dashboard:
```python
import sys
import os

# Add the project directory to Python path
project_dir = '/home/yourusername/labelMaker'
sys.path.insert(0, project_dir)

# Import and create the Flask app
from app import create_app
application = create_app()
```

### 4. Set up Static Files
In PythonAnywhere Web app configuration:
- Static URL: `/static/`
- Static Directory: `/home/yourusername/labelMaker/static`

### 5. Initialize Database
Run: `python setup_database.py`

### 6. Set Environment Variables
In PythonAnywhere Web app configuration, add:
- FLASK_ENV=production
- SECRET_KEY=your-secret-key
- DATABASE_PATH=/home/yourusername/labelMaker/data/product_database.db

### 7. Reload Web App
Click "Reload" in PythonAnywhere Web app configuration.

## 🧪 Testing
1. Visit your PythonAnywhere URL
2. Test file upload functionality
3. Test label generation
4. Check error logs if issues occur

## 📝 Troubleshooting
- Check error logs in PythonAnywhere Web app
- Verify file permissions
- Ensure all dependencies are installed
- Check database file permissions
EOF

print_success "Deployment checklist created"

# Create a simple test script
print_status "Creating test script..."
cat > test_deployment.py << 'EOF'
#!/usr/bin/env python3
"""
Test script for PythonAnywhere deployment
"""
import os
import sys
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported"""
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
    
    return True

def test_project_structure():
    """Test that project structure is correct"""
    required_files = [
        'app.py',
        'wsgi.py',
        'requirements.txt',
        'src/core/data/excel_processor.py'
    ]
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")
            return False
    
    return True

def test_database():
    """Test database setup"""
    try:
        from app import create_app
        app = create_app()
        print("✅ Flask app created successfully")
        return True
    except Exception as e:
        print(f"❌ Flask app creation failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing PythonAnywhere deployment...")
    
    tests = [
        ("Import Tests", test_imports),
        ("Project Structure", test_project_structure),
        ("Database Setup", test_database)
    ]
    
    all_passed = True
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        if not test_func():
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed! Deployment should be ready.")
    else:
        print("\n⚠️  Some tests failed. Please check the issues above.")
EOF

print_success "Test script created"

# Final status
print_success "PythonAnywhere deployment setup complete!"
    echo ""
    echo "📋 Next steps:"
echo "1. Update pythonanywhere_config.py with your username"
echo "2. Follow the DEPLOYMENT_CHECKLIST.md"
echo "3. Run: python test_deployment.py"
echo "4. Set up your web app in PythonAnywhere dashboard"
    echo ""
echo "📁 Project location: ~/labelMaker"
echo "🔗 GitHub repository: $GITHUB_REPO"
echo "�� Branch: $BRANCH" 