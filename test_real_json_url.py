#!/usr/bin/env python3
"""
Test script to test the actual JSON URL provided by the user.
"""

import requests
import json
import time

def test_real_json_url():
    """Test the actual JSON URL provided by the user."""
    base_url = 'http://127.0.0.1:9090'
    json_url = 'https://files.cultivera.com/435553542D57533130383235/Interop/25/16/3EGQ3216P7YSVJCF/Cultivera_ORD-5430_422044.json'
    
    print("🧪 Testing Real JSON URL")
    print("=" * 50)
    print(f"URL: {json_url}")
    
    # Step 1: Check if server is running
    try:
        response = requests.get(f'{base_url}/api/status', timeout=5)
        if response.status_code != 200:
            print("❌ Server not responding properly")
            return False
        print("✅ Server is running")
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return False
    
    # Step 2: Get initial state
    print("\n2. Getting initial state...")
    try:
        response = requests.get(f'{base_url}/api/available-tags')
        if response.status_code != 200:
            print("❌ Failed to get available tags")
            return False
        
        available_tags = response.json()
        initial_available_count = len(available_tags) if isinstance(available_tags, list) else 0
        
        # Get selected tags
        response = requests.get(f'{base_url}/api/selected-tags')
        if response.status_code == 200:
            selected_tags = response.json()
            initial_selected_count = len(selected_tags) if isinstance(selected_tags, list) else 0
        else:
            initial_selected_count = 0
        
        print(f"✅ Initial state:")
        print(f"   Available tags: {initial_available_count}")
        print(f"   Selected tags: {initial_selected_count}")
        
    except Exception as e:
        print(f"❌ Error getting initial state: {e}")
        return False
    
    # Step 3: Test JSON matching with the real URL
    print("\n3. Testing JSON matching with real URL...")
    
    try:
        response = requests.post(f'{base_url}/api/json-match', 
                               json={'url': json_url},
                               headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ JSON match response:")
            print(f"   Success: {result.get('success', False)}")
            print(f"   Matched count: {result.get('matched_count', 0)}")
            print(f"   Matched names: {len(result.get('matched_names', []))}")
            print(f"   Available tags: {len(result.get('available_tags', []))}")
            print(f"   Selected tags: {len(result.get('selected_tags', []))}")
            
            # Check if selected tags are properly populated
            selected_tags = result.get('selected_tags', [])
            if selected_tags:
                print(f"✅ Selected tags populated: {len(selected_tags)} items")
                print("   First few matched products:")
                for i, tag in enumerate(selected_tags[:5]):  # Show first 5
                    product_name = tag.get('Product Name*', 'Unknown')
                    print(f"   {i+1}. {product_name}")
                if len(selected_tags) > 5:
                    print(f"   ... and {len(selected_tags) - 5} more")
            else:
                print("⚠️  No selected tags in response")
                
            # Show some matched names if available
            matched_names = result.get('matched_names', [])
            if matched_names:
                print(f"\n   Matched product names:")
                for i, name in enumerate(matched_names[:5]):
                    print(f"   {i+1}. {name}")
                if len(matched_names) > 5:
                    print(f"   ... and {len(matched_names) - 5} more")
                    
        else:
            error_data = response.json()
            print(f"❌ JSON matching failed: {error_data.get('error', 'Unknown error')}")
            return False
        
    except Exception as e:
        print(f"❌ Error testing JSON match: {e}")
        return False
    
    # Step 4: Verify the selected tags are now in the system
    print("\n4. Verifying selected tags are in the system...")
    try:
        time.sleep(1)  # Give the system time to update
        response = requests.get(f'{base_url}/api/selected-tags')
        if response.status_code == 200:
            final_selected = response.json()
            final_selected_count = len(final_selected) if isinstance(final_selected, list) else 0
            print(f"✅ Final selected tags: {final_selected_count} items")
            
            if final_selected_count > initial_selected_count:
                print(f"✅ Selected tags increased from {initial_selected_count} to {final_selected_count}")
                print("✅ JSON matching successfully added items to Selected Output")
                return True
            elif final_selected_count == initial_selected_count:
                print("⚠️  Selected tags count unchanged")
                return True
            else:
                print(f"❌ Selected tags decreased from {initial_selected_count} to {final_selected_count}")
                return False
        else:
            print("❌ Failed to get final selected tags")
            return False
    except Exception as e:
        print(f"❌ Error verifying final state: {e}")
        return False

if __name__ == "__main__":
    test_real_json_url() 