#!/usr/bin/env python3
"""
Test script to verify the lineage editor fix works properly.
"""

import requests
import time
import json

def test_lineage_editor():
    """Test the lineage editor functionality."""
    base_url = "http://127.0.0.1:9090"
    
    print("Testing Lineage Editor Fix")
    print("=" * 50)
    
    # Test 1: Check if the application is running
    try:
        response = requests.get(f"{base_url}/api/status", timeout=5)
        if response.status_code == 200:
            print("✅ Application is running")
        else:
            print("❌ Application returned status code:", response.status_code)
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to application: {e}")
        return False
    
    # Test 2: Check if the lineage editor modal HTML is accessible
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            if 'lineageEditorModal' in response.text:
                print("✅ Lineage editor modal HTML is present")
            else:
                print("❌ Lineage editor modal HTML not found")
                return False
        else:
            print("❌ Cannot access main page")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot access main page: {e}")
        return False
    
    # Test 3: Check if the API endpoints are available
    try:
        response = requests.get(f"{base_url}/api/available-tags", timeout=5)
        if response.status_code == 200:
            print("✅ Available tags API is working")
        else:
            print("❌ Available tags API returned status code:", response.status_code)
    except requests.exceptions.RequestException as e:
        print(f"❌ Available tags API error: {e}")
    
    # Test 4: Test lineage update API (if we have data)
    try:
        response = requests.get(f"{base_url}/api/available-tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            # Handle both object and array response formats
            tags = data.get('tags', []) if isinstance(data, dict) else data
            if tags and len(tags) > 0:
                # Test with the first tag
                test_tag = tags[0]
                tag_name = test_tag.get('Product Name*', 'Test Product')
                current_lineage = test_tag.get('lineage', 'HYBRID')
                
                print(f"✅ Testing lineage update for: {tag_name}")
                
                # Test the lineage update API
                update_data = {
                    'tag_name': tag_name,
                    'lineage': 'SATIVA'  # Change to SATIVA for testing
                }
                
                response = requests.post(
                    f"{base_url}/api/update-lineage",
                    json=update_data,
                    timeout=10
                )
                
                if response.status_code == 200:
                    print("✅ Lineage update API is working")
                    
                    # Change it back
                    update_data['lineage'] = current_lineage
                    response = requests.post(
                        f"{base_url}/api/update-lineage",
                        json=update_data,
                        timeout=10
                    )
                    if response.status_code == 200:
                        print("✅ Lineage revert successful")
                    else:
                        print("⚠️  Lineage revert failed (non-critical)")
                else:
                    print(f"❌ Lineage update API failed: {response.status_code}")
                    try:
                        error_data = response.json()
                        print(f"   Error: {error_data.get('error', 'Unknown error')}")
                    except:
                        print(f"   Response: {response.text}")
            else:
                print("⚠️  No tags available for testing lineage update")
        else:
            print("❌ Cannot get available tags for testing")
    except requests.exceptions.RequestException as e:
        print(f"❌ Lineage update test error: {e}")
    
    print("\n" + "=" * 50)
    print("Lineage Editor Fix Test Complete")
    print("\nTo test the UI:")
    print("1. Open your browser to http://127.0.0.1:9090")
    print("2. Right-click on any product tag")
    print("3. The lineage editor modal should open")
    print("4. If it gets stuck, try the emergency cleanup function in browser console:")
    print("   emergencyLineageModalCleanup()")
    
    return True

if __name__ == "__main__":
    test_lineage_editor() 