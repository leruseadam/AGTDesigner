#!/usr/bin/env python3
"""
Test JSON matching with local file data.
"""

import requests
import json
import os

def test_json_with_file():
    """Test JSON matching with local file data."""
    
    print("🧪 Testing JSON Matching with Local File")
    print("=" * 50)
    
    base_url = "http://localhost:5002"
    
    try:
        # Read the test JSON file
        test_file = "test_products.json"
        if not os.path.exists(test_file):
            print(f"❌ Test file {test_file} not found")
            return False
            
        with open(test_file, 'r') as f:
            test_data = json.load(f)
        
        print(f"✅ Loaded test data with {len(test_data.get('inventory_transfer_items', []))} products")
        
        # Check initial state
        print("\n1. Initial state...")
        available_response = requests.get(f"{base_url}/api/available-tags")
        initial_available = available_response.json() if isinstance(available_response.json(), list) else []
        print(f"   Available tags: {len(initial_available)}")
        
        # Test JSON matching with the file data
        print("\n2. Testing JSON matching with file data...")
        
        # Create a data URL from the file content
        import base64
        json_str = json.dumps(test_data)
        json_bytes = json_str.encode('utf-8')
        json_b64 = base64.b64encode(json_bytes).decode('utf-8')
        data_url = f"data:application/json;base64,{json_b64}"
        
        print(f"   Using data URL with {len(json_bytes)} bytes")
        
        json_response = requests.post(f"{base_url}/api/json-match", 
                                    json={"url": data_url})
        
        if json_response.status_code == 200:
            data = json_response.json()
            print(f"   ✅ JSON matching successful")
            print(f"   Matched count: {data.get('matched_count', 0)}")
            print(f"   Message: {data.get('message', 'No message')}")
            print(f"   Available tags: {len(data.get('available_tags', []))}")
            print(f"   JSON matched tags: {len(data.get('json_matched_tags', []))}")
            
            # Check if available tags were updated
            print("\n3. Checking results...")
            available_response = requests.get(f"{base_url}/api/available-tags")
            post_available = available_response.json() if isinstance(available_response.json(), list) else []
            
            print(f"   Post-match available: {len(post_available)}")
            print(f"   Available tags changed: {len(post_available) != len(initial_available)}")
            
            # Show some sample matched products
            if data.get('json_matched_tags'):
                print(f"\n4. Sample matched products:")
                for i, product in enumerate(data['json_matched_tags'][:3]):
                    name = product.get('Product Name*', product.get('ProductName', 'Unknown'))
                    brand = product.get('Product Brand', 'Unknown')
                    strain = product.get('Product Strain', 'Unknown')
                    print(f"   {i+1}. {name} (Brand: {brand}, Strain: {strain})")
            
            success = len(data.get('json_matched_tags', [])) > 0
            print(f"\n   ✅ Test {'PASSED' if success else 'FAILED'}")
            return success
        else:
            print(f"   ❌ JSON matching failed: {json_response.status_code}")
            try:
                error_data = json_response.json()
                print(f"   Error details: {error_data}")
            except:
                print(f"   Response text: {json_response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_json_with_file()
