#!/usr/bin/env python3
"""
Test JSON matching frontend integration to ensure products appear in available tags.
"""

import requests
import json
import time

def test_json_matching_frontend():
    """Test that JSON matching properly updates the available tags list."""
    
    print("🧪 Testing JSON Matching Frontend Integration")
    print("=" * 50)
    
    # Test URL
    base_url = "http://127.0.0.1:5002"
    json_url = "https://files.cultivera.com/435553542D5753353635/Interop/25/34/GFJZZ9ZJQKVBWQDR/Cultivera_ORD-11766_422044.json"
    
    try:
        print(f"📦 Testing JSON URL: {json_url}")
        
        # Test JSON matching endpoint
        print(f"\n🔍 Testing JSON matching endpoint...")
        response = requests.post(
            f"{base_url}/api/json-match",
            json={"url": json_url},
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ JSON matching successful!")
            print(f"   Status: {result.get('success', False)}")
            print(f"   Matched count: {result.get('matched_count', 0)}")
            print(f"   Available tags: {len(result.get('available_tags', []))}")
            print(f"   Selected tags: {len(result.get('selected_tags', []))}")
            print(f"   JSON matched tags: {len(result.get('json_matched_tags', []))}")
            
            # Check if products are in available_tags
            available_tags = result.get('available_tags', [])
            if available_tags:
                print(f"\n📋 Sample available tags:")
                for i, tag in enumerate(available_tags[:5], 1):
                    product_name = tag.get('Product Name*', tag.get('ProductName', 'Unknown'))
                    source = tag.get('Source', 'Unknown')
                    print(f"   {i}. {product_name} (Source: {source})")
                
                if len(available_tags) >= 14:
                    print(f"\n✅ SUCCESS: All 14 products are in available_tags!")
                    print(f"   - Products are available for manual selection")
                    print(f"   - Users can choose which ones to generate labels for")
                    return True
                else:
                    print(f"\n❌ ISSUE: Only {len(available_tags)} products in available_tags")
                    print(f"   - Expected: 14 products")
                    print(f"   - Actual: {len(available_tags)} products")
                    return False
            else:
                print(f"\n❌ FAILED: No products in available_tags")
                return False
        else:
            print(f"❌ JSON matching failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_available_tags_endpoint():
    """Test that the available tags endpoint shows the JSON matched products."""
    
    print(f"\n🔍 Testing available tags endpoint...")
    
    try:
        base_url = "http://127.0.0.1:5002"
        response = requests.get(f"{base_url}/api/available-tags", timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, dict):
                available_tags = result.get('tags', [])
            else:
                available_tags = result
            
            print(f"✅ Available tags endpoint successful!")
            print(f"   Total available tags: {len(available_tags)}")
            
            # Look for JSON matched products
            json_matched_count = 0
            for tag in available_tags:
                if isinstance(tag, dict):
                    source = tag.get('Source', '')
                    if 'JSON Match' in source:
                        json_matched_count += 1
            
            print(f"   JSON matched products: {json_matched_count}")
            
            if json_matched_count >= 14:
                print(f"✅ SUCCESS: All 14 JSON matched products are in available tags!")
                return True
            else:
                print(f"❌ ISSUE: Only {json_matched_count} JSON matched products in available tags")
                return False
        else:
            print(f"❌ Available tags endpoint failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting JSON Matching Frontend Integration Test")
    print("=" * 50)
    
    # Wait a moment for the server to start
    print("⏳ Waiting for server to be ready...")
    time.sleep(2)
    
    # Test JSON matching
    json_success = test_json_matching_frontend()
    
    # Test available tags endpoint
    available_success = test_available_tags_endpoint()
    
    print(f"\n📋 Final Results:")
    print(f"   JSON Matching: {'✅ PASSED' if json_success else '❌ FAILED'}")
    print(f"   Available Tags: {'✅ PASSED' if available_success else '❌ FAILED'}")
    
    if json_success and available_success:
        print(f"\n🎉 JSON matching frontend integration is working correctly!")
        print(f"   - All 14 products are processed")
        print(f"   - Products appear in available tags list")
        print(f"   - Users can manually select products")
        print(f"   - Ready for label generation")
    else:
        print(f"\n🔧 JSON matching frontend integration needs work")
        print(f"   - May need additional debugging")
        print(f"   - Check server logs for errors")
