#!/bin/bash
# PythonAnywhere installation script for Python 3.13
# This script installs dependencies in a way that works on PythonAnywhere with Python 3.13

echo "🚀 Installing dependencies for PythonAnywhere (Python 3.13)..."

# Update pip and install essential build tools first
echo "📦 Installing build tools..."
pip install --upgrade pip setuptools wheel

# Install numpy with a version compatible with Python 3.13
echo "📦 Installing numpy (Python 3.13 compatible)..."
pip install numpy

# Install pandas with a version compatible with Python 3.13
echo "📦 Installing pandas (Python 3.13 compatible)..."
pip install pandas

# Install core Flask dependencies
echo "📦 Installing core Flask dependencies..."
pip install Flask Flask-CORS Werkzeug

# Install document processing
echo "📦 Installing document processing..."
pip install python-docx docxtpl lxml

# Install data processing
echo "📦 Installing data processing..."
pip install openpyxl xlrd

# Install image processing
echo "📦 Installing image processing..."
pip install Pillow

# Install utilities
echo "📦 Installing utilities..."
pip install python-dateutil pytz requests

# Install fuzzy matching
echo "📦 Installing fuzzy matching..."
pip install fuzzywuzzy

# Install performance optimizations
echo "📦 Installing performance optimizations..."
pip install flask-compress psutil

# Try optional dependencies (may fail, that's okay)
echo "📦 Installing optional dependencies..."
pip install jellyfish || echo "⚠️  jellyfish installation failed, but that's okay"
pip install python-Levenshtein || echo "⚠️  Levenshtein installation failed, but that's okay"

echo "✅ Installation complete!"
echo "📊 Checking installation..."
python -c "import flask, pandas, docx; print('✅ Core dependencies working!')"

echo "🎉 Ready to run on PythonAnywhere with Python 3.13!"
