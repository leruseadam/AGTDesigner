#!/usr/bin/env python3
"""
REAL PROOF: Test script that simulates your actual JSON scenario with 32+ items.
This proves that the fixes actually work for your real use case.
"""

import requests
import json
import time
import sys

def test_real_json_scenario():
    """Test with a realistic JSON scenario that matches your actual data."""
    
    base_url = "http://127.0.0.1:5003"
    
    print("🔬 REAL PROOF: Testing JSON Matching with 32+ Items")
    print("=" * 60)
    
    # Create realistic JSON data similar to what you're actually using
    # This simulates a real inventory transfer with multiple products
    realistic_json_data = {
        "inventory_transfer_items": [
            # Flower products
            {"product_name": "Trophy Wife Platinum Line Pre-Roll", "vendor": "Grow Op Farms", "brand": "Grow Op", "inventory_type": "flower", "weight": "1g", "strain": "Trophy Wife"},
            {"product_name": "Gummy Bearz Sungrown", "vendor": "Grow Op Farms", "brand": "Grow Op", "inventory_type": "flower", "weight": "3.5g", "strain": "Gummy Bearz"},
            {"product_name": "Tropical Slushie Distillate Cartridge", "vendor": "Grow Op Farms", "brand": "Grow Op", "inventory_type": "vape", "weight": "1g", "strain": "Tropical Slushie"},
            {"product_name": "Kauai Live Resin Icing", "vendor": "Grow Op Farms", "brand": "Grow Op", "inventory_type": "concentrate", "weight": "1g", "strain": "Kauai"},
            {"product_name": "Sour OG Live Resin Sugar", "vendor": "Grow Op Farms", "brand": "Grow Op", "inventory_type": "concentrate", "weight": "1g", "strain": "Sour OG"},
            {"product_name": "Sunset Sherbert Live Resin Sugar", "vendor": "Grow Op Farms", "brand": "Grow Op", "inventory_type": "concentrate", "weight": "1g", "strain": "Sunset Sherbert"},
            
            # Additional flower variations
            {"product_name": "Blue Dream Premium", "vendor": "Grow Op Farms", "brand": "Grow Op", "inventory_type": "flower", "weight": "3.5g", "strain": "Blue Dream"},
            {"product_name": "Blue Dream Premium", "vendor": "Grow Op Farms", "brand": "Grow Op", "inventory_type": "flower", "weight": "7g", "strain": "Blue Dream"},
            {"product_name": "Blue Dream Premium", "vendor": "Grow Op Farms", "brand": "Grow Op", "inventory_type": "flower", "weight": "14g", "strain": "Blue Dream"},
            {"product_name": "Purple Punch Elite", "vendor": "Grow Op Farms", "brand": "Grow Op", "inventory_type": "flower", "weight": "3.5g", "strain": "Purple Punch"},
            {"product_name": "Purple Punch Elite", "vendor": "Grow Op Farms", "brand": "Grow Op", "inventory_type": "flower", "weight": "7g", "strain": "Purple Punch"},
            
            # Concentrate variations
            {"product_name": "Lemon Haze Live Resin", "vendor": "Grow Op Farms", "brand": "Grow Op", "inventory_type": "concentrate", "weight": "1g", "strain": "Lemon Haze"},
            {"product_name": "Lemon Haze Live Resin", "vendor": "Grow Op Farms", "brand": "Grow Op", "inventory_type": "concentrate", "weight": "2g", "strain": "Lemon Haze"},
            {"product_name": "Gelato Live Rosin", "vendor": "Grow Op Farms", "brand": "Grow Op", "inventory_type": "concentrate", "weight": "1g", "strain": "Gelato"},
            {"product_name": "Gelato Live Rosin", "vendor": "Grow Op Farms", "brand": "Grow Op", "inventory_type": "concentrate", "weight": "2g", "strain": "Gelato"},
            
            # Vape cartridges
            {"product_name": "Strawberry Cough Distillate", "vendor": "Grow Op Farms", "brand": "Grow Op", "inventory_type": "vape", "weight": "0.5g", "strain": "Strawberry Cough"},
            {"product_name": "Strawberry Cough Distillate", "vendor": "Grow Op Farms", "brand": "Grow Op", "inventory_type": "vape", "weight": "1g", "strain": "Strawberry Cough"},
            {"product_name": "Northern Lights Live Resin Cart", "vendor": "Grow Op Farms", "brand": "Grow Op", "inventory_type": "vape", "weight": "0.5g", "strain": "Northern Lights"},
            {"product_name": "Northern Lights Live Resin Cart", "vendor": "Grow Op Farms", "brand": "Grow Op", "inventory_type": "vape", "weight": "1g", "strain": "Northern Lights"},
            
            # Edibles
            {"product_name": "Cherry Gummies", "vendor": "Grow Op Farms", "brand": "Grow Op", "inventory_type": "edible", "weight": "100mg", "strain": "Cherry"},
            {"product_name": "Cherry Gummies", "vendor": "Grow Op Farms", "brand": "Grow Op", "inventory_type": "edible", "weight": "200mg", "strain": "Cherry"},
            {"product_name": "Chocolate Bars", "vendor": "Grow Op Farms", "brand": "Grow Op", "inventory_type": "edible", "weight": "100mg", "strain": "Chocolate"},
            {"product_name": "Chocolate Bars", "vendor": "Grow Op Farms", "brand": "Grow Op", "inventory_type": "edible", "weight": "200mg", "strain": "Chocolate"},
            
            # Pre-rolls
            {"product_name": "Wedding Cake Pre-Roll", "vendor": "Grow Op Farms", "brand": "Grow Op", "inventory_type": "flower", "weight": "1g", "strain": "Wedding Cake"},
            {"product_name": "Wedding Cake Pre-Roll", "vendor": "Grow Op Farms", "brand": "Grow Op", "inventory_type": "flower", "weight": "2g", "strain": "Wedding Cake"},
            {"product_name": "Girl Scout Cookies Pre-Roll", "vendor": "Grow Op Farms", "brand": "Grow Op", "inventory_type": "flower", "weight": "1g", "strain": "Girl Scout Cookies"},
            {"product_name": "Girl Scout Cookies Pre-Roll", "vendor": "Grow Op Farms", "brand": "Grow Op", "inventory_type": "flower", "weight": "2g", "strain": "Girl Scout Cookies"},
            
            # Topicals
            {"product_name": "CBD Relief Cream", "vendor": "Grow Op Farms", "brand": "Grow Op", "inventory_type": "topical", "weight": "30ml", "strain": "CBD"},
            {"product_name": "CBD Relief Cream", "vendor": "Grow Op Farms", "brand": "Grow Op", "inventory_type": "topical", "weight": "60ml", "strain": "CBD"},
            {"product_name": "THC Pain Balm", "vendor": "Grow Op Farms", "brand": "Grow Op", "inventory_type": "topical", "weight": "30ml", "strain": "THC"},
            {"product_name": "THC Pain Balm", "vendor": "Grow Op Farms", "brand": "Grow Op", "inventory_type": "topical", "weight": "60ml", "strain": "THC"},
            
            # Additional products to reach 32+
            {"product_name": "OG Kush Premium", "vendor": "Grow Op Farms", "brand": "Grow Op", "inventory_type": "flower", "weight": "3.5g", "strain": "OG Kush"},
            {"product_name": "OG Kush Premium", "vendor": "Grow Op Farms", "brand": "Grow Op", "inventory_type": "flower", "weight": "7g", "strain": "OG Kush"},
            {"product_name": "White Widow Elite", "vendor": "Grow Op Farms", "brand": "Grow Op", "inventory_type": "flower", "weight": "3.5g", "strain": "White Widow"},
            {"product_name": "White Widow Elite", "vendor": "Grow Op Farms", "brand": "Grow Op", "inventory_type": "flower", "weight": "7g", "strain": "White Widow"},
            {"product_name": "Jack Herer Live Resin", "vendor": "Grow Op Farms", "brand": "Grow Op", "inventory_type": "concentrate", "weight": "1g", "strain": "Jack Herer"},
            {"product_name": "Jack Herer Live Resin", "vendor": "Grow Op Farms", "brand": "Grow Op", "inventory_type": "concentrate", "weight": "2g", "strain": "Jack Herer"}
        ],
        "from_license_name": "Grow Op Farms"
    }
    
    total_items = len(realistic_json_data['inventory_transfer_items'])
    print(f"📊 REAL SCENARIO: {total_items} products (similar to your actual data)")
    print(f"📊 This includes products with same names but different weights/strains/types")
    
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
            
            print(f"\n📊 REAL RESULTS:")
            print(f"   - Input items: {total_items}")
            print(f"   - matched_count: {matched_count}")
            print(f"   - available_tags length: {len(available_tags)}")
            print(f"   - json_matched_tags length: {len(json_matched_tags)}")
            
            # CRITICAL TEST: Verify ALL items were processed
            if matched_count == total_items:
                print(f"\n🎉 SUCCESS: All {total_items} items were processed!")
                print(f"🎉 This proves the fixes are working for your real scenario!")
            else:
                print(f"\n❌ FAILURE: Only {matched_count}/{total_items} items were processed")
                print(f"❌ This means the fixes are NOT working")
                return False
                
            if len(available_tags) == total_items:
                print(f"✅ SUCCESS: All {total_items} items are in available_tags!")
            else:
                print(f"❌ FAILURE: Only {len(available_tags)}/{total_items} items in available_tags")
                return False
                
            if len(json_matched_tags) == total_items:
                print(f"✅ SUCCESS: All {total_items} items are in json_matched_tags!")
            else:
                print(f"❌ FAILURE: Only {len(json_matched_tags)}/{total_items} items in json_matched_tags")
                return False
            
            # Show some sample products to prove they're all there
            print(f"\n📋 SAMPLE PRODUCTS PROCESSED:")
            for i, product in enumerate(available_tags[:10]):  # Show first 10
                if isinstance(product, dict):
                    name = product.get('Product Name*', product.get('ProductName', 'Unknown'))
                    weight = product.get('Weight*', product.get('Weight', 'Unknown'))
                    strain = product.get('Product Strain', 'Unknown')
                    print(f"   {i+1}. {name} - {weight} - {strain}")
            
            if len(available_tags) > 10:
                print(f"   ... and {len(available_tags) - 10} more products")
                
        else:
            print(f"❌ JSON matching failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during JSON matching test: {e}")
        return False
    
    print(f"\n🎉 REAL PROOF COMPLETE!")
    print(f"🎉 JSON matching now processes ALL {total_items} items correctly!")
    return True

def main():
    """Main test function."""
    print("Starting REAL PROOF Test...")
    
    success = test_real_json_scenario()
    
    if success:
        print("\n✅ REAL PROOF: JSON matching fixes are working correctly!")
        print("   - All 32+ items are processed without loss")
        print("   - No deduplication is removing legitimate items")
        print("   - This proves the fixes work for your actual use case")
        sys.exit(0)
    else:
        print("\n❌ REAL PROOF: JSON matching still has issues!")
        print("   - Some items are being lost during processing")
        print("   - Additional fixes may be needed")
        sys.exit(1)

if __name__ == "__main__":
    main()
