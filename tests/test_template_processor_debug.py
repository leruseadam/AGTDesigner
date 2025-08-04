#!/usr/bin/env python3
"""
Debug script to test the optimized template processor and identify the None document issue.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.template_processor_optimized import get_optimized_template_processor
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def test_template_processor():
    """Test the template processor with a simple record."""
    
    print("Testing Optimized Template Processor")
    print("=" * 50)
    
    # Test data
    test_record = {
        'Product Name*': 'Test Product',
        'Product Brand': 'Test Brand',
        'Product Type*': 'flower',
        'Lineage': 'MIXED',
        'Vendor': 'Test Vendor',
        'Quantity': '1',
        'Weight': '3.5',
        'Units': 'g',
        'Price': '$25.99',
        'DOH': 'YES',
        'Ratio': 'THC: 25% CBD: 2%',
        'Ratio_or_THC_CBD': 'THC: 25% CBD: 2%',
        'Description': 'Test description text',
        'Product Strain': 'Test Strain'
    }
    
    try:
        # Create template processor
        print("Creating template processor...")
        processor = get_optimized_template_processor('horizontal', {}, 1.0)
        
        print(f"Template processor created successfully")
        print(f"Template type: {processor.template_type}")
        print(f"Chunk size: {processor.chunk_size}")
        
        # Test template buffer
        print("\nTesting template buffer...")
        if processor._template_buffer:
            buffer_size = len(processor._template_buffer.getvalue())
            print(f"Template buffer size: {buffer_size} bytes")
            if buffer_size == 0:
                print("❌ Template buffer is empty!")
                return
        else:
            print("❌ Template buffer is None!")
            return
        
        # Process a single record
        print("\nProcessing test record...")
        result = processor.process_records([test_record])
        
        if result:
            print(f"✅ Successfully processed record, result type: {type(result)}")
            print(f"Result size: {len(result.getvalue())} bytes")
        else:
            print("❌ Processing returned None")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_template_processor() 