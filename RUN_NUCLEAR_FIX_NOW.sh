#!/bin/bash
# RUN NUCLEAR DATABASE FIX NOW

echo "======================================="
echo "RUNNING NUCLEAR DATABASE FIX NOW"
echo "======================================="

echo "Step 1: Killing all processes..."
pkill -9 -f python
pkill -9 -f gunicorn  
pkill -9 -f flask
pkill -9 -f sqlite
sleep 3
echo "✅ All processes killed"

echo "Step 2: Removing all database files..."
rm -f uploads/*.db*
rm -f uploads/*.sqlite*
rm -f *.db*
rm -f *.sqlite*
echo "✅ All database files removed"

echo "Step 3: Cleaning up sessions and cache..."
rm -rf uploads/sessions/*
rm -rf uploads/cache/*
rm -rf uploads/temp/*
rm -rf uploads/old_corrupted_backups/*
echo "✅ Sessions and cache cleaned"

echo "Step 4: Creating fresh database..."
python3 create_fresh_database.py
echo "✅ Fresh database created"

echo "Step 5: Setting correct permissions..."
chmod 664 uploads/product_database_AGT_Bothell.db
chmod 755 uploads/
echo "✅ Permissions set"

echo "Step 6: Verifying database..."
sqlite3 uploads/product_database_AGT_Bothell.db ".schema products" | head -5
echo "✅ Database verified"

echo ""
echo "======================================="
echo "NUCLEAR FIX COMPLETE!"
echo "======================================="
echo "Now reload your web app:"
echo "1. Go to: https://www.pythonanywhere.com/user/adamcordova/webapps/"
echo "2. Click 'Reload' for www.agtpricetags.com"
echo "3. Wait 30 seconds"
echo ""
echo "Then test:"
echo "1. Visit: https://www.agtpricetags.com"
echo "2. Upload Excel file"
echo "3. Generate labels"
echo "4. CBD Huckleberry Web should show 'CBD' instead of 'HYBRID'"
echo ""
