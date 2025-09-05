#!/usr/bin/env python3
"""
Test script that simulates the user's exact workflow to see where the 27-item limit is coming from.
This will help identify the exact point where items are being lost.
"""

import requests
import json
import time
import sys

def test_user_workflow():
    """Test the user's exact workflow to see where items are lost."""
    
    base_url = "http://127.0.0.1:5003"
    
    print("🔬 TESTING USER WORKFLOW - Where Are Items Lost?")
    print("=" * 60)
    
    # Test 1: Check current state
    print("\n1️⃣ Checking current application state...")
    try:
        response = requests.get(f"{base_url}/api/available-tags", timeout=10)
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, dict):
                current_count = len(result.get('tags', []))
            elif isinstance(result, list):
                current_count = len(result)
            else:
                current_count = 0
                
            print(f"📊 Current available tags: {current_count}")
            print(f"📊 These are from Excel data, not JSON matching")
        else:
            print(f"❌ Available tags check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error checking current state: {e}")
        return False
    
    # Test 2: Simulate JSON matching with realistic data
    print("\n2️⃣ Simulating JSON matching with realistic data...")
    
    # Create data that matches your actual scenario
    realistic_json_data = {
        "inventory_transfer_items": [
            # Simulate your actual products - these should all be processed
            {"product_name": "Product 1", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "flower", "weight": "1g", "strain": "Strain 1"},
            {"product_name": "Product 2", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "flower", "weight": "3.5g", "strain": "Strain 2"},
            {"product_name": "Product 3", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "concentrate", "weight": "1g", "strain": "Strain 3"},
            {"product_name": "Product 4", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "concentrate", "weight": "2g", "strain": "Strain 4"},
            {"product_name": "Product 5", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "vape", "weight": "0.5g", "strain": "Strain 5"},
            {"product_name": "Product 6", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "vape", "weight": "1g", "strain": "Strain 6"},
            {"product_name": "Product 7", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "edible", "weight": "100mg", "strain": "Strain 7"},
            {"product_name": "Product 8", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "edible", "weight": "200mg", "strain": "Strain 8"},
            {"product_name": "Product 9", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "flower", "weight": "7g", "strain": "Strain 9"},
            {"product_name": "Product 10", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "flower", "weight": "14g", "strain": "Strain 10"},
            {"product_name": "Product 11", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "concentrate", "weight": "3g", "strain": "Strain 11"},
            {"product_name": "Product 12", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "concentrate", "weight": "4g", "strain": "Strain 12"},
            {"product_name": "Product 13", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "vape", "weight": "1.5g", "strain": "Strain 13"},
            {"product_name": "Product 14", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "vape", "weight": "2g", "strain": "Strain 14"},
            {"product_name": "Product 15", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "edible", "weight": "300mg", "strain": "Strain 15"},
            {"product_name": "Product 16", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "edible", "weight": "400mg", "strain": "Strain 16"},
            {"product_name": "Product 17", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "flower", "weight": "28g", "strain": "Strain 17"},
            {"product_name": "Product 18", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "flower", "weight": "56g", "strain": "Strain 18"},
            {"product_name": "Product 19", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "concentrate", "weight": "5g", "strain": "Strain 19"},
            {"product_name": "Product 20", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "concentrate", "weight": "6g", "strain": "Strain 20"},
            {"product_name": "Product 21", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "vape", "weight": "2.5g", "strain": "Strain 21"},
            {"product_name": "Product 22", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "vape", "weight": "3g", "strain": "Strain 22"},
            {"product_name": "Product 23", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "edible", "weight": "500mg", "strain": "Strain 23"},
            {"product_name": "Product 24", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "edible", "weight": "600mg", "strain": "Strain 24"},
            {"product_name": "Product 25", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "flower", "weight": "112g", "strain": "Strain 25"},
            {"product_name": "Product 26", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "flower", "weight": "224g", "strain": "Strain 26"},
            {"product_name": "Product 27", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "concentrate", "weight": "7g", "strain": "Strain 27"},
            {"product_name": "Product 28", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "concentrate", "weight": "8g", "strain": "Strain 28"},
            {"product_name": "Product 29", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "vape", "weight": "3.5g", "strain": "Strain 29"},
            {"product_name": "Product 30", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "vape", "weight": "4g", "strain": "Strain 30"},
            {"product_name": "Product 31", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "edible", "weight": "700mg", "strain": "Strain 31"},
            {"product_name": "Product 32", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "edible", "weight": "800mg", "strain": "Strain 32"},
            {"product_name": "Product 33", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "flower", "weight": "448g", "strain": "Strain 33"},
            {"product_name": "Product 34", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "flower", "weight": "896g", "strain": "Strain 34"},
            {"product_name": "Product 35", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "concentrate", "weight": "9g", "strain": "Strain 35"},
            {"product_name": "Product 36", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "concentrate", "weight": "10g", "strain": "Strain 36"},
            {"product_name": "Product 37", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "vape", "weight": "4.5g", "strain": "Strain 37"}
        ],
        "from_license_name": "Test Vendor"
    }
    
    total_items = len(realistic_json_data['inventory_transfer_items'])
    print(f"📊 Test data contains {total_items} products")
    print(f"📊 This should generate {total_items} tags if fixes are working")
    
    # Convert to data URL
    import base64
    json_str = json.dumps(realistic_json_data)
    data_url = f"data:application/json;base64,{base64.b64encode(json_str.encode()).decode()}"
    
    # Test JSON matching
    print(f"\n🔬 Testing JSON matching with {total_items} products...")
    try:
        response = requests.post(f"{base_url}/api/json-match", 
                               json={'url': data_url}, 
                               timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ JSON matching request successful")
            
            # Check the response data
            matched_count = result.get('matched_count', 0)
            available_tags = result.get('available_tags', [])
            json_matched_tags = result.get('json_matched_tags', [])
            
            print(f"\n📊 WORKFLOW RESULTS:")
            print(f"   - Input items: {total_items}")
            print(f"   - matched_count: {matched_count}")
            print(f"   - available_tags length: {len(available_tags)}")
            print(f"   - json_matched_tags length: {len(json_matched_tags)}")
            
            # CRITICAL TEST: Verify ALL items were processed
            if matched_count == total_items:
                print(f"\n🎉 SUCCESS: All {total_items} items were processed!")
                print(f"🎉 This means the fixes ARE working in isolation")
                print(f"🎉 The issue must be with your specific JSON data or workflow")
            else:
                print(f"\n❌ FAILURE: Only {matched_count}/{total_items} items were processed")
                print(f"❌ This means the fixes are NOT working")
                print(f"❌ The issue is in the core JSON matching logic")
                return False
            
            # Test 3: Check if the tags are now in available tags
            print(f"\n3️⃣ Checking if JSON matched tags are now in available tags...")
            time.sleep(2)  # Wait for cache to update
            
            try:
                response = requests.get(f"{base_url}/api/available-tags", timeout=10)
                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, dict):
                        new_available_count = len(result.get('tags', []))
                    elif isinstance(result, list):
                        new_available_count = len(result)
                    else:
                        new_available_count = 0
                        
                    print(f"📊 Available tags after JSON matching: {new_available_count}")
                    print(f"📊 Previous count: {current_count}")
                    
                    if new_available_count > current_count:
                        print(f"✅ SUCCESS: JSON matched tags were added to available tags!")
                        print(f"✅ Added {new_available_count - current_count} new tags")
                    else:
                        print(f"❌ FAILURE: No new tags were added to available tags")
                        print(f"❌ This explains why you only see 27 tags")
                        
                else:
                    print(f"❌ Available tags check failed: {response.status_code}")
            except Exception as e:
                print(f"❌ Error checking available tags after JSON matching: {e}")
                
        else:
            print(f"❌ JSON matching failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during JSON matching test: {e}")
        return False
    
    print(f"\n🔍 WORKFLOW ANALYSIS COMPLETE!")
    print(f"🔍 This test shows whether the issue is in the core logic or your specific data")
    return True

def main():
    """Main test function."""
    print("Starting User Workflow Test...")
    
    success = test_user_workflow()
    
    if success:
        print("\n🔍 WORKFLOW ANALYSIS COMPLETE!")
        print("   - Check the results above")
        print("   - If all items are processed, the issue is with your specific data")
        print("   - If items are still lost, the issue is in the core logic")
    else:
        print("\n❌ WORKFLOW ANALYSIS FAILED!")
        print("   - The core JSON matching logic has issues")
        print("   - Additional fixes are needed")

if __name__ == "__main__":
    main()
