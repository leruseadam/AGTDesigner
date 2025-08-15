#!/usr/bin/env python3
"""
Debug script to check the actual context after building.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.core.generation.template_processor import TemplateProcessor

def debug_context():
    """Debug the context building to see where duplication occurs."""
    
    # Test record that should show the duplication
    test_record = {
        'ProductName': 'Grape Moonshot',
        'ProductBrand': 'CONSTELLATION CANNABIS',
        'Product Type*': 'edible (solid)',
        'Description': 'Grape Moonshot -1.7oz',
        'WeightUnits': '1.7oz',
        'Price': '$15',
        'THC': '100.0%',
        'CBD': '0%',
        'Lineage': 'MIXED'
    }
    
    print("=== DEBUGGING CONTEXT BUILDING ===")
    print(f"Test record: {test_record}")
    
    # Test with horizontal template
    from src.core.generation.template_processor import get_font_scheme
    font_scheme = get_font_scheme('horizontal')
    processor = TemplateProcessor('horizontal', font_scheme)
    
    try:
        # Create a dummy document for context building
        from docx import Document
        doc = Document()
        
        # Set the TemplateProcessor logger to DEBUG level
        import logging
        logging.getLogger('src.core.generation.template_processor').setLevel(logging.DEBUG)
        
        # Build the label context
        print("\nBuilding label context...")
        label_context = processor._build_label_context(test_record, doc)
        
        print("\n=== CONTEXT AFTER BUILDING ===")
        for key, value in label_context.items():
            if 'CONSTELLATION' in str(value):
                print(f"🔍 {key}: '{value}'")
            else:
                print(f"   {key}: '{value}'")
        
        # Check for duplication in the context itself
        print("\n=== CHECKING FOR DUPLICATION IN CONTEXT ===")
        duplication_found = False
        for key, value in label_context.items():
            if 'CONSTELLATION CANNABISCONSTELLATION CANNABIS' in str(value):
                print(f"❌ DUPLICATION FOUND in context field '{key}': '{value}'")
                duplication_found = True
            elif 'CONSTELLATION CANNABIS' in str(value):
                print(f"✅ Field '{key}' contains 'CONSTELLATION CANNABIS' (correct)")
        
        if not duplication_found:
            print("✅ No duplication found in context")
        else:
            print("❌ DUPLICATION WAS CREATED DURING CONTEXT BUILDING")
            
    except Exception as e:
        print(f"❌ Error during context building: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_context()
