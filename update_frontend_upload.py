#!/usr/bin/env python3
"""
Update frontend to use simple upload for PythonAnywhere
"""

import os
import re

def update_frontend_upload():
    """Update the frontend JavaScript to use simple upload for PythonAnywhere"""
    
    js_file = 'static/js/main.js'
    if not os.path.exists(js_file):
        print(f"❌ {js_file} not found")
        return False
    
    # Read the current file
    with open(js_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add detection for PythonAnywhere and use simple upload
    pythonanywhere_detection = '''
    // Detect if running on PythonAnywhere
    function isPythonAnywhere() {
        return window.location.hostname.includes('pythonanywhere.com');
    }
    
    // Choose upload endpoint based on environment
    function getUploadEndpoint() {
        if (isPythonAnywhere()) {
            return '/upload-pythonanywhere';
        } else {
            return '/upload';
        }
    }
'''
    
    # Find where to insert the detection code (after the first function)
    insert_location = content.find('function ')
    if insert_location == -1:
        insert_location = 0
    
    # Insert the detection code
    new_content = content[:insert_location] + pythonanywhere_detection + content[insert_location:]
    
    # Update the upload function to use the appropriate endpoint
    old_upload_pattern = r"fetch\('/upload'"
    new_upload_pattern = "fetch(getUploadEndpoint()"
    
    new_content = re.sub(old_upload_pattern, new_upload_pattern, new_content)
    
    # Write the updated file
    with open(js_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Updated frontend to use simple upload for PythonAnywhere")
    return True

if __name__ == "__main__":
    update_frontend_upload()
