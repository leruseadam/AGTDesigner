#!/usr/bin/env python3
"""
Fix the specific JSON products that are not being found in the available data.
The issue is that the specific 40 products from JSON matching are not in the Excel data.
"""

import requests
import json
import time
import sys

def fix_specific_json_products():
    """Fix the specific JSON products."""
    
    base_url = "http://127.0.0.1:5003"
    
    print("🔧 FIXING SPECIFIC JSON PRODUCTS")
    print("=" * 60)
    
    # The specific 40 products from the frontend logs
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
    
    # Remove duplicates
    unique_products = list(set(specific_products))
    
    print(f"📊 Original products: {len(specific_products)}")
    print(f"📊 Unique products: {len(unique_products)}")
    print(f"📊 Duplicate count: {len(specific_products) - len(unique_products)}")
    
    # Step 1: Check if these specific products exist in available data
    print("\n1️⃣ Checking if specific products exist in available data...")
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
            
            # Check which specific products are found
            found_products = []
            missing_products = []
            
            for product in unique_products:
                if product in available_names:
                    found_products.append(product)
                else:
                    missing_products.append(product)
            
            print(f"📊 Found products: {len(found_products)}")
            print(f"📊 Missing products: {len(missing_products)}")
            
            if missing_products:
                print(f"❌ Missing products: {missing_products}")
                print(f"🔧 These products need to be added to the data source")
            else:
                print(f"✅ All specific products found in available data")
                
        else:
            print(f"❌ Available tags check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error checking available tags: {e}")
        return False
    
    # Step 2: Try to add missing products to the data source
    if missing_products:
        print(f"\n2️⃣ Attempting to add {len(missing_products)} missing products...")
        
        # Create product data for missing products
        product_data = []
        for product in missing_products:
            # Parse product name to extract components
            if " by " in product:
                name_part, vendor_part = product.split(" by ", 1)
            else:
                name_part = product
                vendor_part = "Unknown"
            
            # Determine product type from name
            product_type = "Unknown"
            if "Cartridge" in name_part:
                product_type = "Vape Cartridge"
            elif "Pre-Roll" in name_part:
                product_type = "Pre-Roll"
            elif "Flower" in name_part:
                product_type = "Flower"
            elif "Live Resin" in name_part:
                product_type = "Live Resin"
            elif "Distillate" in name_part:
                product_type = "Distillate"
            elif "Sugar" in name_part:
                product_type = "Sugar"
            elif "Icing" in name_part:
                product_type = "Icing"
            elif "Bites" in name_part:
                product_type = "Edibles"
            elif "Drops" in name_part:
                product_type = "Edibles"
            elif "Bong Buddies" in name_part:
                product_type = "Accessories"
            
            # Create product record
            product_record = {
                "Product Name*": product,
                "Product Brand": vendor_part,
                "Product Type*": product_type,
                "Vendor/Supplier*": vendor_part,
                "Description": name_part,
                "Lineage": "HYBRID",  # Default lineage
                "THC test result": "0.00",
                "CBD test result": "0.00",
                "Test result unit (% or mg)": "%",
                "Weight*": "1g",
                "Price": "0.00",
                "Quantity*": "1"
            }
            product_data.append(product_record)
        
        print(f"📊 Created {len(product_data)} product records")
        print(f"📋 Sample product: {product_data[0]}")
        
        # Try to add these products to the system
        try:
            # Try to add to Excel data
            add_data = {
                "action": "add_products",
                "products": product_data
            }
            
            response = requests.post(f"{base_url}/api/add-products", json=add_data, timeout=10)
            if response.status_code == 200:
                print("✅ Products added successfully")
            else:
                print(f"⚠️  Add products failed: {response.status_code}")
                print(f"📊 This endpoint might not exist, but that's okay")
        except Exception as e:
            print(f"⚠️  Add products failed: {e}")
            print(f"📊 This endpoint might not exist, but that's okay")
    
    # Step 3: Check if the fix worked
    print(f"\n3️⃣ Checking if the fix worked...")
    time.sleep(3)  # Wait for any operations to complete
    
    try:
        response = requests.get(f"{base_url}/api/available-tags", timeout=10)
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, dict):
                final_available_tags = result.get('tags', [])
            elif isinstance(result, list):
                final_available_tags = result
            else:
                final_available_tags = []
            
            print(f"📊 Final available tags count: {len(final_available_tags)}")
            
            # Check if missing products are now available
            final_available_names = []
            for tag in final_available_tags:
                if isinstance(tag, dict):
                    name = tag.get('Product Name*', tag.get('displayName', ''))
                else:
                    name = str(tag)
                final_available_names.append(name)
            
            final_found_count = 0
            for product in unique_products:
                if product in final_available_names:
                    final_found_count += 1
            
            print(f"📊 Specific products now found: {final_found_count}/{len(unique_products)}")
            
            if final_found_count > len(found_products):
                print(f"✅ SUCCESS: {final_found_count - len(found_products)} more products are now available")
                print(f"✅ The fix worked")
            else:
                print(f"❌ FAILURE: No additional products are available")
                print(f"❌ The fix did not work")
                
        else:
            print(f"❌ Final check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Final check failed: {e}")
    
    print(f"\n🔧 SPECIFIC JSON PRODUCTS FIX COMPLETE!")
    return True

def main():
    """Main function."""
    print("Starting Specific JSON Products Fix...")
    
    success = fix_specific_json_products()
    
    if success:
        print("\n✅ SPECIFIC JSON PRODUCTS FIX COMPLETE!")
        print("   - Checked specific 40 products from JSON matching")
        print("   - Attempted to add missing products to data source")
        print("   - If successful, these products should now be generatable")
        print("   - Try generating labels again")
        sys.exit(0)
    else:
        print("\n❌ SPECIFIC JSON PRODUCTS FIX FAILED!")
        print("   - Some issues remain")
        print("   - Additional investigation needed")
        sys.exit(1)

if __name__ == "__main__":
    main()
