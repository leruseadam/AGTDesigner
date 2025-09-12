#!/usr/bin/env python3
"""
Direct fix for PythonAnywhere app.py file
This script will be converted to bash commands to fix the corrupted app.py
"""

# The fixes needed for the PythonAnywhere app.py file
fixes = [
    # Fix 1: Remove stray 'quests' on line 51
    {
        'search': 'quests\nfrom pathlib import Path',
        'replace': 'from pathlib import Path'
    },
    # Fix 2: Fix malformed function definition
    {
        'search': 'def simple_# Use simple initialization on PythonAnywhere to prevent hangs',
        'replace': '# Use simple initialization on PythonAnywhere to prevent hangs'
    },
    # Fix 3: Fix corrupted initialization code
    {
        'search': 'else:\n    initialize_excel_processor():\n    """Simple initialization that won\'t get stuck - for PythonAnywhere"""',
        'replace': 'else:\n    initialize_excel_processor()\n\ndef simple_initialize_excel_processor():\n    """Simple initialization that won\'t get stuck - for PythonAnywhere"""'
    }
]

print("#!/bin/bash")
print("# Direct fix for PythonAnywhere app.py file")
print("echo 'Fixing PythonAnywhere app.py file...'")
print("")

for i, fix in enumerate(fixes, 1):
    print(f"# Fix {i}: {fix['search'][:50]}...")
    search_escaped = fix['search'].replace('|', '\\|').replace("'", "'\"'\"'")
    replace_escaped = fix['replace'].replace('|', '\\|').replace("'", "'\"'\"'")
    print(f"sed -i 's|{search_escaped}|{replace_escaped}|g' /home/adamcordova/AGTDesigner/app.py")
    print("")

print("echo 'Fixes applied successfully!'")
print("echo 'Reloading web app...'")
print("touch /var/www/www_agtpricetags_com_wsgi.py")
print("echo 'Web app reloaded!'")
