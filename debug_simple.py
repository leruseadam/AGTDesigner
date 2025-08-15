#!/usr/bin/env python3
"""
Very simple debug script to see exactly what's happening.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

try:
    print("=== SIMPLE DEBUG TEST ===")
    
    # Import
    from src.core.generation.template_processor import TemplateProcessor
    from src.core.generation.template_processor import get_font_scheme
    from docx import Document
    
    # Create instance
    font_scheme = get_font_scheme('horizontal')
    processor = TemplateProcessor('horizontal', font_scheme)
    
    # Test record
    test_record = {
        'ProductName': 'Test',
        'ProductBrand': 'TEST BRAND',
        'Product Type*': 'edible (solid)',
        'Description': 'Test Description',
        'WeightUnits': '1oz',
        'Price': '$10',
        'THC': '10%',
        'CBD': '0%',
        'Lineage': 'TEST'
    }
    
    print(f"Test record: {test_record}")
    
    # Create dummy doc
    doc = Document()
    
    # Set logger to DEBUG
    import logging
    logging.getLogger('src.core.generation.template_processor').setLevel(logging.DEBUG)
    
    # Call method
    print("\nCalling _build_label_context...")
    result = processor._build_label_context(test_record, doc)
    
    print(f"\nResult keys: {list(result.keys())}")
    print(f"ProductBrand: {result.get('ProductBrand', 'NOT_FOUND')}")
    print(f"Lineage: {result.get('Lineage', 'NOT_FOUND')}")
    
    # Check if the fix worked
    if 'PRODUCTBRAND_CENTER_START' in str(result.get('Lineage', '')):
        print("❌ FIX DID NOT WORK: Lineage still contains wrapped ProductBrand content")
    else:
        print("✅ FIX WORKED: Lineage does not contain wrapped ProductBrand content")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
