#!/bin/bash
# Emergency fix for agtpricetags.com database issues

echo "🚨 Emergency Database Fix for PythonAnywhere"
echo "============================================="

# 1. Check if files exist
echo "1. Checking critical files..."
ls -la /home/adamcordova/AGTDesigner/app.py
ls -la /home/adamcordova/AGTDesigner/product_database.db
ls -la /home/adamcordova/AGTDesigner/core/data/product_database.py

# 2. Check database content
echo "2. Checking database content..."
sqlite3 /home/adamcordova/AGTDesigner/product_database.db "SELECT COUNT(*) FROM products;"

# 3. Check PythonAnywhere web app status
echo "3. Checking web app status..."
echo "Go to PythonAnywhere Web tab and check if the app is running"

# 4. Restart web app
echo "4. To restart web app:"
echo "   - Go to PythonAnywhere Web tab"
echo "   - Click 'Reload' for your web app"
echo "   - Wait 30 seconds for restart"

# 5. Test endpoints
echo "5. Testing endpoints after restart..."
curl -s https://agtpricetags.com/api/database-stats | head -5
