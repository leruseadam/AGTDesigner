#!/usr/bin/env python3
"""
Test template ratio processing logic
"""

from src.core.generation.text_processing import format_ratio_multiline

def test_template_ratio_processing():
    """Test the exact template processing logic for ratio formatting."""
    
    print("Testing Template Ratio Processing Logic")
    print("=" * 60)
    
    # Simulate the exact logic from template_processor.py
    def simulate_template_processing(record):
        """Simulate the exact ratio processing logic from template_processor.py"""
        
        # Get ratio value
        ratio_val = record.get('Ratio', '')
        if not ratio_val:
            return ''
        
        # Clean the ratio
        import re
        cleaned_ratio = re.sub(r'^[-\s]+', '', ratio_val)
        
        # Get product type (using the same logic as template processor)
        product_type = (record.get('ProductType', '').strip().lower() or 
                       record.get('Product Type*', '').strip().lower())
        
        print(f"  Original ratio: '{ratio_val}'")
        print(f"  Cleaned ratio: '{cleaned_ratio}'")
        print(f"  Product type: '{product_type}'")
        
        # Define types (same as template processor)
        edible_types = {"edible (solid)", "edible (liquid)", "high cbd edible liquid", "tincture", "topical", "capsule"}
        classic_types = ["flower", "pre-roll", "infused pre-roll", "concentrate", "solventless concentrate", "vape cartridge", "rso/co2 tankers"]
        
        print(f"  Is edible type: {product_type in edible_types}")
        print(f"  Is classic type: {product_type in classic_types}")
        print(f"  Contains 'mg': {'mg' in cleaned_ratio.lower()}")
        
        if product_type in classic_types:
            # For classic types, check if content contains mg values
            if 'mg' in cleaned_ratio.lower():
                # Use format_ratio_multiline to add line breaks after every 2nd word
                print(f"  Processing: Classic type with mg values - applying format_ratio_multiline")
                final_ratio = format_ratio_multiline(cleaned_ratio)
            else:
                # For non-mg content, use classic ratio formatting
                print(f"  Processing: Classic type without mg values - using classic formatting")
                final_ratio = cleaned_ratio  # Simplified for this test
        elif product_type in edible_types or 'mg' in cleaned_ratio.lower():
            # For edibles OR any product type with mg values, add line breaks
            if 'mg' in cleaned_ratio.lower():
                # Use format_ratio_multiline to add line breaks after every 2nd word
                print(f"  Processing: Non-classic type with mg values - applying format_ratio_multiline")
                final_ratio = format_ratio_multiline(cleaned_ratio)
            else:
                print(f"  Processing: Edible type without mg values - keeping as-is")
                final_ratio = cleaned_ratio
        else:
            # For other types, keep as-is
            print(f"  Processing: Other type - keeping as-is")
            final_ratio = cleaned_ratio
        
        return final_ratio
    
    # Test cases
    test_cases = [
        {
            'name': 'Concentrate with mg values',
            'record': {
                'Ratio': '230mg CBD 50mg THC 10mg CBG 10mg CBN',
                'ProductType': 'concentrate'
            }
        },
        {
            'name': 'Edible with mg values',
            'record': {
                'Ratio': '100mg THC 200mg CBD',
                'ProductType': 'edible (solid)'
            }
        },
        {
            'name': 'Flower without mg values',
            'record': {
                'Ratio': '1:1:1:1',
                'ProductType': 'flower'
            }
        },
        {
            'name': 'Unknown type with mg values',
            'record': {
                'Ratio': '50mg THC 100mg CBD',
                'ProductType': 'unknown'
            }
        },
        {
            'name': 'Non-classic type with mg values',
            'record': {
                'Ratio': '230mg CBD 50mg THC 10mg CBG 10mg CBN',
                'ProductType': 'tincture'
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['name']}")
        print("-" * 40)
        
        final_ratio = simulate_template_processing(test_case['record'])
        
        print(f"  Final ratio: '{final_ratio}'")
        
        if '\n' in final_ratio:
            print(f"  ✅ Line breaks found in final ratio")
            lines = final_ratio.split('\n')
            print(f"  Split into {len(lines)} lines:")
            for j, line in enumerate(lines, 1):
                print(f"    Line {j}: '{line}'")
        else:
            print(f"  ❌ No line breaks in final ratio")
        
        print()
    
    return True

if __name__ == "__main__":
    test_template_ratio_processing() 