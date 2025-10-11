#!/usr/bin/env python3
"""Test vendor fallback functionality for brand enrichment."""

import logging
from src.core.generation.template_processor import TemplateProcessor, get_font_scheme
from docx import Document

# Set up logging
logging.basicConfig(level=logging.INFO)

def test_vendor_fallback():
    """Test that vendor is used as fallback when brand is missing."""
    
    print("🧪 Testing vendor fallback functionality...")
    
    # Create test records - one with missing brand that should get vendor fallback
    test_records = [
        {
            'ProductName': 'Test Product No Brand',
            'Product Brand': '',  # Missing brand
            'ProductBrand': '',   # Also missing
            'Vendor': 'Test Vendor Company',  # Should be used as fallback
            'Product Type*': 'accessory',
            'Price': '$10.00'
        },
        {
            'ProductName': 'Test Product With Brand',
            'Product Brand': 'Existing Brand',  # Has brand
            'ProductBrand': 'Existing Brand',
            'Vendor': 'Test Vendor Company',  # Should NOT be used
            'Product Type*': 'accessory', 
            'Price': '$15.00'
        }
    ]
    
    # Set up template processor
    font_scheme = get_font_scheme('vertical')
    processor = TemplateProcessor('vertical', font_scheme)
    
    # Create a dummy document for context building
    doc = Document()
    
    # Test each record
    for i, record in enumerate(test_records, 1):
        print(f"\n🧪 Test {i}: {record['ProductName']}")
        print(f"   Original brand: '{record.get('Product Brand', '')}'")
        print(f"   Vendor: '{record.get('Vendor', '')}'")
        
        # Build label context (this should trigger brand enrichment)
        enriched_context = processor._build_label_context(record, doc)
        
        # Check the enriched brand
        enriched_brand = enriched_context.get('Product Brand', '')
        print(f"   Enriched brand: '{enriched_brand}'")
        
        # Verify results
        if record['ProductName'] == 'Test Product No Brand':
            if enriched_brand == 'Test Vendor Company':
                print("   ✅ SUCCESS: Vendor fallback worked!")
            else:
                print("   ❌ FAILED: Vendor fallback did not work")
        elif record['ProductName'] == 'Test Product With Brand':
            if enriched_brand == 'Existing Brand':
                print("   ✅ SUCCESS: Existing brand preserved!")
            else:
                print("   ❌ FAILED: Existing brand was overwritten")

if __name__ == '__main__':
    test_vendor_fallback()
    print("\n✅ Vendor fallback test completed!")