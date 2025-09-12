#!/bin/bash
# Fix duplicate upload_file_fixed function in PythonAnywhere app.py
echo "Fixing duplicate upload_file_fixed function..."

# Create backup
cp /home/adamcordova/AGTDesigner/app.py /home/adamcordova/AGTDesigner/app.py.backup.$(date +%Y%m%d_%H%M%S)

# Remove the duplicate upload_file_fixed function (the one that was added by our script)
echo "Removing duplicate upload_file_fixed function..."
sed -i '/^@app.route.*upload.*methods.*POST.*$/,/^def upload_file_fixed/,/^}$/d' /home/adamcordova/AGTDesigner/app.py

# Also remove any duplicate performance endpoints
echo "Removing duplicate performance endpoints..."
sed -i '/^@app.route.*performance.*status.*$/,/^def performance_status/,/^}$/d' /home/adamcordova/AGTDesigner/app.py
sed -i '/^@app.route.*performance.*clear-cache.*$/,/^def clear_performance_cache/,/^}$/d' /home/adamcordova/AGTDesigner/app.py

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
