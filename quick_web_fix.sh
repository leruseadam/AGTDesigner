#!/bin/bash
# Quick fix script for web deployment

echo "🚀 AGT Label Maker - Quick Web Fix"
echo "=================================="

# Pull latest changes
echo "📥 Pulling latest changes..."
git pull origin main

# Run database schema fix
echo "🔧 Fixing database schema..."
python fix_database_schema.py

# Check if fix was successful
if [ $? -eq 0 ]; then
    echo "✅ Database schema fix completed successfully"
    echo "🎯 Ready to restart application"
else
    echo "❌ Database schema fix failed"
    echo "📞 Please check the logs and try again"
fi

echo "📋 Next steps:"
echo "1. Restart your web application"
echo "2. Test Excel file upload"
echo "3. Test tag generation"
echo "4. Check for performance improvements"
