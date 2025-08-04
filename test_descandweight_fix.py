#!/usr/bin/env python3

import requests
import json

def test_descandweight_fix():
    """Test the DescAndWeight field fix to ensure it shows the correct format."""
    
    try:
        # Test the available-tags endpoint
        response = requests.get('http://127.0.0.1:9090/api/available-tags')
        
        if response.status_code == 200:
            tags = response.json()
            print(f"Found {len(tags)} tags")
            
            # Look for the specific product we're testing
            target_product = "Hustler's Ambition - Wax - Acapulco Gold (S) - 1g"
            
            for i, tag in enumerate(tags[:10]):  # Check first 10 tags
                product_name = tag.get('Product Name*', '')
                desc_and_weight = tag.get('DescAndWeight', '')
                
                print(f"\nTag {i+1}:")
                print(f"  Product Name: {product_name}")
                print(f"  DescAndWeight: {desc_and_weight}")
                
                # Check if this is our target product
                if target_product in product_name:
                    print(f"  ✓ FOUND TARGET PRODUCT!")
                    print(f"  Expected format: Acapulco Gold Wax - 1g")
                    print(f"  Actual format: {desc_and_weight}")
                    
                    if "Acapulco Gold Wax - 1g" in desc_and_weight:
                        print(f"  ✓ SUCCESS: DescAndWeight format is correct!")
                    else:
                        print(f"  ❌ FAILURE: DescAndWeight format is incorrect")
                        print(f"  Expected: Acapulco Gold Wax - 1g")
                        print(f"  Got: {desc_and_weight}")
            
            # Check if any tags have the new format
            tags_with_correct_format = []
            for tag in tags:
                desc_and_weight = tag.get('DescAndWeight', '')
                if ' - ' in desc_and_weight and ('Wax' in desc_and_weight or 'Flower' in desc_and_weight or 'Concentrate' in desc_and_weight):
                    tags_with_correct_format.append(tag)
            
            print(f"\nSummary:")
            print(f"  Tags with correct format: {len(tags_with_correct_format)}/{len(tags)}")
            
            if tags_with_correct_format:
                print("  ✓ SUCCESS: DescAndWeight field is now using the correct format!")
                print("  Sample correct formats:")
                for tag in tags_with_correct_format[:3]:
                    print(f"    - {tag.get('DescAndWeight', '')}")
            else:
                print("  ❌ ISSUE: No tags found with the correct format")
                
        else:
            print(f"Error: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server. Make sure the app is running on http://127.0.0.1:9090")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_descandweight_fix() 