#!/usr/bin/env python3
"""
Test script to verify PythonAnywhere upload functionality
"""

import os
import sys
import tempfile
import shutil

def test_upload_functionality():
    """Test upload directory and file creation."""
    
    print("🧪 Testing PythonAnywhere Upload Functionality...")
    
    # Get project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    uploads_dir = os.path.join(project_dir, 'uploads')
    
    print(f"Project directory: {project_dir}")
    print(f"Uploads directory: {uploads_dir}")
    
    # Test 1: Check if uploads directory exists
    if os.path.exists(uploads_dir):
        print("✅ Uploads directory exists")
    else:
        print("❌ Uploads directory does not exist")
        return False
    
    # Test 2: Check permissions
    try:
        stat_info = os.stat(uploads_dir)
        permissions = oct(stat_info.st_mode)[-3:]
        print(f"✅ Uploads directory permissions: {permissions}")
        
        if permissions == '755':
            print("✅ Permissions are correct")
        else:
            print(f"⚠️  Permissions should be 755, got {permissions}")
    except Exception as e:
        print(f"❌ Error checking permissions: {e}")
        return False
    
    # Test 3: Test file creation
    try:
        test_file = os.path.join(uploads_dir, 'test_upload.txt')
        with open(test_file, 'w') as f:
            f.write('Test upload functionality')
        
        print("✅ Successfully created test file")
        
        # Clean up
        os.remove(test_file)
        print("✅ Successfully removed test file")
        
    except Exception as e:
        print(f"❌ Error creating test file: {e}")
        return False
    
    # Test 4: Test Flask app import
    try:
        sys.path.insert(0, project_dir)
        from app import create_app
        
        app = create_app()
        upload_folder = app.config.get('UPLOAD_FOLDER')
        print(f"✅ Flask app created successfully")
        print(f"✅ Upload folder configured: {upload_folder}")
        
    except Exception as e:
        print(f"❌ Error importing Flask app: {e}")
        return False
    
    print("✅ All upload tests passed!")
    return True

if __name__ == "__main__":
    success = test_upload_functionality()
    sys.exit(0 if success else 1)
