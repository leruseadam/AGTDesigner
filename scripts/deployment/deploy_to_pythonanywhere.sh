#!/bin/bash
# Run this script on PythonAnywhere to deploy the database

echo "=================================================="
echo "🚀 DEPLOYING DATABASE TO PYTHONANYWHERE"
echo "=================================================="

# Check if we're in the right directory
if [ ! -d "uploads" ]; then
    echo "Creating uploads directory..."
    mkdir -p uploads
fi

# Extract the database
echo "Extracting database..."
unzip -o production_database_fix_*.zip

# Move database to uploads directory
echo "Moving database to uploads directory..."
mv product_database_AGT_Bothell.db uploads/

# Set correct permissions
echo "Setting database permissions..."
chmod 644 uploads/product_database_AGT_Bothell.db

# Clean up
echo "Cleaning up..."
rm -f production_database_fix_*.zip

# Test the database
echo "Testing database..."
python3 debug_production_db.py

echo ""
echo "✅ Database deployment complete!"
echo "Now reload your web app in the PythonAnywhere Web tab"
