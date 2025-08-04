#!/usr/bin/env python3
"""
Test script to verify that THC/CBD content is no longer appearing as weight options.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.data.excel_processor import ExcelProcessor
import pandas as pd
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_weight_options_fix():
    """Test that THC/CBD content is not appearing as weight options."""
    
    print("Testing Weight Options Fix")
    print("=" * 40)
    
    # Create test data with various weight and THC/CBD scenarios
    test_data = {
        'Product Name*': [
            'Test Product 1',
            'Test Product 2', 
            'Test Product 3',
            'Test Product 4',
            'Test Product 5'
        ],
        'Product Type*': [
            'flower',
            'pre-roll',
            'concentrate',
            'edible (solid)',
            'infused pre-roll'
        ],
        'Weight*': [
            '3.5',
            '1.0',
            '1.0',
            '100',
            '2.0'
        ],
        'Units': [
            'g',
            'g',
            'g',
            'mg',
            'g'
        ],
        'JointRatio': [
            '',
            'THC: 25% CBD: 2%',
            '',
            '',
            ''  # This should trigger the fallback case
        ],
        'Ratio': [
            '',
            '',
            'THC: 80% CBD: 5%',
            'THC: 10mg CBD: 2mg',
            ''
        ]
    }
    
    try:
        # Create ExcelProcessor and load test data
        processor = ExcelProcessor()
        processor.df = pd.DataFrame(test_data)
        
        print("\n1. Testing _format_weight_units method...")
        
        # Test each record individually
        for i, (_, row) in enumerate(processor.df.iterrows()):
            row_dict = row.to_dict()
            result = processor._format_weight_units(row_dict)
            product_type = row_dict.get('Product Type*', '')
            print(f"   Record {i+1} ({product_type}): '{result}'")
            
            # Note: _format_weight_units can return THC/CBD content for pre-rolls, which is correct
            # The issue is whether this content appears in the weight filter dropdown
        
        print("\n2. Testing get_dynamic_filter_options method...")
        
        # Get filter options
        options = processor.get_dynamic_filter_options({})
        
        if 'weight' in options:
            weight_options = options['weight']
            print(f"   Weight options generated: {weight_options}")
            
            # Check for any THC/CBD content in weight options
            problematic_options = []
            for option in weight_options:
                if any(keyword in str(option).lower() for keyword in ['thc', 'cbd', 'ratio', '|br|']):
                    problematic_options.append(option)
            
            if problematic_options:
                print(f"   ❌ ERROR: Found THC/CBD content in weight options: {problematic_options}")
                return False
            else:
                print("   ✓ No THC/CBD content found in weight options")
        else:
            print("   ❌ ERROR: No weight options found")
            return False
        
        print("\n3. Testing specific edge cases...")
        
        # Test pre-roll with no JointRatio (should return empty string, not "THC:|BR|CBD:")
        preroll_row = processor.df[processor.df['Product Type*'] == 'infused pre-roll'].iloc[0]
        preroll_dict = preroll_row.to_dict()
        preroll_result = processor._format_weight_units(preroll_dict)
        
        if preroll_result == "THC:|BR|CBD:":
            print("   ❌ ERROR: Pre-roll with no JointRatio still returns 'THC:|BR|CBD:'")
            return False
        elif preroll_result == "":
            print("   ✓ Pre-roll with no JointRatio correctly returns empty string")
        else:
            print(f"   ✓ Pre-roll with no JointRatio returns: '{preroll_result}'")
        
        print("\n" + "=" * 40)
        print("✓ ALL TESTS PASSED!")
        print("✓ THC/CBD content is no longer appearing as weight options")
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_weight_options_fix()
    sys.exit(0 if success else 1) 