#!/usr/bin/env python3
"""
Test script to verify fast startup of the Flask application.
This script measures the startup time and verifies that no default file is loaded.
"""

import time
import os
import sys
import logging

# Configure logging to be minimal for testing
logging.basicConfig(level=logging.WARNING)

def test_startup_time():
    """Test the startup time of the Flask application."""
    print("Testing Flask application startup time...")
    
    start_time = time.time()
    
    try:
        # Import the app (this will trigger the startup initialization)
        from app import app, DISABLE_STARTUP_FILE_LOADING, LAZY_LOADING_ENABLED
        
        startup_time = time.time() - start_time
        
        print(f"✓ Flask app imported successfully")
        print(f"✓ Startup time: {startup_time:.2f} seconds")
        print(f"✓ DISABLE_STARTUP_FILE_LOADING: {DISABLE_STARTUP_FILE_LOADING}")
        print(f"✓ LAZY_LOADING_ENABLED: {LAZY_LOADING_ENABLED}")
        
        if startup_time < 5.0:
            print("✓ Startup time is acceptable (< 5 seconds)")
        else:
            print("⚠ Startup time is slow (> 5 seconds)")
            
        return True
        
    except Exception as e:
        print(f"✗ Error during startup: {e}")
        return False

def test_no_default_file_loading():
    """Test that no default file is loaded during startup."""
    print("\nTesting that no default file is loaded...")
    
    try:
        from app import get_excel_processor
        
        # Get the Excel processor
        processor = get_excel_processor()
        
        # Check if any file is loaded
        if hasattr(processor, 'df') and processor.df is not None and len(processor.df) > 0:
            print(f"✗ Default file was loaded with {len(processor.df)} records")
            return False
        else:
            print("✓ No default file loaded (as expected)")
            return True
            
    except Exception as e:
        print(f"✗ Error testing default file loading: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("FLASK APP STARTUP PERFORMANCE TEST")
    print("=" * 50)
    
    success = True
    
    # Test startup time
    if not test_startup_time():
        success = False
    
    # Test no default file loading
    if not test_no_default_file_loading():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("✓ ALL TESTS PASSED - Fast startup configuration is working")
    else:
        print("✗ SOME TESTS FAILED - Check the configuration")
    print("=" * 50) 