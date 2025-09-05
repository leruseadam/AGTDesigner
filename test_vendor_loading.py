#!/usr/bin/env python3
"""
Test script to check vendor loading
"""

import os
import sys

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_vendor_loading():
    """Test vendor loading from Excel files"""
    
    try:
        from src.core.data.excel_processor import ExcelProcessor
        
        print("✅ ExcelProcessor imported successfully")
        
        # Check what files are available
        uploads_dir = "uploads"
        if os.path.exists(uploads_dir):
            excel_files = [f for f in os.listdir(uploads_dir) if f.endswith('.xlsx')]
            print(f"\n📁 Found {len(excel_files)} Excel files in uploads directory:")
            for file in excel_files:
                print(f"  - {file}")
        
        # Try to load the main inventory file
        main_file = "uploads/A Greener Today - Bothell_inventory_08-20-2025 12_22 PM.xlsx"
        if os.path.exists(main_file):
            print(f"\n🔍 Testing main file: {main_file}")
            
            processor = ExcelProcessor()
            success = processor.load_file(main_file)
            
            if success:
                print("✅ File loaded successfully")
                print(f"📊 DataFrame shape: {processor.df.shape}")
                print(f"📋 Columns: {list(processor.df.columns)}")
                
                # Check vendor data
                if 'Vendor/Supplier*' in processor.df.columns:
                    vendors = processor.df['Vendor/Supplier*'].dropna().unique()
                    print(f"\n🏪 Vendor data found:")
                    print(f"  - Column: Vendor/Supplier*")
                    print(f"  - Unique vendors: {list(vendors)}")
                    print(f"  - Count: {len(vendors)}")
                else:
                    print("\n❌ Vendor/Supplier* column not found!")
                    vendor_cols = [col for col in processor.df.columns if 'vendor' in col.lower() or 'supplier' in col.lower()]
                    if vendor_cols:
                        print(f"  - Found vendor-related columns: {vendor_cols}")
                    else:
                        print("  - No vendor-related columns found")
                
                # Test get_available_tags
                print(f"\n🔍 Testing get_available_tags...")
                tags = processor.get_available_tags()
                print(f"  - Retrieved {len(tags)} tags")
                
                if tags:
                    first_tag = tags[0]
                    print(f"  - First tag structure: {list(first_tag.keys())}")
                    print(f"  - First tag vendor: {first_tag.get('Vendor', 'NOT FOUND')}")
                    print(f"  - First tag Vendor/Supplier*: {first_tag.get('Vendor/Supplier*', 'NOT FOUND')}")
                    
                    # Check vendor values in tags
                    vendor_values = set()
                    for tag in tags:
                        vendor = tag.get('Vendor') or tag.get('Vendor/Supplier*') or tag.get('vendor')
                        if vendor:
                            vendor_values.add(vendor)
                    
                    print(f"  - Unique vendor values in tags: {list(vendor_values)}")
                else:
                    print("  - No tags returned!")
                    
            else:
                print("❌ Failed to load file")
        else:
            print(f"❌ Main file not found: {main_file}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_vendor_loading()
