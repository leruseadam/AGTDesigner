#!/usr/bin/env python3
"""
Debug script to investigate why Product Strain is showing Brand values in nonclassic types.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.template_processor import TemplateProcessor
from src.core.constants import CLASSIC_TYPES
from docx import Document
from docx.shared import Pt
import tempfile
import os

def debug_productstrain_brand_issue():
    """Debug why Product Strain is showing Brand values in nonclassic types."""
    print("Debugging Product Strain showing Brand values in nonclassic types")
    
    # Test with a non-classic type (edible)
    non_classic_record = {
        'ProductName': 'Test Edible',
        'ProductBrand': 'Test Brand',
        'ProductStrain': 'CBD Blend',  # This should show, not the brand
        'ProductType': 'edible (solid)',  # Non-classic type
        'ProductVendor': 'Test Vendor',
        'Lineage': 'MIXED',
        'Price': '$25.00',
        'WeightUnits': '3.5g',
        'Description': 'Test Description'
    }
    
    # Test with a classic type (flower)
    classic_record = {
        'ProductName': 'Test Flower',
        'ProductBrand': 'Test Brand',
        'ProductStrain': 'OG Kush',  # This should show
        'ProductType': 'flower',  # Classic type
        'ProductVendor': 'Test Vendor',
        'Lineage': 'HYBRID',
        'Price': '$25.00',
        'WeightUnits': '3.5g',
        'Description': 'Test Description'
    }
    
    print("\n=== Testing Non-Classic Type (Edible) ===")
    print(f"Product Type: {non_classic_record['ProductType']}")
    print(f"Product Brand: {non_classic_record['ProductBrand']}")
    print(f"Product Strain: {non_classic_record['ProductStrain']}")
    print(f"Lineage: {non_classic_record['Lineage']}")
    
    # Test template processing
    processor = TemplateProcessor('vertical', 'default', 1.0)
    
    # Build context for non-classic type
    doc = Document()
    context = processor._build_label_context(non_classic_record, doc)
    
    print(f"\nContext after _build_label_context:")
    print(f"ProductStrain: '{context.get('ProductStrain', '')}'")
    print(f"ProductBrand: '{context.get('ProductBrand', '')}'")
    print(f"Lineage: '{context.get('Lineage', '')}'")
    
    # Check if ProductStrain contains ProductBrand value
    if context.get('ProductStrain', '') and context.get('ProductBrand', ''):
        if context.get('ProductStrain', '') == context.get('ProductBrand', ''):
            print("❌ PROBLEM: ProductStrain equals ProductBrand!")
        elif context.get('ProductBrand', '') in context.get('ProductStrain', ''):
            print("❌ PROBLEM: ProductStrain contains ProductBrand value!")
        else:
            print("✅ ProductStrain and ProductBrand are different")
    
    print("\n=== Testing Classic Type (Flower) ===")
    print(f"Product Type: {classic_record['ProductType']}")
    print(f"Product Brand: {classic_record['ProductBrand']}")
    print(f"Product Strain: {classic_record['ProductStrain']}")
    print(f"Lineage: {classic_record['Lineage']}")
    
    # Build context for classic type
    context = processor._build_label_context(classic_record, doc)
    
    print(f"\nContext after _build_label_context:")
    print(f"ProductStrain: '{context.get('ProductStrain', '')}'")
    print(f"ProductBrand: '{context.get('ProductBrand', '')}'")
    print(f"Lineage: '{context.get('Lineage', '')}'")
    
    # Check if ProductStrain contains ProductBrand value
    if context.get('ProductStrain', '') and context.get('ProductBrand', ''):
        if context.get('ProductStrain', '') == context.get('ProductBrand', ''):
            print("❌ PROBLEM: ProductStrain equals ProductBrand!")
        elif context.get('ProductBrand', '') in context.get('ProductStrain', ''):
            print("❌ PROBLEM: ProductStrain contains ProductBrand value!")
        else:
            print("✅ ProductStrain and ProductBrand are different")
    
    print("\n=== Summary ===")
    print("The issue might be:")
    print("1. Template rendering problem")
    print("2. Post-processing issue")
    print("3. Template expansion problem")
    print("4. Context building issue")

if __name__ == "__main__":
    debug_productstrain_brand_issue() 