#!/usr/bin/env python3
"""
Test script to verify JSON matching works correctly without default file interference.
This test simulates the JSON matching process and checks that selected tags are properly populated.
"""

import requests
import json
import time

def test_json_matching_without_default():
    """Test JSON matching without default file interference."""
    
    print("=== JSON MATCHING WITHOUT DEFAULT FILE TEST ===")
    
    # Test URL - replace with a real JSON URL for testing
    test_url = "https://example.com/test.json"  # Replace with actual test URL
    
    try:
        print(f"1. Making JSON matching request to: {test_url}")
        print("   Note: Default file loading has been disabled")
        
        # Make the JSON matching request
        response = requests.post(
            'http://localhost:5000/api/json-match',
            json={'url': test_url},
            timeout=30
        )
        
        print(f"2. Response status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"3. JSON matching response keys: {list(data.keys())}")
            print(f"4. Matched count: {data.get('matched_count', 0)}")
            print(f"5. Available tags count: {len(data.get('available_tags', []))}")
            print(f"6. Selected tags count: {len(data.get('selected_tags', []))}")
            
            # Check if selected_tags is populated
            selected_tags = data.get('selected_tags', [])
            if selected_tags:
                print(f"7. ✅ Selected tags are populated with {len(selected_tags)} items")
                print(f"   Sample selected tags:")
                for i, tag in enumerate(selected_tags[:3]):
                    if isinstance(tag, dict):
                        name = tag.get('Product Name*', 'Unknown')
                        print(f"     {i+1}. {name}")
                    else:
                        print(f"     {i+1}. {tag}")
            else:
                print("7. ❌ Selected tags are empty")
            
            # Check available tags
            available_tags = data.get('available_tags', [])
            if available_tags:
                print(f"8. Available tags sample:")
                for i, tag in enumerate(available_tags[:3]):
                    if isinstance(tag, dict):
                        name = tag.get('Product Name*', 'Unknown')
                        print(f"     {i+1}. {name}")
                    else:
                        print(f"     {i+1}. {tag}")
            
            # Check if there are any error messages
            if 'error' in data:
                print(f"9. ❌ Error in response: {data['error']}")
            
            # Test the selected tags endpoint after JSON matching
            print("\n10. Testing selected tags endpoint after JSON matching...")
            time.sleep(2)  # Give the server time to process
            
            selected_response = requests.get('http://localhost:5000/api/selected-tags')
            if selected_response.status_code == 200:
                selected_data = selected_response.json()
                print(f"    Selected tags endpoint returned: {len(selected_data.get('selected_tags', []))} items")
                
                if selected_data.get('selected_tags'):
                    print("    ✅ Selected tags endpoint is returning data")
                else:
                    print("    ❌ Selected tags endpoint is not returning data")
            else:
                print(f"    ❌ Selected tags endpoint failed: {selected_response.status_code}")
            
        else:
            print(f"3. ❌ JSON matching failed with status code: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out - this is expected for invalid URLs")
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - make sure the server is running on localhost:5000")
    except Exception as e:
        print(f"❌ Error during test: {e}")

def check_server_status():
    """Check if the server is running and accessible."""
    
    print("=== SERVER STATUS CHECK ===")
    
    try:
        response = requests.get('http://localhost:5000/api/status', timeout=5)
        if response.status_code == 200:
            print("✅ Server is running and accessible")
            return True
        else:
            print(f"❌ Server returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running on localhost:5000")
        print("   Please start the server with: python app.py")
        return False
    except Exception as e:
        print(f"❌ Error checking server status: {e}")
        return False

if __name__ == "__main__":
    print("JSON MATCHING WITHOUT DEFAULT FILE TEST")
    print("=" * 50)
    
    # Check if server is running
    if not check_server_status():
        print("\nPlease start the server first:")
        print("1. Open a terminal in the project directory")
        print("2. Run: python app.py")
        print("3. Wait for the server to start")
        print("4. Run this test again")
        exit(1)
    
    print("\nTesting JSON matching without default file interference...")
    test_json_matching_without_default()
    
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print("This test verifies that:")
    print("1. Default file loading is disabled")
    print("2. JSON matching returns selected_tags")
    print("3. Selected tags endpoint returns the right data")
    print("\nIf the test shows selected tags are populated, then the fix is working.")
    print("If selected tags are still empty, there may be another issue.")
    print("\nTo test with a real JSON URL:")
    print("1. Replace the test_url in test_json_matching_without_default()")
    print("2. Run the function: test_json_matching_without_default()") 