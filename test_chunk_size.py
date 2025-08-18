#!/usr/bin/env python3
"""
Test script to check chunk size and context building.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.template_processor import TemplateProcessor

def test_chunk_size():
    """Test chunk size and context building logic."""
    
    try:
        print("Testing horizontal template chunk size...")
        processor = TemplateProcessor('horizontal', {}, 1.0)
        
        print(f"Chunk size: {processor.chunk_size}")
        print(f"Template type: {processor.template_type}")
        
        # Test with 3 records
        test_records = [
            {'ProductName': 'Test 1', 'ProductType': 'Flower', 'Lineage': 'SATIVA'},
            {'ProductName': 'Test 2', 'ProductType': 'Flower', 'Lineage': 'INDICA'},
            {'ProductName': 'Test 3', 'ProductType': 'Flower', 'Lineage': 'HYBRID'}
        ]
        
        print(f"\nTesting with {len(test_records)} records:")
        print(f"Expected chunk size: {processor.chunk_size}")
        print(f"Actual records: {len(test_records)}")
        
        # Simulate the context building logic
        context = {}
        for i, record in enumerate(test_records):
            context[f'Label{i+1}'] = {'ProductName': record['ProductName']}
            print(f"  Created Label{i+1}: {record['ProductName']}")
        
        # Fill remaining labels with empty context
        for i in range(len(test_records), processor.chunk_size):
            context[f'Label{i+1}'] = {}
            print(f"  Created empty Label{i+1}")
        
        print(f"\nFinal context keys: {list(context.keys())}")
        print(f"Total labels created: {len(context)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in chunk size test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_chunk_size()
