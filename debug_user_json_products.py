#!/usr/bin/env python3
"""
Debug why the user's specific 40 products are not being matched by JSON matching.
"""

import requests
import json
import time
import sys

def debug_user_json_products():
    """Debug the user's specific JSON products."""
    
    base_url = "http://127.0.0.1:5003"
    
    print("🔍 DEBUGGING USER'S SPECIFIC JSON PRODUCTS")
    print("=" * 60)
    
    # The user's specific 40 products from the frontend logs
    user_products = [
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
        "White Gummie Bears Live Resin Cake Icing by Dabstract",
        "Lime Bars Core Flower by Phat Panda",
        "Sativa Live Resin Milk Chocolate Bites by Hot Sugar",
        "Raspberry Skywalker Firecracker Infused Pre-Roll by Phat Panda",
        "Hawaiian Golden Pineapple Live Resin Cartridge by Dabstract",
        "Hawaiian Golden Pineapple Live Resin Cartridge by Dabstract",
        "Strawberry Fritter Banger Pre-Roll by Phat Panda",
        "Golden Pineapple Bong Buddies by Phat Panda",
        "Tartz Core Flower by Phat Panda",
        "Tartz Core Flower by Phat Panda",
        "Hawaiian Snow Live Resin Cartridge by Dabstract",
        "Tartz Core Flower by Phat Panda",
        "Hawaiian Snow Live Resin Cartridge by Dabstract",
        "Raspberry Skywalker Firecracker Infused Pre-Roll by Phat Panda",
        "Sativa Rosin Infused Golden Pineapple Fruit Drops by Hot Sugar",
        "Chicken & Waffles Platinum Line by Phat Panda",
        "Chicken & Waffles Platinum Line by Phat Panda",
        "Chicken & Waffles Platinum Line by Phat Panda",
        "Red Velvet Cake Platinum Line by Phat Panda",
        "Red Velvet Cake Platinum Line by Phat Panda",
        "Red Velvet Cake Platinum Line by Phat Panda",
        "Forbidden Fruit Core Flower Pre-Roll by Phat Panda",
        "Trophy Wife Platinum Line by Phat Panda",
        "Trophy Wife Platinum Line by Phat Panda",
        "Gummy Bearz Sungrown by Snickle Fritz",
        "Tropical Slushie Distillate Cartridge by Snickle Fritz",
        "Kauai Live Resin Icing by Snickle Fritz",
        "Sour OG Live Resin Sugar by Snickle Fritz",
        "Sunset Sherbert Live Resin Sugar by Snickle Fritz",
        "Lime Bars Core Flower by Phat Panda"
    ]
    
    print(f"📊 User's specific products: {len(user_products)}")
    
    # Step 1: Check if these products exist in the available tags
    print("\n1️⃣ Checking if user's products exist in available tags...")
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
            
            print(f"📊 Available tags count: {len(available_tags)}")
            
            # Extract available tag names
            available_names = []
            for tag in available_tags:
                if isinstance(tag, dict):
                    name = tag.get('Product Name*', tag.get('displayName', ''))
                else:
                    name = str(tag)
                available_names.append(name)
            
            # Check which user products are found
            found_products = []
            missing_products = []
            
            for product in user_products:
                if product in available_names:
                    found_products.append(product)
                else:
                    missing_products.append(product)
            
            print(f"📊 User products found in available tags: {len(found_products)}")
            print(f"📊 User products missing from available tags: {len(missing_products)}")
            
            if missing_products:
                print(f"❌ Missing products: {missing_products[:5]}...")
                if len(missing_products) > 5:
                    print(f"   ... and {len(missing_products) - 5} more")
            else:
                print(f"✅ All user products found in available tags")
                
        else:
            print(f"❌ Available tags check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error checking available tags: {e}")
        return False
    
    # Step 2: Check if these products exist in the database
    print("\n2️⃣ Checking if user's products exist in database...")
    try:
        from src.core.data.product_database import get_product_database
        product_db = get_product_database()
        
        if product_db:
            # Get unique user products
            unique_user_products = list(set(user_products))
            print(f"📊 Unique user products: {len(unique_user_products)}")
            
            # Check database for these products
            db_records = product_db.get_products_by_names(unique_user_products)
            
            if db_records:
                print(f"📊 Found {len(db_records)} products in database")
                
                # Show what was found
                found_names = []
                for record in db_records:
                    if isinstance(record, dict):
                        name = record.get('Product Name*', record.get('ProductName', ''))
                        if name:
                            found_names.append(name)
                
                print(f"📊 Database found: {found_names[:5]}...")
                if len(found_names) > 5:
                    print(f"   ... and {len(found_names) - 5} more")
                
                # Check which user products are missing from database
                missing_from_db = [p for p in unique_user_products if p not in found_names]
                print(f"📊 Missing from database: {len(missing_from_db)}")
                
                if missing_from_db:
                    print(f"❌ Missing from database: {missing_from_db[:5]}...")
                    if len(missing_from_db) > 5:
                        print(f"   ... and {len(missing_from_db) - 5} more")
                else:
                    print(f"✅ All user products found in database")
            else:
                print(f"❌ No user products found in database")
        else:
            print(f"❌ Product database not available")
            
    except Exception as e:
        print(f"❌ Error checking database: {e}")
    
    # Step 3: Check if these products need to be added via JSON matching
    print("\n3️⃣ Checking if user's products need JSON matching...")
    
    print(f"📊 The issue might be:")
    print(f"   1. User's products are not in the JSON data that was matched")
    print(f"   2. User needs to upload their JSON file with these specific products")
    print(f"   3. The JSON matching process didn't include these products")
    
    # Step 4: Test generation with the missing products
    print("\n4️⃣ Testing generation with missing products...")
    
    if 'missing_products' in locals() and missing_products:
        # Test with a few missing products
        test_products = missing_products[:3]
        
        generation_data = {
            "template_type": "vertical",
            "scale_factor": 1.0,
            "selected_tags": test_products
        }
        
        print(f"📊 Testing generation with {len(test_products)} missing products")
        print(f"📋 Test products: {test_products}")
        
        try:
            response = requests.post(f"{base_url}/api/generate", json=generation_data, timeout=30)
            
            if response.status_code == 200:
                content_length = len(response.content)
                print(f"✅ Generation successful!")
                print(f"📊 Content Length: {content_length} bytes")
                
                if content_length > 1000:
                    print(f"✅ DOCX file generated successfully!")
                    print(f"✅ Missing products can be generated!")
                else:
                    print(f"⚠️  Response seems too small for a DOCX file")
                    
            else:
                print(f"❌ Generation failed: {response.status_code}")
                print(f"📊 Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Generation test failed: {e}")
    else:
        print(f"✅ No missing products to test")
    
    # Step 5: Summary
    print(f"\n5️⃣ Summary...")
    
    print(f"\n🔍 ANALYSIS RESULTS:")
    print(f"   - User's specific products: {len(user_products)}")
    print(f"   - Found in available tags: {len(found_products) if 'found_products' in locals() else 'Unknown'}")
    print(f"   - Missing from available tags: {len(missing_products) if 'missing_products' in locals() else 'Unknown'}")
    print(f"   - Found in database: {len(found_names) if 'found_names' in locals() else 'Unknown'}")
    print(f"   - Missing from database: {len(missing_from_db) if 'missing_from_db' in locals() else 'Unknown'}")
    
    print(f"\n🔍 ROOT CAUSE:")
    if 'missing_products' in locals() and len(missing_products) > 0:
        print(f"   - User's specific products are not in the available tags")
        print(f"   - These products need to be added via JSON matching")
        print(f"   - User should upload their JSON file with these products")
    else:
        print(f"   - User's products are in the available tags")
        print(f"   - The issue might be in the generation process")
    
    return True

def main():
    """Main debug function."""
    print("Starting User JSON Products Debug...")
    
    success = debug_user_json_products()
    
    if success:
        print("\n🔍 DEBUG COMPLETE!")
        print("   - Check the results above for detailed analysis")
        print("   - The root cause should be clear now")
        sys.exit(0)
    else:
        print("\n❌ DEBUG FAILED!")
        print("   - Some issues remain")
        print("   - Additional investigation needed")
        sys.exit(1)

if __name__ == "__main__":
    main()
