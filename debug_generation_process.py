#!/usr/bin/env python3
"""
Debug the generation process to see why only 27 out of 40 tags are being processed.
This will help identify where tags are being lost during generation.
"""

import requests
import json
import time
import sys

def debug_generation_process():
    """Debug the generation process."""
    
    base_url = "http://127.0.0.1:5003"
    
    print("🔍 DEBUGGING GENERATION PROCESS - Why Only 27/40 Tags?")
    print("=" * 70)
    
    # Step 1: Check what tags are being sent to generation
    print("\n1️⃣ Checking what tags are being sent to generation...")
    
    # Simulate the exact same generation request as the frontend
    generation_data = {
        "template_type": "vertical",
        "scale_factor": 1.0,
        "selected_tags": [
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
    }
    
    print(f"📊 Sending {len(generation_data['selected_tags'])} tags to generation")
    print(f"📋 Sample tags: {generation_data['selected_tags'][:5]}")
    
    # Step 2: Check for duplicates in the selected tags
    print("\n2️⃣ Checking for duplicates in selected tags...")
    unique_tags = list(set(generation_data['selected_tags']))
    duplicate_count = len(generation_data['selected_tags']) - len(unique_tags)
    
    print(f"📊 Original tag count: {len(generation_data['selected_tags'])}")
    print(f"📊 Unique tag count: {len(unique_tags)}")
    print(f"📊 Duplicate count: {duplicate_count}")
    
    if duplicate_count > 0:
        print(f"⚠️  Found {duplicate_count} duplicate tags")
        print(f"⚠️  This could explain why only {len(unique_tags)} unique tags are processed")
        
        # Find the duplicates
        from collections import Counter
        tag_counts = Counter(generation_data['selected_tags'])
        duplicates = [tag for tag, count in tag_counts.items() if count > 1]
        print(f"📋 Duplicate tags: {duplicates}")
    else:
        print(f"✅ No duplicates found")
    
    # Step 3: Check if the tags exist in the available data
    print("\n3️⃣ Checking if tags exist in available data...")
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
            
            # Check how many of our selected tags exist in available data
            available_tag_names = []
            for tag in available_tags:
                if isinstance(tag, dict):
                    name = tag.get('Product Name*', tag.get('displayName', ''))
                else:
                    name = str(tag)
                available_tag_names.append(name)
            
            found_tags = []
            missing_tags = []
            
            for selected_tag in unique_tags:
                if selected_tag in available_tag_names:
                    found_tags.append(selected_tag)
                else:
                    missing_tags.append(selected_tag)
            
            print(f"📊 Found tags: {len(found_tags)}")
            print(f"📊 Missing tags: {len(missing_tags)}")
            
            if missing_tags:
                print(f"❌ Missing tags: {missing_tags}")
            else:
                print(f"✅ All selected tags found in available data")
                
        else:
            print(f"❌ Available tags check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error checking available tags: {e}")
    
    # Step 4: Try a test generation to see what happens
    print("\n4️⃣ Testing generation process...")
    try:
        # Use unique tags only
        test_generation_data = {
            "template_type": "vertical",
            "scale_factor": 1.0,
            "selected_tags": unique_tags
        }
        
        print(f"📊 Testing generation with {len(unique_tags)} unique tags")
        
        # Send the generation request
        response = requests.post(f"{base_url}/api/generate", json=test_generation_data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Generation successful")
            print(f"📊 Response: {result}")
            
            # Check if there are any error messages or warnings
            if 'error' in result:
                print(f"❌ Generation error: {result['error']}")
            if 'warning' in result:
                print(f"⚠️  Generation warning: {result['warning']}")
                
        else:
            print(f"❌ Generation failed: {response.status_code}")
            print(f"📊 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Generation test failed: {e}")
    
    # Step 5: Check the backend logs for any clues
    print("\n5️⃣ Analyzing the issue...")
    
    print(f"\n🔍 ANALYSIS:")
    print(f"   - Frontend sends 40 tags to generation")
    print(f"   - {duplicate_count} tags are duplicates")
    print(f"   - {len(unique_tags)} unique tags remain")
    print(f"   - Only 27 tags appear in final DOCX")
    
    print(f"\n🔍 POSSIBLE CAUSES:")
    print(f"   1. Duplicate tags are being filtered out")
    print(f"   2. Some tags don't exist in the database/Excel data")
    print(f"   3. Tag validation is removing some tags")
    print(f"   4. There's a hard limit of 27 tags in generation")
    print(f"   5. Some tags fail validation and are silently dropped")
    
    print(f"\n🔍 NEXT STEPS:")
    print(f"   1. Remove duplicate tags from selection")
    print(f"   2. Verify all tags exist in the data source")
    print(f"   3. Check backend logs for validation errors")
    print(f"   4. Test with fewer tags to isolate the issue")
    
    return True

def main():
    """Main diagnostic function."""
    print("Starting Generation Process Debug...")
    
    success = debug_generation_process()
    
    if success:
        print("\n🔍 DEBUG COMPLETE!")
        print("   - Check the analysis above for possible causes")
        print("   - Focus on duplicate tags and validation issues")
        print("   - Test with unique tags only")
        sys.exit(0)
    else:
        print("\n❌ DEBUG FAILED!")
        print("   - Some issues remain")
        print("   - Additional investigation needed")
        sys.exit(1)

if __name__ == "__main__":
    main()
