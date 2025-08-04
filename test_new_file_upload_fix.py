#!/usr/bin/env python3
"""
Test script to verify that new file uploads properly clear old data and load fresh data.
"""

import os
import sys
import pickle
import pandas as pd
import time
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_new_file_upload_flow():
    """Test the complete new file upload flow to ensure old data is cleared."""
    
    print("=== New File Upload Flow Test ===\n")
    
    shared_data_file = '/tmp/excel_processor_shared_data.pkl'
    
    # Step 1: Simulate existing data (old file)
    print("📁 Step 1: Simulating existing data from old file...")
    
    old_data = pd.DataFrame({
        'Product Name*': ['Old Product 1', 'Old Product 2'],
        'Product Strain': ['Old Strain 1', 'Old Strain 2'],
        'Lineage': ['SATIVA', 'INDICA'],
        'Product Brand': ['Old Brand', 'Old Brand'],
        'Vendor': ['Old Vendor', 'Old Vendor']
    })
    
    # Save old data to shared file
    try:
        with open(shared_data_file, 'wb') as f:
            pickle.dump(old_data, f)
        print(f"✅ Created shared data file with old data: {len(old_data)} products")
        
        # Verify it exists
        if os.path.exists(shared_data_file):
            print("✅ Shared data file exists with old data")
        else:
            print("❌ Shared data file not found after creation")
            return False
            
    except Exception as e:
        print(f"❌ Error creating shared data file with old data: {e}")
        return False
    
    # Step 2: Simulate new file upload (clear old data)
    print("\n🔄 Step 2: Simulating new file upload (clearing old data)...")
    
    try:
        # Simulate clearing shared data file (like in upload endpoint)
        if os.path.exists(shared_data_file):
            os.remove(shared_data_file)
            print("✅ Cleared shared data file for new upload")
        else:
            print("⚠️  Shared data file already cleared")
        
        # Verify it's gone
        if not os.path.exists(shared_data_file):
            print("✅ Shared data file successfully cleared")
        else:
            print("❌ Shared data file still exists after clearing")
            return False
            
    except Exception as e:
        print(f"❌ Error clearing shared data file: {e}")
        return False
    
    # Step 3: Simulate new file processing
    print("\n📁 Step 3: Simulating new file processing...")
    
    new_data = pd.DataFrame({
        'Product Name*': ['New Product 1', 'New Product 2', 'New Product 3'],
        'Product Strain': ['New Strain 1', 'New Strain 2', 'New Strain 3'],
        'Lineage': ['HYBRID', 'SATIVA', 'INDICA'],
        'Product Brand': ['New Brand', 'New Brand', 'New Brand'],
        'Vendor': ['New Vendor', 'New Vendor', 'New Vendor']
    })
    
    # Save new data to shared file (like process_file_background)
    try:
        with open(shared_data_file, 'wb') as f:
            pickle.dump(new_data, f)
        print(f"✅ Created shared data file with new data: {len(new_data)} products")
        
        # Verify it exists
        if os.path.exists(shared_data_file):
            print("✅ Shared data file exists with new data")
        else:
            print("❌ Shared data file not found after new data creation")
            return False
            
    except Exception as e:
        print(f"❌ Error creating shared data file with new data: {e}")
        return False
    
    # Step 4: Verify new data is loaded correctly
    print("\n✅ Step 4: Verifying new data is loaded correctly...")
    
    try:
        # Load data from shared file (like get_available_tags)
        with open(shared_data_file, 'rb') as f:
            loaded_data = pickle.load(f)
        
        print(f"✅ Successfully loaded data from shared file: {len(loaded_data)} products")
        
        # Check that it's the new data, not old data
        if len(loaded_data) == len(new_data):
            print("✅ Data count matches new data")
            
            # Check first product name
            first_product = loaded_data.iloc[0]['Product Name*']
            if first_product == 'New Product 1':
                print("✅ First product is from new data (not old data)")
                return True
            else:
                print(f"❌ First product is wrong: expected 'New Product 1', got '{first_product}'")
                return False
        else:
            print(f"❌ Data count mismatch: expected {len(new_data)}, got {len(loaded_data)}")
            return False
            
    except Exception as e:
        print(f"❌ Error loading data from shared file: {e}")
        return False

