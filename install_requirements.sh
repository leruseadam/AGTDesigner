#!/bin/bash
# Automated requirements installation with docxcompose patch
# This script installs all dependencies and automatically applies the pkg_resources fix

set -e  # Exit on error

echo "🔧 Installing requirements..."
pip3 install --user -r requirements.txt

echo ""
echo "🔧 Applying docxcompose patch..."
python3 patch_docxcompose.py

echo ""
echo "✅ Installation complete!"
echo "   - All requirements installed"
echo "   - docxcompose patched (pkg_resources → importlib.metadata)"
echo ""
echo "Run 'python3 app.py' to start the application"

