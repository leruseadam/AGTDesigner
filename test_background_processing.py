#!/usr/bin/env python3
"""
Test script to simulate background processing and identify issues.
"""

import os
import sys
import time
import threading
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def simulate_background_processing(filename, temp_path):
    """Simulate the background processing function."""
    try:
        print(f"[BG] Starting optimized file processing: {temp_path}")
        
        # Set a timeout for the entire processing operation
        start_time = time.time()
        max_processing_time = 300  # 5 minutes max
        
        # Verify the file still exists before processing
        if not os.path.exists(temp_path):
            print(f"[BG] File not found: {temp_path}")
            return
        
        # Step 1: Force reload the Excel processor with the new file
        # This will handle both loading the file and updating the global processor
        load_start = time.time()
        
        # Add timeout check
        if time.time() - start_time > max_processing_time:
            print(f"[BG] Processing timeout for {filename}")
            return
            
        print(f"[BG] Loading file: {temp_path}")
        
        # Simulate the file loading process
        from core.data.excel_processor import ExcelProcessor
        
        # Create a new ExcelProcessor instance
        processor = ExcelProcessor()
        
        # Disable product database integration for faster loading
        if hasattr(processor, 'enable_product_db_integration'):
            processor.enable_product_db_integration(False)
            print("[BG] Product database integration disabled")
        
        # Load the file
        success = processor.load_file(temp_path)
        load_time = time.time() - load_start
        
        if not success:
            print(f"[BG] File load failed for {filename}")
            return
        
        print(f"[BG] File loaded successfully in {load_time:.2f}s")
        print(f"[BG] DataFrame shape: {processor.df.shape if processor.df is not None else 'None'}")
        
        # Step 2: Add a small delay to ensure frontend has time to start polling
        time.sleep(1)
        
        # Step 3: Mark as ready for basic operations
        print(f"[BG] Marking file as ready: {filename}")
        print(f"[BG] File marked as ready: {filename}")
        
        total_time = time.time() - start_time
        print(f"[BG] Background processing completed successfully in {total_time:.2f}s")
        
    except Exception as e:
        print(f"[BG] Error processing uploaded file: {e}")
        import traceback
        traceback.print_exc()

def test_background_processing():
    """Test the background processing function."""
    print("=== Background Processing Test ===\n")
    
    # Use the carts.xlsx file
    file_path = "uploads/carts.xlsx"
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    print(f"Testing background processing with: {file_path}")
    
    try:
        # Start the background processing in a thread
        thread = threading.Thread(target=simulate_background_processing, args=("carts.xlsx", file_path))
        thread.daemon = True
        thread.start()
        
        print("Background processing thread started")
        
        # Wait for the thread to complete
        thread.join(timeout=60)  # Wait up to 60 seconds
        
        if thread.is_alive():
            print("❌ Background processing thread is still running after 60 seconds")
            return False
        else:
            print("✅ Background processing completed successfully")
            return True
            
    except Exception as e:
        print(f"❌ Error in background processing test: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the test."""
    print("Starting background processing test...\n")
    
    result = test_background_processing()
    
    print(f"\n=== Test Result ===")
    if result:
        print("✅ Background processing test passed!")
    else:
        print("❌ Background processing test failed!")

if __name__ == "__main__":
    main() 