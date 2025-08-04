#!/bin/bash

# Upload script for PythonAnywhere
# Run this from your local machine

echo "📤 Uploading files to PythonAnywhere..."

# Configuration
PYTHONANYWHERE_USERNAME="adamcordova"
PROJECT_NAME="AGTDesigner"
PYTHONANYWHERE_PROJECT_PATH="/home/$PYTHONANYWHERE_USERNAME/$PROJECT_NAME"

echo "Uploading to: $PYTHONANYWHERE_PROJECT_PATH"

# Upload files using scp (if you have SSH access)
# scp -r . $PYTHONANYWHERE_USERNAME@ssh.pythonanywhere.com:$PYTHONANYWHERE_PROJECT_PATH/

# Alternative: Manual upload instructions
echo ""
echo "📋 Manual Upload Instructions:"
echo "1. Go to PythonAnywhere Files tab"
echo "2. Navigate to: $PYTHONANYWHERE_PROJECT_PATH"
echo "3. Upload all files from this directory"
echo "4. Run the fix script on PythonAnywhere"
echo ""

echo "✅ Upload script created"