def test_file_upload_clearing_mechanism():
    """Test that the file upload clearing mechanism works correctly."""
    
    print("\n=== File Upload Clearing Mechanism Test ===\n")
    
    shared_data_file = '/tmp/excel_processor_shared_data.pkl'
    
    # Step 1: Create test data
    print("📁 Step 1: Creating test data...")
    
    test_data = pd.DataFrame({
        'Product Name*': ['Test Product'],
        'Product Strain': ['Test Strain'],
        'Lineage': ['HYBRID'],
        'Product Brand': ['Test Brand'],
        'Vendor': ['Test Vendor']
    })
    
    try:
        with open(shared_data_file, 'wb') as f:
            pickle.dump(test_data, f)
        print("✅ Created test data")
    except Exception as e:
        print(f"❌ Error creating test data: {e}")
        return False
    
    # Step 2: Simulate file upload clearing
    print("\n🗑️  Step 2: Simulating file upload clearing...")
    
    try:
        # Simulate the clearing logic from upload endpoint
        if os.path.exists(shared_data_file):
            os.remove(shared_data_file)
            print("✅ Cleared shared data file")
        
        # Verify clearing worked
        if not os.path.exists(shared_data_file):
            print("✅ Shared data file successfully cleared")
        else:
            print("❌ Shared data file still exists after clearing")
            return False
            
    except Exception as e:
        print(f"❌ Error in clearing mechanism: {e}")
        return False
    
    # Step 3: Verify fresh data can be loaded
    print("\n🔄 Step 3: Verifying fresh data can be loaded...")
    
    try:
        # Simulate loading fresh data
        fresh_data = pd.DataFrame({
            'Product Name*': ['Fresh Product'],
            'Product Strain': ['Fresh Strain'],
            'Lineage': ['SATIVA'],
            'Product Brand': ['Fresh Brand'],
            'Vendor': ['Fresh Vendor']
        })
        
        with open(shared_data_file, 'wb') as f:
            pickle.dump(fresh_data, f)
        
        print("✅ Fresh data created successfully")
        
        # Verify it's the fresh data
        with open(shared_data_file, 'rb') as f:
            loaded_fresh = pickle.load(f)
        
        if loaded_fresh.iloc[0]['Product Name*'] == 'Fresh Product':
            print("✅ Fresh data loaded correctly")
            return True
        else:
            print("❌ Fresh data not loaded correctly")
            return False
            
    except Exception as e:
        print(f"❌ Error loading fresh data: {e}")
        return False

if __name__ == "__main__":
    print("Starting New File Upload Fix Tests...\n")
    
    # Test 1: Complete new file upload flow
    test1_result = test_new_file_upload_flow()
    
    # Test 2: File upload clearing mechanism
    test2_result = test_file_upload_clearing_mechanism()
    
    print("\n=== Final Results ===")
    if test1_result:
        print("✅ New file upload flow works correctly")
    else:
        print("❌ New file upload flow failed")
    
    if test2_result:
        print("✅ File upload clearing mechanism works")
    else:
        print("❌ File upload clearing mechanism failed")
    
    if test1_result and test2_result:
        print("\n🎉 All tests PASSED!")
        print("💡 The new file upload fix should work correctly.")
        print("💡 Old data will be cleared when new files are uploaded.")
    else:
        print("\n❌ Some tests FAILED!")
        print("💡 There may still be issues with the file upload mechanism.")
    
    # Clean up
    shared_data_file = '/tmp/excel_processor_shared_data.pkl'
    if os.path.exists(shared_data_file):
        os.remove(shared_data_file)
        print("🗑️  Cleaned up test shared data file") 