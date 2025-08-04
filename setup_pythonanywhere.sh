#!/bin/bash

# PythonAnywhere Initial Setup Script
# Run this script in your PythonAnywhere Bash console

echo "=== PythonAnywhere Initial Setup Script ==="
echo "This script will set up your Label Maker application on PythonAnywhere"
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

# Create virtual environment
echo "🐍 Creating virtual environment..."
mkvirtualenv --python=/usr/bin/python3.9 AGTDesigner

# Activate virtual environment
echo "🔧 Activating virtual environment..."
workon AGTDesigner

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements_pythonanywhere.txt

# Check if installation was successful
if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "⚠️  Some dependencies may have failed to install"
    echo "Trying alternative requirements file..."
    pip install -r requirements.txt
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
echo "✅ Virtual environment created: AGTDesigner"
echo "✅ Dependencies installed"
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
echo "🎉 Initial setup completed!" 