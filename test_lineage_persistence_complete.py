#!/usr/bin/env python3
"""
Comprehensive test for lineage persistence flow.
Tests: file upload → shared data creation → lineage update → shared data update → page reload persistence.
"""

import os
import sys
import pickle
import pandas as pd
import time
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_complete_lineage_persistence_flow():
    """Test the complete lineage persistence flow."""
    
    print("=== Complete Lineage Persistence Flow Test ===\n")
    
    shared_data_file = '/tmp/excel_processor_shared_data.pkl'
    
    # Step 1: Simulate file upload and shared data creation
    print("📁 Step 1: Simulating file upload and shared data creation...")
    
    # Create sample DataFrame (simulating uploaded file)
    sample_data = pd.DataFrame({
        'Product Name*': ['Test Product 1', 'Test Product 2', 'Test Product 3'],
        'Product Strain': ['Test Strain 1', 'Test Strain 2', 'Test Strain 3'],
        'Lineage': ['SATIVA', 'INDICA', 'HYBRID'],
        'Product Brand': ['Test Brand', 'Test Brand', 'Test Brand'],
        'Vendor': ['Test Vendor', 'Test Vendor', 'Test Vendor']
    })
    
    # Save to shared data file (simulating process_file_background)
    try:
        with open(shared_data_file, 'wb') as f:
            pickle.dump(sample_data, f)
        print(f"✅ Created shared data file with {len(sample_data)} products")
        
        # Verify it exists
        if os.path.exists(shared_data_file):
            print("✅ Shared data file exists after creation")
        else:
            print("❌ Shared data file not found after creation")
            return False
            
    except Exception as e:
        print(f"❌ Error creating shared data file: {e}")
        return False
    
    # Step 2: Simulate lineage update
    print("\n🔄 Step 2: Simulating lineage update...")
    
    # Load current data
    try:
        with open(shared_data_file, 'rb') as f:
            current_data = pickle.load(f)
        
        print(f"✅ Loaded current data with shape: {current_data.shape}")
        
        # Simulate lineage update (like the update_lineage endpoint)
        old_lineage = current_data.loc[0, 'Lineage']
        new_lineage = 'MIXED'
        current_data.loc[0, 'Lineage'] = new_lineage
        
        print(f"  • Updated '{current_data.loc[0, 'Product Name*']}' lineage: {old_lineage} → {new_lineage}")
        
        # Save updated data (like save_shared_data in update_lineage)
        with open(shared_data_file, 'wb') as f:
            pickle.dump(current_data, f)
        
        print("✅ Saved updated data to shared file")
        
        # Verify the update
        with open(shared_data_file, 'rb') as f:
            updated_data = pickle.load(f)
        
        if len(updated_data) > 0:
            current_lineage = updated_data.loc[0, 'Lineage']
            print(f"✅ Verified lineage update: {current_lineage}")
            
            if current_lineage != new_lineage:
                print(f"❌ Lineage update failed - expected {new_lineage}, got {current_lineage}")
                return False
        else:
            print("❌ No data to verify")
            return False
            
    except Exception as e:
        print(f"❌ Error in lineage update simulation: {e}")
        return False
    
    # Step 3: Simulate page reload (load from shared data)
    print("\n🔄 Step 3: Simulating page reload (loading from shared data)...")
    
    try:
        # Simulate loading from shared data (like checkForExistingData in frontend)
        if os.path.exists(shared_data_file):
            with open(shared_data_file, 'rb') as f:
                reloaded_data = pickle.load(f)
            
            print(f"✅ Successfully loaded data on 'reload' with shape: {reloaded_data.shape}")
            
            # Check if lineage changes persisted
            if len(reloaded_data) > 0:
                reloaded_lineage = reloaded_data.loc[0, 'Lineage']
                print(f"✅ Lineage on reload: {reloaded_lineage}")
                
                if reloaded_lineage == new_lineage:
                    print("✅ Lineage changes persisted through 'page reload'!")
                    return True
                else:
                    print(f"❌ Lineage changes did not persist - expected {new_lineage}, got {reloaded_lineage}")
                    return False
            else:
                print("❌ No data loaded on 'reload'")
                return False
        else:
            print("❌ Shared data file not found on 'reload'")
            return False
            
    except Exception as e:
        print(f"❌ Error in page reload simulation: {e}")
        return False

