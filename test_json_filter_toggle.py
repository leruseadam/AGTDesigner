#!/usr/bin/env python3
"""
Test script to verify JSON filter toggle functionality.
"""

import requests
import json
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_json_filter_toggle():
    """Test that JSON filter toggle functionality works correctly."""
    
    print("🧪 Testing JSON Filter Toggle Functionality")
    print("=" * 60)
    
    # Test URL - you can replace this with your actual JSON URL
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
    
    # Test 2: Check filter status before JSON matching
    print("\n2️⃣ Checking filter status before JSON matching...")
    
    try:
        response = requests.get("http://127.0.0.1:9090/api/get-filter-status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Filter status API working")
            print(f"   Current mode: {data.get('current_mode', 'unknown')}")
            print(f"   Has full Excel: {data.get('has_full_excel', False)}")
            print(f"   Has JSON matched: {data.get('has_json_matched', False)}")
            print(f"   Can toggle: {data.get('can_toggle', False)}")
        else:
            print(f"❌ Filter status API returned status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Filter status request failed: {e}")
    
    # Test 3: Perform JSON matching
    print("\n3️⃣ Performing JSON matching...")
    
    try:
        response = requests.post(
            "http://127.0.0.1:9090/api/json-match",
            json={"url": test_url},
            timeout=120
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ JSON matching completed")
            print(f"   Matched count: {data.get('matched_count', 0)}")
            print(f"   Filter mode: {data.get('filter_mode', 'unknown')}")
            print(f"   Has full Excel: {data.get('has_full_excel', False)}")
            
            # Test 4: Check filter status after JSON matching
            print("\n4️⃣ Checking filter status after JSON matching...")
            
            response = requests.get("http://127.0.0.1:9090/api/get-filter-status", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print("✅ Filter status updated")
                print(f"   Current mode: {data.get('current_mode', 'unknown')}")
                print(f"   JSON matched count: {data.get('json_matched_count', 0)}")
                print(f"   Full Excel count: {data.get('full_excel_count', 0)}")
                print(f"   Can toggle: {data.get('can_toggle', False)}")
                
                if data.get('can_toggle', False):
                    # Test 5: Toggle to full Excel list
                    print("\n5️⃣ Testing toggle to full Excel list...")
                    
                    response = requests.post(
                        "http://127.0.0.1:9090/api/toggle-json-filter",
                        json={"filter_mode": "full_excel"},
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        print("✅ Toggle to full Excel successful")
                        print(f"   New mode: {data.get('filter_mode', 'unknown')}")
                        print(f"   Mode name: {data.get('mode_name', 'unknown')}")
                        print(f"   Available count: {data.get('available_count', 0)}")
                        print(f"   Previous mode: {data.get('previous_mode', 'unknown')}")
                        
                        # Test 6: Toggle back to JSON matched items
                        print("\n6️⃣ Testing toggle back to JSON matched items...")
                        
                        response = requests.post(
                            "http://127.0.0.1:9090/api/toggle-json-filter",
                            json={"filter_mode": "json_matched"},
                            timeout=10
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            print("✅ Toggle to JSON matched successful")
                            print(f"   New mode: {data.get('filter_mode', 'unknown')}")
                            print(f"   Mode name: {data.get('mode_name', 'unknown')}")
                            print(f"   Available count: {data.get('available_count', 0)}")
                            print(f"   Previous mode: {data.get('previous_mode', 'unknown')}")
                            
                            # Test 7: Test toggle functionality
                            print("\n7️⃣ Testing toggle functionality...")
                            
                            response = requests.post(
                                "http://127.0.0.1:9090/api/toggle-json-filter",
                                json={"filter_mode": "toggle"},
                                timeout=10
                            )
                            
                            if response.status_code == 200:
                                data = response.json()
                                print("✅ Toggle functionality working")
                                print(f"   New mode: {data.get('filter_mode', 'unknown')}")
                                print(f"   Mode name: {data.get('mode_name', 'unknown')}")
                                print(f"   Available count: {data.get('available_count', 0)}")
                            else:
                                print(f"❌ Toggle request failed: {response.status_code}")
                        else:
                            print(f"❌ Toggle to JSON matched failed: {response.status_code}")
                    else:
                        print(f"❌ Toggle to full Excel failed: {response.status_code}")
                else:
                    print("⚠️  Cannot toggle - no JSON matched items or full Excel list available")
            else:
                print(f"❌ Filter status check failed: {response.status_code}")
        else:
            print(f"❌ JSON matching failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"   Response: {response.text[:200]}...")
                
    except requests.exceptions.RequestException as e:
        print(f"❌ JSON matching request failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 Test completed")
    print("\n📝 Manual Testing Instructions:")
    print("1. Open the web interface in your browser")
    print("2. Upload an Excel file with product data")
    print("3. Perform JSON matching with a valid URL")
    print("4. Look for the new filter toggle button/control")
    print("5. Test switching between 'JSON Matched Items' and 'Full Excel List'")
    print("6. Verify that the available tags list updates accordingly")

if __name__ == "__main__":
    test_json_filter_toggle() 