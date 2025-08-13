#!/usr/bin/env python3
"""
Debug script to test the ProductStrain fix and see exactly where the copying is happening
"""

import os
import sys
import pandas as pd

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_productstrain_processing():
    """Test the ProductStrain processing to see where the copying happens"""
    
    print("🔍 Testing ProductStrain processing...")
    
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
        success = processor.load_file(file_path)
        
        if not success:
            print("❌ Failed to load file")
            return
        
        print(f"✅ File loaded successfully")
        print(f"📊 Total records: {len(processor.df)}")
        
        # Check paraphernalia products before processing
        paraphernalia_before = processor.df[
            processor.df['Product Type*'].str.lower().str.contains('paraphernalia', na=False)
        ]
        print(f"🔍 Found {len(paraphernalia_before)} paraphernalia products before processing")
        
        if len(paraphernalia_before) > 0:
            print("\n📋 Sample paraphernalia products BEFORE processing:")
            for idx, row in paraphernalia_before.head(3).iterrows():
                print(f"  Product: {row.get('Product Name*', 'NO NAME')}")
                print(f"    Brand: '{row.get('Product Brand', 'NO BRAND')}'")
                print(f"    Strain: '{row.get('Product Strain', 'NO STRAIN')}'")
                print(f"    Type: '{row.get('Product Type*', 'NO TYPE')}'")
                print("    ---")
        
        # Now get selected records (this triggers the processing)
        print("\n🔄 Processing records...")
        
        # First, select some tags so we have records to process
        # Get available tags and select the first few paraphernalia products
        available_tags = processor.get_available_tags()
        paraphernalia_tags = [
            tag['displayName'] for tag in available_tags 
            if tag.get('productType', '').lower() == 'paraphernalia'
        ]
        
        if paraphernalia_tags:
            # Select the first few paraphernalia tags
            tags_to_select = paraphernalia_tags[:5]  # Select first 5
            processor.select_tags(tags_to_select)
            print(f"📝 Selected {len(tags_to_select)} paraphernalia tags: {tags_to_select}")
        else:
            # If no paraphernalia tags found, just select the first few available tags
            available_tag_names = [tag['displayName'] for tag in available_tags[:5]]
            processor.select_tags(available_tag_names)
            print(f"📝 No paraphernalia tags found, selected first {len(available_tag_names)} available tags: {available_tag_names}")
        
        selected_records = processor.get_selected_records()
        print(f"✅ Processed {len(selected_records)} records")
        
        # Check paraphernalia products after processing
        paraphernalia_after = [
            record for record in selected_records 
            if record.get('ProductType', '').lower() == 'paraphernalia'
        ]
        print(f"🔍 Found {len(paraphernalia_after)} paraphernalia products after processing")
        
        if len(paraphernalia_after) > 0:
            print("\n📋 Sample paraphernalia products AFTER processing:")
            for record in paraphernalia_after[:3]:
                print(f"  Product: {record.get('ProductName', 'NO NAME')}")
                print(f"    Brand: '{record.get('ProductBrand', 'NO BRAND')}'")
                print(f"    Strain: '{record.get('ProductStrain', 'NO STRAIN')}'")
                print(f"    Type: '{record.get('ProductType', 'NO TYPE')}'")
                print("    ---")
        
        # Check for the specific issue: ProductStrain equals ProductBrand
        matching_records = [
            record for record in selected_records
            if (record.get('ProductStrain', '') == record.get('ProductBrand', '') and 
                record.get('ProductStrain', '') != '')
        ]
        
        print(f"\n🔍 Records where ProductStrain equals ProductBrand: {len(matching_records)}")
        
        if len(matching_records) > 0:
            print("\n⚠️  PROBLEM RECORDS:")
            for record in matching_records[:5]:
                print(f"  Product: {record.get('ProductName', 'NO NAME')}")
                print(f"    Brand/Strain: '{record.get('ProductBrand', 'NO BRAND')}'")
                print(f"    Type: '{record.get('ProductType', 'NO TYPE')}'")
                print("    ---")
            
            # Check if they're all paraphernalia
            paraphernalia_matches = [
                record for record in matching_records
                if record.get('ProductType', '').lower() == 'paraphernalia'
            ]
            print(f"  📊 {len(paraphernalia_matches)} of {len(matching_records)} are paraphernalia products")
        else:
            print("✅ No records found where ProductStrain equals ProductBrand")
        
        # Now test template processing to see if the issue happens there
        print("\n🔄 Testing template processing...")
        
        try:
            from src.core.generation.template_processor import TemplateProcessor
            
            # Create template processor
            template_processor = TemplateProcessor('vertical', 'default', 1.0)
            
            # Process a few records through the template
            test_records = selected_records[:3]
            print(f"📝 Processing {len(test_records)} records through template...")
            
            for i, record in enumerate(test_records):
                print(f"\n  Record {i+1}: {record.get('ProductName', 'NO NAME')}")
                print(f"    Before template - Brand: '{record.get('ProductBrand', 'NO BRAND')}'")
                print(f"    Before template - Strain: '{record.get('ProductStrain', 'NO STRAIN')}'")
                
                # Build context
                context = template_processor._build_label_context(record, None)
                print(f"    After context - Brand: '{context.get('ProductBrand', 'NO BRAND')}'")
                print(f"    After context - Strain: '{context.get('ProductStrain', 'NO STRAIN')}'")
                
                # Check if any copying happened
                if context.get('ProductStrain', '') == context.get('ProductBrand', '') and context.get('ProductStrain', '') != '':
                    print(f"    ⚠️  WARNING: ProductStrain equals ProductBrand in context!")
                else:
                    print(f"    ✅ ProductStrain and ProductBrand are different in context")
        
        except Exception as e:
            print(f"❌ Template processing test failed: {e}")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_productstrain_processing() 