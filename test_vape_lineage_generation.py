#!/usr/bin/env python3
"""
Test script to simulate Vape Cartridge lineage generation and verify alignment.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.template_processor import TemplateProcessor
from src.core.constants import CLASSIC_TYPES

def test_vape_cartridge_lineage_generation():
    """Test the actual lineage generation process for Vape Cartridge products."""
    print("=== Testing Vape Cartridge Lineage Generation ===")
    
    # Create a mock record for Vape Cartridge
    record = {
        'ProductType': 'Vape Cartridge',
        'Product Name*': 'Test Vape Cartridge',
        'ProductStrain': 'Blue Dream',
        'ProductBrand': 'Test Brand',
        'Vendor': 'Test Vendor'
    }
    
    print(f"Test record: {record}")
    
    # Create a mock document (we'll just test the context building)
    class MockDoc:
        def __init__(self):
            self.tables = []
    
    # Create template processor
    processor = TemplateProcessor('horizontal', 1.0, 'default')
    
    # Test the _build_label_context method
    print("\n=== Testing _build_label_context ===")
    try:
        label_context = processor._build_label_context(record, MockDoc())
        print(f"Generated label_context: {label_context}")
        
        # Check if Lineage is set correctly
        lineage = label_context.get('Lineage', '')
        print(f"Lineage content: '{lineage}'")
        
        # Check if it contains the expected markers
        if 'LINEAGE_START' in lineage and 'LINEAGE_END' in lineage:
            print("✓ Lineage contains expected markers")
        else:
            print("✗ Lineage missing expected markers")
            
    except Exception as e:
        print(f"Error in _build_label_context: {e}")
        import traceback
        traceback.print_exc()
    
    # Test the lineage alignment logic directly
    print("\n=== Testing Lineage Alignment Logic ===")
    
    # Simulate the current_product_type setting
    current_product_type = record.get('ProductType', '').lower()
    print(f"current_product_type: '{current_product_type}'")
    
    # Test the alignment logic
    product_type = current_product_type
    is_classic_product = product_type and product_type.lower() in CLASSIC_TYPES
    print(f"is_classic_product: {is_classic_product}")
    
    # Test the fallback logic
    if product_type:
        is_classic_product_fallback = product_type.lower() in CLASSIC_TYPES
        print(f"is_classic_product_fallback: {is_classic_product_fallback}")
    
    # Test with different lineage content
    test_lineage_contents = [
        "SATIVA",
        "INDICA", 
        "HYBRID",
        "HYBRID/SATIVA",
        "CBD"
    ]
    
    print(f"\n=== Testing Different Lineage Contents ===")
    for lineage_content in test_lineage_contents:
        content_upper = lineage_content.upper()
        classic_lineages = [
            "SATIVA", "INDICA", "HYBRID", "HYBRID/SATIVA", "HYBRID/INDICA", 
            "CBD", "MIXED", "PARAPHERNALIA", "PARA"
        ]
        is_classic_lineage = content_upper in classic_lineages
        
        # Final alignment decision
        should_left_align = is_classic_product or is_classic_lineage
        alignment = "LEFT" if should_left_align else "CENTER"
        
        print(f"  '{lineage_content}' -> is_classic_lineage: {is_classic_lineage} -> alignment: {alignment}")

if __name__ == "__main__":
    test_vape_cartridge_lineage_generation()
