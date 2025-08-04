#!/usr/bin/env python3
"""
Test script to verify that the new THC/CBD formatting is applied correctly
in the template generation process.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.template_processor import TemplateProcessor
from src.core.generation.template_processor import get_font_scheme

def test_template_thc_cbd_formatting():
    """Test that THC/CBD formatting is applied correctly in templates."""
    
    # Create a test record with THC/CBD data
    test_record = {
        'ProductType': 'Flower',
        'ProductStrain': 'Test Strain',
        'ProductBrand': 'Test Brand',
        'Price': '12.00',
        'Lineage': 'HYBRID',
        'Ratio_or_THC_CBD': 'THC: 74.51% CBD: 0.15%',
        'AI': '74.51',  # Total THC
        'AK': '0.15',   # Total CBD
        'Product Description': 'Test product description'
    }
    
    # Test different template types
    template_types = ['vertical', 'horizontal', 'mini', 'double']
    
    print("Testing THC/CBD Formatting in Templates")
    print("=" * 50)
    
    for template_type in template_types:
        print(f"\nTesting {template_type.upper()} template:")
        
        try:
            # Create template processor
            font_scheme = get_font_scheme(template_type)
            processor = TemplateProcessor(template_type, font_scheme)
            
            # Build label context
            label_context = processor._build_label_context(test_record, None)
            
            # Check if THC/CBD formatting was applied
            ratio_content = label_context.get('Ratio_or_THC_CBD', '')
            
            print(f"  Original: 'THC: 74.51% CBD: 0.15%'")
            print(f"  Formatted: '{ratio_content}'")
            
            # Check if the formatting looks correct
            if 'THC:\n' in ratio_content and 'CBD:\n' in ratio_content:
                print(f"  ✓ Correct format applied")
            else:
                print(f"  ✗ Format not applied correctly")
                
        except Exception as e:
            print(f"  ✗ Error processing {template_type} template: {e}")
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    test_template_thc_cbd_formatting() 