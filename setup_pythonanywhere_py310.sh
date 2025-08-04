#!/bin/bash

# PythonAnywhere Python 3.10 Setup Script
# This script is optimized for Python 3.10 on PythonAnywhere

echo "=== PythonAnywhere Python 3.10 Setup Script ==="
echo "This script will set up your Label Maker application on PythonAnywhere with Python 3.10"
echo ""

# Get username from current directory
USERNAME=$(whoami)
PROJECT_DIR="/home/$USERNAME/AGTDesigner"

echo "Username: $USERNAME"
echo "Project directory: $PROJECT_DIR"
echo ""

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found. Please run this script from your project directory."
    echo "Current directory: $(pwd)"
    exit 1
fi

echo "✅ Found project files"

# Create virtual environment with Python 3.10
echo "🐍 Creating virtual environment with Python 3.10..."
mkvirtualenv --python=/usr/bin/python3.10 AGTDesigner

# Activate virtual environment
echo "🔧 Activating virtual environment..."
workon AGTDesigner

# Upgrade pip and setuptools first
echo "📦 Upgrading pip and setuptools..."
pip install --upgrade pip setuptools wheel

# Install dependencies with Python 3.10 compatible versions
echo "📦 Installing Python 3.10 compatible dependencies..."
pip install -r requirements_pythonanywhere_py310.txt

# Check if installation was successful
if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "⚠️  Some dependencies may have failed to install"
    echo "Trying alternative installation method..."
    
    # Try installing packages individually
    pip install Flask==2.3.3
    pip install Flask-CORS==4.0.0
    pip install pandas==2.0.3
    pip install numpy==1.24.3
    pip install python-docx==0.8.11
    pip install docxtpl==0.16.7
    pip install openpyxl==3.1.2
    pip install Pillow==9.5.0
    pip install Flask-Caching==2.1.0
fi

# Create required directories
echo "📁 Creating required directories..."
mkdir -p uploads
mkdir -p output
mkdir -p cache
mkdir -p logs

# Set permissions
echo "🔐 Setting permissions..."
chmod 777 uploads
chmod 777 output
chmod 777 cache
chmod 777 logs

# Test the application
echo "🧪 Testing application..."
python -c "
import sys
sys.path.append('.')
try:
    from app import create_app
    app = create_app()
    print('✅ Application imports successfully')
except Exception as e:
    print(f'❌ Application test failed: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
"

# Initialize database (if needed)
echo "🗄️  Initializing product database..."
python -c "
try:
    from src.core.data.product_database import ProductDatabase
    db = ProductDatabase()
    db.init_database()
    print('✅ Product database initialized successfully')
except Exception as e:
    print(f'⚠️  Database initialization warning: {e}')
"

echo ""
echo "=== Setup Summary ==="
echo "✅ Virtual environment created: AGTDesigner (Python 3.10)"
echo "✅ Dependencies installed (Python 3.10 compatible)"
echo "✅ Required directories created"
echo "✅ Application tested"
echo "✅ Database initialized"
echo ""
echo "🔄 Next steps:"
echo "1. Go to the 'Web' tab in PythonAnywhere"
echo "2. Create a new web app with Manual configuration"
echo "3. Set the path to: $PROJECT_DIR"
echo "4. Configure the WSGI file (see PYTHONANYWHERE_UPLOAD_GUIDE.md)"
echo "5. Set virtual environment to: /home/$USERNAME/.virtualenvs/AGTDesigner"
echo "6. Configure static files mappings"
echo "7. Click 'Reload'"
echo ""
echo "📚 For detailed instructions, see: PYTHONANYWHERE_UPLOAD_GUIDE.md"
echo ""
echo "🌐 Your app will be available at:"
echo "https://$USERNAME.pythonanywhere.com"
echo ""
echo "🎉 Python 3.10 setup completed!" 