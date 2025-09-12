#!/bin/bash
# Direct fix for PythonAnywhere app.py file
echo 'Fixing PythonAnywhere app.py file...'

# Fix 1: quests
from pathlib import Path...
sed -i 's|quests
from pathlib import Path|from pathlib import Path|g' /home/adamcordova/AGTDesigner/app.py

# Fix 2: def simple_# Use simple initialization on PythonAn...
sed -i 's|def simple_# Use simple initialization on PythonAnywhere to prevent hangs|# Use simple initialization on PythonAnywhere to prevent hangs|g' /home/adamcordova/AGTDesigner/app.py

# Fix 3: else:
    initialize_excel_processor():
    """Sim...
sed -i 's|else:
    initialize_excel_processor():
    """Simple initialization that won'"'"'t get stuck - for PythonAnywhere"""|else:
    initialize_excel_processor()

def simple_initialize_excel_processor():
    """Simple initialization that won'"'"'t get stuck - for PythonAnywhere"""|g' /home/adamcordova/AGTDesigner/app.py

echo 'Fixes applied successfully!'
echo 'Reloading web app...'
touch /var/www/www_agtpricetags_com_wsgi.py
echo 'Web app reloaded!'
