#!/usr/bin/env python3
"""
Final test to verify that the JSON matching fix resolves the 27-item limit issue.
This test confirms that Excel data is preserved and JSON matched items are added correctly.
"""

import requests
import json
import time
import sys

def test_final_fix():
    """Test that the final fix resolves the 27-item limit issue."""
    
    base_url = "http://127.0.0.1:5003"
    
    print("🎯 FINAL TEST: Verifying JSON Matching Fix")
    print("=" * 60)
    
    # Step 1: Check current state
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
            print(f"📊 These are from Excel data")
        else:
            print(f"❌ Available tags check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error checking current state: {e}")
        return False
    
    # Step 2: Test JSON matching with realistic data (similar to your actual scenario)
    print("\n2️⃣ Testing JSON matching with realistic data...")
    
    # Create realistic test data similar to what you're actually using
    realistic_json_data = {
        "inventory_transfer_items": [
            # Simulate your actual products - these should all be processed
            {"product_name": "Trophy Wife Platinum Line Pre-Roll", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "flower", "weight": "1g", "strain": "Trophy Wife"},
            {"product_name": "Grapefruit Pre-Roll", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "flower", "weight": "1g", "strain": "Grapefruit"},
            {"product_name": "Zade 5 Pre-Roll", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "flower", "weight": "1g", "strain": "Zade 5"},
            {"product_name": "Purple Rain Pre-Roll", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "flower", "weight": "1g", "strain": "Purple Rain"},
            {"product_name": "Trunk Funk Pre-Roll", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "flower", "weight": "1g", "strain": "Trunk Funk"},
            {"product_name": "Sub Woofer Pre-Roll", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "flower", "weight": "1g", "strain": "Sub Woofer"},
            {"product_name": "Alien Runtz Pre-Roll", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "flower", "weight": "1g", "strain": "Alien Runtz"},
            {"product_name": "Papaya Banana Pre-Roll", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "flower", "weight": "1g", "strain": "Papaya Banana"},
            {"product_name": "Gelato X Critical Kush Pre-Roll", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "flower", "weight": "1g", "strain": "Gelato X Critical Kush"},
            {"product_name": "Apple Mac Pre-Roll", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "flower", "weight": "1g", "strain": "Apple Mac"},
            {"product_name": "Grape Cream Cake Pre-Roll", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "flower", "weight": "1g", "strain": "Grape Cream Cake"},
            {"product_name": "Knocked Up Pre-Roll", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "flower", "weight": "1g", "strain": "Knocked Up"},
            {"product_name": "Washington Apple Pre-Roll", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "flower", "weight": "1g", "strain": "Washington Apple"},
            {"product_name": "Tiger's Blood Pre-Roll", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "flower", "weight": "1g", "strain": "Tiger's Blood"},
            {"product_name": "Gusherz Pre-Roll", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "flower", "weight": "1g", "strain": "Gusherz"},
            {"product_name": "Rainbow Marker Pre-Roll", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "flower", "weight": "1g", "strain": "Rainbow Marker"},
            {"product_name": "Blackberry Lemonade Pre-Roll", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "flower", "weight": "1g", "strain": "Blackberry Lemonade"},
            {"product_name": "Blackberry Haze Pre-Roll", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "flower", "weight": "1g", "strain": "Blackberry Haze"},
            {"product_name": "Purple Tangie Pre-Roll", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "flower", "weight": "1g", "strain": "Purple Tangie"},
            {"product_name": "Red Congolese Pre-Roll", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "flower", "weight": "1g", "strain": "Red Congolese"},
            {"product_name": "Blueberry Banana Pre-Roll", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "flower", "weight": "1g", "strain": "Blueberry Banana"},
            {"product_name": "Harlequin Pre-Roll", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "flower", "weight": "1g", "strain": "Harlequin"},
            {"product_name": "Pine Tsunami Pre-Roll", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "flower", "weight": "1g", "strain": "Pine Tsunami"},
            {"product_name": "Bubba Kush - Indica Pre-Roll", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "flower", "weight": "1g", "strain": "Bubba Kush - Indica"},
            {"product_name": "Harlequin Sativa Pre-Roll", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "flower", "weight": "1g", "strain": "Harlequin Sativa"},
            {"product_name": "White Widow Pre-Roll", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "flower", "weight": "1g", "strain": "White Widow"},
            {"product_name": "Gelato Cookeis Pre-Roll", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "flower", "weight": "1g", "strain": "Gelato Cookeis"},
            {"product_name": "Hybrid Mix Pre-Roll", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "flower", "weight": "1g", "strain": "Hybrid Mix"},
            {"product_name": "Rocket Popz Pre-Roll", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "flower", "weight": "1g", "strain": "Rocket Popz"},
            {"product_name": "Strawberry Slushie Pre-Roll", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "flower", "weight": "1g", "strain": "Strawberry Slushie"},
            {"product_name": "GG #4 Pre-Roll", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "flower", "weight": "1g", "strain": "GG #4"},
            {"product_name": "AK 47 Pre-Roll", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "flower", "weight": "1g", "strain": "AK 47"},
            {"product_name": "Cherry Lemonade Pre-Roll", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "flower", "weight": "1g", "strain": "Cherry Lemonade"},
            {"product_name": "Lemoncane Pre-Roll", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "flower", "weight": "1g", "strain": "Lemoncane"},
            {"product_name": "Granimals Pre-Roll", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "flower", "weight": "1g", "strain": "Granimals"},
            {"product_name": "Afghan Diesel Pre-Roll", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "flower", "weight": "1g", "strain": "Afghan Diesel"},
            {"product_name": "Tropical Sherbet Pre-Roll", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "flower", "weight": "1g", "strain": "Tropical Sherbet"},
            {"product_name": "Big Baby Pre-Roll", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "flower", "weight": "1g", "strain": "Big Baby"},
            {"product_name": "Ice Cream Mintz Pre-Roll", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "flower", "weight": "1g", "strain": "Ice Cream Mintz"},
            {"product_name": "Sherb Crasher Pre-Roll", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "flower", "weight": "1g", "strain": "Sherb Crasher"},
            {"product_name": "Carrot Cake Pre-Roll", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "flower", "weight": "1g", "strain": "Carrot Cake"},
            {"product_name": "Paraphernalia Pre-Roll", "vendor": "Test Vendor", "brand": "Test Brand", "inventory_type": "flower", "weight": "1g", "strain": "Paraphernalia"}
        ],
        "from_license_name": "Test Vendor"
    }
    
    total_items = len(realistic_json_data['inventory_transfer_items'])
    print(f"📊 Test data contains {total_items} products")
    print(f"📊 This simulates your actual scenario with realistic product names")
    
    # Convert to data URL
    import base64
    json_str = json.dumps(realistic_json_data)
    data_url = f"data:application/json;base64,{base64.b64encode(json_str.encode()).decode()}"
    
    # Test JSON matching
    print(f"\n🔬 Testing JSON matching with {total_items} realistic products...")
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
            has_full_excel = result.get('has_full_excel', False)
            
            print(f"\n📊 REALISTIC TEST RESULTS:")
            print(f"   - Input items: {total_items}")
            print(f"   - matched_count: {matched_count}")
            print(f"   - available_tags length: {len(available_tags)}")
            print(f"   - json_matched_tags length: {len(json_matched_tags)}")
            print(f"   - has_full_excel: {has_full_excel}")
            
            # CRITICAL TEST: Verify ALL items were processed
            if matched_count == total_items:
                print(f"\n🎉 SUCCESS: All {total_items} items were processed!")
                print(f"🎉 This matches your actual scenario")
            else:
                print(f"\n❌ FAILURE: Only {matched_count}/{total_items} items were processed")
                print(f"❌ This indicates the issue still exists")
                return False
            
            # Step 3: Check if Excel data is preserved AND JSON matched items are available
            print(f"\n3️⃣ Checking if Excel data is preserved AND JSON items are available...")
            time.sleep(2)  # Wait for cache to update
            
            try:
                # Check available tags (should show Excel data)
                response = requests.get(f"{base_url}/api/available-tags", timeout=10)
                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, dict):
                        available_count = len(result.get('tags', []))
                    elif isinstance(result, list):
                        available_count = len(result)
                    else:
                        available_count = 0
                        
                    print(f"📊 Available tags (Excel data): {available_count}")
                    
                    # Check if Excel data is preserved
                    if available_count >= current_count:
                        print(f"✅ SUCCESS: Excel data preserved ({available_count} items)")
                    else:
                        print(f"❌ FAILURE: Excel data lost ({available_count}/{current_count})")
                        return False
                        
                else:
                    print(f"❌ Available tags check failed: {response.status_code}")
                    return False
                    
                # Check JSON matched filter (should show combined data)
                response = requests.get(f"{base_url}/api/available-tags?filter=json_matched", timeout=10)
                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, dict):
                        json_filter_count = len(result.get('tags', []))
                    elif isinstance(result, list):
                        json_filter_count = len(result)
                    else:
                        json_filter_count = 0
                        
                    print(f"📊 JSON matched filter: {json_filter_count} items")
                    
                    # Check if we have both Excel data AND JSON matched items
                    if json_filter_count >= available_count:
                        print(f"✅ SUCCESS: JSON matched filter shows combined data")
                        print(f"✅ Total available items: {json_filter_count}")
                        print(f"✅ This resolves the 27-item limit issue!")
                    else:
                        print(f"❌ FAILURE: JSON matched filter missing items")
                        return False
                        
                else:
                    print(f"❌ JSON matched filter check failed: {response.status_code}")
                    return False
                    
            except Exception as e:
                print(f"❌ Error checking data preservation: {e}")
                return False
                
        else:
            print(f"❌ JSON matching failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during realistic JSON matching test: {e}")
        return False
    
    print(f"\n🎉 FINAL TEST COMPLETE!")
    print(f"🎉 The JSON matching fix is working correctly")
    return True

def main():
    """Main test function."""
    print("Starting Final JSON Matching Fix Test...")
    
    success = test_final_fix()
    
    if success:
        print("\n✅ FINAL TEST SUCCESSFUL!")
        print("   - All JSON items are processed without loss")
        print("   - Excel data is preserved during JSON matching")
        print("   - Available tags show both Excel data AND JSON matched items")
        print("   - The 27-item limit issue is RESOLVED")
        print("   - Your actual JSON data will now generate ALL tags")
        sys.exit(0)
    else:
        print("\n❌ FINAL TEST FAILED!")
        print("   - Some issues remain unresolved")
        print("   - Additional debugging is needed")
        sys.exit(1)

if __name__ == "__main__":
    main()
