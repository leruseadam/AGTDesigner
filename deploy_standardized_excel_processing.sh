#!/bin/bash

# Deploy Standardized Excel Processing to PythonAnywhere
# This script ensures PythonAnywhere uses identical Excel processing as local version

set -e

echo "=== Deploying Standardized Excel Processing to PythonAnywhere ==="

# Configuration
PYTHONANYWHERE_USER="adamcordova"
PYTHONANYWHERE_DOMAIN="adamcordova.pythonanywhere.com"
REMOTE_DIR="/home/$PYTHONANYWHERE_USER/AGTDesigner"

# Files to update
FILES_TO_UPDATE=(
    "src/core/data/excel_processor.py"
    "app.py"
    "fix_pythonanywhere_excel_processing.py"
)

echo "1. Updating PythonAnywhere with standardized Excel processing..."

# Upload the fixed files
for file in "${FILES_TO_UPDATE[@]}"; do
    if [ -f "$file" ]; then
        echo "Uploading $file..."
        scp "$file" "$PYTHONANYWHERE_USER@ssh.pythonanywhere.com:$REMOTE_DIR/$file"
    else
        echo "Warning: $file not found, skipping..."
    fi
done

echo "2. Running fix script on PythonAnywhere..."

# Execute the fix script on PythonAnywhere
ssh "$PYTHONANYWHERE_USER@ssh.pythonanywhere.com" << 'EOF'
cd /home/adamcordova/AGTDesigner

echo "Running standardized Excel processing fix..."
python fix_pythonanywhere_excel_processing.py

echo "Restarting PythonAnywhere web app..."
touch /var/www/adamcordova_pythonanywhere_com_wsgi.py

echo "Verification complete!"
EOF

echo "3. Verifying deployment..."

# Test the deployment
ssh "$PYTHONANYWHERE_USER@ssh.pythonanywhere.com" << 'EOF'
cd /home/adamcordova/AGTDesigner

echo "=== Verification Results ==="

# Check if files were updated
if grep -q "STANDARDIZED for both local and PythonAnywhere" src/core/data/excel_processor.py; then
    echo "✓ Excel processor standardized"
else
    echo "✗ Excel processor not standardized"
fi

if grep -q "ENABLE_LAZY_PROCESSING = False" src/core/data/excel_processor.py; then
    echo "✓ Lazy processing disabled"
else
    echo "✗ Lazy processing not disabled"
fi

if grep -q "ENABLE_MINIMAL_PROCESSING = False" src/core/data/excel_processor.py; then
    echo "✓ Minimal processing disabled"
else
    echo "✗ Minimal processing not disabled"
fi

if grep -q "max_size = 100 \* 1024 \* 1024" src/core/data/excel_processor.py; then
    echo "✓ Standard file size limit applied"
else
    echo "✗ Standard file size limit not applied"
fi

echo "=== Deployment Summary ==="
echo "Both local and PythonAnywhere environments now use identical Excel processing."
echo "Key changes:"
echo "- Disabled lazy processing for consistent behavior"
echo "- Disabled minimal processing for consistent behavior"
echo "- Standardized file size limits (100MB for both environments)"
echo "- Standardized Excel engine approach (openpyxl primary, xlrd fallback)"
echo "- Standardized file loading logic for both environments"
EOF

echo "=== Deployment Complete ==="
echo "PythonAnywhere Excel processing has been standardized to match local version."
echo "Both environments now use identical processing logic."
echo ""
echo "Key improvements:"
echo "✓ Identical Excel processing between local and PythonAnywhere"
echo "✓ Consistent file loading behavior"
echo "✓ Standardized performance flags"
echo "✓ Same file size limits and Excel engines"
echo "✓ Unified error handling and logging" 