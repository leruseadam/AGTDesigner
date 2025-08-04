#!/usr/bin/env python3

import requests
import json
import time
import os

def test_descandweight_fix_final():
    """Test the final DescAndWeight field fix to ensure it shows the correct format."""
    
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
        else:
            print(f"✗ Upload failed: {response.status_code}")
            return
        
        # Wait for processing
        print("Step 2: Waiting for processing...")
        time.sleep(5)
        
        # Check upload status
        status_response = requests.get('http://127.0.0.1:9090/api/upload-status')
        if status_response.status_code == 200:
            status = status_response.json()
            print(f"Upload status: {status}")
        
        # Test the available tags
        print("Step 3: Testing available tags...")
        response = requests.get('http://127.0.0.1:9090/api/available-tags')
        
        if response.status_code == 200:
            tags = response.json()
            print(f"Found {len(tags)} tags")
            
            # Look for Hustler's Ambition products
            hustler_tags = [tag for tag in tags if 'Hustler' in tag.get('Product Name*', '')]
            print(f"Found {len(hustler_tags)} Hustler products")
            
            # Check the first few Hustler products
            for i, tag in enumerate(hustler_tags[:5]):
                product_name = tag.get('Product Name*', '')
                desc_and_weight = tag.get('DescAndWeight', '')
                description = tag.get('Description', '')
                weight_units = tag.get('WeightWithUnits', '')
                
                print(f"\n{i+1}: {product_name}")
                print(f"  Description: {description}")
                print(f"  WeightWithUnits: {weight_units}")
                print(f"  DescAndWeight: {desc_and_weight}")
                
                # Check if DescAndWeight format is correct
                if desc_and_weight and ' - ' in desc_and_weight:
                    print(f"  ✓ DescAndWeight contains hyphen separator")
                else:
                    print(f"  ⚠ DescAndWeight format may need adjustment")
            
            # Check for the specific product mentioned in the issue
            target_product = "Hustler's Ambition - Wax - Acapulco Gold (S) - 1g"
            target_tag = None
            
            for tag in tags:
                if tag.get('Product Name*', '') == target_product:
                    target_tag = tag
                    break
            
            if target_tag:
                print(f"\n✓ Found target product: {target_product}")
                print(f"  DescAndWeight: {target_tag.get('DescAndWeight', 'N/A')}")
                
                # Check if it matches the expected format
                expected_format = "Acapulco Gold Wax - 1g"
                actual_format = target_tag.get('DescAndWeight', '')
                
                if expected_format in actual_format or "Acapulco Gold" in actual_format:
                    print(f"  ✓ SUCCESS: DescAndWeight format is correct!")
                else:
                    print(f"  ❌ FAILURE: Expected format like '{expected_format}', got '{actual_format}'")
            else:
                print(f"\n❌ Target product not found: {target_product}")
                
        else:
            print(f"✗ Failed to get available tags: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_descandweight_fix_final() 