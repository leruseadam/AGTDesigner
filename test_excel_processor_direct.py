#!/usr/bin/env python3
"""
Test script to directly test ExcelProcessor with the problematic file
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.data.excel_processor import ExcelProcessor

def test_excel_processor_direct():
    """Test ExcelProcessor directly with the problematic file"""
    
    print("Testing ExcelProcessor Directly")
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
    
    # Test 1: Create ExcelProcessor and load file
    try:
        print(f"🔄 Creating ExcelProcessor and loading file...")
        
        processor = ExcelProcessor()
        
        # Disable product database integration for faster loading
        if hasattr(processor, 'enable_product_db_integration'):
            processor.enable_product_db_integration(False)
            print("✅ Product database integration disabled")
        
        # Load the file
        success = processor.load_file(test_file)
        
        if success:
            print("✅ File loaded successfully")
            print(f"📊 DataFrame shape: {processor.df.shape if processor.df is not None else 'None'}")
            print(f"📊 DataFrame empty: {processor.df.empty if processor.df is not None else 'N/A'}")
            print(f"📊 Last loaded file: {getattr(processor, '_last_loaded_file', 'None')}")
            
            if processor.df is not None and not processor.df.empty:
                print(f"📊 Sample columns: {list(processor.df.columns)[:10]}")
                print(f"📊 Sample rows: {len(processor.df)}")
                
                # Test getting available tags
                try:
                    available_tags = processor.get_available_tags()
                    print(f"✅ Available tags: {len(available_tags)}")
                    
                    if available_tags:
                        sample_tag = available_tags[0]
                        print(f"📊 Sample tag: {sample_tag.get('Product Name*', 'No name')}")
                        print(f"📊 Sample lineage: {sample_tag.get('Lineage', 'No lineage')}")
                        
                        return True
                    else:
                        print("❌ No available tags found")
                        return False
                except Exception as e:
                    print(f"❌ Error getting available tags: {e}")
                    return False
            else:
                print("❌ DataFrame is empty or None")
                return False
        else:
            print("❌ File load failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing ExcelProcessor: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_excel_processor_direct()
    
    if success:
        print("\n🎉 ExcelProcessor test passed!")
        print("✅ The ExcelProcessor can load files correctly")
    else:
        print("\n❌ ExcelProcessor test failed")
        print("⚠️  There may be an issue with the ExcelProcessor")
    
    print("=" * 60) 