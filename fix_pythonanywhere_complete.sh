#!/bin/bash

# Complete PythonAnywhere Fix Script
# Run this in your PythonAnywhere bash console

echo "=== Complete PythonAnywhere Fix ==="

# Step 1: Check current Python version
echo "Current Python version:"
python --version

# Step 2: Navigate to project
cd ~/AGTDesigner

# Step 3: Create Python 3.10 virtual environment
echo "Creating Python 3.10 virtual environment..."
mkvirtualenv --python=/usr/bin/python3.10 myflaskapp-env-py310

# Step 4: Activate the environment
echo "Activating virtual environment..."
workon myflaskapp-env-py310

# Step 5: Upgrade pip and setuptools
echo "Upgrading pip and setuptools..."
pip install --upgrade pip setuptools wheel

# Step 6: Install requirements
echo "Installing requirements..."
pip install -r requirements_pythonanywhere_py310.txt

# Step 7: Pull latest changes
echo "Pulling latest changes from GitHub..."
git pull origin main

# Step 8: Clear cache
echo "Clearing cache..."
rm -rf __pycache__
rm -rf src/__pycache__
rm -rf src/core/__pycache__
rm -rf src/core/data/__pycache__
rm -rf src/core/generation/__pycache__

# Step 9: Set permissions
echo "Setting permissions..."
chmod -R 755 .
chmod -R 755 uploads output cache logs static

echo ""
echo "=== Fix Complete ==="
echo ""
echo "IMPORTANT: You need to update your web app configuration:"
echo "1. Go to Web tab in PythonAnywhere"
echo "2. Click 'Edit' next to your web app"
echo "3. Change Python version to 3.10"
echo "4. Set Virtual environment to: /home/adamcordova/.virtualenvs/myflaskapp-env-py310"
echo "5. Click 'Save'"
echo "6. Click 'Reload'"
echo ""
echo "Your virtual environment path is: /home/adamcordova/.virtualenvs/myflaskapp-env-py310" 