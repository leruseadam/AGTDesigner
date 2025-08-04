#!/usr/bin/env python3
"""
Test script to verify that RSO Tankers and C02/Ethanol Extract get the same formatting as edibles.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.template_processor import TemplateProcessor

def test_edible_formatting():
    """Test that RSO Tankers and C02/Ethanol Extract get the same formatting as edibles."""
    
    # Create a template processor instance
    processor = TemplateProcessor('vertical', None)
    
    # Test data with different product types
    test_cases = [
        {
            'name': 'Edible Test',
            'product_type': 'edible (solid)',
            'ratio': 'THC 10mg CBD 5mg CBG 2mg'
        },
        {
            'name': 'RSO Tankers Test',
            'product_type': 'rso/co2 tankers',
            'ratio': 'THC 10mg CBD 5mg CBG 2mg'
        },
        {
            'name': 'RSO/CO2 Tankers Test',
            'product_type': 'rso/co2 tankers',
            'ratio': 'THC 10mg CBD 5mg CBG 2mg'
        },
        {
            'name': 'Capsule Test',
            'product_type': 'capsule',
            'ratio': 'THC 10mg CBD 5mg CBG 2mg'
        },
        {
            'name': 'Classic Type Test (should be different)',
            'product_type': 'flower',
            'ratio': 'THC 10mg CBD 5mg CBG 2mg'
        }
    ]
    
    print("Testing edible formatting for different product types:")
    print("=" * 60)
    
    for test_case in test_cases:
        # Create a mock record
        record = {
            'Product Type*': test_case['product_type'],
            'Ratio': test_case['ratio']
        }
        
        # Create a mock document (we don't need a real one for this test)
        class MockDoc:
            def __init__(self):
                self.tables = []
        
        doc = MockDoc()
        
        # Build the label context
        context = processor._build_label_context(record, doc)
        
        # Get the formatted ratio
        formatted_ratio = context.get('Ratio_or_THC_CBD', '')
        
        # Remove markers for display
        if 'RATIO_START' in formatted_ratio:
            formatted_ratio = formatted_ratio.replace('RATIO_START', '').replace('RATIO_END', '')
        
        print(f"\n{test_case['name']}:")
        print(f"  Product Type: {test_case['product_type']}")
        print(f"  Original Ratio: {test_case['ratio']}")
        print(f"  Formatted Ratio: {formatted_ratio}")
        
        # Check if it has the edible formatting (line breaks after every 2nd space)
        if test_case['product_type'] in ['edible (solid)', 'rso/co2 tankers', 'capsule']:
            if '\n' in formatted_ratio:
                print(f"  ✅ PASS: Has edible formatting (line breaks)")
            else:
                print(f"  ❌ FAIL: Missing edible formatting (no line breaks)")
        elif test_case['product_type'] == 'flower':
            if '\n' in formatted_ratio and 'THC:' in formatted_ratio and 'CBD:' in formatted_ratio:
                print(f"  ✅ PASS: Has classic formatting (THC:/CBD:)")
            else:
                print(f"  ❌ FAIL: Missing classic formatting")

if __name__ == "__main__":
    test_edible_formatting() 