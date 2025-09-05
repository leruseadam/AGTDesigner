#!/bin/bash

# Database Fixes Deployment Script for agtpricetags.com
# This script deploys the database fixes to the production server

echo "=== Database Fixes Deployment Script ==="
echo "Target: agtpricetags.com"
echo ""

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "ERROR: Please run this script from the project root directory"
    exit 1
fi

echo "1. Verifying local database status..."
if [ -f "uploads/product_database.db" ]; then
    DB_SIZE=$(ls -lh uploads/product_database.db | awk '{print $5}')
    echo "   ✓ Local database found: uploads/product_database.db ($DB_SIZE)"
else
    echo "   ✗ ERROR: Local database not found in uploads/product_database.db"
    exit 1
fi

echo ""
echo "2. Production Server Deployment Steps:"
echo ""
echo "   A. SSH into the production server:"
echo "      ssh username@agtpricetags.com"
echo ""
echo "   B. Navigate to the project directory:"
echo "      cd /path/to/labelmaker/project"
echo ""
echo "   C. Pull the latest code:"
echo "      git pull origin main"
echo ""
echo "   D. Copy the working database:"
echo "      scp uploads/product_database.db username@agtpricetags.com:/path/to/labelmaker/uploads/"
echo ""
echo "   E. Restart the Flask application:"
echo "      sudo systemctl restart labelmaker"
echo "      # OR if using screen/tmux:"
echo "      pkill -f 'python app.py'"
echo "      python app.py"
echo ""
echo "3. Verify the deployment:"
echo "   - Check https://www.agtpricetags.com/api/database-vendor-stats"
echo "   - Should return database stats instead of 500 error"
echo ""

echo "=== Deployment Package Ready ==="
echo ""
echo "Next steps:"
echo "1. Run this script on the production server"
echo "2. Or manually follow the steps above"
echo "3. Test the database endpoints"
echo ""
echo "Need help? Check the logs on the production server for any errors."
