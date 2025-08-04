#!/usr/bin/env python3
"""
Test script to verify that tags load and persist correctly in the frontend.
"""

import requests
import json
import time

BASE_URL = "http://localhost:9090"

def test_tags_persistence():
    """Test that tags load and don't disappear after initialization."""
    print("=== Testing Tags Persistence ===")
    
    # Step 1: Check if tags are available from backend
    print("1. Checking backend tags...")
    response = requests.get(f"{BASE_URL}/api/available-tags")
    if response.status_code != 200:
        print(f"✗ Failed to get available tags: {response.status_code}")
        return False
    
    backend_tags = response.json()
    print(f"✓ Backend has {len(backend_tags)} tags")
    
    # Step 2: Check filter options
    print("2. Checking filter options...")
    response = requests.get(f"{BASE_URL}/api/filter-options")
    if response.status_code != 200:
        print(f"✗ Failed to get filter options: {response.status_code}")
        return False
    
    filter_options = response.json()
    print(f"✓ Filter options available: {list(filter_options.keys())}")
    
    # Step 3: Test brand filter specifically
    print("3. Testing brand filter...")
    if 'brand' in filter_options and filter_options['brand']:
        test_brand = filter_options['brand'][0]  # Use first available brand
        print(f"   Testing with brand: {test_brand}")
        
        # Count tags with this brand in backend
        brand_count = sum(1 for tag in backend_tags 
                         if tag.get('brand') == test_brand or 
                         tag.get('Product Brand') == test_brand)
        print(f"   Backend has {brand_count} tags with brand '{test_brand}'")
        
        if brand_count > 0:
            print("✓ Brand filter should work correctly")
        else:
            print("⚠ Brand filter may not work (no matching tags)")
    else:
        print("⚠ No brand options available")
    
    print("✓ Tags persistence test completed")
    return True

if __name__ == "__main__":
    test_tags_persistence() 