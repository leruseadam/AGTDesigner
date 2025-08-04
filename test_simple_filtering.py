#!/usr/bin/env python3
"""
Simple test to verify that filtering functionality works.
"""

import requests
import json

def test_simple_filtering():
    """Test basic filtering functionality."""
    base_url = 'http://127.0.0.1:9090'
    
    print("🧪 Testing Simple Filtering")
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
    
    # Step 2: Get available tags without filters
    print("\n2. Getting available tags without filters...")
    try:
        response = session.get(f'{base_url}/api/available-tags')
        if response.status_code != 200:
            print(f"❌ Failed to get available tags: {response.status_code}")
            return False
        
        available_tags = response.json()
        print(f"✅ Available tags retrieved: {len(available_tags)}")
        if len(available_tags) > 0:
            print(f"   First tag: {available_tags[0]}")
    except Exception as e:
        print(f"❌ Error getting available tags: {e}")
        return False
    
    # Step 3: Test filtering with vendor filter
    print("\n3. Testing filtering with vendor filter...")
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
            'filters': filters
        })
        
        if response.status_code != 200:
            print(f"❌ Filter request failed: {response.status_code}")
            return False
        
        filter_result = response.json()
        filtered_available_tags = filter_result.get('available_tags', [])
        
        print(f"✅ Filter applied successfully!")
        print(f"   Available tags after filter: {len(filtered_available_tags)}")
        
        if len(filtered_available_tags) < len(available_tags):
            print(f"   ✅ Filtering is working correctly!")
            print(f"   Original available: {len(available_tags)}")
            print(f"   Filtered available: {len(filtered_available_tags)}")
            
            # Show some examples of filtered tags
            if filtered_available_tags:
                print(f"   First filtered tag: {filtered_available_tags[0]}")
        else:
            print(f"   ⚠️  No filtering effect (this might be expected if all tags match the filter)")
            
    except Exception as e:
        print(f"❌ Error testing filtering: {e}")
        return False
    
    # Step 4: Test with product type filter
    print("\n4. Testing filtering with product type filter...")
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
            'filters': filters
        })
        
        if response.status_code != 200:
            print(f"❌ Filter request failed: {response.status_code}")
            return False
        
        filter_result = response.json()
        filtered_available_tags = filter_result.get('available_tags', [])
        
        print(f"✅ Product type filter applied successfully!")
        print(f"   Available tags after filter: {len(filtered_available_tags)}")
        
        if len(filtered_available_tags) < len(available_tags):
            print(f"   ✅ Product type filtering is working correctly!")
            print(f"   Original available: {len(available_tags)}")
            print(f"   Filtered available: {len(filtered_available_tags)}")
            
            # Show some examples of filtered tags
            if filtered_available_tags:
                print(f"   First filtered tag: {filtered_available_tags[0]}")
        else:
            print(f"   ⚠️  No filtering effect (this might be expected if all tags match the filter)")
            
    except Exception as e:
        print(f"❌ Error testing product type filtering: {e}")
        return False
    
    print("\n🎉 Simple filtering test completed successfully!")
    return True

if __name__ == "__main__":
    test_simple_filtering() 