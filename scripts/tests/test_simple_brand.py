#!/usr/bin/env python3
"""
Simple test to verify brand fix is working
"""

from src.core.generation.template_processor import TemplateProcessor

def test_simple_brand():
    """Test brand processing with a simple record."""
    print("🧪 Testing simple brand processing...")
    
    # Create a simple test record with Ratio brand
    test_record = {
        'Product Name*': 'Test Ratio Shot - 100mg THC',
        'Product Brand': 'Ratio',
        'Product Type*': 'Edible (Liquid)',
        'Product Strain': 'Mixed',
        'Vendor/Supplier*': 'Lucid Brands Co',
        'THC test result': '100',
        'CBD test result': '0',
        'Test result unit (% or mg)': 'mg',
        'Price* (Tier Name for Bulk)': '20',
        'Weight*': '1',
        'Weight Unit* (grams/gm or ounces/oz)': 'unit',
        'Barcode*': '123456789',
        'Description': 'Test Ratio Product',
        'Quantity*': '10',
    }
    
    print(f"📋 Test record: {test_record['Product Name*']}")
    print(f"   Brand: {test_record['Product Brand']}")
    print(f"   Type: {test_record['Product Type*']}")
    
    # Process with vertical template
    import logging
    logging.basicConfig(level=logging.DEBUG)
    processor = TemplateProcessor('vertical', 'default')
    
    try:
        doc_buffer = processor.process_records([test_record])
        
        # Save the result
        output_path = "test_simple_ratio.docx"
        if hasattr(doc_buffer, 'save'):
            doc_buffer.save(output_path)
        else:
            with open(output_path, 'wb') as f:
                f.write(doc_buffer.getvalue())
        
        print(f"✅ Generated: {output_path}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_brand()