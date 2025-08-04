#!/usr/bin/env python3
"""
Test script to verify WSGI performance optimizations
"""

import os
import time
import sys

def test_wsgi_import():
    """Test importing the WSGI application with performance optimizations."""
    print("Testing WSGI import performance...")
    
    # Set environment variables for testing
    os.environ['DISABLE_DEFAULT_FILE_LOADING'] = 'True'
    os.environ['LAZY_LOADING_ENABLED'] = 'True'
    os.environ['PYTHONANYWHERE_SITE'] = 'True'
    
    start_time = time.time()
    
    try:
        # Import the WSGI application
        from wsgi_pythonanywhere import application
        import_time = time.time() - start_time
        
        print(f"✅ WSGI application imported successfully in {import_time:.2f} seconds")
        print(f"✅ Application type: {type(application)}")
        
        # Test basic functionality
        if hasattr(application, 'config'):
            print(f"✅ Flask config loaded: {application.config.get('DEBUG', 'N/A')}")
        
        return True
        
    except Exception as e:
        import_time = time.time() - start_time
        print(f"❌ Failed to import WSGI application after {import_time:.2f} seconds")
        print(f"❌ Error: {e}")
        return False

def test_default_file_loading_disabled():
    """Test that default file loading is properly disabled."""
    print("\nTesting default file loading disable...")
    
    try:
        from src.core.data.excel_processor import get_default_upload_file
        
        # Test with environment variable set
        os.environ['DISABLE_DEFAULT_FILE_LOADING'] = 'True'
        result = get_default_upload_file()
        
        if result is None:
            print("✅ Default file loading properly disabled")
            return True
        else:
            print(f"❌ Default file loading not disabled, returned: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing default file loading: {e}")
        return False

def test_lazy_loading():
    """Test that lazy loading is working correctly."""
    print("\nTesting lazy loading...")
    
    try:
        from app import get_excel_processor
        
        # Test with lazy loading enabled
        os.environ['LAZY_LOADING_ENABLED'] = 'True'
        
        start_time = time.time()
        processor = get_excel_processor()
        load_time = time.time() - start_time
        
        if processor is not None:
            print(f"✅ Excel processor created in {load_time:.2f} seconds")
            
            # Check if DataFrame is empty (indicating lazy loading)
            if hasattr(processor, 'df') and processor.df.empty:
                print("✅ Lazy loading working - DataFrame is empty")
                return True
            else:
                print("❌ Lazy loading not working - DataFrame is not empty")
                return False
        else:
            print("❌ Failed to create Excel processor")
            return False
            
    except Exception as e:
        print(f"❌ Error testing lazy loading: {e}")
        return False

def main():
    """Run all performance tests."""
    print("🚀 WSGI Performance Optimization Test")
    print("=" * 50)
    
    tests = [
        test_wsgi_import,
        test_default_file_loading_disabled,
        test_lazy_loading
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! WSGI optimizations are working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 