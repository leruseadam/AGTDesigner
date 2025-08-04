#!/usr/bin/env python3
"""
Debug script to investigate why the default list is still showing instead of JSON matched products.
"""

import requests
import json
import time

def test_json_matching_debug():
    """Test JSON matching and check what data is being returned."""
    
    print("=== JSON MATCHING DEBUG TEST ===")
    
    # Test URL - replace with a real JSON URL for testing
    test_url = "https://example.com/test.json"  # Replace with actual test URL
    
    try:
        print(f"1. Making JSON matching request to: {test_url}")
        
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
            
        else:
            print(f"3. ❌ JSON matching failed with status code: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out - this is expected for invalid URLs")
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - make sure the server is running on localhost:5000")
    except Exception as e:
        print(f"❌ Error during test: {e}")

def test_selected_tags_endpoint():
    """Test the selected tags endpoint to see what data is being returned."""
    
    print("\n=== SELECTED TAGS ENDPOINT TEST ===")
    
    try:
        print("1. Making request to /api/selected-tags")
        
        response = requests.get('http://localhost:5000/api/selected-tags')
        
        print(f"2. Response status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"3. Selected tags response keys: {list(data.keys())}")
            print(f"4. Selected tags count: {len(data.get('selected_tags', []))}")
            
            selected_tags = data.get('selected_tags', [])
            if selected_tags:
                print(f"5. Selected tags sample:")
                for i, tag in enumerate(selected_tags[:5]):
                    if isinstance(tag, dict):
                        name = tag.get('Product Name*', 'Unknown')
                        print(f"     {i+1}. {name}")
                    else:
                        print(f"     {i+1}. {tag}")
            else:
                print("5. No selected tags found")
                
        else:
            print(f"3. ❌ Selected tags request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - make sure the server is running on localhost:5000")
    except Exception as e:
        print(f"❌ Error during test: {e}")

def test_available_tags_endpoint():
    """Test the available tags endpoint to see what data is being returned."""
    
    print("\n=== AVAILABLE TAGS ENDPOINT TEST ===")
    
    try:
        print("1. Making request to /api/available-tags")
        
        response = requests.get('http://localhost:5000/api/available-tags')
        
        print(f"2. Response status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"3. Available tags count: {len(data)}")
            
            if data:
                print(f"4. Available tags sample:")
                for i, tag in enumerate(data[:5]):
                    if isinstance(tag, dict):
                        name = tag.get('Product Name*', 'Unknown')
                        print(f"     {i+1}. {name}")
                    else:
                        print(f"     {i+1}. {tag}")
            else:
                print("4. No available tags found")
                
        else:
            print(f"3. ❌ Available tags request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - make sure the server is running on localhost:5000")
    except Exception as e:
        print(f"❌ Error during test: {e}")

def check_session_data():
    """Check session data to see if selected tags are being stored."""
    
    print("\n=== SESSION DATA TEST ===")
    
    try:
        print("1. Making request to /api/session-stats")
        
        response = requests.get('http://localhost:5000/api/session-stats')
        
        print(f"2. Response status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"3. Session stats: {data}")
            
            # Check if selected tags are in session
            if 'selected_tags_count' in data:
                print(f"4. Selected tags in session: {data['selected_tags_count']}")
            else:
                print("4. No selected tags count in session stats")
                
        else:
            print(f"3. ❌ Session stats request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - make sure the server is running on localhost:5000")
    except Exception as e:
        print(f"❌ Error during test: {e}")

if __name__ == "__main__":
    print("JSON MATCHING DEFAULT LIST DEBUG")
    print("=" * 50)
    
    # Test the endpoints to see what data is being returned
    test_selected_tags_endpoint()
    test_available_tags_endpoint()
    check_session_data()
    
    print("\n" + "=" * 50)
    print("DEBUG SUMMARY")
    print("=" * 50)
    print("This test will help identify:")
    print("1. Whether JSON matching is returning selected_tags")
    print("2. Whether the selected tags endpoint is returning the right data")
    print("3. Whether the available tags endpoint is showing the right data")
    print("4. Whether session data is being properly stored")
    print("\nTo test JSON matching with a real URL:")
    print("1. Replace the test_url in test_json_matching_debug()")
    print("2. Run the function: test_json_matching_debug()") 