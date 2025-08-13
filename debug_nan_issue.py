#!/usr/bin/env python3
"""
Debug script to identify where NaN values are coming from in THC/CBD processing.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import logging

# Set up logging to see debug output
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

from src.core.generation.template_processor import TemplateProcessor

def debug_nan_issue():
    """Debug the NaN issue in THC/CBD processing."""
    
    print("Debugging NaN Issue in THC/CBD Processing")
    print("=" * 50)
    
    # Create a template processor instance
    tp = TemplateProcessor('double', 'arial', 1.0)
    
    # Test with various data scenarios that might cause NaN
    test_cases = [
        {
            'name': 'Normal values',
            'data': {
                'Product Type*': 'flower',
                'Total THC': '18.5',
                'THCA': '20.1',
                'CBDA': '0.8',
                'Ratio': 'THC:|BR|CBD:'
            }
        },
        {
            'name': 'Empty Total THC, use THCA',
            'data': {
                'Product Type*': 'flower',
                'Total THC': '',
                'THCA': '22.3',
                'CBDA': '1.2',
                'Ratio': 'THC:|BR|CBD:'
            }
        },
        {
            'name': 'Zero Total THC, use THCA',
            'data': {
                'Product Type*': 'flower',
                'Total THC': '0',
                'THCA': '19.8',
                'CBDA': '0.5',
                'Ratio': 'THC:|BR|CBD:'
            }
        },
        {
            'name': 'Missing columns (simulate real data)',
            'data': {
                'Product Type*': 'flower',
                'Ratio': 'THC:|BR|CBD:'
            }
        },
        {
            'name': 'None values',
            'data': {
                'Product Type*': 'flower',
                'Total THC': None,
                'THCA': None,
                'CBDA': None,
                'Ratio': 'THC:|BR|CBD:'
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {test_case['name']}")
        print(f"   Data: {test_case['data']}")
        
        try:
            # Test format_classic_ratio directly
            result = tp.format_classic_ratio("THC:|BR|CBD:", test_case['data'])
            print(f"   Result: '{result}'")
            
            # Check if result contains 'nan'
            if 'nan' in result.lower():
                print("   ❌ CONTAINS 'nan' - This is the problem!")
            else:
                print("   ✅ No 'nan' found")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("Debug completed!")
    print("\nIf you see 'nan' in any results, check:")
    print("1. Excel file for empty cells in THC/CBD columns")
    print("2. Data loading process for NaN conversion")
    print("3. Column names match exactly (case-sensitive)")

if __name__ == "__main__":
    debug_nan_issue()
