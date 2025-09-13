#!/bin/bash
# Fix duplicate upload_status function
echo "Fixing duplicate upload_status function..."

# Create backup
cp /home/adamcordova/AGTDesigner/app.py /home/adamcordova/AGTDesigner/app.py.backup.$(date +%Y%m%d_%H%M%S)

# Remove the duplicate upload_status function (keep only the first one)
# Find the line numbers of both upload_status functions
echo "Finding duplicate upload_status functions..."
grep -n "def upload_status" /home/adamcordova/AGTDesigner/app.py

# Remove the second occurrence and everything after it until the next function or end of file
echo "Removing duplicate function..."
python3 << 'EOF'
import re

# Read the file
with open('/home/adamcordova/AGTDesigner/app.py', 'r') as f:
    content = f.read()

# Find all upload_status function definitions
matches = list(re.finditer(r'@app\.route\([\'"][^\'"]*upload-status[^\'"]*[\'"].*?\n.*?def upload_status\(\):', content, re.DOTALL))

if len(matches) > 1:
    print(f"Found {len(matches)} upload_status functions")
    
    # Keep only the first one, remove the rest
    first_end = matches[0].end()
    
    # Find the end of the first function (next @app.route or end of file)
    next_route = content.find('@app.route', first_end)
    if next_route == -1:
        # No more routes, keep everything up to the first function
        new_content = content[:first_end]
    else:
        # Find the start of the next route and remove everything in between
        new_content = content[:first_end] + content[next_route:]
    
    # Write the cleaned content
    with open('/home/adamcordova/AGTDesigner/app.py', 'w') as f:
        f.write(new_content)
    
    print("✅ Removed duplicate upload_status function")
else:
    print("No duplicates found or only one function exists")

EOF

# Verify the file compiles
echo "Verifying Python syntax..."
python3 -m py_compile /home/adamcordova/AGTDesigner/app.py
if [ $? -eq 0 ]; then
    echo "✅ Python syntax is valid!"
    echo "✅ Duplicate upload_status function removed!"
    echo "Reloading web app..."
    touch /var/www/www_agtpricetags_com_wsgi.py
    echo "Web app reloaded! Upload should work now."
else
    echo "❌ Syntax errors found. Restoring backup..."
    cp /home/adamcordova/AGTDesigner/app.py.backup.* /home/adamcordova/AGTDesigner/app.py
    exit 1
fi

echo "Duplicate upload_status fix applied successfully!"
