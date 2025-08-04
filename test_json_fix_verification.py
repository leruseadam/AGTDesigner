#!/usr/bin/env python3
"""
Test script to verify that the JSON matching fix is working correctly.
This tests that JSON matching returns dictionary objects instead of strings.
"""

import requests
import json
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_json_matching_fix():
    """Test that JSON matching now returns proper dictionary objects instead of strings."""
    
    print("🧪 Testing JSON Matching Fix - Dictionary Objects")
    print("=" * 60)
    
    # Test URL - using a simple test URL
    test_url = "https://api-trace.getbamboo.com/api/v1/inventory-transfers/12345"
    
    try:
        # Test 1: Check if the server is running
        print("\n1️⃣ Checking server status...")
        response = requests.get("http://127.0.0.1:9090/api/status", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print("❌ Server returned status code:", response.status_code)
            return
    except requests.exceptions.RequestException as e:
        print("❌ Server is not running or not accessible")
        print("   Error:", str(e))
        print("\n💡 To test this fix, please:")
        print("   1. Start the server: python app.py")
        print("   2. Upload an Excel file with product data")
        print("   3. Run this test again")
        return
    
    # Test 2: Test JSON matching with the fix
    print("\n2️⃣ Testing JSON matching fix...")
    
    try:
        # Make the JSON matching request
        response = requests.post(
            "http://127.0.0.1:9090/api/json-match",
            json={"url": test_url},
            timeout=120  # 2 minutes timeout
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ JSON matching request successful")
            
            # Check the response structure
            print(f"   Matched count: {data.get('matched_count', 0)}")
            print(f"   Available tags count: {len(data.get('available_tags', []))}")
            print(f"   Selected tags count: {len(data.get('selected_tags', []))}")
            print(f"   JSON matched tags count: {len(data.get('json_matched_tags', []))}")
            
            # Check if selected tags are dictionaries
            selected_tags = data.get('selected_tags', [])
            if selected_tags:
                print(f"\n3️⃣ Checking selected tags structure...")
                string_count = 0
                dict_count = 0
                
                for i, tag in enumerate(selected_tags[:5]):  # Check first 5 tags
                    if isinstance(tag, dict):
                        dict_count += 1
                        print(f"   Tag {i+1}: ✅ Dictionary with keys: {list(tag.keys())[:5]}...")
                        # Show a sample of the dictionary content
                        if 'Product Name*' in tag:
                            print(f"      Product Name: {tag['Product Name*']}")
                    elif isinstance(tag, str):
                        string_count += 1
                        print(f"   Tag {i+1}: ❌ String: {tag[:50]}...")
                    else:
                        print(f"   Tag {i+1}: ❓ Unknown type: {type(tag)}")
                
                if dict_count > 0 and string_count == 0:
                    print(f"\n✅ SUCCESS: All checked tags are dictionaries!")
                    print(f"   Dictionary tags: {dict_count}")
                    print(f"   String tags: {string_count}")
                elif dict_count > 0:
                    print(f"\n⚠️  PARTIAL SUCCESS: Some tags are dictionaries, some are strings")
                    print(f"   Dictionary tags: {dict_count}")
                    print(f"   String tags: {string_count}")
                else:
                    print(f"\n❌ FAILURE: No dictionary tags found")
                    print(f"   Dictionary tags: {dict_count}")
                    print(f"   String tags: {string_count}")
            else:
                print("   No selected tags to check")
            
            # Check if JSON matched tags are dictionaries
            json_matched_tags = data.get('json_matched_tags', [])
            if json_matched_tags:
                print(f"\n4️⃣ Checking JSON matched tags structure...")
                string_count = 0
                dict_count = 0
                
                for i, tag in enumerate(json_matched_tags[:5]):  # Check first 5 tags
                    if isinstance(tag, dict):
                        dict_count += 1
                        print(f"   JSON Tag {i+1}: ✅ Dictionary with keys: {list(tag.keys())[:5]}...")
                        # Show a sample of the dictionary content
                        if 'Product Name*' in tag:
                            print(f"      Product Name: {tag['Product Name*']}")
                    elif isinstance(tag, str):
                        string_count += 1
                        print(f"   JSON Tag {i+1}: ❌ String: {tag[:50]}...")
                    else:
                        print(f"   JSON Tag {i+1}: ❓ Unknown type: {type(tag)}")
                
                if dict_count > 0 and string_count == 0:
                    print(f"\n✅ SUCCESS: All JSON matched tags are dictionaries!")
                else:
                    print(f"\n⚠️  JSON matched tags have mixed types")
                    print(f"   Dictionary tags: {dict_count}")
                    print(f"   String tags: {string_count}")
            else:
                print("   No JSON matched tags to check")
                
        else:
            print(f"❌ JSON matching request failed with status code: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"   Response: {response.text[:200]}...")
                
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 Test completed")

if __name__ == "__main__":
    test_json_matching_fix() 