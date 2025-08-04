#!/usr/bin/env python3
"""
Debug script to understand THC/CBD content processing.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.template_processor import TemplateProcessor

def debug_thc_cbd_content():
    """Debug THC/CBD content processing."""
    
    print("Debugging THC/CBD Content Processing")
    print("=" * 50)
    
    # Create test data with classic product type
    test_data = {
        'ProductName': 'Test Product',
        'ProductBrand': 'Test Brand',
        'Price': '$25.99',
        'Lineage': 'Sativa',
        'THC_CBD': 'THC: 87.01% CBD: 0.45%',
        'Ratio_or_THC_CBD': 'THC: 87.01% CBD: 0.45%',
        'Ratio': 'THC: 87.01% CBD: 0.45%',
        'WeightUnits': '1g',
        'ProductStrain': 'Test Strain',
        'DOH': 'Yes',
        'ProductType': 'flower'  # This should make it a classic type
    }
    
    print(f"Test data: {test_data}")
    
    # Create template processor
    tp = TemplateProcessor(template_type='vertical', font_scheme='Arial')
    
    # Build label context
    from src.core.generation.template_processor import wrap_with_marker, unwrap_marker
    from src.core.generation.text_processing import format_ratio_multiline
    
    # Simulate the content building logic
    ratio_val = test_data.get('Ratio_or_THC_CBD') or test_data.get('Ratio', '')
    print(f"Initial ratio_val: {ratio_val}")
    
    if ratio_val:
        cleaned_ratio = ratio_val.lstrip('- ')
        product_type = test_data.get('ProductType', '').lower()
        print(f"Product type: {product_type}")
        
        # Check if it's a classic type
        classic_types = {'flower', 'concentrate', 'edible', 'pre-roll', 'infused pre-roll', 'tincture', 'topical'}
        is_classic = product_type in classic_types
        print(f"Is classic: {is_classic}")
        
        if is_classic and 'mg' in cleaned_ratio.lower():
            cleaned_ratio = format_ratio_multiline(cleaned_ratio)
        elif is_classic:
            cleaned_ratio = tp.format_classic_ratio(cleaned_ratio, test_data)
        
        print(f"Cleaned ratio: {cleaned_ratio}")
        
        # Fast marker wrapping
        content = cleaned_ratio.replace('|BR|', '\n')
        print(f"Content after BR replacement: {content}")
        
        # Force line breaks for vertical and double templates
        if tp.template_type in ['vertical', 'double'] and content.strip().startswith('THC:') and 'CBD:' in content:
            content = content.replace('THC: CBD:', 'THC:\nCBD:').replace('THC:  CBD:', 'THC:\nCBD:')
        
        print(f"Content after line break processing: {content}")
        
        marker = 'THC_CBD' if is_classic else 'RATIO'
        print(f"Marker: {marker}")
        
        wrapped_content = wrap_with_marker(content, marker)
        print(f"Wrapped content: {wrapped_content}")
        
        # Check what should be in label context
        label_context = {}
        label_context['Ratio_or_THC_CBD'] = wrapped_content
        
        if is_classic:
            label_context['THC_CBD'] = wrap_with_marker(content, 'THC_CBD')
        else:
            label_context['THC_CBD'] = ''
        
        print(f"Label context Ratio_or_THC_CBD: {label_context.get('Ratio_or_THC_CBD')}")
        print(f"Label context THC_CBD: {label_context.get('THC_CBD')}")
    
    print("\n" + "=" * 50)
    print("Debug complete")

if __name__ == "__main__":
    debug_thc_cbd_content() 