#!/usr/bin/env python3
"""
Debug script to identify why JSON matched tags are not being loaded.
This script will test the JSON matching process step by step.
"""

import requests
import json
import time

def test_json_matching_step_by_step():
    """Test JSON matching step by step to identify the issue."""
    
    print("=== JSON MATCHING DEBUG - STEP BY STEP ===")
    
    # Test URL - use the local test file
    test_url = "http://localhost:5000/test_products.json"
    
    try:
        print(f"1. Testing JSON URL accessibility: {test_url}")
        
        # First, test if the JSON URL is accessible
        json_response = requests.get(test_url, timeout=10)
        if json_response.status_code == 200:
            json_data = json_response.json()
            print(f"   ✅ JSON URL accessible, contains {len(json_data)} products")
            print(f"   Sample product: {json_data[0] if json_data else 'None'}")
        else:
            print(f"   ❌ JSON URL not accessible: {json_response.status_code}")
            return
        
        print(f"\n2. Making JSON matching request...")
        
        # Make the JSON matching request
        response = requests.post(
            'http://localhost:5000/api/json-match',
            json={'url': test_url},
            timeout=60
        )
        
        print(f"   Response status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n3. JSON matching response analysis:")
            print(f"   Response keys: {list(data.keys())}")
            print(f"   Success: {data.get('success', False)}")
            print(f"   Matched count: {data.get('matched_count', 0)}")
            print(f"   Available tags count: {len(data.get('available_tags', []))}")
            print(f"   Selected tags count: {len(data.get('selected_tags', []))}")
            
            # Check if selected_tags is populated
            selected_tags = data.get('selected_tags', [])
            if selected_tags:
                print(f"   ✅ Selected tags are populated with {len(selected_tags)} items")
                print(f"   Sample selected tags:")
                for i, tag in enumerate(selected_tags[:3]):
                    if isinstance(tag, dict):
                        name = tag.get('Product Name*', 'Unknown')
                        print(f"     {i+1}. {name}")
                    else:
                        print(f"     {i+1}. {tag}")
            else:
                print(f"   ❌ Selected tags are empty")
            
            # Check available tags
            available_tags = data.get('available_tags', [])
            if available_tags:
                print(f"   ✅ Available tags populated with {len(available_tags)} items")
                print(f"   Sample available tags:")
                for i, tag in enumerate(available_tags[:3]):
                    if isinstance(tag, dict):
                        name = tag.get('Product Name*', 'Unknown')
                        print(f"     {i+1}. {name}")
                    else:
                        print(f"     {i+1}. {tag}")
            else:
                print(f"   ❌ Available tags are empty")
            
            # Check if there are any error messages
            if 'error' in data:
                print(f"   ❌ Error in response: {data['error']}")
            
            # Check cache status
            cache_status = data.get('cache_status', 'Unknown')
            print(f"   Cache status: {cache_status}")
            
            # Check filter mode
            filter_mode = data.get('filter_mode', 'Unknown')
            print(f"   Filter mode: {filter_mode}")
            
        else:
            print(f"   ❌ JSON matching failed with status code: {response.status_code}")
            print(f"   Response: {response.text}")
            return
        
        print(f"\n4. Testing selected tags endpoint after JSON matching...")
        time.sleep(2)  # Give the server time to process
        
        selected_response = requests.get('http://localhost:5000/api/selected-tags')
        if selected_response.status_code == 200:
            selected_data = selected_response.json()
            print(f"   ✅ Selected tags endpoint returned: {len(selected_data.get('selected_tags', []))} items")
            
            if selected_data.get('selected_tags'):
                print("   ✅ Selected tags endpoint is returning data")
                print("   Sample selected tags from endpoint:")
                for i, tag in enumerate(selected_data['selected_tags'][:3]):
                    if isinstance(tag, dict):
                        name = tag.get('Product Name*', 'Unknown')
                        print(f"     {i+1}. {name}")
                    else:
                        print(f"     {i+1}. {tag}")
            else:
                print("   ❌ Selected tags endpoint is not returning data")
        else:
            print(f"   ❌ Selected tags endpoint failed: {selected_response.status_code}")
        
        print(f"\n5. Testing available tags endpoint...")
        
        available_response = requests.get('http://localhost:5000/api/available-tags')
        if available_response.status_code == 200:
            available_data = available_response.json()
            print(f"   ✅ Available tags endpoint returned: {len(available_data)} items")
            
            if available_data:
                print("   ✅ Available tags endpoint is returning data")
                print("   Sample available tags from endpoint:")
                for i, tag in enumerate(available_data[:3]):
                    if isinstance(tag, dict):
                        name = tag.get('Product Name*', 'Unknown')
                        print(f"     {i+1}. {name}")
                    else:
                        print(f"     {i+1}. {tag}")
            else:
                print("   ❌ Available tags endpoint is not returning data")
        else:
            print(f"   ❌ Available tags endpoint failed: {available_response.status_code}")
        
        print(f"\n6. Testing session data...")
        
        session_response = requests.get('http://localhost:5000/api/session-stats')
        if session_response.status_code == 200:
            session_data = session_response.json()
            print(f"   ✅ Session stats: {session_data}")
            
            if 'selected_tags_count' in session_data:
                print(f"   Selected tags in session: {session_data['selected_tags_count']}")
            else:
                print("   No selected tags count in session")
        else:
            print(f"   ❌ Session stats failed: {session_response.status_code}")
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - make sure the server is running on localhost:5000")
    except Exception as e:
        print(f"❌ Error during test: {e}")

def test_with_different_modes():
    """Test JSON matching with different default file modes."""
    
    print("\n=== TESTING DIFFERENT MODES ===")
    
    print("Mode 1: With default file loading (DISABLE_DEFAULT_FOR_TESTING = False)")
    print("Mode 2: Without default file loading (DISABLE_DEFAULT_FOR_TESTING = True)")
    
    print("\nTo test different modes:")
    print("1. Edit src/core/data/excel_processor.py")
    print("2. Set DISABLE_DEFAULT_FOR_TESTING = False or True")
    print("3. Restart the server")
    print("4. Run this test again")

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
    print("JSON MATCHING DEBUG - IDENTIFYING THE ISSUE")
    print("=" * 60)
    
    # Check if server is running
    if not check_server_status():
        print("\nPlease start the server first:")
        print("1. Open a terminal in the project directory")
        print("2. Run: python app.py")
        print("3. Wait for the server to start")
        print("4. Run this test again")
        exit(1)
    
    print("\nTesting JSON matching step by step...")
    test_json_matching_step_by_step()
    
    print("\n" + "=" * 60)
    print("DEBUG SUMMARY")
    print("=" * 60)
    print("This test will help identify:")
    print("1. Whether the JSON URL is accessible")
    print("2. Whether JSON matching is returning selected_tags")
    print("3. Whether the selected tags endpoint is working")
    print("4. Whether the available tags endpoint is working")
    print("5. Whether session data is being stored")
    print("\nCommon issues:")
    print("- JSON URL not accessible")
    print("- JSON matching not returning selected_tags")
    print("- Session data not being stored")
    print("- Frontend not calling updateSelectedTags")
    
    test_with_different_modes() 