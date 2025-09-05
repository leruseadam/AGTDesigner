#!/bin/bash

# Database Transfer Script
# Transfers the working database to the production server

echo "=== Database Transfer Script ==="
echo ""

# Configuration - UPDATE THESE VALUES FOR YOUR PRODUCTION SERVER
PROD_SERVER="username@agtpricetags.com"
PROD_PATH="/path/to/labelmaker/uploads/"
LOCAL_DB="uploads/product_database.db"

echo "Configuration:"
echo "  Production Server: $PROD_SERVER"
echo "  Production Path: $PROD_PATH"
echo "  Local Database: $LOCAL_DB"
echo ""

# Check if local database exists
if [ ! -f "$LOCAL_DB" ]; then
    echo "ERROR: Local database not found at $LOCAL_DB"
    exit 1
fi

echo "Local database found:"
ls -lh "$LOCAL_DB"
echo ""

echo "Ready to transfer database to production server."
echo ""
echo "IMPORTANT: Update the PROD_SERVER and PROD_PATH variables in this script first!"
echo ""
echo "Then run:"
echo "  ./transfer_database.sh"
echo ""
echo "Or manually transfer with:"
echo "  scp $LOCAL_DB $PROD_SERVER:$PROD_PATH"
echo ""

# Uncomment the line below after updating the server details
# scp "$LOCAL_DB" "$PROD_SERVER:$PROD_PATH"
