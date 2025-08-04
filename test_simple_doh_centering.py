#!/usr/bin/env python3
"""
Simple test for DOH image centering.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_doh_centering():
    """Test DOH image centering."""
    print("🧪 Testing DOH Image Centering")
    print("=" * 35)
    
    try:
        from src.core.generation.template_processor import TemplateProcessor
        from src.core.constants import FONT_SCHEME_DOUBLE
        
        # Create a test record
        test_record = {
            'Description': 'Test Product with DOH',
            'DOH': 'YES',
            'Product Type*': 'Flower',
            'Product Name*': 'Test Product',
            'Brand': 'Test Brand',
            'Price': '$10.00',
            'THC': '15.5%',
            'CBD': '0.5%',
            'Lineage': 'SATIVA'
        }
        
        # Create template processor
        processor = TemplateProcessor('double', FONT_SCHEME_DOUBLE)
        
        # Process the test record
        result = processor.process_records([test_record])
        print("✅ Document generated successfully")
        
        # Check for DOH images
        doh_found = False
        for table in result.tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        if paragraph.alignment and 'CENTER' in str(paragraph.alignment):
                            doh_found = True
                            print("✅ Found centered DOH image")
                            break
        
        if doh_found:
            print("✅ SUCCESS: DOH images are properly centered")
            return True
        else:
            print("❌ No centered DOH images found")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_doh_centering()
    if success:
        print("\n✅ TEST PASSED: DOH centering is working")
    else:
        print("\n❌ TEST FAILED: DOH centering needs work")
