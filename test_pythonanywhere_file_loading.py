#!/usr/bin/env python3
"""
Test script for PythonAnywhere file loading and upload performance.
"""

import os
import time
import requests
from pathlib import Path

def test_default_file_loading():
    """Test if default file loading works."""
    print("🔍 Testing default file loading...")
    
    try:
        from src.core.data.excel_processor import get_default_upload_file
        
        file_path = get_default_upload_file()
        if file_path:
            print(f"✅ Default file found: {file_path}")
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                print(f"✅ File exists and is {file_size:,} bytes")
                return True
            else:
                print(f"❌ File path exists but file not found: {file_path}")
        else:
            print("❌ No default file found")
    except Exception as e:
        print(f"❌ Error testing default file loading: {e}")
    
    return False

def test_upload_performance():
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
        return False

def main():
    """Run all tests."""
    print("🧪 PythonAnywhere File Loading and Upload Tests")
    print("=" * 50)
    
    # Test default file loading
    default_file_ok = test_default_file_loading()
    
    # Test upload performance
    upload_ok = test_upload_performance()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"Default File Loading: {'✅ PASS' if default_file_ok else '❌ FAIL'}")
    print(f"Upload Configuration: {'✅ PASS' if upload_ok else '❌ FAIL'}")
    
    if default_file_ok and upload_ok:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()
