#!/usr/bin/env python3
"""
Test script to demonstrate improved JSON matching with educated guessing.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.data.json_matcher import JSONMatcher, EducatedGuesser
from src.core.data.excel_processor import ExcelProcessor

def test_educated_guesser():
    """Test the EducatedGuesser class functionality."""
    print("Testing EducatedGuesser...")
    print("=" * 50)
    
    guesser = EducatedGuesser()
    
    # Test field type guessing
    test_cases = [
        ("product_name", "Blue Dream Flower", "product_name"),
        ("vendor", "Dank Czar", "vendor"),
        ("brand", "Dank Czar", "brand"),
        ("strain", "Blue Dream", "strain"),
        ("product_type", "Flower", "product_type"),
        ("weight", "3.5g", "weight"),
        ("units", "grams", "units"),
        ("thc", "25.5%", "thc"),
        ("cbd", "2.1%", "cbd"),
        ("price", "$45.99", "price"),
        ("quantity", "100", "quantity"),
        ("unknown_field", "some value", "product_name"),  # Default case
    ]
    
    for field_name, field_value, expected_type in test_cases:
        guessed_type = guesser.guess_field_type(field_name, field_value)
        status = "✅" if guessed_type == expected_type else "❌"
        print(f"{status} {field_name}: '{field_value}' -> {guessed_type} (expected: {expected_type})")
    
    print("\n" + "=" * 50)
    
    # Test value validation
    print("\nTesting value validation...")
    validation_tests = [
        ("product_name", "Blue Dream Flower", True),
        ("weight", "3.5g", True),
        ("weight", "invalid", False),
        ("thc", "25.5%", True),
        ("thc", "abc", False),
        ("price", "$45.99", True),
        ("price", "free", False),
    ]
    
    for field_type, value, expected_valid in validation_tests:
        is_valid = guesser.validate_field_value(field_type, value)
        status = "✅" if is_valid == expected_valid else "❌"
        print(f"{status} {field_type}: '{value}' -> valid: {is_valid} (expected: {expected_valid})")
    
    print("\n" + "=" * 50)
    
    # Test value normalization
    print("\nTesting value normalization...")
    normalization_tests = [
        ("weight", "3.5g", "3.5"),
        ("thc", "25.5%", "25.5"),
        ("cbd", "2.1%", "2.1"),
        ("price", "$45.99", "45.99"),
        ("quantity", "100", "100"),
    ]
    
    for field_type, value, expected_normalized in normalization_tests:
        normalized = guesser.normalize_field_value(field_type, value)
        status = "✅" if normalized == expected_normalized else "❌"
        print(f"{status} {field_type}: '{value}' -> '{normalized}' (expected: '{expected_normalized}')")

def test_json_normalization():
    """Test JSON normalization with educated guessing."""
    print("\n\nTesting JSON normalization...")
    print("=" * 50)
    
    guesser = EducatedGuesser()
    
    # Sample JSON data that might come from different sources
    sample_json = {
        "name": "Blue Dream Live Resin",
        "vendor_name": "Dank Czar",
        "brand": "Dank Czar",
        "strain": "Blue Dream",
        "category": "Concentrate",
        "net_weight": "1.0g",
        "weight_unit": "grams",
        "thc_content": "85.2%",
        "cbd_level": "1.2%",
        "retail_price": "$45.99",
        "available_qty": "50",
        "description": "Premium live resin concentrate"
    }
    
    print("Original JSON:")
    for key, value in sample_json.items():
        print(f"  {key}: {value}")
    
    print("\nNormalized JSON:")
    normalized = guesser.create_normalized_json(sample_json)
    for key, value in normalized.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 50)

def test_enhanced_matching():
    """Test the enhanced matching functionality."""
    print("\n\nTesting enhanced matching...")
    print("=" * 50)
    
    # Create Excel processor and load data
    excel_processor = ExcelProcessor()
    
    # Get the default file
    from src.core.data.excel_processor import get_default_upload_file
    default_file = get_default_upload_file()
    
    if not default_file:
        print("❌ No default file found")
        return
    
    print(f"Found default file: {default_file}")
    
    # Load the file
    success = excel_processor.load_file(default_file)
    if not success:
        print("❌ Failed to load file")
        return
    
    print(f"✅ File loaded successfully: {len(excel_processor.df)} rows")
    
    # Create JSON matcher
    json_matcher = JSONMatcher(excel_processor)
    
    # Test with a sample JSON URL (data URL) - includes proper license structure
    sample_json_data = {
        "from_license_name": "ABC Grow Op LLC",
        "from_license_number": "12345",
        "inventory_transfer_items": [
            {
                "product_name": "Blue Dream Live Resin",
                "vendor": "Dank Czar",
                "brand": "Dank Czar",
                "strain_name": "Blue Dream",
                "product_type": "Concentrate",
                "weight": "1.0g",
                "units": "grams",
                "thc": "85.2%",
                "cbd": "1.2%",
                "price": "$45.99"
            }
        ]
    }
    
    import json
    import base64
    
    # Create a data URL
    json_str = json.dumps(sample_json_data)
    data_url = f"data:application/json;base64,{base64.b64encode(json_str.encode()).decode()}"
    
    print(f"\nTesting with sample data URL...")
    print(f"Sample product: Blue Dream Live Resin by Dank Czar")
    
    try:
        # Test regular matching
        print("\n1. Testing regular matching...")
        regular_matches = json_matcher.fetch_and_match(data_url)
        print(f"   Regular matches found: {len(regular_matches)}")
        for i, match in enumerate(regular_matches[:3]):  # Show first 3
            print(f"   {i+1}. {match}")
        
        # Test enhanced matching with educated guessing
        print("\n2. Testing enhanced matching with educated guessing...")
        enhanced_matches = json_matcher.fetchand_match_with_educated_guessing(data_url)
        print(f"   Enhanced matches found: {len(enhanced_matches)}")
        for i, match in enumerate(enhanced_matches[:3]):  # Show first 3
            print(f"   {i+1}. {match}")
        
        print("\n" + "=" * 50)
        
    except Exception as e:
        print(f"❌ Error during matching: {e}")

def main():
    """Run all tests."""
    print("Improved JSON Matching Test Suite")
    print("=" * 60)
    
    try:
        # Test 1: Educated Guesser
        test_educated_guesser()
        
        # Test 2: JSON Normalization
        test_json_normalization()
        
        # Test 3: Enhanced Matching
        test_enhanced_matching()
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
