#!/usr/bin/env python3


"""
Test script to demonstrate JSON matching with items that don't exist in the dataset.
This shows how the system can create new entries for JSON items not found in the Excel data.
"""

import requests
import json
import base64

def test_json_matching_with_new_items():
    """Test JSON matching with items that don't exist in the dataset."""
    
    # Create JSON data with items that exist and items that don't exist
    json_data = {
        'inventory_transfer_items': [
            # Item that exists in the dataset
            {
                'product_name': 'Core Reactor Quartz Banger',
                'brand': 'Test Brand',
                'vendor': 'Test Vendor',
                'quantity': 1,
                'unit_of_measure': 'each'
            },
            # Item that exists in the dataset
            {
                'product_name': 'Terp Slurper Quartz Banger',
                'brand': 'Test Brand',
                'vendor': 'Test Vendor',
                'quantity': 2,
                'unit_of_measure': 'each'
            },
            # Item that DEFINITELY doesn't exist in the dataset (new item)
            {
                'product_name': 'Super Ultra Mega New Product 2025',
                'brand': 'New Brand',
                'vendor': 'New Vendor',
                'quantity': 5,
                'unit_of_measure': 'each',
                'price': '$45.99',
                'thc': 25.5,
                'cbd': 0.0
            },
            # Another item that DEFINITELY doesn't exist
            {
                'product_name': 'Completely Unique Product Name XYZ123',
                'brand': 'Another Brand',
                'vendor': 'Another Vendor',
                'quantity': 3,
                'unit_of_measure': 'each',
                'price': '$32.50',
                'thc': 18.2,
                'cbd': 2.1
            }
        ]
    }
    
    # Convert to data URL
    json_str = json.dumps(json_data)
    data_url = f"data:application/json;base64,{base64.b64encode(json_str.encode()).decode()}"
    
    test_data = {
        'url': data_url
    }
    
    try:
        # Make request to the JSON matching endpoint
        response = requests.post('http://127.0.0.1:5001/api/json-match', 
                               json=test_data, 
                               timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            
            print("=== JSON Matching with New Items Test ===")
            print(f"Success: {result.get('success', False)}")
            print(f"Matched count: {result.get('matched_count', 0)}")
            print(f"Available tags count: {len(result.get('available_tags', []))}")
            print(f"JSON matched tags count: {len(result.get('json_matched_tags', []))}")
            
            print("\n📋 Available Tags (should include both existing and new items):")
            available_tags = result.get('available_tags', [])
            for i, tag in enumerate(available_tags, 1):
                product_name = tag.get('Product Name*', tag.get('ProductName', 'Unknown'))
                source = tag.get('Source', 'Unknown')
                vendor = tag.get('Vendor', 'Unknown')
                price = tag.get('Price', 'Unknown')
                print(f"  {i}. {product_name}")
                print(f"     Source: {source}")
                print(f"     Vendor: {vendor}")
                print(f"     Price: {price}")
                print()
            
            print("\n🔍 Analysis:")
            existing_items = [tag for tag in available_tags if tag.get('Source') == 'JSON Match']
            new_items = [tag for tag in available_tags if tag.get('Source') == 'JSON Match - New Item']
            
            print(f"  • Existing items found: {len(existing_items)}")
            print(f"  • New items created: {len(new_items)}")
            print(f"  • Total items in Available Tags: {len(available_tags)}")
            
            if new_items:
                print("\n✅ SUCCESS: New items were created for JSON items not found in the dataset!")
                print("This means the system can handle JSON inventory that includes products not in the Excel file.")
            else:
                print("\n⚠️  NOTE: No new items were created. This might mean:")
                print("   - All JSON items were found in the dataset")
                print("   - The new item creation logic needs to be implemented")
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_json_matching_with_new_items() 