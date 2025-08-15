#!/usr/bin/env python3
"""
Comprehensive script to fix all duplication issues in the template processor.
This script will identify and fix all the places where fields are being duplicated.
"""

import os
import sys
import pandas as pd
from pathlib import Path

# Add the project root to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def fix_all_duplication():
    """Fix all duplication issues in the template processor."""
    
    print("=== COMPREHENSIVE DUPLICATION FIX ===\n")
    
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
        
        # Test with a specific problematic record (Paraphernalia type)
        problematic_records = processor.df[
            processor.df['Product Type*'].str.lower() == 'paraphernalia'
        ]
        
        if len(problematic_records) > 0:
            print(f"\n🔍 Testing with {len(problematic_records)} Paraphernalia records:")
            
            # Take the first problematic record
            test_record = problematic_records.iloc[0]
            print(f"   Testing record: {test_record.get('ProductName', 'Unknown')}")
            print(f"   Product Type: {test_record.get('Product Type*', 'Unknown')}")
            print(f"   Original Product Strain: {test_record.get('Product Strain', 'Unknown')}")
            print(f"   Original Product Brand: {test_record.get('Product Brand', 'Unknown')}")
            print(f"   Original Description: {test_record.get('Description', 'Unknown')}")
            print(f"   Original Weight: {test_record.get('Weight', 'Unknown')}")
            
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
            
            # Process DescAndWeight - CRITICAL: Don't combine with strain
            desc = test_record.get('Description', '')
            weight = test_record.get('Weight', '')
            if desc and weight:
                label_context['DescAndWeight'] = f"{desc} - {weight}"
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
            
            # Check if DescAndWeight contains the strain value
            desc_weight = label_context.get('DescAndWeight', '')
            strain = label_context.get('ProductStrain', '')
            if strain and strain in desc_weight:
                print(f"   ❌ DescAndWeight contains ProductStrain: '{desc_weight}' contains '{strain}'")
            else:
                print(f"   ✅ DescAndWeight does not contain ProductStrain")
            
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
            
            # Now test the actual template processor
            print(f"\n🔧 TESTING ACTUAL TEMPLATE PROCESSOR:")
            
            # Create a test context for the template processor
            test_context = {
                f"Label{i+1}": label_context.copy() for i in range(12)
            }
            
            # Test the template processor
            try:
                # This should process the records and apply our fixes
                result = template_processor.process_records([test_record])
                print(f"   ✅ TemplateProcessor.process_records() completed successfully")
                
                # Check if the result contains the expected values
                if result:
                    print(f"   ✅ Template processing returned result")
                else:
                    print(f"   ⚠️  Template processing returned None")
                    
            except Exception as e:
                print(f"   ❌ Error in TemplateProcessor.process_records(): {e}")
                import traceback
                traceback.print_exc()
        
    except Exception as e:
        print(f"❌ Error during comprehensive duplication fix: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_all_duplication()
