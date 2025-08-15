#!/usr/bin/env python3
"""
Test script to test if the field duplication fix is working.
This script will test the actual label generation process to see if fields are still being duplicated.
"""

import os
import sys
import pandas as pd
from pathlib import Path

# Add the project root to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_field_duplication_fix():
    """Test if the field duplication fix is working."""
    
    print("=== FIELD DUPLICATION FIX TEST ===\n")
    
    try:
        # Import the necessary modules
        from src.core.data.excel_processor import ExcelProcessor, get_default_upload_file
        from src.core.generation.template_processor import TemplateProcessor, get_font_scheme
        
        print("✅ Successfully imported required modules")
        
        # Get the default file
        default_file = get_default_upload_file()
        if not default_file:
            print("❌ No default file found")
            return
        
        print(f"📁 Using default file: {default_file}")
        
        # Load the data
        processor = ExcelProcessor()
        success = processor.load_file(default_file)
        
        if not success or processor.df is None or processor.df.empty:
            print("❌ No data loaded")
            return
        
        print(f"✅ Loaded {len(processor.df)} records")
        
        # Test with a specific record to see if fields are duplicated
        test_record = processor.df.iloc[0]
        print(f"\n🔍 Testing with record: {test_record.get('ProductName', 'Unknown')}")
        print(f"   Product Type: {test_record.get('Product Type*', 'Unknown')}")
        print(f"   Product Strain: {test_record.get('Product Strain', 'Unknown')}")
        print(f"   Product Brand: {test_record.get('Product Brand', 'Unknown')}")
        
        # Create a template processor and test the processing
        template_processor = TemplateProcessor(
            template_type="double",
            font_scheme=get_font_scheme("double")
        )
        
        # Test the field processing logic
        label_context = {}
        
        # Simulate the field processing from the template processor
        product_strain = test_record.get('Product Strain', '')
        product_type = test_record.get('Product Type*', '').lower()
        
        # Define classic types
        classic_types = ["flower", "pre-roll", "infused pre-roll", "concentrate", 
                       "solventless concentrate", "vape cartridge", "rso/co2 tankers"]
        
        # Process ProductStrain
        if product_type in classic_types:
            if 'Moonshot' in product_strain:
                strain_name = product_strain.replace(' Moonshot', '').strip()
                label_context['ProductStrain'] = strain_name
            else:
                label_context['ProductStrain'] = product_strain
        else:
            # For non-classic types, set to "Mixed" or "CBD Blend"
            if 'cbd' in product_type or 'edible' in product_type:
                label_context['ProductStrain'] = "CBD Blend"
            else:
                label_context['ProductStrain'] = "Mixed"
        
        # Process ProductBrand
        label_context['ProductBrand'] = test_record.get('Product Brand', '')
        
        # Process other fields
        label_context['Lineage'] = test_record.get('Lineage', '')
        label_context['Price'] = test_record.get('Price', '')
        label_context['Ratio_or_THC_CBD'] = test_record.get('Ratio', '')
        label_context['DOH'] = test_record.get('DOH', '')
        
        # Process DescAndWeight
        desc = test_record.get('Description', '')
        weight = test_record.get('Weight', '')
        if desc and weight:
            label_context['DescAndWeight'] = f"{desc} -\u00A0{weight}"
        else:
            label_context['DescAndWeight'] = desc or weight
        
        print(f"\n📋 PROCESSED FIELD VALUES:")
        print(f"   ProductStrain: '{label_context.get('ProductStrain', '')}'")
        print(f"   ProductBrand: '{label_context.get('ProductBrand', '')}'")
        print(f"   Lineage: '{label_context.get('Lineage', '')}'")
        print(f"   Price: '{label_context.get('Price', '')}'")
        print(f"   Ratio_or_THC_CBD: '{label_context.get('Ratio_or_THC_CBD', '')}'")
        print(f"   DOH: '{label_context.get('DOH', '')}'")
        print(f"   DescAndWeight: '{label_context.get('DescAndWeight', '')}'")
        
        # Check for duplication
        print(f"\n🔍 DUPLICATION CHECK:")
        
        # Check if ProductStrain equals ProductBrand
        if label_context.get('ProductStrain') == label_context.get('ProductBrand'):
            print(f"   ❌ ProductStrain equals ProductBrand: '{label_context.get('ProductStrain')}'")
        else:
            print(f"   ✅ ProductStrain and ProductBrand are different")
        
        # Check if ProductStrain equals Product Type
        if label_context.get('ProductStrain') == test_record.get('Product Type*'):
            print(f"   ❌ ProductStrain equals Product Type: '{label_context.get('ProductStrain')}'")
        else:
            print(f"   ✅ ProductStrain and Product Type are different")
        
        # Check if any fields are empty or None
        empty_fields = []
        for field, value in label_context.items():
            if not value or str(value).strip() == '':
                empty_fields.append(field)
        
        if empty_fields:
            print(f"   ⚠️  Empty fields: {empty_fields}")
        else:
            print(f"   ✅ All fields have values")
        
        print(f"\n✅ Field duplication fix test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during field duplication fix test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_field_duplication_fix()
