#!/usr/bin/env python3
"""Test brand enrichment for Ratio products specifically."""

import logging
from src.core.generation.template_processor import TemplateProcessor, get_font_scheme
from docx import Document

# Set up logging
logging.basicConfig(level=logging.INFO)

def test_ratio_brand_enrichment():
    """Test brand enrichment for specific Ratio products."""
    
    print("🧪 Testing Ratio brand enrichment...")
    
    # Create test record based on what we found in database
    test_record = {
        'ProductName': 'Strawberry Burst Shot by Ratio - 100mg THC',
        'Product Name*': 'Strawberry Burst Shot by Ratio - 100mg THC',
        'Product Brand': 'Ratio',  # This should exist in database
        'ProductBrand': 'Ratio',   
        'Vendor/Supplier*': 'Lucid Brands Co',
        'Product Type*': 'Edible (Liquid)',
        'Price': '$12',
        'Description': 'Strawberry Burst Shot',
        'WeightUnits': '2.5oz'
    }
    
    print(f"🔍 Testing: {test_record['ProductName']}")
    print(f"   Original brand: '{test_record.get('Product Brand', '')}'")
    print(f"   Vendor: '{test_record.get('Vendor/Supplier*', '')}'")
    print(f"   Type: '{test_record.get('Product Type*', '')}'")
    
    # Set up template processor
    font_scheme = get_font_scheme('vertical')
    processor = TemplateProcessor('vertical', font_scheme)
    
    # Create a dummy document for context building
    doc = Document()
    
    # Build label context (this should trigger brand enrichment)
    enriched_context = processor._build_label_context(test_record, doc)
    
    # Check the enriched brand
    enriched_brand = enriched_context.get('Product Brand', '')
    lineage_value = enriched_context.get('Lineage', '')
    
    print(f"   Enriched brand: '{enriched_brand}'")
    print(f"   Lineage value: '{lineage_value}'")
    print(f"   ProductBrand: '{enriched_context.get('ProductBrand', '')}'")
    
    # For edible liquid (non-classic type), the brand should appear in Lineage field
    if enriched_context.get('Product Type*', '').lower() == 'edible (liquid)':
        print(f"   ✅ This is a non-classic type (edible liquid)")
        print(f"   🔍 For non-classic types, brand should appear in Lineage field")
        if 'RATIO' in lineage_value.upper():
            print(f"   ✅ SUCCESS: Brand 'Ratio' found in Lineage field!")
        else:
            print(f"   ❌ ISSUE: Brand 'Ratio' NOT found in Lineage field")
    
    return enriched_context

if __name__ == '__main__':
    result = test_ratio_brand_enrichment()
    print(f"\n📋 Full enriched context:")
    for key, value in result.items():
        if 'brand' in key.lower() or 'lineage' in key.lower() or 'vendor' in key.lower():
            print(f"   {key}: '{value}'")
    print("\n✅ Ratio brand test completed!")