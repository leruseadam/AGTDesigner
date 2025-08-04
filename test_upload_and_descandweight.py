#!/usr/bin/env python3

import requests
import json
import time
import os

def test_upload_and_descandweight():
    """Test uploading a file and then checking the DescAndWeight field format."""
    
    # File to upload
    file_path = "uploads/A Greener Today - Bothell_inventory_07-13-2025  5_18 AM.xlsx"
    
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return
    
    try:
        print("Step 1: Uploading file...")
        
        # Upload the file
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            response = requests.post('http://127.0.0.1:9090/upload', files=files)
        
        if response.status_code == 200:
            print("✓ File uploaded successfully")
            
            # Wait for processing to complete
            print("Step 2: Waiting for processing to complete...")
            max_wait = 30  # 30 seconds max
            wait_time = 0
            
            while wait_time < max_wait:
                status_response = requests.get('http://127.0.0.1:9090/api/upload-status')
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    if status_data.get('status') == 'done':
                        print("✓ Processing completed")
                        break
                    elif status_data.get('status') == 'error':
                        print(f"❌ Processing failed: {status_data.get('message', 'Unknown error')}")
                        return
                    else:
                        print(f"Processing status: {status_data.get('status', 'unknown')}")
                
                time.sleep(2)
                wait_time += 2
            
            if wait_time >= max_wait:
                print("❌ Processing timed out")
                return
            
            # Test the DescAndWeight field
            print("Step 3: Testing DescAndWeight field...")
            time.sleep(2)  # Give a moment for the data to be available
            
            tags_response = requests.get('http://127.0.0.1:9090/api/available-tags')
            
            if tags_response.status_code == 200:
                tags = tags_response.json()
                print(f"Found {len(tags)} tags")
                
                # Look for products with the expected format
                target_products = [
                    "Hustler's Ambition - Wax - Acapulco Gold (S) - 1g",
                    "Hustler's Ambition - Wax - Blue Dream (S) - 1g",
                    "Hustler's Ambition - Wax - Forbidden Fruit (I) - 1g"
                ]
                
                found_targets = []
                
                for i, tag in enumerate(tags[:20]):  # Check first 20 tags
                    product_name = tag.get('Product Name*', '')
                    desc_and_weight = tag.get('DescAndWeight', '')
                    
                    print(f"\nTag {i+1}:")
                    print(f"  Product Name: {product_name}")
                    print(f"  DescAndWeight: {desc_and_weight}")
                    
                    # Check if this is one of our target products
                    for target in target_products:
                        if target in product_name:
                            found_targets.append((target, desc_and_weight))
                            print(f"  ✓ FOUND TARGET PRODUCT!")
                            break
                
                print(f"\nSummary:")
                print(f"  Target products found: {len(found_targets)}")
                
                for target, desc_and_weight in found_targets:
                    print(f"  Target: {target}")
                    print(f"  DescAndWeight: {desc_and_weight}")
                    
                    # Check if the format is correct
                    if ' - ' in desc_and_weight and ('Wax' in desc_and_weight or 'Flower' in desc_and_weight):
                        print(f"  ✓ Format looks correct")
                    else:
                        print(f"  ❌ Format may be incorrect")
                
                # Check overall format patterns
                correct_formats = 0
                for tag in tags:
                    desc_and_weight = tag.get('DescAndWeight', '')
                    if ' - ' in desc_and_weight and ('Wax' in desc_and_weight or 'Flower' in desc_and_weight or 'Concentrate' in desc_and_weight):
                        correct_formats += 1
                
                print(f"\nOverall Results:")
                print(f"  Tags with correct format: {correct_formats}/{len(tags)}")
                
                if correct_formats > 0:
                    print("  ✓ SUCCESS: DescAndWeight field is now using the correct format!")
                else:
                    print("  ❌ ISSUE: No tags found with the correct format")
                    
            else:
                print(f"Error getting tags: HTTP {tags_response.status_code}")
                print(f"Response: {tags_response.text}")
                
        else:
            print(f"Error uploading file: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server. Make sure the app is running on http://127.0.0.1:9090")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_upload_and_descandweight() 