#!/usr/bin/env python3
"""
Test script to verify that DescAndWeight and Price fields are now included
in the available tags API response.
"""

import requests
import json
import time

def test_available_tags_api():
    """Test the available-tags API endpoint to check for DescAndWeight and Price fields."""
    
    print("Testing available-tags API endpoint...")
    
    try:
        # Make request to the available-tags endpoint
        response = requests.get('http://localhost:5000/api/available-tags')
        
        if response.status_code == 200:
            tags = response.json()
            
            if not tags:
                print("No tags returned - this is normal if no file is uploaded")
                return
            
            print(f"Found {len(tags)} tags")
            
            # Check the first few tags for the new fields
            for i, tag in enumerate(tags[:3]):
                print(f"\nTag {i+1}:")
                print(f"  Product Name: {tag.get('Product Name*', 'N/A')}")
                print(f"  DescAndWeight: {tag.get('DescAndWeight', 'MISSING')}")
                print(f"  Price: {tag.get('Price', 'MISSING')}")
                print(f"  Description: {tag.get('Description', 'N/A')}")
                print(f"  Weight*: {tag.get('Weight*', 'N/A')}")
                print(f"  Weight Unit*: {tag.get('Weight Unit* (grams/gm or ounces/oz)', 'N/A')}")
                
                # Check if DescAndWeight is properly formatted
                if tag.get('DescAndWeight'):
                    if ' - ' in tag.get('DescAndWeight', ''):
                        print(f"  ✓ DescAndWeight contains hyphen separator")
                    else:
                        print(f"  ⚠ DescAndWeight format may need adjustment")
                else:
                    print(f"  ❌ DescAndWeight is missing")
                
                # Check if Price is present
                if tag.get('Price'):
                    print(f"  ✓ Price field is present")
                else:
                    print(f"  ❌ Price field is missing")
            
            # Check if any tags have the new fields
            tags_with_desc_weight = [t for t in tags if t.get('DescAndWeight')]
            tags_with_price = [t for t in tags if t.get('Price')]
            
            print(f"\nSummary:")
            print(f"  Tags with DescAndWeight: {len(tags_with_desc_weight)}/{len(tags)}")
            print(f"  Tags with Price: {len(tags_with_price)}/{len(tags)}")
            
            if tags_with_desc_weight and tags_with_price:
                print("  ✓ SUCCESS: Both DescAndWeight and Price fields are being included!")
            else:
                print("  ❌ ISSUE: Some fields are still missing")
                
        else:
            print(f"Error: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server. Make sure the app is running on localhost:5000")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_available_tags_api() 