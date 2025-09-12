#!/bin/bash
# Simple fix for duplicate upload_file_fixed function
echo "Fixing duplicate upload_file_fixed function..."

# Create backup
cp /home/adamcordova/AGTDesigner/app.py /home/adamcordova/AGTDesigner/app.py.backup.$(date +%Y%m%d_%H%M%S)

# Find and remove the duplicate upload_file_fixed function
echo "Finding duplicate functions..."
grep -n "def upload_file_fixed" /home/adamcordova/AGTDesigner/app.py

# Remove the second occurrence of upload_file_fixed function
echo "Removing duplicate upload_file_fixed function..."
# This will remove everything from the second @app.route('/upload' to the end of the second upload_file_fixed function
sed -i '/^@app.route.*upload.*methods.*POST.*$/,/^}$/d' /home/adamcordova/AGTDesigner/app.py

# Also remove duplicate performance functions
echo "Removing duplicate performance functions..."
sed -i '/^@app.route.*performance.*status.*$/,/^}$/d' /home/adamcordova/AGTDesigner/app.py
sed -i '/^@app.route.*performance.*clear-cache.*$/,/^}$/d' /home/adamcordova/AGTDesigner/app.py

# Verify the file compiles
echo "Verifying Python syntax..."
python3 -m py_compile /home/adamcordova/AGTDesigner/app.py
if [ $? -eq 0 ]; then
    echo "✅ Python syntax is now valid!"
    echo "✅ Duplicate functions removed!"
    echo "Reloading web app..."
    touch /var/www/www_agtpricetags_com_wsgi.py
    echo "Web app reloaded! Should work now."
else
    echo "❌ Still has syntax errors. Restoring backup..."
    cp /home/adamcordova/AGTDesigner/app.py.backup.* /home/adamcordova/AGTDesigner/app.py
    exit 1
fi

echo "Duplicate function fix applied successfully!"
