#!/bin/bash
# Comprehensive fix for PythonAnywhere app.py file
echo "Starting comprehensive fix for PythonAnywhere..."

# First, let's backup the current file
echo "Creating backup..."
cp /home/adamcordova/AGTDesigner/app.py /home/adamcordova/AGTDesigner/app.py.backup.$(date +%Y%m%d_%H%M%S)

# Fix 1: Remove stray 'quests' on line 51
echo "Fixing stray 'quests'..."
sed -i '/^quests$/d' /home/adamcordova/AGTDesigner/app.py

# Fix 2: Fix malformed function definition
echo "Fixing malformed function definition..."
sed -i 's/def simple_# Use simple initialization on PythonAnywhere to prevent hangs/# Use simple initialization on PythonAnywhere to prevent hangs/' /home/adamcordova/AGTDesigner/app.py

# Fix 3: Fix corrupted initialization code structure
echo "Fixing initialization code structure..."
sed -i 's/else:\n    initialize_excel_processor():/else:\n    initialize_excel_processor()\n\ndef simple_initialize_excel_processor():/' /home/adamcordova/AGTDesigner/app.py

# Fix 4: Remove any remaining malformed function definitions
echo "Cleaning up malformed functions..."
sed -i '/^def #/d' /home/adamcordova/AGTDesigner/app.py

# Fix 5: Ensure proper function structure
echo "Ensuring proper function structure..."
sed -i 's/^# Use simple initialization on PythonAnywhere to prevent hangs$/# Use simple initialization on PythonAnywhere to prevent hangs\nif os.environ.get("PYTHONANYWHERE_DOMAIN"):\n    simple_initialize_excel_processor()\nelse:\n    initialize_excel_processor()/' /home/adamcordova/AGTDesigner/app.py

# Verify the file compiles
echo "Verifying Python syntax..."
python3 -m py_compile /home/adamcordova/AGTDesigner/app.py
if [ $? -eq 0 ]; then
    echo "✅ Python syntax is now valid!"
else
    echo "❌ Still has syntax errors. Restoring backup..."
    cp /home/adamcordova/AGTDesigner/app.py.backup.* /home/adamcordova/AGTDesigner/app.py
    exit 1
fi

echo "Fixes applied successfully!"
echo "Reloading web app..."
touch /var/www/www_agtpricetags_com_wsgi.py
echo "Web app reloaded!"
echo "Check your web app now - it should work!"
