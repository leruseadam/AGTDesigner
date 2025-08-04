#!/usr/bin/env python3
"""
Find the correct WSGI file and force PythonAnywhere to use it.
"""

import os
import time

def create_wsgi_finder():
    """Create a script to help find the correct WSGI file."""
    
    unique_id = int(time.time())
    
    print("=== PYTHONANYWHERE WSGI FILE FINDER ===")
    print(f"Unique ID: {unique_id}")
    print()
    
    print("=== POSSIBLE WSGI FILE LOCATIONS ===")
    possible_paths = [
        "/var/www/www_agtpricetags_com_wsgi.py",
        "/home/adamcordova/AGTDesigner/wsgi.py",
        "/home/adamcordova/wsgi.py",
        "/var/www/wsgi.py"
    ]
    
    for path in possible_paths:
        print(f"• {path}")
    
    print()
    print("=== INSTRUCTIONS TO FIND THE RIGHT FILE ===")
    print("1. Go to PythonAnywhere dashboard")
    print("2. Navigate to Web tab")
    print("3. Click on your web app (www.agtpricetags.com)")
    print("4. Look for 'WSGI configuration file' section")
    print("5. Click to edit the WSGI file")
    print("6. Check the file path shown in the editor")
    print("7. The path should be: /var/www/www_agtpricetags_com_wsgi.py")
    print()
    
    print("=== FORCE RELOAD WSGI ===")
    print("Use this WSGI to force PythonAnywhere to reload:")
    print("-" * 50)
    
    wsgi_content = f'''#!/usr/bin/env python3
"""
FORCE RELOAD WSGI - ID: {unique_id}
This will force PythonAnywhere to use the correct file.
"""

import sys
import os
import time

# Force reload with unique ID
UNIQUE_ID = {unique_id}
TIMESTAMP = {int(time.time())}

print(f"FORCE RELOAD WSGI - ID: {{UNIQUE_ID}} - TIMESTAMP: {{TIMESTAMP}}")
print(f"File: {{__file__}}")
print(f"Directory: {{os.getcwd()}}")

# Add project directory
project_dir = '/home/adamcordova/AGTDesigner'
sys.path.insert(0, project_dir)

# Try to import the app
try:
    from app import create_app
    application = create_app()
    print(f"✓ SUCCESS: App loaded - ID: {{UNIQUE_ID}}")
except Exception as e:
    print(f"✗ ERROR: {{e}} - ID: {{UNIQUE_ID}}")
    from flask import Flask
    application = Flask(__name__)
    
    @application.route('/')
    def error():
        return f"""
        <h1>Force Reload WSGI - ID: {{UNIQUE_ID}}</h1>
        <p>Timestamp: {{TIMESTAMP}}</p>
        <p>Error: {{e}}</p>
        <p>File: {{__file__}}</p>
        <p>Directory: {{os.getcwd()}}</p>
        """, 500

if __name__ == "__main__":
    application.run()
'''
    
    print(wsgi_content)
    print("-" * 50)
    
    print()
    print("=== STEP-BY-STEP FIX ===")
    print("1. Go to PythonAnywhere Web tab")
    print("2. Click on your web app")
    print("3. Go to WSGI configuration file")
    print("4. DELETE EVERYTHING in the current file")
    print("5. Copy and paste the force reload WSGI above")
    print("6. SAVE the file (make sure it saves)")
    print("7. Go back to main web app page")
    print("8. Click RELOAD 3-4 times")
    print("9. Wait 5 minutes")
    print("10. Check error logs for: 'FORCE RELOAD WSGI - ID: {unique_id}'")
    print()
    
    print("=== WHAT TO LOOK FOR ===")
    print(f"In error logs, you should see:")
    print(f"FORCE RELOAD WSGI - ID: {unique_id}")
    print(f"Timestamp: {int(time.time())}")
    print()
    
    print("=== IF YOU STILL SEE OLD ERRORS ===")
    print("If you still see the old shell script error:")
    print("1. You might be editing the wrong file")
    print("2. Try creating a new web app")
    print("3. Contact PythonAnywhere support")
    
    return wsgi_content, unique_id

if __name__ == "__main__":
    create_wsgi_finder() 