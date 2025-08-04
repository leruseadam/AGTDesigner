#!/bin/bash

# PythonAnywhere Dependency Installation Script
# This script installs all necessary dependencies for the AGT Designer application

echo "=== PythonAnywhere Dependency Installation ==="
echo "Installing all necessary dependencies..."
echo ""

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "Error: Please run this script from the project root directory"
    exit 1
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Run the Python installation script
echo "Running dependency installation script..."
python3 install_pythonanywhere_dependencies.py

echo ""
echo "=== Installation Complete ==="
echo "Check the output above for any errors."
echo ""
echo "If all dependencies are installed successfully:"
echo "1. Go to the Web tab in PythonAnywhere dashboard"
echo "2. Click 'Reload' to restart your web app"
echo "3. Test the application at your PythonAnywhere URL"
echo ""
echo "If there were errors, please review them and try again."
