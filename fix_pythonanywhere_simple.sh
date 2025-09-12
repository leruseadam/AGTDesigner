#!/bin/bash
# Direct fix for PythonAnywhere app.py file
echo "Fixing PythonAnywhere app.py file..."

# Fix 1: Remove stray 'quests' on line 51
sed -i 's/quests//g' /home/adamcordova/AGTDesigner/app.py

# Fix 2: Fix malformed function definition
sed -i 's/def simple_# Use simple initialization on PythonAnywhere to prevent hangs/# Use simple initialization on PythonAnywhere to prevent hangs/g' /home/adamcordova/AGTDesigner/app.py

# Fix 3: Fix corrupted initialization code
sed -i 's/else:\n    initialize_excel_processor():/else:\n    initialize_excel_processor()\n\ndef simple_initialize_excel_processor():/g' /home/adamcordova/AGTDesigner/app.py

echo "Fixes applied successfully!"
echo "Reloading web app..."
touch /var/www/www_agtpricetags_com_wsgi.py
echo "Web app reloaded!"
