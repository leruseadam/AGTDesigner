#!/usr/bin/env python3
"""
Debug script to examine DOH context structure for mini templates.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.template_processor import TemplateProcessor
from docx import Document
from io import BytesIO

def debug_doh_context():
    """Debug the DOH context structure for mini templates."""
    
    print("Debugging DOH Context Structure for Mini Templates")
    print("=" * 60)
    
    # Test data with DOH field
    test_records = [
        {
            'ProductName': 'Test Product 1',
            'ProductBrand': 'Test Brand 1',
            'Price': '$25.99',
            'Lineage': 'MIXED',
            'Ratio_or_THC_CBD': 'THC: 25% CBD: 2%',
            'Description': 'Test description text 1',
            'ProductStrain': 'Mixed 1',
            'ProductType': 'tincture',
            'DOH': 'YES'  # Add DOH field
        }
    ]
    
    try:
        # Create processor
        processor = TemplateProcessor('mini', 'default')
        print("✅ Processor created successfully")
        
        # Process records
        print(f"\nProcessing {len(test_records)} records...")
        
        # Hook into the context building process
        original_build_label_context = processor._build_label_context
        
        captured_contexts = []
        
        def capture_context(record, doc):
            context = original_build_label_context(record, doc)
            captured_contexts.append(context)
            return context
        
        processor._build_label_context = capture_context
        
        result = processor.process_records(test_records)
        
        if result:
            print("✅ Records processed successfully")
            
            # Examine the captured context structure
            print("\nExamining captured context structure...")
            
            if captured_contexts:
                context = captured_contexts[0]  # First record's context
                print(f"Context keys: {list(context.keys())}")
                
                # Check DOH-related fields in the flat context
                print(f"\nDOH-related fields:")
                print(f"  DOH: {repr(context.get('DOH', 'NOT_FOUND'))}")
                print(f"  _DOH_IMAGE_PATH: {repr(context.get('_DOH_IMAGE_PATH', 'NOT_FOUND'))}")
                print(f"  _DOH_IMAGE_WIDTH: {repr(context.get('_DOH_IMAGE_WIDTH', 'NOT_FOUND'))}")
                
                # Show all context values
                print(f"\nAll context values:")
                for key, value in context.items():
                    print(f"  {key}: {repr(value)}")
            else:
                print("❌ No contexts captured")
                
        else:
            print("❌ Failed to process records")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_doh_context()
