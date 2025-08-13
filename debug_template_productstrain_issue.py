#!/usr/bin/env python3
"""
Debug script to test template processing and see exactly where ProductStrain is getting copied to ProductBrand
"""

import os
import sys
import pandas as pd

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_template_processing():
    """Test the template processing to see where ProductStrain gets copied to ProductBrand"""
    
    print("🔍 Testing template processing for ProductStrain issue...")
    
    # Load the actual data file
    file_path = 'uploads/A Greener Today - Bothell_inventory_08-09-2025  9_47 PM.xlsx'
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return
    
    print(f"📁 Loading: {file_path}")
    
    try:
        from src.core.data.excel_processor import ExcelProcessor
        
        # Create processor and load file
        processor = ExcelProcessor()
        processor.load_file(file_path)
        
        print(f"✅ File loaded successfully")
        print(f"📊 Total records: {len(processor.df)}")
        
        # Check paraphernalia products BEFORE processing
        paraphernalia_before = processor.df[processor.df['Product Type*'].str.lower().str.contains('paraphernalia', na=False)]
        print(f"🔍 Found {len(paraphernalia_before)} paraphernalia products before processing")
        
        if len(paraphernalia_before) > 0:
            print("\n📋 Sample paraphernalia products before processing:")
            for idx, row in paraphernalia_before.head(3).iterrows():
                print(f"Product: {row.get('ProductName', 'NO NAME')}")
                print(f"  Brand: {row.get('Product Brand', 'NO BRAND')}")
                print(f"  Strain: {row.get('Product Strain', 'NO STRAIN')}")
                print(f"  Type: {row.get('Product Type*', 'NO TYPE')}")
                print("---")
            
            # Check if ProductStrain equals ProductBrand for paraphernalia
            matching = paraphernalia_before[
                (paraphernalia_before['Product Brand'].fillna('') == paraphernalia_before['Product Strain'].fillna('')) & 
                (paraphernalia_before['Product Brand'].fillna('') != '')
            ]
            print(f"\n🔍 Products where ProductStrain equals ProductBrand: {len(matching)}")
            
            if len(matching) > 0:
                print("\n📋 Examples:")
                for idx, row in matching.head(3).iterrows():
                    print(f"Product: {row.get('ProductName', 'NO NAME')}")
                    print(f"  Brand/Strain: {row.get('Product Brand', 'NO BRAND')}")
                    print("---")
        
        # Now get the processed records
        print("\n🔄 Getting processed records...")
        records = processor.get_selected_records()
        print(f"📊 Processed records: {len(records)}")
        
        # Check if any paraphernalia products remain in processed records
        paraphernalia_after = [r for r in records if r.get('Product Type*', '').lower().find('paraphernalia') != -1]
        print(f"🔍 Paraphernalia products in processed records: {len(paraphernalia_after)}")
        
        if len(paraphernalia_after) > 0:
            print("\n📋 Sample paraphernalia products after processing:")
            for record in paraphernalia_after[:3]:
                print(f"Product: {record.get('ProductName', 'NO NAME')}")
                print(f"  Brand: {record.get('ProductBrand', 'NO BRAND')}")
                print(f"  Strain: {record.get('ProductStrain', 'NO STRAIN')}")
                print(f"  Type: {record.get('Product Type*', 'NO TYPE')}")
                print("---")
                
                # Check if ProductStrain equals ProductBrand
                if record.get('ProductStrain') == record.get('ProductBrand'):
                    print(f"  ⚠️  WARNING: ProductStrain equals ProductBrand!")
        
        # Test template processing with a few records
        if len(records) > 0:
            print(f"\n🧪 Testing template processing with {min(3, len(records))} records...")
            
            try:
                from src.core.generation.template_processor import TemplateProcessor
                
                # Create template processor
                template_processor = TemplateProcessor()
                
                # Test with first few records
                test_records = records[:3]
                for i, record in enumerate(test_records):
                    print(f"\n📝 Record {i+1}:")
                    print(f"  Product: {record.get('ProductName', 'NO NAME')}")
                    print(f"  Brand: {record.get('ProductBrand', 'NO BRAND')}")
                    print(f"  Strain: {record.get('ProductStrain', 'NO STRAIN')}")
                    
                    # Build context for this record
                    context = template_processor._build_label_context(record)
                    
                    print(f"  Context Brand: {context.get('ProductBrand', 'NO BRAND')}")
                    print(f"  Context Strain: {context.get('ProductStrain', 'NO STRAIN')}")
                    
                    # Check if there's any copying happening
                    if context.get('ProductBrand') == context.get('ProductStrain'):
                        print(f"  ⚠️  WARNING: Context ProductBrand equals ProductStrain!")
                    
            except Exception as e:
                print(f"❌ Error during template processing: {e}")
                import traceback
                traceback.print_exc()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_template_processing() 