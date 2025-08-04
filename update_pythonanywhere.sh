#!/bin/bash

# PythonAnywhere Update Script
# Run this in your PythonAnywhere bash console

echo "=== Updating PythonAnywhere Deployment ==="

# Step 1: Navigate to your project directory
cd ~/AGTDesigner

# Step 2: Pull latest changes
echo "Pulling latest changes from GitHub..."
git pull origin main

# Step 3: Update configuration for production
echo "Updating configuration for production..."
if [ -f "config_production.py" ]; then
    echo "Production config found - ensuring DEVELOPMENT_MODE is false"
    # The config_production.py should already have the right settings
else
    echo "Creating production config..."
    cp config.py config_production.py
    # Update the config to use environment variables
    sed -i 's/DEVELOPMENT_MODE = True/DEVELOPMENT_MODE = os.environ.get("DEVELOPMENT_MODE", "False").lower() == "true"/' config_production.py
fi

# Step 4: Clear any cached files
echo "Clearing cache..."
rm -rf __pycache__
rm -rf src/__pycache__
rm -rf src/core/__pycache__
rm -rf src/core/data/__pycache__
rm -rf src/core/generation/__pycache__

# Step 5: Ensure proper permissions
echo "Setting permissions..."
chmod -R 755 .
chmod -R 755 uploads output cache logs static

# Step 6: Check if virtual environment is active
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  WARNING: Not in virtual environment!"
    echo "Please activate your virtual environment:"
    echo "source ~/.virtualenvs/myflaskapp-env/bin/activate"
    echo "Then run this script again."
    exit 1
fi

# Step 7: Install any new dependencies
echo "Checking for new dependencies..."
pip install -r requirements_pythonanywhere.txt

echo ""
echo "=== Update Complete ==="
echo "Next steps:"
echo "1. Go to PythonAnywhere Web tab"
echo "2. Click 'Reload' for your web app"
echo "3. Test the application at https://www.agtpricetags.com"
echo ""
echo "If you see any errors, check the error logs in the Web tab." 