#!/bin/bash

# Web Deployment Setup for PythonAnywhere
# This script sets up your Label Maker project for web deployment

set -e  # Exit on any error

echo "🌐 Setting up Label Maker for Web Deployment"
echo "============================================="

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

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    print_error "app.py not found. Please run this script from your project directory."
    exit 1
fi

print_status "Current directory: $(pwd)"
print_status "Project files found: $(ls -1 | wc -l) files"

# Create web-specific virtual environment
print_status "Creating web virtual environment..."
python3.11 -m venv venv_web

# Activate virtual environment
print_status "Activating virtual environment..."
source venv_web/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install web-specific requirements
print_status "Installing web dependencies..."
pip install -r requirements_pythonanywhere.txt

# Install additional web dependencies
print_status "Installing additional web dependencies..."
pip install flask-caching python-dotenv gunicorn

# Test the web environment
print_status "Testing web environment..."
python -c "from app import create_app; print('✅ Web environment ready!')"

# Create WSGI file for PythonAnywhere
print_status "Creating WSGI configuration..."
cat > wsgi.py << 'EOF'
import sys
import os

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Import the Flask app
from app import create_app

# Create the application instance
application = create_app()

if __name__ == "__main__":
    application.run()
EOF

# Create PythonAnywhere specific configuration
print_status "Creating PythonAnywhere configuration..."
cat > pythonanywhere_config.py << 'EOF'
# PythonAnywhere Configuration
import os

# Set environment variables for PythonAnywhere
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = 'False'

# Database path for PythonAnywhere
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'product_database.db')

# Static files configuration
STATIC_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
TEMPLATE_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
EOF

# Create deployment instructions
print_status "Creating deployment instructions..."
cat > PYTHONANYWHERE_DEPLOYMENT.md << 'EOF'
# PythonAnywhere Deployment Guide

## Quick Setup

1. **Log into PythonAnywhere**
   - Go to www.pythonanywhere.com
   - Log into your account

2. **Clone Repository**
   ```bash
   git clone https://github.com/leruseadam/AGTDesigner.git
   cd AGTDesigner
   git checkout restored-working-version
   ```

3. **Create Virtual Environment**
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate
   pip install -r requirements_pythonanywhere.txt
   pip install flask-caching python-dotenv gunicorn
   ```

4. **Configure Web App**
   - Go to Web tab in PythonAnywhere
   - Add a new web app
   - Choose Manual configuration
   - Python version: 3.11
   - Source code: /home/yourusername/AGTDesigner
   - Working directory: /home/yourusername/AGTDesigner
   - WSGI configuration file: /home/yourusername/AGTDesigner/wsgi.py

5. **Set Environment Variables**
   - In Web tab, go to Environment variables
   - Add: FLASK_ENV=production
   - Add: FLASK_DEBUG=False

6. **Reload Web App**
   - Click "Reload" button in Web tab

## File Structure
```
AGTDesigner/
├── app.py                 # Main application
├── wsgi.py               # WSGI entry point
├── requirements_pythonanywhere.txt
├── static/               # Static files
├── templates/            # HTML templates
├── src/                  # Source code
└── product_database.db   # Database
```

## Troubleshooting

- **Import errors**: Make sure all dependencies are installed
- **Database errors**: Check file permissions on product_database.db
- **Static files**: Ensure static/ and templates/ directories exist
- **Port issues**: PythonAnywhere handles ports automatically

## Monitoring

- Check error logs in Web tab
- Monitor application in Files tab
- Use Console for debugging
EOF

print_success "Web deployment setup complete!"
print_status "Files created:"
echo "  - wsgi.py (WSGI entry point)"
echo "  - pythonanywhere_config.py (Configuration)"
echo "  - PYTHONANYWHERE_DEPLOYMENT.md (Instructions)"

print_status "Next steps:"
echo "  1. Push to GitHub: git push origin restored-working-version"
echo "  2. Log into PythonAnywhere"
echo "  3. Follow instructions in PYTHONANYWHERE_DEPLOYMENT.md"

print_success "Your project is ready for web deployment! 🚀" 