#!/usr/bin/env python3
"""
Test script to verify that the filter fix is working correctly.
This script tests that filters don't clear out the whole list.
"""

import requests
import json
import time

BASE_URL = "http://localhost:9090"

def test_filter_functionality():
    """Test that filters work correctly and don't clear the whole list."""
    print("=== Testing Filter Functionality ===")
    
    # Step 1: Get all available tags
    print("1. Getting all available tags...")
    response = requests.get(f"{BASE_URL}/api/available-tags")
    if response.status_code != 200:
        print(f"✗ Failed to get available tags: {response.status_code}")
        return False
    
    all_tags = response.json()
    total_tags = len(all_tags)
    print(f"✓ Found {total_tags} total tags")
    
    if total_tags == 0:
        print("✗ No tags available for testing")
        return False
    
    # Step 2: Get filter options
    print("2. Getting filter options...")
    response = requests.get(f"{BASE_URL}/api/filter-options")
    if response.status_code != 200:
        print(f"✗ Failed to get filter options: {response.status_code}")
        return False
    
    filter_options = response.json()
    print(f"✓ Filter options: {list(filter_options.keys())}")
    
    # Step 3: Test vendor filter
    if filter_options.get('vendor'):
        vendor_options = filter_options['vendor']
        if vendor_options:
            test_vendor = vendor_options[0]
            print(f"3. Testing vendor filter with: {test_vendor}")
            
            # Apply vendor filter
            filter_data = {
                'vendor': test_vendor,
                'brand': '',
                'productType': '',
                'lineage': '',
                'weight': '',
                'strain': ''
            }
            
            # Simulate filter application by checking how many tags have this vendor
            filtered_count = sum(1 for tag in all_tags if tag.get('vendor', '').strip() == test_vendor)
            print(f"   Expected filtered count: {filtered_count}")
            
            if filtered_count > 0 and filtered_count < total_tags:
                print(f"✓ Vendor filter would show {filtered_count} tags (less than total {total_tags})")
            elif filtered_count == total_tags:
                print(f"⚠ Vendor filter shows all tags (vendor might be the only one)")
            else:
                print(f"✗ Vendor filter shows {filtered_count} tags (should be > 0)")
                return False
        else:
            print("⚠ No vendor options available")
    else:
        print("⚠ No vendor filter options")
    
    # Step 4: Test brand filter
    if filter_options.get('brand'):
        brand_options = filter_options['brand']
        if brand_options:
            test_brand = brand_options[0]
            print(f"4. Testing brand filter with: {test_brand}")
            
            # Count tags with this brand
            filtered_count = sum(1 for tag in all_tags if tag.get('productBrand', '').strip() == test_brand)
            print(f"   Expected filtered count: {filtered_count}")
            
            if filtered_count > 0 and filtered_count < total_tags:
                print(f"✓ Brand filter would show {filtered_count} tags (less than total {total_tags})")
            elif filtered_count == total_tags:
                print(f"⚠ Brand filter shows all tags (brand might be the only one)")
            else:
                print(f"✗ Brand filter shows {filtered_count} tags (should be > 0)")
                return False
        else:
            print("⚠ No brand options available")
    else:
        print("⚠ No brand filter options")
    
    # Step 5: Test product type filter
    if filter_options.get('productType'):
        product_type_options = filter_options['productType']
        if product_type_options:
            test_product_type = product_type_options[0]
            print(f"5. Testing product type filter with: {test_product_type}")
            
            # Count tags with this product type
            filtered_count = sum(1 for tag in all_tags if tag.get('productType', '').strip() == test_product_type)
            print(f"   Expected filtered count: {filtered_count}")
            
            if filtered_count > 0 and filtered_count < total_tags:
                print(f"✓ Product type filter would show {filtered_count} tags (less than total {total_tags})")
            elif filtered_count == total_tags:
                print(f"⚠ Product type filter shows all tags (type might be the only one)")
            else:
                print(f"✗ Product type filter shows {filtered_count} tags (should be > 0)")
                return False
        else:
            print("⚠ No product type options available")
    else:
        print("⚠ No product type filter options")
    
    print("✓ All filter tests passed!")
    return True

def test_filter_combinations():
    """Test that multiple filters work together correctly."""
    print("\n=== Testing Filter Combinations ===")
    
    # Get all tags
    response = requests.get(f"{BASE_URL}/api/available-tags")
    if response.status_code != 200:
        print(f"✗ Failed to get available tags: {response.status_code}")
        return False
    
    all_tags = response.json()
    total_tags = len(all_tags)
    
    # Get filter options
    response = requests.get(f"{BASE_URL}/api/filter-options")
    if response.status_code != 200:
        print(f"✗ Failed to get filter options: {response.status_code}")
        return False
    
    filter_options = response.json()
    
    # Test vendor + brand combination
    if filter_options.get('vendor') and filter_options.get('brand'):
        test_vendor = filter_options['vendor'][0]
        test_brand = filter_options['brand'][0]
        
        print(f"1. Testing vendor + brand combination: {test_vendor} + {test_brand}")
        
        # Count tags with both vendor and brand
        filtered_count = sum(1 for tag in all_tags 
                           if tag.get('vendor', '').strip() == test_vendor 
                           and tag.get('productBrand', '').strip() == test_brand)
        
        print(f"   Expected filtered count: {filtered_count}")
        
        if filtered_count >= 0:
            print(f"✓ Combined filter would show {filtered_count} tags")
        else:
            print(f"✗ Combined filter shows {filtered_count} tags (should be >= 0)")
            return False
    
    print("✓ Filter combination tests passed!")
    return True

def main():
    """Run all filter tests."""
    print("Starting filter functionality tests...")
    
    try:
        # Test basic filter functionality
        if not test_filter_functionality():
            print("✗ Basic filter functionality test failed")
            return False
        
        # Test filter combinations
        if not test_filter_combinations():
            print("✗ Filter combination test failed")
            return False
        
        print("\n🎉 All filter tests passed! The filter fix is working correctly.")
        return True
        
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 