#!/usr/bin/env python3
"""
Test to verify session persistence.
"""

import requests
import json

def test_session():
    """Test session persistence."""
    
    print("🧪 Testing Session Persistence")
    print("=" * 40)
    
    base_url = "http://localhost:5001"
    
    try:
        # Step 1: Check initial session
        print("1. Checking initial session...")
        filter_response = requests.get(f"{base_url}/api/get-filter-status")
        if filter_response.status_code == 200:
            filter_data = filter_response.json()
            print(f"   Initial filter mode: {filter_data.get('current_mode', 'unknown')}")
        
        # Step 2: Set a test value in session
        print("2. Setting test value in session...")
        test_response = requests.post(f"{base_url}/api/json-match", 
                                    json={"url": "https://httpbin.org/json"})
        
        if test_response.status_code == 200:
            print("   ✅ JSON matching successful")
            
            # Step 3: Check session again
            print("3. Checking session after JSON matching...")
            filter_response = requests.get(f"{base_url}/api/get-filter-status")
            if filter_response.status_code == 200:
                filter_data = filter_response.json()
                print(f"   Filter mode: {filter_data.get('current_mode', 'unknown')}")
                print(f"   Has JSON matched: {filter_data.get('has_json_matched', False)}")
                print(f"   JSON matched count: {filter_data.get('json_matched_count', 0)}")
                
                if filter_data.get('current_mode') == 'json_matched':
                    print("   ✅ Session is working correctly")
                    return True
                else:
                    print("   ❌ Session is not persisting")
                    return False
            else:
                print(f"   ❌ Failed to get filter status: {filter_response.status_code}")
                return False
        else:
            print(f"   ❌ JSON matching failed: {test_response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Test error: {e}")
        return False

if __name__ == "__main__":
    success = test_session()
    if success:
        print("\n🎉 Session persistence is working!")
    else:
        print("\n💥 Session persistence is not working.") 