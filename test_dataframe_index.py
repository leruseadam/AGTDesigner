#!/usr/bin/env python3
"""
Test script to check DataFrame index issues
"""

import pandas as pd
import os

def test_dataframe_index():
    """Test DataFrame index right after creation"""
    
    print("Testing DataFrame Index Issues")
    print("=" * 50)
    
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
    
    # Test 1: Read the file directly with pandas
    try:
        print(f"🔄 Reading file with pandas...")
        
        # Read the file
        df = pd.read_excel(test_file, engine='openpyxl')
        
        print(f"✅ File read successfully")
        print(f"📊 DataFrame shape: {df.shape}")
        print(f"📊 DataFrame index type: {type(df.index)}")
        print(f"📊 DataFrame index length: {len(df.index)}")
        print(f"📊 DataFrame index unique length: {len(df.index.unique())}")
        print(f"📊 Has duplicate indices: {df.index.duplicated().any()}")
        
        if df.index.duplicated().any():
            print(f"❌ DataFrame has duplicate indices!")
            print(f"📊 Duplicate indices: {df.index[df.index.duplicated()].tolist()}")
            return False
        else:
            print(f"✅ DataFrame has no duplicate indices")
            return True
            
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_dataframe_index()
    
    if success:
        print("\n🎉 DataFrame index test passed!")
        print("✅ The DataFrame has no duplicate indices")
    else:
        print("\n❌ DataFrame index test failed")
        print("⚠️  The DataFrame has duplicate indices")
    
    print("=" * 60) 