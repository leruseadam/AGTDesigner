#!/bin/bash
# Complete production fix deployment script for PythonAnywhere

echo "=================================================="
echo "🚀 DEPLOYING COMPLETE PRODUCTION FIX"
echo "=================================================="

# Check if we're in the right directory
if [ ! -d "uploads" ]; then
    echo "Creating uploads directory..."
    mkdir -p uploads
fi

if [ ! -d "static/js" ]; then
    echo "Creating static/js directory..."
    mkdir -p static/js
fi

# Extract the complete fix package
echo "Extracting complete fix package..."
unzip -o complete_production_fix_*.zip

# Set correct permissions
echo "Setting permissions..."
chmod 644 uploads/product_database_AGT_Bothell.db
chmod 644 static/js/*.js

# Test the database
echo "Testing database..."
python3 debug_production_db.py

# Clean up
echo "Cleaning up..."
rm -f complete_production_fix_*.zip

echo ""
echo "✅ Complete fix deployment finished!"
echo ""
echo "Next steps:"
echo "1. Reload your web app in PythonAnywhere Web tab"
echo "2. Wait 30 seconds for reload to complete"
echo "3. Visit https://www.agtpricetags.com"
echo "4. Should now show 10,543+ products"
echo ""
echo "If still showing 0 products:"
echo "1. Check PythonAnywhere error logs"
echo "2. Verify database file exists: ls -la uploads/"
echo "3. Check database integrity: sqlite3 uploads/product_database_AGT_Bothell.db 'PRAGMA integrity_check;'"
