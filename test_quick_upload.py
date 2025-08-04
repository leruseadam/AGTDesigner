#!/usr/bin/env python3
"""
Quick test to verify upload processing works without product database integration
"""

import os
import sys
import time
import shutil
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_quick_upload():
    """Test upload processing without product database integration"""
    
    print("=== QUICK UPLOAD TEST (Product DB Disabled) ===")
    
    # Get the default file
    from src.core.data.excel_processor import get_default_upload_file
    default_file = get_default_upload_file()
    
    if not default_file or not os.path.exists(default_file):
        print("❌ No default file found")
        return False
    
    # Create a test copy
    test_file = "test_upload.xlsx"
    shutil.copy2(default_file, test_file)
    
    try:
        # Test 1: Create ExcelProcessor with product DB disabled
        print("\n1. Testing ExcelProcessor with product DB disabled...")
        from src.core.data.excel_processor import ExcelProcessor
        
        processor = ExcelProcessor()
        processor.enable_product_db_integration(False)  # Disable product DB
        
        # Test 2: Load file quickly
        print("\n2. Testing quick file loading...")
        start_time = time.time()
        success = processor.load_file(test_file)
        load_time = time.time() - start_time
        
        if success:
            print(f"✅ File loaded successfully in {load_time:.2f}s")
            print(f"   DataFrame shape: {processor.df.shape if processor.df is not None else 'None'}")
            print(f"   Product DB enabled: {getattr(processor, '_product_db_enabled', 'Unknown')}")
        else:
            print(f"❌ File loading failed")
            return False
        
        # Test 3: Test force reload
        print("\n3. Testing quick force reload...")
        from app import force_reload_excel_processor
        
        start_time = time.time()
        force_reload_excel_processor(test_file)
        reload_time = time.time() - start_time
        
        print(f"✅ Force reload completed in {reload_time:.2f}s")
        
        # Test 4: Verify product DB is still disabled
        from app import get_excel_processor
        excel_processor = get_excel_processor()
        product_db_enabled = getattr(excel_processor, '_product_db_enabled', True)
        print(f"   Product DB enabled after reload: {product_db_enabled}")
        
        if product_db_enabled:
            print("⚠️  Warning: Product DB was re-enabled during reload")
        else:
            print("✅ Product DB remains disabled")
        
        return True
        
    finally:
        # Clean up
        if os.path.exists(test_file):
            os.remove(test_file)
            print(f"\n🧹 Cleaned up test file: {test_file}")

if __name__ == "__main__":
    print("Starting quick upload test...")
    
    success = test_quick_upload()
    
    if success:
        print("\n🎉 Quick upload test passed! Upload processing should be fast now.")
    else:
        print("\n❌ Quick upload test failed.")
        sys.exit(1) 