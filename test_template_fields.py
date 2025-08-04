#!/usr/bin/env python3
"""
Test script to verify that all necessary template fields are being created correctly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.data.excel_processor import ExcelProcessor

def test_template_fields():
    """Test that all necessary template fields are being created."""
    print("Testing template field creation...")
    
    # Initialize ExcelProcessor
    processor = ExcelProcessor()
    
    # Try to load a default file
    from src.core.data.excel_processor import get_default_upload_file
    default_file = get_default_upload_file()
    
    if not default_file or not os.path.exists(default_file):
        print("❌ No default file found for testing")
        return False
    
    print(f"Loading file: {default_file}")
    success = processor.load_file(default_file)
    
    if not success:
        print("❌ Failed to load file")
        return False
    
    print(f"✓ File loaded successfully. DataFrame shape: {processor.df.shape}")
    
    # Get available tags
    tags = processor.get_available_tags()
    print(f"✓ Retrieved {len(tags)} tags")
    
    if not tags:
        print("❌ No tags found")
        return False
    
    # Check the first few tags for required fields
    required_fields = [
        'DescAndWeight',
        'Description', 
        'Price',
        'Ratio_or_THC_CBD',
        'ProductStrain',
        'DOH',
        'ProductBrand',
        'Lineage',
        'WeightUnits'
    ]
    
    print("\nChecking required fields in first 5 tags:")
    for i, tag in enumerate(tags[:5]):
        print(f"\nTag {i+1}: {tag.get('Product Name*', 'Unknown')}")
        for field in required_fields:
            value = tag.get(field, 'MISSING')
            if value == 'MISSING':
                print(f"  ❌ {field}: MISSING")
            elif not value:
                print(f"  ⚠ {field}: (empty)")
            else:
                print(f"  ✓ {field}: {value}")
    
    # Count how many tags have all required fields
    complete_tags = 0
    for tag in tags:
        missing_fields = [field for field in required_fields if not tag.get(field)]
        if not missing_fields:
            complete_tags += 1
    
    print(f"\nSummary:")
    print(f"  Total tags: {len(tags)}")
    print(f"  Tags with all required fields: {complete_tags}")
    print(f"  Tags missing some fields: {len(tags) - complete_tags}")
    
    if complete_tags > 0:
        print("✓ SUCCESS: Template fields are being created correctly!")
        return True
    else:
        print("❌ ISSUE: No tags have all required fields")
        return False

if __name__ == "__main__":
    test_template_fields() 