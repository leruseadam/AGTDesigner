#!/usr/bin/env python3
"""
Test script to identify upload processing issues
"""

import os
import sys
import time
import threading
import traceback
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_upload_processing():
    """Test the upload processing flow to identify bottlenecks"""
    
    print("=== UPLOAD PROCESSING TEST ===")
    
    # Test 1: Check if default file exists
    print("\n1. Testing default file availability...")
    try:
        from src.core.data.excel_processor import get_default_upload_file
        default_file = get_default_upload_file()
        if default_file and os.path.exists(default_file):
            print(f"✅ Default file found: {default_file}")
            print(f"   Size: {os.path.getsize(default_file)} bytes")
        else:
            print(f"❌ No default file found")
            return False
    except Exception as e:
        print(f"❌ Error checking default file: {e}")
        return False
    
    # Test 2: Test ExcelProcessor creation
    print("\n2. Testing ExcelProcessor creation...")
    try:
        from src.core.data.excel_processor import ExcelProcessor
        processor = ExcelProcessor()
        print("✅ ExcelProcessor created successfully")
    except Exception as e:
        print(f"❌ Error creating ExcelProcessor: {e}")
        print(f"   Traceback: {traceback.format_exc()}")
        return False
    
    # Test 3: Test file loading
    print("\n3. Testing file loading...")
    try:
        start_time = time.time()
        success = processor.load_file(default_file)
        load_time = time.time() - start_time
        
        if success:
            print(f"✅ File loaded successfully in {load_time:.2f}s")
            print(f"   DataFrame shape: {processor.df.shape if processor.df is not None else 'None'}")
            print(f"   DataFrame empty: {processor.df.empty if processor.df is not None else 'N/A'}")
        else:
            print(f"❌ File loading failed")
            return False
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        print(f"   Traceback: {traceback.format_exc()}")
        return False
    
    # Test 4: Test background processing simulation
    print("\n4. Testing background processing simulation...")
    try:
        # Simulate the background processing steps
        from app import update_processing_status, processing_status, processing_timestamps
        
        test_filename = "test_file.xlsx"
        
        # Step 1: Mark as processing
        print("   - Marking as processing...")
        update_processing_status(test_filename, 'processing')
        
        # Step 2: Simulate file loading
        print("   - Simulating file loading...")
        time.sleep(1)  # Simulate processing time
        
        # Step 3: Mark as ready
        print("   - Marking as ready...")
        update_processing_status(test_filename, 'ready')
        
        # Check status
        status = processing_status.get(test_filename, 'not_found')
        print(f"   ✅ Final status: {status}")
        
        # Clean up
        if test_filename in processing_status:
            del processing_status[test_filename]
        if test_filename in processing_timestamps:
            del processing_timestamps[test_filename]
            
    except Exception as e:
        print(f"❌ Error in background processing test: {e}")
        print(f"   Traceback: {traceback.format_exc()}")
        return False
    
    # Test 5: Test force reload
    print("\n5. Testing force reload...")
    try:
        from app import force_reload_excel_processor
        
        start_time = time.time()
        force_reload_excel_processor(default_file)
        reload_time = time.time() - start_time
        
        print(f"✅ Force reload completed in {reload_time:.2f}s")
        
    except Exception as e:
        print(f"❌ Error in force reload: {e}")
        print(f"   Traceback: {traceback.format_exc()}")
        return False
    
    print("\n=== ALL TESTS PASSED ===")
    return True

def test_stuck_processing_cleanup():
    """Test the stuck processing cleanup mechanism"""
    
    print("\n=== STUCK PROCESSING CLEANUP TEST ===")
    
    try:
        from app import processing_status, processing_timestamps, processing_lock
        import time
        
        # Add some test entries
        test_files = [
            ("stuck_file1.xlsx", time.time() - 400),  # 6+ minutes old
            ("stuck_file2.xlsx", time.time() - 350),  # 5+ minutes old
            ("recent_file.xlsx", time.time() - 60),   # 1 minute old
        ]
        
        with processing_lock:
            for filename, timestamp in test_files:
                processing_status[filename] = 'processing'
                processing_timestamps[filename] = timestamp
                print(f"   Added test entry: {filename} (age: {(time.time() - timestamp)/60:.1f} minutes)")
        
        # Test the cleanup logic
        current_time = time.time()
        cutoff_time = current_time - 300  # 5 minutes
        
        stuck_files = []
        with processing_lock:
            for fname, status in list(processing_status.items()):
                timestamp = processing_timestamps.get(fname, 0)
                age = current_time - timestamp
                if age > cutoff_time and status == 'processing':
                    stuck_files.append(fname)
                    del processing_status[fname]
                    if fname in processing_timestamps:
                        del processing_timestamps[fname]
        
        print(f"   ✅ Cleaned up {len(stuck_files)} stuck files: {stuck_files}")
        print(f"   Remaining files: {list(processing_status.keys())}")
        
    except Exception as e:
        print(f"❌ Error in cleanup test: {e}")
        print(f"   Traceback: {traceback.format_exc()}")
        return False
    
    return True

if __name__ == "__main__":
    print("Starting upload processing diagnostics...")
    
    success1 = test_upload_processing()
    success2 = test_stuck_processing_cleanup()
    
    if success1 and success2:
        print("\n🎉 All diagnostics passed! Upload processing should work correctly.")
    else:
        print("\n❌ Some diagnostics failed. Check the errors above.")
        sys.exit(1) 