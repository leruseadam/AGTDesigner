#!/usr/bin/env python3
"""
Upload Issues Fix Script for PythonAnywhere
This script diagnoses and fixes common upload problems on PythonAnywhere.
"""

import os
import sys
import stat
import logging
from pathlib import Path

def setup_logging():
    """Setup logging for the fix script."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def check_directory_permissions(directory):
    """Check and fix directory permissions."""
    try:
        if not os.path.exists(directory):
            print(f"📁 Creating directory: {directory}")
            os.makedirs(directory, exist_ok=True)
        
        # Check current permissions
        current_mode = os.stat(directory).st_mode
        print(f"📁 Directory: {directory}")
        print(f"   Current permissions: {oct(current_mode)[-3:]}")
        
        # Set proper permissions (read, write, execute for owner and group)
        target_mode = stat.S_IRWXU | stat.S_IRWXG  # 770 permissions
        if current_mode != target_mode:
            print(f"   Fixing permissions to: {oct(target_mode)[-3:]}")
            os.chmod(directory, target_mode)
            print("   ✅ Permissions fixed")
        else:
            print("   ✅ Permissions are correct")
            
        return True
    except Exception as e:
        print(f"   ❌ Error fixing directory {directory}: {e}")
        return False

def check_file_permissions(file_path):
    """Check and fix file permissions."""
    try:
        if os.path.exists(file_path):
            current_mode = os.stat(file_path).st_mode
            print(f"📄 File: {file_path}")
            print(f"   Current permissions: {oct(current_mode)[-3:]}")
            
            # Set proper permissions (read, write for owner and group)
            target_mode = stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP  # 660 permissions
            if current_mode != target_mode:
                print(f"   Fixing permissions to: {oct(target_mode)[-3:]}")
                os.chmod(file_path, target_mode)
                print("   ✅ Permissions fixed")
            else:
                print("   ✅ Permissions are correct")
        else:
            print(f"📄 File: {file_path} (does not exist)")
            
        return True
    except Exception as e:
        print(f"   ❌ Error fixing file {file_path}: {e}")
        return False

def check_upload_configuration():
    """Check upload configuration settings."""
    print("\n🔧 Checking Upload Configuration...")
    
    # Check Flask app configuration
    try:
        from app import app
        print("✅ Flask app imported successfully")
        
        # Check upload folder configuration
        upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
        print(f"📁 Upload folder configured as: {upload_folder}")
        
        # Check max file size
        max_size = app.config.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024)
        print(f"📏 Max file size: {max_size / (1024*1024):.1f} MB")
        
        return upload_folder
    except Exception as e:
        print(f"❌ Error checking Flask configuration: {e}")
        return 'uploads'

def create_test_upload_file():
    """Create a test upload file to verify functionality."""
    try:
        import pandas as pd
        from datetime import datetime
        
        # Create a simple test DataFrame
        test_data = {
            'Product Name*': ['Test Product 1', 'Test Product 2'],
            'Vendor': ['Test Vendor', 'Test Vendor'],
            'Product Type*': ['Concentrate', 'Concentrate'],
            'Price': [25.00, 30.00],
            'THC test result': [20.5, 22.1],
            'CBD test result': [0.5, 0.3]
        }
        
        df = pd.DataFrame(test_data)
        
        # Create uploads directory if it doesn't exist
        uploads_dir = 'uploads'
        os.makedirs(uploads_dir, exist_ok=True)
        
        # Create test file with absolute path
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        test_file = os.path.abspath(os.path.join(uploads_dir, f'test_upload_{timestamp}.xlsx'))
        
        df.to_excel(test_file, index=False)
        print(f"✅ Created test upload file: {test_file}")
        
        # Verify file exists
        if os.path.exists(test_file):
            print(f"✅ Test file verified to exist: {test_file}")
            return test_file
        else:
            print(f"❌ Test file was not created: {test_file}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating test file: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_upload_functionality():
    """Test the upload functionality."""
    print("\n🧪 Testing Upload Functionality...")
    
    try:
        from app import app
        
        # Create test file
        test_file = create_test_upload_file()
        if not test_file:
            print("❌ Could not create test file")
            return False
        
        # Verify file exists before testing
        if not os.path.exists(test_file):
            print(f"❌ Test file does not exist: {test_file}")
            return False
        
        print(f"✅ Test file exists: {test_file}")
        print(f"✅ File size: {os.path.getsize(test_file)} bytes")
        
        # Test the upload endpoint
        with app.test_client() as client:
            with open(test_file, 'rb') as f:
                filename = os.path.basename(test_file)
                print(f"📤 Testing upload with file: {filename}")
                response = client.post('/upload', 
                                     data={'file': (f, filename, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')})
                
                print(f"📤 Upload test response status: {response.status_code}")
                
                try:
                    response_data = response.get_json()
                    print(f"📤 Upload test response: {response_data}")
                except Exception as e:
                    print(f"📤 Upload test response (raw): {response.data}")
                
                if response.status_code == 200:
                    print("✅ Upload functionality test passed")
                    return True
                else:
                    print("❌ Upload functionality test failed")
                    return False
                    
    except Exception as e:
        print(f"❌ Error testing upload functionality: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_basic_app_functionality():
    """Test basic app functionality."""
    print("\n🧪 Testing Basic App Functionality...")
    
    try:
        from app import app
        
        with app.test_client() as client:
            # Test status endpoint
            response = client.get('/api/status')
            print(f"📊 Status endpoint response: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Status endpoint working")
                return True
            else:
                print("❌ Status endpoint not working")
                return False
                
    except Exception as e:
        print(f"❌ Error testing basic app functionality: {e}")
        return False

def main():
    """Main function to fix upload issues."""
    print("🔧 PythonAnywhere Upload Issues Fix Script")
    print("=" * 50)
    
    setup_logging()
    
    # Get current working directory
    cwd = os.getcwd()
    print(f"📍 Current working directory: {cwd}")
    
    # Check and fix directory permissions
    print("\n📁 Checking Directory Permissions...")
    
    directories_to_check = [
        'uploads',
        'output',
        'cache',
        'logs',
        'static',
        'templates'
    ]
    
    for directory in directories_to_check:
        check_directory_permissions(directory)
    
    # Check upload configuration
    upload_folder = check_upload_configuration()
    
    # Check specific upload folder permissions
    print(f"\n📁 Checking Upload Folder: {upload_folder}")
    check_directory_permissions(upload_folder)
    
    # Check app.py permissions
    print("\n📄 Checking App File Permissions...")
    check_file_permissions('app.py')
    
    # Test basic app functionality first
    basic_works = test_basic_app_functionality()
    
    # Test upload functionality
    upload_works = test_upload_functionality()
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 SUMMARY")
    print("=" * 50)
    
    if basic_works:
        print("✅ Basic app functionality is working")
    else:
        print("❌ Basic app functionality needs attention")
    
    if upload_works:
        print("✅ Upload functionality is working correctly")
    else:
        print("❌ Upload functionality needs attention")
        print("\n🔧 Additional troubleshooting steps:")
        print("1. Check PythonAnywhere error logs")
        print("2. Verify virtual environment is activated")
        print("3. Ensure all dependencies are installed")
        print("4. Check web app configuration in PythonAnywhere")
        print("5. Test with a simple Excel file manually")
    
    print("\n📁 Directories checked and fixed:")
    for directory in directories_to_check:
        if os.path.exists(directory):
            print(f"   ✅ {directory}")
        else:
            print(f"   ❌ {directory} (not found)")
    
    print(f"\n📁 Upload folder: {upload_folder}")
    if os.path.exists(upload_folder):
        print(f"   ✅ Upload folder exists and has correct permissions")
    else:
        print(f"   ❌ Upload folder not found")
    
    print("\n🎉 Fix script completed!")

if __name__ == "__main__":
    main() 