#!/usr/bin/env python3
"""
Test script to check where duplicate indices are created during DataFrame operations
"""

import pandas as pd
import os

def test_dataframe_operations():
    """Test DataFrame operations to find where duplicate indices are created"""
    
    print("Testing DataFrame Operations for Duplicate Indices")
    print("=" * 60)
    
    # Find the test file
    uploads_dir = "uploads"
    if not os.path.exists(uploads_dir):
        print(f"❌ Uploads directory not found: {uploads_dir}")
        return False
    
    # Find the most recent Excel file
    excel_files = []
    for file in os.listdir(uploads_dir):
        if file.endswith('.xlsx') and 'A Greener Today' in file:
            file_path = os.path.join(uploads_dir, file)
            mtime = os.path.getmtime(file_path)
            excel_files.append((file_path, mtime))
    
    if not excel_files:
        print("❌ No Excel files found in uploads directory")
        return False
    
    # Sort by modification time (most recent first)
    excel_files.sort(key=lambda x: x[1], reverse=True)
    test_file = excel_files[0][0]
    print(f"✅ Found test file: {test_file}")
    
    try:
        print(f"🔄 Reading file with pandas...")
        
        # Read the file
        df = pd.read_excel(test_file, engine='openpyxl')
        
        print(f"✅ File read successfully")
        print(f"📊 Initial DataFrame shape: {df.shape}")
        print(f"📊 Initial has duplicate indices: {df.index.duplicated().any()}")
        
        # Test 1: Check after drop_duplicates
        print(f"\n🔄 Testing drop_duplicates...")
        df_test = df.copy()
        df_test.drop_duplicates(inplace=True)
        df_test.reset_index(drop=True, inplace=True)
        print(f"📊 After drop_duplicates: has duplicate indices: {df_test.index.duplicated().any()}")
        
        # Test 2: Check after column operations
        print(f"\n🔄 Testing column operations...")
        df_test = df.copy()
        df_test.drop_duplicates(inplace=True)
        df_test.reset_index(drop=True, inplace=True)
        
        # Simulate the column operations from ExcelProcessor
        if "ProductName" in df_test.columns:
            df_test["Product Name*"] = df_test["ProductName"].str.lstrip()
        print(f"📊 After column operations: has duplicate indices: {df_test.index.duplicated().any()}")
        
        # Test 3: Check after filtering
        print(f"\n🔄 Testing filtering operations...")
        df_test = df.copy()
        df_test.drop_duplicates(inplace=True)
        df_test.reset_index(drop=True, inplace=True)
        
        # Simulate filtering operations
        if "Product Type*" in df_test.columns:
            df_test = df_test[~df_test["Product Type*"].isin(["sample", "test"])]
            df_test.reset_index(drop=True, inplace=True)
        print(f"📊 After filtering: has duplicate indices: {df_test.index.duplicated().any()}")
        
        # Test 4: Check after apply operation
        print(f"\n🔄 Testing apply operation...")
        df_test = df.copy()
        df_test.drop_duplicates(inplace=True)
        df_test.reset_index(drop=True, inplace=True)
        
        # Simulate the apply operation that's failing
        if "ProductName" in df_test.columns:
            def get_description(name):
                if pd.isna(name) or name == "":
                    return ""
                name = str(name).strip()
                if " - " in name:
                    return name.rsplit(' - ', 1)[0].strip()
                return name.strip()
            
            # This is the operation that's failing
            df_test["Description"] = df_test["ProductName"].apply(get_description)
            print(f"📊 After apply operation: has duplicate indices: {df_test.index.duplicated().any()}")
            
            if df_test.index.duplicated().any():
                print(f"❌ Duplicate indices found after apply operation!")
                print(f"📊 Duplicate indices: {df_test.index[df_test.index.duplicated()].tolist()}")
                return False
            else:
                print(f"✅ No duplicate indices after apply operation")
        
        return True
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_dataframe_operations()
    
    if success:
        print("\n🎉 DataFrame operations test passed!")
        print("✅ No duplicate indices created during operations")
    else:
        print("\n❌ DataFrame operations test failed")
        print("⚠️  Duplicate indices were created during operations")
    
    print("=" * 60) 