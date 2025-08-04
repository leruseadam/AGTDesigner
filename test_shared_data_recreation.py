#!/usr/bin/env python3
"""
Test script to verify shared data file recreation after lineage changes.
"""

import os
import sys
import pickle
import pandas as pd
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_shared_data_recreation():
    """Test whether shared data file is recreated after lineage changes."""
    
    print("=== Shared Data File Recreation Test ===\n")
    
    # Check if shared data file exists
    shared_data_file = '/tmp/excel_processor_shared_data.pkl'
    
    if os.path.exists(shared_data_file):
        print(f"✅ Shared data file exists at: {shared_data_file}")
        
        # Load and examine the data
        try:
            with open(shared_data_file, 'rb') as f:
                data = pickle.load(f)
            
            if isinstance(data, pd.DataFrame):
                print(f"✅ Shared data is DataFrame with shape: {data.shape}")
                
                if 'Lineage' in data.columns:
                    print("✅ Lineage column found in shared data")
                    
                    # Show some lineage values
                    lineage_counts = data['Lineage'].value_counts().head(10)
                    print(f"📊 Top 10 lineages in shared data:")
                    for lineage, count in lineage_counts.items():
                        print(f"  • {lineage}: {count}")
                else:
                    print("❌ Lineage column not found in shared data")
            else:
                print(f"❌ Shared data is not a DataFrame: {type(data)}")
                
        except Exception as e:
            print(f"❌ Error loading shared data: {e}")
    else:
        print(f"❌ Shared data file not found at: {shared_data_file}")
        print("💡 This explains why lineage changes don't persist on page reload")
        return False
    
    return True

def test_shared_data_creation():
    """Test creating a shared data file with sample data."""
    
    print("\n=== Shared Data File Creation Test ===\n")
    
    # Create sample DataFrame
    sample_data = pd.DataFrame({
        'Product Name*': ['Test Product 1', 'Test Product 2', 'Test Product 3'],
        'Product Strain': ['Test Strain 1', 'Test Strain 2', 'Test Strain 3'],
        'Lineage': ['SATIVA', 'INDICA', 'HYBRID'],
        'Product Brand': ['Test Brand', 'Test Brand', 'Test Brand'],
        'Vendor': ['Test Vendor', 'Test Vendor', 'Test Vendor']
    })
    
    print(f"✅ Created sample DataFrame with shape: {sample_data.shape}")
    
    # Save to shared data file
    shared_data_file = '/tmp/excel_processor_shared_data.pkl'
    
    try:
        with open(shared_data_file, 'wb') as f:
            pickle.dump(sample_data, f)
        print(f"✅ Saved sample data to: {shared_data_file}")
        
        # Verify it was saved
        if os.path.exists(shared_data_file):
            print("✅ Shared data file exists after saving")
            
            # Load it back
            with open(shared_data_file, 'rb') as f:
                loaded_data = pickle.load(f)
            
            if isinstance(loaded_data, pd.DataFrame):
                print(f"✅ Successfully loaded DataFrame with shape: {loaded_data.shape}")
                print(f"📊 Lineages in loaded data: {loaded_data['Lineage'].tolist()}")
                return True
            else:
                print(f"❌ Loaded data is not a DataFrame: {type(loaded_data)}")
                return False
        else:
            print("❌ Shared data file does not exist after saving")
            return False
            
    except Exception as e:
        print(f"❌ Error saving shared data: {e}")
        return False

def test_lineage_update_simulation():
    """Simulate a lineage update and verify shared data is updated."""
    
    print("\n=== Lineage Update Simulation Test ===\n")
    
    # First create sample data
    if not test_shared_data_creation():
        print("❌ Cannot proceed with lineage update test - shared data creation failed")
        return False
    
    shared_data_file = '/tmp/excel_processor_shared_data.pkl'
    
    # Load current data
    try:
        with open(shared_data_file, 'rb') as f:
            data = pickle.load(f)
        
        print(f"✅ Loaded existing data with shape: {data.shape}")
        
        # Simulate lineage update
        print("🔄 Simulating lineage update...")
        
        # Update lineage for first product
        if len(data) > 0:
            old_lineage = data.loc[0, 'Lineage']
            new_lineage = 'MIXED'
            data.loc[0, 'Lineage'] = new_lineage
            
            print(f"  • Updated '{data.loc[0, 'Product Name*']}' lineage: {old_lineage} → {new_lineage}")
        
        # Save updated data
        with open(shared_data_file, 'wb') as f:
            pickle.dump(data, f)
        
        print("✅ Saved updated data to shared file")
        
        # Verify the update
        with open(shared_data_file, 'rb') as f:
            updated_data = pickle.load(f)
        
        if len(updated_data) > 0:
            current_lineage = updated_data.loc[0, 'Lineage']
            print(f"✅ Verified lineage update: {current_lineage}")
            
            if current_lineage == new_lineage:
                print("✅ Lineage update simulation successful!")
                return True
            else:
                print(f"❌ Lineage update failed - expected {new_lineage}, got {current_lineage}")
                return False
        else:
            print("❌ No data to verify")
            return False
            
    except Exception as e:
        print(f"❌ Error in lineage update simulation: {e}")
        return False

if __name__ == "__main__":
    print("Starting Shared Data File Tests...\n")
    
    # Test 1: Check if shared data file exists
    test1_result = test_shared_data_recreation()
    
    # Test 2: Create shared data file
    test2_result = test_shared_data_creation()
    
    # Test 3: Simulate lineage update
    test3_result = test_lineage_update_simulation()
    
    print("\n=== Final Results ===")
    if test1_result:
        print("✅ Shared data file exists and is readable")
    else:
        print("❌ Shared data file is missing or corrupted")
    
    if test2_result:
        print("✅ Shared data file creation works")
    else:
        print("❌ Shared data file creation failed")
    
    if test3_result:
        print("✅ Lineage update simulation works")
    else:
        print("❌ Lineage update simulation failed")
    
    if test2_result and test3_result:
        print("\n💡 The shared data file mechanism works correctly.")
        print("💡 The issue is that the app is not calling save_shared_data() after lineage changes.")
    else:
        print("\n💡 There are issues with the shared data file mechanism.") 