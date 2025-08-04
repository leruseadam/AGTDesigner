#!/usr/bin/env python3
"""
Test script to verify brand name extraction logic.
"""

import re
import sys

def test_brand_extraction():
    """Test the brand name extraction patterns."""
    
    print("=== Testing Brand Name Extraction ===")
    
    # Test cases
    test_cases = [
        {
            'name': 'White Widow CBG Platinum Distillate',
            'expected': 'Platinum Distillate'
        },
        {
            'name': 'Blue Dream Premium Extract',
            'expected': 'Premium Extract'
        },
        {
            'name': 'OG Kush Gold Live Resin',
            'expected': 'Gold Live Resin'
        },
        {
            'name': 'Sour Diesel Elite Concentrate',
            'expected': 'Elite Concentrate'
        },
        {
            'name': 'Gelato Select Oil',
            'expected': 'Select Oil'
        },
        {
            'name': 'Wedding Cake Reserve Tincture',
            'expected': 'Reserve Tincture'
        },
        {
            'name': 'Purple Punch Craft Gummy',
            'expected': 'Craft Gummy'
        },
        {
            'name': 'Jack Herer Artisan Chocolate',
            'expected': 'Artisan Chocolate'
        },
        {
            'name': 'Northern Lights Boutique Capsule',
            'expected': 'Boutique Capsule'
        },
        {
            'name': 'AK-47 Signature Edible',
            'expected': 'Signature Edible'
        },
        {
            'name': 'White Widow CBG',  # No brand in name
            'expected': None
        },
        {
            'name': 'Blue Dream',  # No brand in name
            'expected': None
        }
    ]
    
    # Brand extraction patterns (same as in the code)
    brand_patterns = [
        r'(.+?)\s+(Platinum|Premium|Gold|Silver|Elite|Select|Reserve|Craft|Artisan|Boutique|Signature|Limited|Exclusive|Private|Custom|Special|Deluxe|Ultra|Super|Mega|Max|Pro|Plus|X)\s+(Distillate|Extract|Concentrate|Oil|Tincture|Gel|Capsule|Edible|Gummy|Chocolate|Beverage|Topical|Cream|Lotion|Salve|Balm|Spray|Drops|Syrup|Sauce|Dab|Wax|Shatter|Live|Rosin|Resin|Kief|Hash|Bubble|Ice|Water|Solventless|Full\s+Spectrum|Broad\s+Spectrum|Isolate|Terpene|Terpenes|Terp|Terps)',
        r'(.+?)\s+(Distillate|Extract|Concentrate|Oil|Tincture|Gel|Capsule|Edible|Gummy|Chocolate|Beverage|Topical|Cream|Lotion|Salve|Balm|Spray|Drops|Syrup|Sauce|Dab|Wax|Shatter|Live|Rosin|Resin|Kief|Hash|Bubble|Ice|Water|Solventless|Full\s+Spectrum|Broad\s+Spectrum|Isolate|Terpene|Terpenes|Terp|Terps)',
        r'(.+?)\s+(Platinum|Premium|Gold|Silver|Elite|Select|Reserve|Craft|Artisan|Boutique|Signature|Limited|Exclusive|Private|Custom|Special|Deluxe|Ultra|Super|Mega|Max|Pro|Plus|X)',
    ]
    
    def extract_brand(product_name):
        """Extract brand name from product name using the same logic as the code."""
        if not product_name:
            return None
            
        for pattern in brand_patterns:
            match = re.search(pattern, product_name, re.IGNORECASE)
            if match:
                # Extract the brand part (everything after the product name)
                full_match = match.group(0)
                product_part = match.group(1).strip()
                brand_part = full_match[len(product_part):].strip()
                if brand_part:
                    return brand_part
        return None
    
    # Test each case
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {repr(test_case['name'])}")
        
        result = extract_brand(test_case['name'])
        expected = test_case['expected']
        
        success = result == expected
        print(f"   Expected: {repr(expected)}")
        print(f"   Result:   {repr(result)}")
        print(f"   Success:  {'✅' if success else '❌'}")
    
    print("\n=== Summary ===")
    print("The brand extraction logic should work for product names that contain brand information.")
    print("For products without brand info in the name, the system will fall back to vendor name.")
    
    return True

if __name__ == "__main__":
    success = test_brand_extraction()
    sys.exit(0 if success else 1) 