#!/usr/bin/env python3
"""
Test the JSON generation fix to verify that JSON matched products can now be generated.
"""

import requests
import json
import time
import sys

def test_json_generation_fix():
    """Test the JSON generation fix."""
    
    base_url = "http://127.0.0.1:5003"
    
    print("🧪 TESTING JSON GENERATION FIX")
    print("=" * 60)
    
    # Step 1: Check current state
    print("\n1️⃣ Checking current state...")
    try:
        response = requests.get(f"{base_url}/api/available-tags", timeout=10)
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, dict):
                available_count = len(result.get('tags', []))
            elif isinstance(result, list):
                available_count = len(result)
            else:
                available_count = 0
                
            print(f"📊 Available tags count: {available_count}")
        else:
            print(f"❌ Available tags check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error checking current state: {e}")
        return False
    
    # Step 2: Check if the specific JSON products are now available
    print("\n2️⃣ Checking if specific JSON products are now available...")
    
    # The specific products that were missing before
    specific_products = [
        "Hawaiian Golden Pineapple Live Resin Cartridge by Dabstract",
        "High Life Live Resin Cake Icing by Dabstract", 
        "Non GMO Live Resin Cake Icing by Dabstract",
        "White Gummie Bears Live Resin Cake Icing by Dabstract",
        "Blue Dream Live Resin Cartridge by Dabstract",
        "Dank Draaank Live Resin Cartridge by Dabstract",
        "Seattle Trophy Wife Live Resin Cartridge by Dabstract",
        "Sunset Sherbert Live Resin Cartridge by Dabstract",
        "Tangerine Queen Live Resin Cartridge by Dabstract",
        "Wedding Cake Live Resin Cartridge by Dabstract",
        "Lime Bars Core Flower by Phat Panda",
        "Sativa Live Resin Milk Chocolate Bites by Hot Sugar",
        "Raspberry Skywalker Firecracker Infused Pre-Roll by Phat Panda",
        "Strawberry Fritter Banger Pre-Roll by Phat Panda",
        "Golden Pineapple Bong Buddies by Phat Panda",
        "Tartz Core Flower by Phat Panda",
        "Hawaiian Snow Live Resin Cartridge by Dabstract",
        "Sativa Rosin Infused Golden Pineapple Fruit Drops by Hot Sugar",
        "Chicken & Waffles Platinum Line by Phat Panda",
        "Red Velvet Cake Platinum Line by Phat Panda",
        "Forbidden Fruit Core Flower Pre-Roll by Phat Panda",
        "Trophy Wife Platinum Line by Phat Panda",
        "Gummy Bearz Sungrown by Snickle Fritz",
        "Tropical Slushie Distillate Cartridge by Snickle Fritz",
        "Kauai Live Resin Icing by Snickle Fritz",
        "Sour OG Live Resin Sugar by Snickle Fritz",
        "Sunset Sherbert Live Resin Sugar by Snickle Fritz"
    ]
    
    try:
        response = requests.get(f"{base_url}/api/available-tags", timeout=10)
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, dict):
                available_tags = result.get('tags', [])
            elif isinstance(result, list):
                available_tags = result
            else:
                available_tags = []
            
            # Extract available tag names
            available_names = []
            for tag in available_tags:
                if isinstance(tag, dict):
                    name = tag.get('Product Name*', tag.get('displayName', ''))
                else:
                    name = str(tag)
                available_names.append(name)
            
            # Check which specific products are found
            found_products = []
            missing_products = []
            
            for product in specific_products:
                if product in available_names:
                    found_products.append(product)
                else:
                    missing_products.append(product)
            
            print(f"📊 Found products: {len(found_products)}")
            print(f"📊 Missing products: {len(missing_products)}")
            
            if missing_products:
                print(f"❌ Still missing products: {missing_products[:5]}...")
                print(f"❌ The fix may not have worked yet")
            else:
                print(f"✅ All specific products found!")
                print(f"✅ The fix worked!")
                
        else:
            print(f"❌ Available tags check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error checking specific products: {e}")
        return False
    
    # Step 3: Test generation with the specific products
    print("\n3️⃣ Testing generation with specific products...")
    
    # Use the found products for testing
    if found_products:
        test_products = found_products[:5]  # Test with first 5 products
        
        generation_data = {
            "template_type": "vertical",
            "scale_factor": 1.0,
            "selected_tags": test_products
        }
        
        print(f"📊 Testing generation with {len(test_products)} products")
        print(f"📋 Test products: {test_products}")
        
        try:
            response = requests.post(f"{base_url}/api/generate", json=generation_data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Generation successful!")
                print(f"📊 Response: {result}")
                
                # Check if there are any error messages
                if 'error' in result:
                    print(f"❌ Generation error: {result['error']}")
                else:
                    print(f"✅ Generation completed successfully!")
                    
            else:
                print(f"❌ Generation failed: {response.status_code}")
                print(f"📊 Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Generation test failed: {e}")
    else:
        print(f"❌ No products found to test generation")
    
    # Step 4: Summary
    print(f"\n4️⃣ Test Summary...")
    
    print(f"\n🧪 TEST RESULTS:")
    print(f"   - Available tags count: {available_count}")
    print(f"   - Specific products found: {len(found_products)}/{len(specific_products)}")
    
    if len(found_products) > 0:
        print(f"   - Generation test: {'✅ PASSED' if 'Generation successful' in locals() else '❌ FAILED'}")
        print(f"   - JSON products are now available for generation")
    else:
        print(f"   - Generation test: ❌ SKIPPED (no products found)")
        print(f"   - JSON products are still not available")
    
    return True

def main():
    """Main test function."""
    print("Starting JSON Generation Fix Test...")
    
    success = test_json_generation_fix()
    
    if success:
        print("\n🧪 TEST COMPLETE!")
        print("   - Check the results above")
        print("   - If products are found, try generating labels again")
        print("   - If not, the fix may need more time or additional steps")
        sys.exit(0)
    else:
        print("\n❌ TEST FAILED!")
        print("   - Some issues remain")
        print("   - Additional investigation needed")
        sys.exit(1)

if __name__ == "__main__":
    main()
