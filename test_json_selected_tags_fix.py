#!/usr/bin/env python3
"""
Test script to verify that JSON matched tags are properly added to the selected list.
"""

import requests
import json
import time

def test_json_selected_tags_fix():
    """Test that JSON matched tags are properly added to selected list."""
    
    base_url = "http://localhost:5000"
    
    print("🧪 Testing JSON Selected Tags Fix")
    print("=" * 50)
    
    # Step 1: Check if server is running
    try:
        response = requests.get(f"{base_url}/api/status")
        if response.status_code != 200:
            print("❌ Server not responding properly")
            return False
        print("✅ Server is running")
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return False
    
    # Step 2: Test JSON matching with a simple JSON URL
    json_url = f"{base_url}/test_products.json"
    
    print(f"\n📋 Testing JSON matching with URL: {json_url}")
    
    try:
        response = requests.post(f"{base_url}/api/json-match", 
                               json={"url": json_url})
        
        if response.status_code != 200:
            print(f"❌ JSON matching failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        match_result = response.json()
        print("✅ JSON matching completed successfully")
        
        # Check the response structure
        print(f"\n📊 Response Analysis:")
        print(f"  - Success: {match_result.get('success', False)}")
        print(f"  - Matched count: {match_result.get('matched_count', 0)}")
        print(f"  - Available tags count: {len(match_result.get('available_tags', []))}")
        print(f"  - Selected tags count: {len(match_result.get('selected_tags', []))}")
        print(f"  - JSON matched tags count: {len(match_result.get('json_matched_tags', []))}")
        
        # Step 3: Check if selected tags are now properly populated
        selected_tags = match_result.get('selected_tags', [])
        
        if selected_tags:
            print(f"\n✅ SUCCESS: Selected tags are populated!")
            print(f"  - {len(selected_tags)} items in selected tags")
            
            # Show sample selected tags
            print(f"\n📝 Sample Selected Tags:")
            for i, tag in enumerate(selected_tags[:3]):
                if isinstance(tag, dict):
                    name = tag.get('Product Name*', 'Unknown')
                    source = tag.get('Source', 'Unknown')
                    print(f"  {i+1}. {name} (Source: {source})")
                else:
                    print(f"  {i+1}. {tag}")
            
            # Step 4: Verify that the selected tags are accessible via the API
            print(f"\n🔍 Verifying selected tags via API...")
            
            response = requests.get(f"{base_url}/api/selected-tags")
            if response.status_code == 200:
                api_selected_tags = response.json()
                print(f"✅ API selected tags: {len(api_selected_tags)} items")
                
                if api_selected_tags:
                    print(f"📝 API Selected Tags Sample:")
                    for i, tag in enumerate(api_selected_tags[:3]):
                        if isinstance(tag, dict):
                            name = tag.get('Product Name*', 'Unknown')
                            print(f"  {i+1}. {name}")
                        else:
                            print(f"  {i+1}. {tag}")
                else:
                    print("⚠️  API returned empty selected tags")
            else:
                print(f"❌ Failed to get selected tags via API: {response.status_code}")
            
            return True
        else:
            print(f"\n❌ FAILED: No items in selected tags")
            return False
            
    except Exception as e:
        print(f"❌ Error during JSON matching test: {e}")
        return False

def test_session_storage():
    """Test that selected tags are properly stored in session."""
    
    print(f"\n💾 Testing Session Storage")
    print("=" * 40)
    
    base_url = "http://localhost:5000"
    
    try:
        # Get session stats to see if selected tags are stored
        response = requests.get(f"{base_url}/api/session-stats")
        if response.status_code == 200:
            stats = response.json()
            selected_count = stats.get('selected_tags_count', 0)
            print(f"✅ Session selected tags count: {selected_count}")
            
            if selected_count > 0:
                print("✅ Selected tags are properly stored in session")
                return True
            else:
                print("⚠️  No selected tags found in session")
                return False
        else:
            print(f"❌ Failed to get session stats: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking session storage: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting JSON Selected Tags Fix Test")
    print("=" * 60)
    
    # Test JSON matching and selected tags population
    matching_success = test_json_selected_tags_fix()
    
    # Test session storage
    session_success = test_session_storage()
    
    print(f"\n📋 Test Summary")
    print("=" * 30)
    print(f"JSON Matching Test: {'✅ PASSED' if matching_success else '❌ FAILED'}")
    print(f"Session Storage Test: {'✅ PASSED' if session_success else '❌ FAILED'}")
    
    if matching_success and session_success:
        print(f"\n🎉 All tests passed! JSON matched tags are now properly added to selected list.")
    else:
        print(f"\n⚠️  Some tests failed. Please check the implementation.") 