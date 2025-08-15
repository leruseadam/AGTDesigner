#!/usr/bin/env python3
"""
Test script to verify that the vendor duplication fix is working correctly.
This script will test if vendor information is properly excluded for non-classic types.
"""

import os
import sys
import pandas as pd
from pathlib import Path

# Add the project root to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_vendor_fix():
    """Test that vendor duplication is fixed for non-classic types."""
    
    print("=== VENDOR DUPLICATION FIX TEST ===\n")
    
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
        
        print(f"✅ Loaded {len(processor.df)} records\n")
        
        # Test with different product types
        test_cases = [
            ("Paraphernalia", "non-classic"),
            ("Edible (Liquid)", "non-classic"), 
            ("Flower", "classic"),
            ("Pre-roll", "classic")
        ]
        
        for product_type, expected_category in test_cases:
            print(f"🔍 Testing Product Type: '{product_type}' (Expected: {expected_category})")
            
            # Find products with this type
            products = processor.df[
                processor.df['Product Type*'].str.lower() == product_type.lower()
            ]
            
            if len(products) == 0:
                print(f"   ❌ No products found with type '{product_type}'")
                continue
            
            # Take the first product
            test_record = products.iloc[0]
            print(f"   📋 Product: '{test_record.get('ProductName', 'Unknown')}'")
            print(f"   🏷️  Product Brand: '{test_record.get('Product Brand', 'Unknown')}'")
            print(f"   🏪 Vendor: '{test_record.get('Vendor', 'Unknown')}'")
            
            # Check if vendor equals product brand (duplication)
            vendor = test_record.get('Vendor', '')
            brand = test_record.get('Product Brand', '')
            
            if vendor and brand and vendor == brand:
                print(f"   ❌ DUPLICATION DETECTED: Vendor '{vendor}' equals Product Brand '{brand}'")
            else:
                print(f"   ✅ No duplication: Vendor '{vendor}' ≠ Product Brand '{brand}'")
            
            # Test the context building
            print(f"   🔧 Testing context building...")
            
            # Create a template processor
            template_processor = TemplateProcessor(
                template_type="double",
                font_scheme=get_font_scheme("double")
            )
            
            # Convert the record to a dictionary
            record_dict = test_record.to_dict()
            
            # Test the context building logic
            product_type_lower = product_type.lower()
            classic_types = ["flower", "pre-roll", "infused pre-roll", "concentrate", 
                           "solventless concentrate", "vape cartridge", "rso/co2 tankers"]
            
            is_classic = product_type_lower in classic_types
            print(f"      Is Classic Type: {is_classic}")
            
            # Simulate the vendor logic
            if is_classic:
                expected_vendor = record_dict.get('Vendor', '')
                print(f"      Expected Vendor: '{expected_vendor}' (classic type)")
            else:
                expected_vendor = ''
                print(f"      Expected Vendor: '{expected_vendor}' (non-classic type)")
            
            # Test the actual context building
            try:
                # Create a mock document for testing
                from docx import Document
                doc = Document()
                
                # Test the context building
                label_context = template_processor._build_label_context(record_dict, doc)
                
                # Check if ProductVendor is set correctly
                product_vendor = label_context.get('ProductVendor', '')
                if is_classic:
                    if product_vendor:
                        print(f"      ✅ ProductVendor set correctly: '{product_vendor}'")
                    else:
                        print(f"      ❌ ProductVendor not set for classic type")
                else:
                    if not product_vendor:
                        print(f"      ✅ ProductVendor correctly excluded: '{product_vendor}'")
                    else:
                        print(f"      ❌ ProductVendor incorrectly set for non-classic type: '{product_vendor}'")
                
            except Exception as e:
                print(f"      ❌ Error testing context building: {e}")
            
            print()  # Empty line for readability
        
        print("✅ Vendor duplication fix test completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_vendor_fix()
