#!/usr/bin/env python3

"""
Verification script for PythonAnywhere setup
Run this after setup to verify everything is working
"""

import os
import sys
import subprocess

def check_pythonanywhere_environment():
    """Check if we're running on PythonAnywhere."""
    print("🔍 Checking PythonAnywhere environment...")
    
    is_pythonanywhere = os.environ.get('PYTHONANYWHERE', 'false').lower() == 'true'
    hostname = os.uname().nodename if hasattr(os, 'uname') else 'unknown'
    
    print(f"  Hostname: {hostname}")
    print(f"  PYTHONANYWHERE env var: {is_pythonanywhere}")
    
    if 'pythonanywhere' in hostname.lower() or is_pythonanywhere:
        print("✅ Running on PythonAnywhere")
        return True
    else:
        print("⚠️  Not running on PythonAnywhere")
        return False

def check_directories():
    """Check if required directories exist and have correct permissions."""
    print("\n📁 Checking directories...")
    
    directories = ['uploads', 'output', 'cache', 'logs', 'temp']
    
    for dir_name in directories:
        if os.path.exists(dir_name):
            stat_info = os.stat(dir_name)
            permissions = oct(stat_info.st_mode)[-3:]
            print(f"  ✅ {dir_name}/ - permissions: {permissions}")
            
            if permissions != '755':
                print(f"    ⚠️  {dir_name}/ should have 755 permissions")
        else:
            print(f"  ❌ {dir_name}/ - directory not found")

def check_flask_app():
    """Check if Flask app can be imported and created."""
    print("\n🐍 Checking Flask app...")
    
    try:
        from app import create_app
        print("  ✅ Flask app imported successfully")
        
        app = create_app()
        print("  ✅ Flask app created successfully")
        
        # Check configuration
        upload_folder = app.config.get('UPLOAD_FOLDER')
        print(f"  ✅ Upload folder configured: {upload_folder}")
        
        return True
    except Exception as e:
        print(f"  ❌ Flask app error: {e}")
        return False

def check_file_upload():
    """Test file upload functionality."""
    print("\n📤 Testing file upload...")
    
    upload_dir = os.path.join(os.getcwd(), 'uploads')
    
    try:
        # Test file creation
        test_file = os.path.join(upload_dir, 'test_upload.txt')
        with open(test_file, 'w') as f:
            f.write('Test upload functionality')
        
        print("  ✅ Test file created successfully")
        
        # Check file size
        file_size = os.path.getsize(test_file)
        print(f"  ✅ Test file size: {file_size} bytes")
        
        # Clean up
        os.remove(test_file)
        print("  ✅ Test file cleaned up")
        
        return True
    except Exception as e:
        print(f"  ❌ File upload test failed: {e}")
        return False

def check_dependencies():
    """Check if required dependencies are installed."""
    print("\n📦 Checking dependencies...")
    
    required_packages = [
        'flask',
        'pandas',
        'openpyxl',
        'werkzeug'
    ]
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package} - installed")
        except ImportError:
            print(f"  ❌ {package} - not installed")

def main():
    """Main verification function."""
    print("🧪 PythonAnywhere Setup Verification")
    print("=" * 40)
    
    # Check environment
    is_pythonanywhere = check_pythonanywhere_environment()
    
    # Check directories
    check_directories()
    
    # Check Flask app
    flask_ok = check_flask_app()
    
    # Check file upload
    upload_ok = check_file_upload()
    
    # Check dependencies
    check_dependencies()
    
    # Summary
    print("\n📊 Summary:")
    print("=" * 40)
    
    if is_pythonanywhere:
        print("✅ PythonAnywhere environment detected")
    else:
        print("⚠️  Not running on PythonAnywhere")
    
    if flask_ok:
        print("✅ Flask app working correctly")
    else:
        print("❌ Flask app has issues")
    
    if upload_ok:
        print("✅ File upload working correctly")
    else:
        print("❌ File upload has issues")
    
    print("\n🎯 Next steps:")
    if flask_ok and upload_ok:
        print("✅ Setup appears to be working correctly!")
        print("   You can now test the web interface")
    else:
        print("❌ Some issues detected")
        print("   Check the error messages above")
        print("   Run the fix script again if needed")

if __name__ == "__main__":
    main()