def test_shared_data_file_lifecycle():
    """Test the complete lifecycle of the shared data file."""
    
    print("\n=== Shared Data File Lifecycle Test ===\n")
    
    shared_data_file = '/tmp/excel_processor_shared_data.pkl'
    
    # Step 1: Check initial state
    print("🔍 Step 1: Checking initial state...")
    if os.path.exists(shared_data_file):
        print(f"⚠️  Shared data file already exists at: {shared_data_file}")
        # Remove it to start fresh
        os.remove(shared_data_file)
        print("🗑️  Removed existing shared data file to start fresh")
    else:
        print("✅ No existing shared data file found")
    
    # Step 2: Simulate app startup (clear_processing_status)
    print("\n🚀 Step 2: Simulating app startup (clear_processing_status)...")
    try:
        # This would normally clear the shared data file
        if os.path.exists(shared_data_file):
            os.remove(shared_data_file)
            print("🗑️  Cleared shared data file on startup")
        else:
            print("✅ No shared data file to clear on startup")
    except Exception as e:
        print(f"❌ Error clearing shared data file on startup: {e}")
    
    # Step 3: Simulate file upload
    print("\n📁 Step 3: Simulating file upload...")
    sample_data = pd.DataFrame({
        'Product Name*': ['Test Product'],
        'Product Strain': ['Test Strain'],
        'Lineage': ['ORIGINAL'],
        'Product Brand': ['Test Brand'],
        'Vendor': ['Test Vendor']
    })
    
    try:
        with open(shared_data_file, 'wb') as f:
            pickle.dump(sample_data, f)
        print("✅ Created shared data file after file upload")
    except Exception as e:
        print(f"❌ Error creating shared data file after upload: {e}")
        return False
    
    # Step 4: Simulate lineage update
    print("\n🔄 Step 4: Simulating lineage update...")
    try:
        with open(shared_data_file, 'rb') as f:
            data = pickle.load(f)
        
        data.loc[0, 'Lineage'] = 'UPDATED'
        
        with open(shared_data_file, 'wb') as f:
            pickle.dump(data, f)
        
        print("✅ Updated shared data file with lineage change")
    except Exception as e:
        print(f"❌ Error updating shared data file: {e}")
        return False
    
    # Step 5: Verify persistence
    print("\n✅ Step 5: Verifying persistence...")
    try:
        with open(shared_data_file, 'rb') as f:
            final_data = pickle.load(f)
        
        final_lineage = final_data.loc[0, 'Lineage']
        print(f"✅ Final lineage: {final_lineage}")
        
        if final_lineage == 'UPDATED':
            print("✅ Lineage persistence test PASSED!")
            return True
        else:
            print(f"❌ Lineage persistence test FAILED - expected 'UPDATED', got '{final_lineage}'")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying persistence: {e}")
        return False

if __name__ == "__main__":
    print("Starting Complete Lineage Persistence Tests...\n")
    
    # Test 1: Complete flow test
    test1_result = test_complete_lineage_persistence_flow()
    
    # Test 2: Lifecycle test
    test2_result = test_shared_data_file_lifecycle()
    
    print("\n=== Final Results ===")
    if test1_result:
        print("✅ Complete lineage persistence flow works")
    else:
        print("❌ Complete lineage persistence flow failed")
    
    if test2_result:
        print("✅ Shared data file lifecycle works")
    else:
        print("❌ Shared data file lifecycle failed")
    
    if test1_result and test2_result:
        print("\n🎉 All tests PASSED!")
        print("💡 The shared data file mechanism works correctly.")
        print("💡 The issue might be in the timing or error handling in the actual app.")
    else:
        print("\n❌ Some tests FAILED!")
        print("💡 There are issues with the shared data file mechanism.")
    
    # Clean up
    shared_data_file = '/tmp/excel_processor_shared_data.pkl'
    if os.path.exists(shared_data_file):
        os.remove(shared_data_file)
        print("🗑️  Cleaned up test shared data file") 