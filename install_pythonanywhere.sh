#!/bin/bash
# PythonAnywhere installation script
# This script installs dependencies in a way that works on PythonAnywhere

echo "🚀 Installing dependencies for PythonAnywhere..."

# Update pip first
pip install --upgrade pip

# Install numpy first (required for pandas)
echo "📦 Installing numpy..."
pip install numpy==1.24.3

# Install pandas with a compatible version
echo "📦 Installing pandas..."
pip install pandas==1.5.3

# Install other core dependencies
echo "📦 Installing core dependencies..."
pip install Flask==2.3.3 Flask-CORS==4.0.0 Werkzeug==2.3.7

# Install document processing
echo "📦 Installing document processing..."
pip install python-docx==0.8.11 docxtpl==0.16.7 lxml==4.9.3

# Install data processing
echo "📦 Installing data processing..."
pip install openpyxl==3.1.2 xlrd==2.0.1

# Install image processing
echo "📦 Installing image processing..."
pip install Pillow==10.1.0

# Install utilities
echo "📦 Installing utilities..."
pip install python-dateutil==2.8.2 pytz==2023.3 requests>=2.32.0

# Install fuzzy matching (optional)
echo "📦 Installing fuzzy matching..."
pip install fuzzywuzzy>=0.18.0

# Install performance optimizations
echo "📦 Installing performance optimizations..."
pip install flask-compress==1.18 psutil==7.0.0

# Try to install jellyfish (optional)
echo "📦 Installing jellyfish (optional)..."
pip install jellyfish==1.2.0 || echo "⚠️  jellyfish installation failed, but that's okay"

# Try to install Levenshtein (optional)
echo "📦 Installing Levenshtein (optional)..."
pip install python-Levenshtein>=0.27.0 || echo "⚠️  Levenshtein installation failed, but that's okay"

echo "✅ Installation complete!"
echo "📊 Checking installation..."
python -c "import flask, pandas, docx; print('✅ Core dependencies working!')"

echo "🎉 Ready to run on PythonAnywhere!"