#!/bin/bash

echo "Running PythonAnywhere Default File Diagnostic..."
echo "================================================"

# Upload the diagnostic script to PythonAnywhere
echo "Uploading diagnostic script to PythonAnywhere..."
scp debug_pythonanywhere_default_file.py adamcordova@ssh.pythonanywhere.com:/home/adamcordova/AGTDesigner/

# Run the diagnostic on PythonAnywhere
echo "Running diagnostic on PythonAnywhere..."
ssh adamcordova@ssh.pythonanywhere.com "cd /home/adamcordova/AGTDesigner && python3 debug_pythonanywhere_default_file.py"

echo ""
echo "Diagnostic completed!" 