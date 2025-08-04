#!/usr/bin/env python3
"""
Fix for PythonAnywhere test script - remove localhost upload test
"""

import os
import time
import requests
from pathlib import Path

def fix_test_script():
    """Fix the test script to work on PythonAnywhere."""
    
    # Read the current test script
    with open('test_pythonanywhere_file_loading.py', 'r') as f:
        content = f.read()
    
    # Replace the upload test with a PythonAnywhere-compatible version
    old_upload_test = '''def test_upload_performance():
    """Test upload performance with a small file."""
    print("🚀 Testing upload performance...")
    
    # Create a small test file
    test_file_path = "/tmp/test_upload.xlsx"
    test_content = b"PK\\x03\\x04"  # Minimal Excel file header
    
    try:
        with open(test_file_path, 'wb') as f:
            f.write(test_content)
        
        # Test upload
        start_time = time.time()
        
        with open(test_file_path, 'rb') as f:
            files = {'file': ('test_upload.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            response = requests.post('http://localhost:5000/upload', files=files, timeout=30)
        
        upload_time = time.time() - start_time
        
        if response.status_code == 200:
            print(f"✅ Upload successful in {upload_time:.2f} seconds")
            return True
        else:
            print(f"❌ Upload failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing upload: {e}")
    finally:
        # Clean up test file
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
    
    return False'''
    
    new_upload_test = '''def test_upload_performance():
    """Test upload performance configuration."""
    print("🚀 Testing upload performance configuration...")
    
    try:
        # Test if upload performance optimizations are in place
        with open('app.py', 'r') as f:
            app_content = f.read()
        
        # Check for performance optimizations
        optimizations_found = []
        
        if "UPLOAD_PERFORMANCE_MODE = True" in app_content:
            optimizations_found.append("Upload performance mode enabled")
        
        if "UPLOAD_CHUNK_SIZE = 1024 * 1024" in app_content:
            optimizations_found.append("Upload chunk size optimized")
        
        if "UPLOAD_DISABLE_HEAVY_PROCESSING = True" in app_content:
            optimizations_found.append("Heavy processing disabled during upload")
        
        if "MAX_CONTENT_LENGTH = 25 * 1024 * 1024" in app_content:
            optimizations_found.append("File size limit increased to 25MB")
        
        if optimizations_found:
            print(f"✅ Upload performance optimizations found:")
            for opt in optimizations_found:
                print(f"   - {opt}")
            return True
        else:
            print("❌ Upload performance optimizations not found")
            return False
            
    except Exception as e:
        print(f"❌ Error testing upload configuration: {e}")
        return False'''
    
    if old_upload_test in content:
        content = content.replace(old_upload_test, new_upload_test)
        print("✅ Updated upload performance test for PythonAnywhere")
    else:
        print("⚠️  Could not find upload test to replace")
    
    # Also update the main function to reflect the change
    content = content.replace(
        "print(f\"Upload Performance: {'✅ PASS' if upload_ok else '❌ FAIL'}\")",
        "print(f\"Upload Configuration: {'✅ PASS' if upload_ok else '❌ FAIL'}\")"
    )
    
    # Write back the updated content
    with open('test_pythonanywhere_file_loading.py', 'w') as f:
        f.write(content)

def create_pythonanywhere_upload_test():
    """Create a separate upload test for PythonAnywhere."""
    
    upload_test = '''#!/usr/bin/env python3
"""
PythonAnywhere Upload Test
Tests actual file upload functionality on PythonAnywhere.
"""

import os
import time
import requests
from pathlib import Path

def test_actual_upload():
    """Test actual file upload on PythonAnywhere."""
    print("🚀 Testing actual file upload on PythonAnywhere...")
    
    # Find a test file to upload
    test_files = []
    
    # Look for small Excel files in uploads directory
    uploads_dir = "/home/adamcordova/AGTDesigner/uploads"
    if os.path.exists(uploads_dir):
        for filename in os.listdir(uploads_dir):
            if filename.lower().endswith('.xlsx') and filename.startswith('A Greener Today'):
                file_path = os.path.join(uploads_dir, filename)
                file_size = os.path.getsize(file_path)
                if file_size < 1000000:  # Less than 1MB for testing
                    test_files.append((file_path, filename, file_size))
    
    if not test_files:
        print("❌ No suitable test files found (need small Excel files)")
        return False
    
    # Use the smallest file for testing
    test_files.sort(key=lambda x: x[2])
    test_file_path, test_filename, test_file_size = test_files[0]
    
    print(f"📁 Using test file: {test_filename} ({test_file_size:,} bytes)")
    
    try:
        # Test upload using the web interface
        print("📤 Testing file upload...")
        start_time = time.time()
        
        with open(test_file_path, 'rb') as f:
            files = {'file': (test_filename, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            
            # Use your actual PythonAnywhere domain
            upload_url = "https://yourusername.pythonanywhere.com/upload"
            
            response = requests.post(upload_url, files=files, timeout=60)
        
        upload_time = time.time() - start_time
        
        if response.status_code == 200:
            print(f"✅ Upload successful in {upload_time:.2f} seconds")
            return True
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ Error testing upload: {e}")
        return False

def main():
    """Run the upload test."""
    print("🧪 PythonAnywhere Upload Test")
    print("=" * 40)
    
    success = test_actual_upload()
    
    print("\\n" + "=" * 40)
    if success:
        print("🎉 Upload test passed!")
    else:
        print("⚠️  Upload test failed. Check the output above.")

if __name__ == "__main__":
    main()
'''
    
    with open('test_pythonanywhere_upload.py', 'w') as f:
        f.write(upload_test)
    
    print("✅ Created test_pythonanywhere_upload.py")

def main():
    """Main fix function."""
    print("🔧 Fixing PythonAnywhere Test Script")
    print("=" * 40)
    
    try:
        fix_test_script()
        create_pythonanywhere_upload_test()
        
        print("\\n" + "=" * 40)
        print("✅ Test script fixes complete!")
        print("\\n📋 Changes made:")
        print("1. Removed localhost upload test (not applicable on PythonAnywhere)")
        print("2. Added upload configuration verification")
        print("3. Created separate upload test for actual file uploads")
        
        print("\\n📋 Next steps:")
        print("1. Run: python3 test_pythonanywhere_file_loading.py")
        print("2. For actual upload testing: python3 test_pythonanywhere_upload.py")
        print("3. Update the upload URL in test_pythonanywhere_upload.py with your domain")
        
    except Exception as e:
        print(f"❌ Error during fix: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 