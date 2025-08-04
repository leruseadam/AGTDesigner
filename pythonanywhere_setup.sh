#!/bin/bash

# PythonAnywhere Setup Script
# Run this in your PythonAnywhere bash console

echo "=== Setting up Label Maker on PythonAnywhere ==="

# Step 1: Create virtual environment
echo "Creating virtual environment..."
python3.10 -m venv ~/labelmaker-venv
source ~/labelmaker-venv/bin/activate

# Step 2: Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Step 3: Install dependencies
echo "Installing dependencies..."
pip install -r requirements_pythonanywhere.txt

# Step 4: Create necessary directories
echo "Creating directories..."
mkdir -p ~/labelmaker/uploads
mkdir -p ~/labelmaker/output
mkdir -p ~/labelmaker/cache
mkdir -p ~/labelmaker/logs

# Step 5: Set permissions
echo "Setting permissions..."
chmod -R 755 ~/labelmaker/

echo "Setup complete!"
echo "Next steps:"
echo "1. Go to Web tab in PythonAnywhere dashboard"
echo "2. Create a new web app"
echo "3. Choose Manual configuration"
echo "4. Choose Python 3.10"
echo "5. Set source code path to: /home/yourusername/labelmaker"
echo "6. Set virtual environment path to: /home/yourusername/labelmaker-venv"
echo "7. Edit WSGI file and reload app"
