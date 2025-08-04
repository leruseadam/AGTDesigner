#!/bin/bash

# Quick PythonAnywhere Setup Script
# Run this directly on PythonAnywhere to set up your project

echo "🚀 Quick PythonAnywhere Setup for Label Maker"
echo "=============================================="

# Configuration
GITHUB_REPO="https://github.com/leruseadam/AGTDesigner.git"
BRANCH="restored-working-version"
PROJECT_DIR="~/labelMaker"

echo "📋 Configuration:"
echo "  Repository: $GITHUB_REPO"
echo "  Branch: $BRANCH"
echo "  Directory: $PROJECT_DIR"
echo ""

# Create project directory
echo "📁 Setting up project directory..."
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

# Clone repository
echo "📥 Cloning repository..."
git clone -b $BRANCH $GITHUB_REPO .

# Create virtual environment
echo "🐍 Creating virtual environment..."
python3.11 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements_pythonanywhere.txt

# Create necessary directories
echo "📂 Creating directories..."
mkdir -p static/uploads
mkdir -p logs
mkdir -p data

# Initialize database
echo "🗄️  Setting up database..."
python setup_database.py

# Test the setup
echo "🧪 Testing setup..."
python test_deployment.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Go to PythonAnywhere Web tab"
echo "2. Add a new web app"
echo "3. Choose Manual configuration"
echo "4. Set source code to: $PROJECT_DIR"
echo "5. Set working directory to: $PROJECT_DIR"
echo "6. Configure WSGI file"
echo "7. Set up static files"
echo "8. Reload the web app"
echo ""
echo "🌐 Your app will be available at your PythonAnywhere URL" 