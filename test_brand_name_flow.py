#!/usr/bin/env python3
"""
Test script to debug the brand name flow from UI selection to label generation.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_brand_name_flow():
    """Test the complete brand name flow from UI to label generation."""
    
    print("=== Testing Brand Name Flow (with Fallback) ===")
    
    # Test cases with different scenarios
    test_cases = [
        {
            'name': 'White Widow CBG',
            'product_brand': '',  # Empty brand field
            'vendor': 'Test Vendor',
            'expected_brand': 'Test Vendor'  # Should fall back to vendor
        },
        {
            'name': 'White Widow CBG Platinum Distillate',
            'product_brand': '',  # Empty brand field
            'vendor': 'Test Vendor',
            'expected_brand': 'Platinum Distillate'  # Should extract from product name
        },
        {
            'name': 'Blue Dream',
            'product_brand': 'Premium Brand',  # Has brand field
            'vendor': 'Test Vendor',
            'expected_brand': 'Premium Brand'  # Should use brand field
        },
        {
            'name': 'OG Kush Gold Live Resin',
            'product_brand': '',  # Empty brand field
            'vendor': 'Test Vendor',
            'expected_brand': 'Gold Live'  # Should extract from product name
        }
    ]
    
    # Simulate the excel processor get_selected_records method with fallback
    def simulate_get_selected_records_with_fallback(selected_tag_names, template_type):
        """Simulate how get_selected_records processes the data with fallback."""
        
        print(f"\n2. Processing in get_selected_records (with fallback):")
        print(f"   Selected tag names: {selected_tag_names}")
        print(f"   Template type: {template_type}")
        
        # Process each test case
        processed_records = []
        for test_case in test_cases:
            if test_case['name'] in selected_tag_names:
                print(f"\n   Processing record: {test_case['name']}")
                
                # Get product brand with fallback logic
                product_brand = test_case['product_brand'].upper()
                
                # If no brand name, try to extract from product name
                if not product_brand or product_brand.strip() == '':
                    product_name = test_case['name']
                    if product_name:
                        # Look for common brand patterns in product name
                        import re
                        brand_patterns = [
                            r'(.+?)\s+(Platinum|Premium|Gold|Silver|Elite|Select|Reserve|Craft|Artisan|Boutique|Signature|Limited|Exclusive|Private|Custom|Special|Deluxe|Ultra|Super|Mega|Max|Pro|Plus|X)\s+(Distillate|Extract|Concentrate|Oil|Tincture|Gel|Capsule|Edible|Gummy|Chocolate|Beverage|Topical|Cream|Lotion|Salve|Balm|Spray|Drops|Syrup|Sauce|Dab|Wax|Shatter|Live|Rosin|Resin|Kief|Hash|Bubble|Ice|Water|Solventless|Full\s+Spectrum|Broad\s+Spectrum|Isolate|Terpene|Terpenes|Terp|Terps)',
                            r'(.+?)\s+(Distillate|Extract|Concentrate|Oil|Tincture|Gel|Capsule|Edible|Gummy|Chocolate|Beverage|Topical|Cream|Lotion|Salve|Balm|Spray|Drops|Syrup|Sauce|Dab|Wax|Shatter|Live|Rosin|Resin|Kief|Hash|Bubble|Ice|Water|Solventless|Full\s+Spectrum|Broad\s+Spectrum|Isolate|Terpene|Terpenes|Terp|Terps)',
                            r'(.+?)\s+(Platinum|Premium|Gold|Silver|Elite|Select|Reserve|Craft|Artisan|Boutique|Signature|Limited|Exclusive|Private|Custom|Special|Deluxe|Ultra|Super|Mega|Max|Pro|Plus|X)',
                        ]
                        
                        for pattern in brand_patterns:
                            match = re.search(pattern, product_name, re.IGNORECASE)
                            if match:
                                # Extract the brand part (everything after the product name)
                                full_match = match.group(0)
                                product_part = match.group(1).strip()
                                brand_part = full_match[len(product_part):].strip()
                                if brand_part:
                                    product_brand = brand_part.upper()
                                    print(f"     → Extracted brand from product name: {product_brand}")
                                    break
                    
                    # If still no brand, try vendor as fallback
                    if not product_brand or product_brand.strip() == '':
                        vendor = test_case['vendor']
                        if vendor and vendor.strip() != '':
                            product_brand = vendor.strip().upper()
                            print(f"     → Using vendor as brand fallback: {product_brand}")
                
                print(f"     Raw Product Brand: {repr(test_case['product_brand'])}")
                print(f"     Final Product Brand: {repr(product_brand)}")
                
                # Simulate the processed record structure
                processed_record = {
                    'ProductName': test_case['name'],
                    'Product Brand': product_brand,
                    'ProductType': 'vape cartridge',
                    'Price': '35',
                    'Lineage': 'HYBRID',
                    'DOH': 'YES',
                    'Vendor': test_case['vendor']
                }
                
                processed_records.append(processed_record)
                print(f"     Final processed record: {processed_record}")
        
        return processed_records
    
    # Simulate the template processor _build_label_context method
    def simulate_build_label_context(record, template_type):
        """Simulate how _build_label_context processes the record."""
        
        print(f"\n3. Processing in _build_label_context:")
        print(f"   Record: {record}")
        
        # Get product brand (same logic as template processor)
        product_brand = record.get('ProductBrand') or record.get('Product Brand', '')
        print(f"     Raw Product Brand: {repr(product_brand)}")
        
        if product_brand:
            # Clean the brand data
            product_type = record.get('ProductType', '').strip().lower()
            classic_types = ["flower", "pre-roll", "infused pre-roll", "concentrate", "solventless concentrate", "vape cartridge", "rso/co2 tankers"]
            
            if product_type in classic_types:
                print(f"     → Using PRODUCTBRAND marker (classic type)")
                final_brand = f"PRODUCTBRAND_START{product_brand}PRODUCTBRAND_END"
            else:
                print(f"     → Using PRODUCTBRAND_CENTER marker (non-classic type)")
                final_brand = f"PRODUCTBRAND_CENTER_START{product_brand}PRODUCTBRAND_CENTER_END"
        else:
            print(f"     → No brand name found!")
            final_brand = ""
        
        print(f"     Final brand for template: {repr(final_brand)}")
        return final_brand
    
    # Test the complete flow
    selected_tag_names = ['White Widow CBG', 'White Widow CBG Platinum Distillate', 'Blue Dream', 'OG Kush Gold Live Resin']
    
    # Step 1: Get selected records with fallback
    records = simulate_get_selected_records_with_fallback(selected_tag_names, 'vertical')
    
    # Step 2: Process each record through template processor
    for record in records:
        final_brand = simulate_build_label_context(record, 'vertical')
        print(f"\n4. Final Result:")
        print(f"   Product: {record['ProductName']}")
        print(f"   Brand in template: {final_brand}")
        
        if final_brand:
            print(f"   ✅ Brand name will appear in label")
        else:
            print(f"   ❌ Brand name will NOT appear in label")
    
    print("\n=== Summary ===")
    print("The brand name fallback mechanism should now ensure that:")
    print("1. If Product Brand field is empty, extract brand from product name")
    print("2. If no brand in product name, use vendor name as fallback")
    print("3. Brand names will always appear in labels when available")
    
    return True

if __name__ == "__main__":
    success = test_brand_name_flow()
    sys.exit(0 if success else 1) 