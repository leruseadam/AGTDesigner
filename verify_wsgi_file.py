#!/usr/bin/env python3
"""
Verify which WSGI file is being used and force PythonAnywhere to recognize changes.
"""

import os
import time

def create_verification_wsgi():
    """Create a WSGI file that will help us verify which file is being used."""
    
    # Generate unique identifier
    unique_id = int(time.time())
    
    wsgi_content = f'''#!/usr/bin/env python3
"""
VERIFICATION WSGI - UNIQUE ID: {unique_id}
This will help us verify which WSGI file PythonAnywhere is actually using.
"""

import sys
import os
import time

# Unique identifier to verify this file is being used
UNIQUE_ID = {unique_id}
TIMESTAMP = {int(time.time())}

print(f"VERIFICATION WSGI LOADED - ID: {{UNIQUE_ID}} - TIMESTAMP: {{TIMESTAMP}}")
print(f"File path: {{__file__}}")
print(f"Current directory: {{os.getcwd()}}")

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
        <h1>Verification WSGI - ID: {{UNIQUE_ID}}</h1>
        <p>Timestamp: {{TIMESTAMP}}</p>
        <p>Error: {{e}}</p>
        <p>File: {{__file__}}</p>
        <p>Directory: {{os.getcwd()}}</p>
        """, 500

if __name__ == "__main__":
    application.run()
'''
    
    with open('verification_wsgi.py', 'w') as f:
        f.write(wsgi_content)
    
    print(f"✓ Created verification WSGI with ID: {unique_id}")
    print(f"Timestamp: {int(time.time())}")
    return wsgi_content, unique_id

def main():
    """Main function to create verification WSGI."""
    print("Creating verification WSGI...")
    print("=" * 50)
    
    content, unique_id = create_verification_wsgi()
    
    print(f"\n=== VERIFICATION WSGI CONTENT ===")
    print(f"Copy this to PythonAnywhere:")
    print("-" * 50)
    print(content)
    print("-" * 50)
    
    print(f"\n=== INSTRUCTIONS ===")
    print(f"1. Go to PythonAnywhere Web tab")
    print(f"2. Click on your web app")
    print(f"3. Go to WSGI configuration file")
    print(f"4. DELETE EVERYTHING in the current file")
    print(f"5. Copy and paste the verification WSGI content above")
    print(f"6. SAVE the file")
    print(f"7. Go back and click RELOAD")
    print(f"8. Wait 2-3 minutes")
    print(f"9. Check error logs for: 'VERIFICATION WSGI LOADED - ID: {unique_id}'")
    print(f"10. If you see the ID {unique_id}, the file is being used")
    print(f"11. If you don't see the ID, you're editing the wrong file")
    
    print(f"\n=== WHAT TO LOOK FOR ===")
    print(f"In error logs, you should see:")
    print(f"VERIFICATION WSGI LOADED - ID: {unique_id}")
    print(f"Timestamp: {int(time.time())}")
    print(f"File path: /var/www/www_agtpricetags_com_wsgi.py")
    
    print(f"\n=== IF YOU DON'T SEE THE ID ===")
    print(f"If you don't see the unique ID in the error logs:")
    print(f"1. You might be editing the wrong WSGI file")
    print(f"2. The file might not be saving properly")
    print(f"3. PythonAnywhere might be using a cached version")
    print(f"4. Try creating a new web app instead")

if __name__ == "__main__":
    main() 