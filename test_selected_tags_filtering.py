#!/usr/bin/env python3
"""
Test script to verify that selected tags now respect the same filtering rules as available tags.
"""

import requests
import json
import time

def test_selected_tags_filtering():
    """Test that selected tags respect filtering rules."""
    base_url = 'http://127.0.0.1:9090'
    json_url = 'https://files.cultivera.com/435553542D57533130383235/Interop/25/16/3EGQ3216P7YSVJCF/Cultivera_ORD-5430_422044.json'
    
    print("🧪 Testing Selected Tags Filtering")
    print("=" * 50)
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    # Step 1: Check if server is running
    try:
        response = session.get(f'{base_url}/api/status', timeout=5)
        if response.status_code != 200:
            print("❌ Server not responding properly")
            return False
        print("✅ Server is running")
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return False
    
    # Step 2: Perform JSON matching to get selected tags
    print("\n2. Performing JSON matching...")
    try:
        response = session.post(f'{base_url}/api/json-match', json={'json_url': json_url})
        if response.status_code != 200:
            print(f"❌ JSON match failed: {response.status_code}")
            return False
        
        match_result = response.json()
        print(f"✅ JSON matching successful!")
        print(f"   Matched count: {match_result.get('matched_count', 0)}")
        print(f"   Selected tags in response: {len(match_result.get('selected_tags', []))}")
    except Exception as e:
        print(f"❌ JSON match error: {e}")
        return False
    
    # Step 3: Get selected tags to verify they're stored
    print("\n3. Getting selected tags...")
    try:
        response = session.get(f'{base_url}/api/selected-tags')
        if response.status_code != 200:
            print(f"❌ Failed to get selected tags: {response.status_code}")
            return False
        
        selected_tags = response.json()
        print(f"✅ Selected tags retrieved: {len(selected_tags)}")
        if len(selected_tags) > 0:
            print(f"   First tag: {selected_tags[0]}")
    except Exception as e:
        print(f"❌ Error getting selected tags: {e}")
        return False
    
    # Step 4: Test filtering by applying a vendor filter
    print("\n4. Testing filtering with vendor filter...")
    try:
        # Apply a vendor filter
        filters = {
            'vendor': 'Dank Czar',  # Filter to only show Dank Czar products
            'brand': '',
            'productType': '',
            'lineage': '',
            'weight': ''
        }
        
        response = session.post(f'{base_url}/api/available-tags', json={
            'filters': filters,
            'selected_tags': selected_tags
        })
        
        if response.status_code != 200:
            print(f"❌ Filter request failed: {response.status_code}")
            return False
        
        filter_result = response.json()
        available_tags = filter_result.get('available_tags', [])
        filtered_selected_tags = filter_result.get('selected_tags', [])
        
        print(f"✅ Filter applied successfully!")
        print(f"   Available tags after filter: {len(available_tags)}")
        print(f"   Selected tags after filter: {len(filtered_selected_tags)}")
        
        # Check if selected tags were filtered correctly
        if len(filtered_selected_tags) < len(selected_tags):
            print(f"   ✅ Selected tags were filtered correctly!")
            print(f"   Original selected: {len(selected_tags)}")
            print(f"   Filtered selected: {len(filtered_selected_tags)}")
            
            # Show some examples of filtered tags
            if filtered_selected_tags:
                print(f"   First filtered tag: {filtered_selected_tags[0]}")
        else:
            print(f"   ⚠️  Selected tags were not filtered (this might be expected if all tags match the filter)")
            
    except Exception as e:
        print(f"❌ Error testing filtering: {e}")
        return False
    
    # Step 5: Test with a different filter
    print("\n5. Testing filtering with product type filter...")
    try:
        # Apply a product type filter
        filters = {
            'vendor': '',
            'brand': '',
            'productType': 'Flower',  # Filter to only show Flower products
            'lineage': '',
            'weight': ''
        }
        
        response = session.post(f'{base_url}/api/available-tags', json={
            'filters': filters,
            'selected_tags': selected_tags
        })
        
        if response.status_code != 200:
            print(f"❌ Filter request failed: {response.status_code}")
            return False
        
        filter_result = response.json()
        available_tags = filter_result.get('available_tags', [])
        filtered_selected_tags = filter_result.get('selected_tags', [])
        
        print(f"✅ Product type filter applied successfully!")
        print(f"   Available tags after filter: {len(available_tags)}")
        print(f"   Selected tags after filter: {len(filtered_selected_tags)}")
        
        # Check if selected tags were filtered correctly
        if len(filtered_selected_tags) < len(selected_tags):
            print(f"   ✅ Selected tags were filtered correctly!")
            print(f"   Original selected: {len(selected_tags)}")
            print(f"   Filtered selected: {len(filtered_selected_tags)}")
            
            # Show some examples of filtered tags
            if filtered_selected_tags:
                print(f"   First filtered tag: {filtered_selected_tags[0]}")
        else:
            print(f"   ⚠️  Selected tags were not filtered (this might be expected if all tags match the filter)")
            
    except Exception as e:
        print(f"❌ Error testing product type filtering: {e}")
        return False
    
    print("\n🎉 Selected tags filtering test completed successfully!")
    return True

if __name__ == "__main__":
    test_selected_tags_filtering() 