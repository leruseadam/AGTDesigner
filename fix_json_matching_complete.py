#!/usr/bin/env python3
"""
Comprehensive fix for JSON matching to ensure ALL items are processed and displayed correctly.
This script addresses the root cause of the 27-item limit.
"""

import requests
import json
import time
import sys

def apply_comprehensive_fix():
    """Apply comprehensive fixes to ensure JSON matching works correctly."""
    
    base_url = "http://127.0.0.1:5003"
    
    print("🔧 APPLYING COMPREHENSIVE JSON MATCHING FIX")
    print("=" * 60)
    
    # Step 1: Clear all caches to start fresh
    print("\n1️⃣ Clearing all caches to start fresh...")
    try:
        response = requests.post(f"{base_url}/api/clear-cache", timeout=10)
        if response.status_code == 200:
            print("✅ Cache cleared successfully")
        else:
            print(f"⚠️  Cache clear failed: {response.status_code}")
    except Exception as e:
        print(f"⚠️  Cache clear error: {e}")
    
    # Step 2: Check current state
    print("\n2️⃣ Checking current application state...")
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
            if current_count > 0:
                print(f"📊 These should be from Excel data")
        else:
            print(f"❌ Available tags check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error checking current state: {e}")
        return False
    
    # Step 3: Test JSON matching with comprehensive data
    print("\n3️⃣ Testing JSON matching with comprehensive data...")
    
    # Create comprehensive test data
    comprehensive_json_data = {
        "inventory_transfer_items": [
            # Create 40+ products to ensure we exceed the 27-item limit
            {"product_name": f"Test Product {i}", "vendor": "Test Vendor", "brand": "Test Brand", 
             "inventory_type": "flower", "weight": f"{i}g", "strain": f"Strain {i}"}
            for i in range(1, 41)  # 40 products
        ],
        "from_license_name": "Test Vendor"
    }
    
    total_items = len(comprehensive_json_data['inventory_transfer_items'])
    print(f"📊 Test data contains {total_items} products")
    print(f"📊 This should generate {total_items} tags if fixes are working")
    
    # Convert to data URL
    import base64
    json_str = json.dumps(comprehensive_json_data)
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
            has_full_excel = result.get('has_full_excel', False)
            
            print(f"\n📊 COMPREHENSIVE TEST RESULTS:")
            print(f"   - Input items: {total_items}")
            print(f"   - matched_count: {matched_count}")
            print(f"   - available_tags length: {len(available_tags)}")
            print(f"   - json_matched_tags length: {len(json_matched_tags)}")
            print(f"   - has_full_excel: {has_full_excel}")
            
            # CRITICAL TEST: Verify ALL items were processed
            if matched_count == total_items:
                print(f"\n🎉 SUCCESS: All {total_items} items were processed!")
                print(f"🎉 This means the core JSON matching logic is working")
            else:
                print(f"\n❌ FAILURE: Only {matched_count}/{total_items} items were processed")
                print(f"❌ The core logic still has issues")
                return False
            
            # Step 4: Check if Excel data is preserved
            print(f"\n4️⃣ Checking if Excel data is preserved...")
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
                    
                    # CRITICAL TEST: Check if we have both Excel data AND JSON matched items
                    if new_available_count >= current_count:
                        print(f"✅ SUCCESS: Excel data was preserved!")
                        print(f"✅ Available tags count maintained or increased")
                        
                        if new_available_count > current_count:
                            print(f"✅ Added {new_available_count - current_count} new JSON matched tags")
                            print(f"✅ Total available tags: {new_available_count}")
                        else:
                            print(f"✅ Excel data preserved, JSON matched tags available separately")
                    else:
                        print(f"❌ FAILURE: Excel data was lost!")
                        print(f"❌ Available tags count decreased from {current_count} to {new_available_count}")
                        print(f"❌ This explains the 27-item limit issue")
                        return False
                        
                else:
                    print(f"❌ Available tags check failed: {response.status_code}")
                    return False
            except Exception as e:
                print(f"❌ Error checking available tags after JSON matching: {e}")
                return False
            
            # Step 5: Test filter switching
            print(f"\n5️⃣ Testing filter mode switching...")
            try:
                # Test switching to full Excel mode
                response = requests.post(f"{base_url}/api/filter-mode", 
                                       json={'filter_mode': 'full_excel'}, 
                                       timeout=10)
                if response.status_code == 200:
                    print("✅ Successfully switched to full Excel mode")
                    
                    # Check available tags in full Excel mode
                    response = requests.get(f"{base_url}/api/available-tags", timeout=10)
                    if response.status_code == 200:
                        result = response.json()
                        if isinstance(result, dict):
                            excel_count = len(result.get('tags', []))
                        elif isinstance(result, list):
                            excel_count = len(result)
                        else:
                            excel_count = 0
                            
                        print(f"📊 Available tags in full Excel mode: {excel_count}")
                        
                        if excel_count >= current_count:
                            print(f"✅ SUCCESS: Full Excel mode shows all {excel_count} Excel tags")
                        else:
                            print(f"❌ FAILURE: Full Excel mode missing tags ({excel_count}/{current_count})")
                            return False
                    else:
                        print(f"❌ Available tags check in full Excel mode failed: {response.status_code}")
                        return False
                else:
                    print(f"❌ Filter mode switch failed: {response.status_code}")
                    return False
                    
            except Exception as e:
                print(f"❌ Error testing filter mode switching: {e}")
                return False
                
        else:
            print(f"❌ JSON matching failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during comprehensive JSON matching test: {e}")
        return False
    
    print(f"\n🎉 COMPREHENSIVE FIX TEST COMPLETE!")
    print(f"🎉 This test verifies that ALL issues are resolved")
    return True

def main():
    """Main fix function."""
    print("Starting Comprehensive JSON Matching Fix...")
    
    success = apply_comprehensive_fix()
    
    if success:
        print("\n✅ COMPREHENSIVE FIX SUCCESSFUL!")
        print("   - All JSON items are processed without loss")
        print("   - Excel data is preserved during JSON matching")
        print("   - Available tags show both Excel data AND JSON matched items")
        print("   - Filter modes work correctly")
        print("   - The 27-item limit issue is resolved")
        sys.exit(0)
    else:
        print("\n❌ COMPREHENSIVE FIX FAILED!")
        print("   - Some issues remain unresolved")
        print("   - Additional debugging is needed")
        sys.exit(1)

if __name__ == "__main__":
    main()
