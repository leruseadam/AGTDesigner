#!/usr/bin/env python3
"""
Quick test to verify lineage is being set in DOCX generation
"""
import logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Test record with lineage
test_record = {
    'ProductName': 'Test Flower',
    'Product Name*': 'Test Flower',
    'Product Type*': 'Flower',
    'ProductType': 'Flower',
    'Lineage': 'SATIVA',
    'Product Brand': 'Test Brand',
    'ProductBrand': 'Test Brand',
    'Product Strain': 'Test Strain',
    'ProductStrain': 'Test Strain',
    'Price': '$10.00',
    'WeightUnits': '3.5g',
    'Description': 'Premium flower'
}

print("=" * 80)
print("LINEAGE DOCX GENERATION TEST")
print("=" * 80)
print(f"\nTest Record:")
print(f"  Product: {test_record['ProductName']}")
print(f"  Type: {test_record['Product Type*']}")
print(f"  Lineage: {test_record['Lineage']}")
print(f"  Brand: {test_record['Product Brand']}")
print(f"  Strain: {test_record['Product Strain']}")
print("\n" + "=" * 80)

try:
    from src.core.generation.template_processor import TemplateProcessor
    
    # Create template processor
    processor = TemplateProcessor(template_type='vertical', font_scheme='standard')
    
    # Build label context
    print("\nBuilding label context...")
    label_context = processor._build_label_context(test_record, None)
    
    print(f"\n📋 Label Context Lineage Field:")
    lineage_value = label_context.get('Lineage', 'NOT_SET')
    print(f"  Lineage: '{lineage_value}'")
    
    if not lineage_value or lineage_value == 'NOT_SET':
        print("\n❌ ERROR: Lineage field is empty or not set!")
    elif 'SATIVA' in lineage_value.upper():
        print(f"\n✅ SUCCESS: Lineage contains expected value 'SATIVA'")
    else:
        print(f"\n⚠️  WARNING: Lineage set but doesn't contain expected value")
    
    print("\n" + "=" * 80)
    print("Test completed - check logs above for detailed lineage processing")
    print("=" * 80)
    
except Exception as e:
    print(f"\n❌ ERROR: Test failed with exception:")
    print(f"   {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
