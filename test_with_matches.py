#!/usr/bin/env python3
"""
Test JSON matching with data that should actually match.
"""

import requests
import json
import time

def test_with_matches():
    """Test JSON matching with data that should match existing products."""
    
    print("🧪 Testing JSON Matching with Matches")
    print("=" * 45)
    
    base_url = "http://localhost:5001"
    
    try:
        # Step 1: Get initial available tags
        print("1. Getting initial available tags...")
        available_response = requests.get(f"{base_url}/api/available-tags")
        initial_available = available_response.json() if isinstance(available_response.json(), list) else []
        print(f"   Initial available tags: {len(initial_available)}")
        
        # Step 2: Create JSON data that should match existing products
        print("2. Creating JSON data with matching products...")
        
        # Create a simple HTTP server to serve the JSON data
        import subprocess
        import time
        import threading
        import os
        
        # Create test JSON file with products that should match
        test_json_data = [
            {
                "Product Name*": "Banana OG Distillate Cartridge by Hustler's Ambition - 1g",
                "Product Brand": "Hustler's Ambition",
                "Product Strain": "Banana OG",
                "Product Type*": "Vape Cartridge",
                "Description": "A test product that should match",
                "Weight*": "1",
                "Units": "g",
                "THC test result": "85.5",
                "CBD test result": "0.1",
                "Test result unit (% or mg)": "%",
                "Price": "45.00",
                "Vendor": "Test Vendor"
            },
            {
                "Product Name*": "Core Reactor Quartz Banger",
                "Product Brand": "Test Brand",
                "Product Strain": "Test Strain",
                "Product Type*": "Paraphernalia",
                "Description": "Another test product that should match",
                "Weight*": "1",
                "Units": "g",
                "THC test result": "0",
                "CBD test result": "0",
                "Test result unit (% or mg)": "%",
                "Price": "25.00",
                "Vendor": "Test Vendor"
            }
        ]
        
        # Save test data to a file
        with open("test_matching_products.json", "w") as f:
            json.dump(test_json_data, f)
        
        # Start HTTP server
        def start_server():
            subprocess.run(["python", "-m", "http.server", "8000"], cwd=os.getcwd(), capture_output=True)
        
        server_thread = threading.Thread(target=start_server, daemon=True)
        server_thread.start()
        time.sleep(2)  # Wait for server to start
        
        # Step 3: Perform JSON matching
        print("3. Performing JSON matching...")
        json_response = requests.post(f"{base_url}/api/json-match", 
                                    json={"url": "http://localhost:8000/test_matching_products.json"})
        
        if json_response.status_code == 200:
            data = json_response.json()
            print(f"   ✅ JSON matching successful")
            print(f"   Matched count: {data.get('matched_count', 0)}")
            print(f"   Filter mode: {data.get('filter_mode', 'unknown')}")
            
            # Step 4: Check available tags after JSON matching
            print("4. Checking available tags after JSON matching...")
            time.sleep(2)  # Wait for processing
            
            available_response = requests.get(f"{base_url}/api/available-tags")
            post_available = available_response.json() if isinstance(available_response.json(), list) else []
            print(f"   Post-match available tags: {len(post_available)}")
            
            # Step 5: Check if the available list changed
            if len(post_available) != len(initial_available):
                print(f"   ✅ Available list changed: {len(initial_available)} -> {len(post_available)}")
                return True
            else:
                print(f"   ❌ Available list unchanged: {len(post_available)}")
                return False
        else:
            print(f"   ❌ JSON matching failed: {json_response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Test error: {e}")
        return False

if __name__ == "__main__":
    success = test_with_matches()
    if success:
        print("\n🎉 Test PASSED: JSON matching with matches works!")
    else:
        print("\n💥 Test FAILED: Available list still showing default data.") 