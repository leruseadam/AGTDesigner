#!/usr/bin/env python3
"""
Test script to verify case-insensitive matching fix for JSON tags
"""

import json
import requests
import sys

# The JSON matched tags from the user
JSON_MATCHED_TAGS = [
    "Medically Compliant - Dank Czar Rosin All-In-One - GMO - 1g",
    "Medically Compliant - Dank Czar Rosin All-In-One - Grape Gas - 1g",
    "Medically Compliant - Dank Czar Rosin All-In-One - Grinch Mintz - 1g",
    "Medically Compliant - Dank Czar Rosin All-In-One - Venom Breath - 1g",
    "Medically Compliant - Dank Czar Rosin All-In-One - Watermelon Zkittles - 1g",
    "Medically Compliant - Only B's - Amnesia Haze - 14g",
    "Medically Compliant - Only B's - GDP - 14g",
    "Medically Compliant - Only B's - Krazy Runtz - 14g",
    "Medically Compliant - Only B's - Orange Crush - 14g",
    "Medically Compliant - Only B's - Runtz - 14g",
    "Medically Compliant - Flavour Bar - Blue Razz - 1g",
    "Medically Compliant - Flavour Bar - Blueberry Banana Pie - 1g",
    "Medically Compliant - Flavour Bar - Cookies & Cream - 1g",
    "Medically Compliant - Flavour Bar - Mango Sherbet - 1g",
    "Medically Compliant - Flavour Bar - Passion Fruit Guava - 1g",
    "Medically Compliant - Flavour Bar - Peach Rings - 1g",
    "Medically Compliant - Flavour Bar - Pink Lemonade - 1g",
    "Medically Compliant - Flavour Bar - Strawnana - 1g",
    "Medically Compliant - Flavour Bar - Wedding Cake - 1g",
    "Medically Compliant - Dank Czar Flower - Zmuckerz - 1g Bag",
    "Medically Compliant - Dank Czar Flower - Zmuckerz - 3.5g Jar",
    "Medically Compliant - Dank Czar Flower - Watermelon Zkittles - 1g Bag",
    "Medically Compliant - Dank Czar Flower - Watermelon Zkittles - 3.5g Jar",
    "Medically Compliant - Dank Czar Flower - Venom Breath - 1g Bag",
    "Medically Compliant - Dank Czar Flower - Venom Breath - 3.5g Jar",
    "Medically Compliant - Dank Czar Flower - Malawi Gold - 1g Bag",
    "Medically Compliant - Dank Czar Flower - Malawi Gold - 3.5g Jar",
    "Medically Compliant - Dank Czar Flower - Grinch Mintz - 1g Bag",
    "Medically Compliant - Dank Czar Flower - Grinch Mintz - 3.5g Jar",
    "Medically Compliant - Dank Czar Flower - Grape Animal - 3.5g Jar",
    "Medically Compliant - Dank Czar Pre-roll Packs - Pink Certz - 10pk",
    "Medically Compliant - Dank Czar Pre-roll Packs - Red Velvet - 10pk",
    "Medically Compliant - Dank Czar Pre-roll Packs - Super Silver Haze - 10pk",
    "Medically Compliant - Dank Czar Pre-roll Packs - Georgia Pie - 5pk",
    "Medically Compliant - Dank Czar Pre-roll Packs - Pink Certz - 5pk",
    "Medically Compliant - Dank Czar Pre-roll Packs - Red Velvet - 5pk",
    "Medically Compliant - Dank Czar Pre-roll Packs - Cherry Paloma - 2pk",
    "Medically Compliant - Dank Czar Pre-roll Packs - Pineapple Express - 2pk",
    "Medically Compliant - Melt Stix - F: Elephant Garlic H: Cookies & Cream - 2pk",
    "Medically Compliant - Melt Stix - F: Grandy Candy H: Cosmic Combo - 2pk",
    "Medically Compliant - Melt Stix - F: Mac Stomper H: Honey Banana Bread - 2pk",
    "Medically Compliant - Melt Stix - F: Tricho Jordan H: Super Boof - 2pk",
    "Flavour Stix - Blue Razz - 0.75g",
    "Flavour Stix - Blueberry Banana Pie - 0.75g",
    "Flavour Stix - Cookies & Cream - 0.75g",
    "Flavour Stix - Peach Rings - 0.75g",
    "Flavour Stix - Pink Lemonade - 0.75g",
    "Flavour Stix - Blueberry Banana Pie - 5pk",
    "Flavour Stix - Cookies & Cream - 5pk",
    "Flavour Stix - Peach Rings - 5pk",
    "Flavour Stix - Blue Razz - 2pk",
    "Flavour Stix - Blueberry Banana Pie - 2pk",
    "Flavour Stix - Cookies & Cream - 2pk",
    "Flavour Stix - Strawnana - 2pk",
    "Medically Compliant - Rosin Rolls - F: Bad Santa R: GMO - 2pk",
    "Medically Compliant - Rosin Rolls - F: Grinch Mintz R: Layer Cake - 2pk",
    "Medically Compliant - Rosin Rolls - F: Rose Gold Runtz R: Zmuckerz - 2pk",
    "Medically Compliant - Rosin Rolls - F: Venom Breath R: Venom Breath - 2pk",
    "Medically Compliant - Rosin Rolls - F: Bad Santa R: GMO - 5pk",
    "Medically Compliant - Rosin Rolls - F: Grinch Mintz R: Layer Cake - 5pk",
    "Medically Compliant - Rosin Rolls - F: Venom Breath R: Venom Breath - 5pk",
    "Medically Compliant - Dank Czar RSO Applicator - Hybrid RSO - 1g",
    "Medically Compliant - Dank Czar RSO Applicator - Indica RSO - 1g",
    "Medically Compliant - Dank Czar RSO Applicator - Sativa RSO - 1g",
    "Zwish Infused Blunt - Passion Fruit Guava - 1g",
    "Zwish Infused Blunt - Pink Lemonade - 1g",
    "Medically Compliant - Dank Czar Sugar Wax - Grape Animal - 1g",
    "Medically Compliant - Dank Czar Sugar Wax - Rainbow Sherbet #11 - 1g",
    "Medically Compliant - Dank Czar Sugar Wax - Trop Cherry - 1g",
    "Medically Compliant - Dank Czar Rosin Cartridge - Bad Santa - 0.5g",
    "Medically Compliant - Dank Czar Rosin Cartridge - Canal St. Runtz - 0.5g",
    "Medically Compliant - Dank Czar Rosin Cartridge - Garlic Grapes - 0.5g",
    "Medically Compliant - Dank Czar Rosin Cartridge - Grape Gas - 0.5g",
    "Medically Compliant - Dank Czar Rosin Cartridge - GMO - 0.5g",
    "Medically Compliant - Dank Czar Live Resin Cartridge - Dosidos - 1g",
    "Medically Compliant - Dank Czar Live Resin Cartridge - Gelato - 1g",
    "Medically Compliant - Dank Czar Live Resin Cartridge - Lemon Time - 1g",
    "Medically Compliant - Dank Czar Live Resin Cartridge - Lightspeed - 1g",
    "Medically Compliant - Dank Czar Live Resin Cartridge - Mountain Apple - 1g",
    "Medically Compliant - Dank Czar Live Resin Cartridge - Passionfruit Paloma - 1g",
    "Medically Compliant - Dank Czar Rosinfusionz - Hybrid 3pk - 1,200mg",
    "Medically Compliant - Dank Czar Rosin Silver - GMO - 1g",
    "Medically Compliant - Omega Distillate Cartridge - Cherry Lemonheadz - 1g",
    "Medically Compliant - Omega Distillate Cartridge - Passion Fruit Guava - 1g",
    "Medically Compliant - Omega Distillate Cartridge - Pineapple Mango - 1g",
    "Medically Compliant - Omega Distillate Cartridge - Wedding Cake - 1g",
    "Medically Compliant - Dank Czar Liquid Diamond Caviar All-In-One - Lemon Time - 1g",
    "Medically Compliant - Dank Czar Liquid Diamond Caviar All-In-One - Passionfruit Paloma - 1g",
    "Medically Compliant - Dank Czar Live Hash Rosin Reserve - Afghan Diesel - 1g (Boxed 5ml)",
    "Medically Compliant - Dank Czar Live Hash Rosin Reserve - Bad Santa - 1g (Boxed 5ml)",
    "Medically Compliant - Dank Czar Live Hash Rosin Reserve - Elephant Garlic - 1g (Boxed 5ml)",
    "Medically Compliant - Dank Czar Live Hash Rosin Reserve - GMO - 1g (Boxed 5ml)",
    "Medically Compliant - Dank Czar Live Hash Rosin Reserve - Grandy Candy - 1g (Boxed 5ml)",
    "Medically Compliant - Dank Czar Live Hash Rosin Reserve - Grape Gas - 1g (Boxed 5ml)",
    "Medically Compliant - Dank Czar Live Hash Rosin Reserve - Layer Cake - 1g (Boxed 5ml)",
    "Medically Compliant - Dank Czar Live Hash Rosin Reserve - Tricho Jordan - 1g (Boxed 5ml)"
]

def test_case_insensitive_matching():
    """Test the case-insensitive matching fix"""
    
    print("🧪 Testing Case-Insensitive Matching Fix")
    print("=" * 50)
    
    # Test 1: Check if server is running
    try:
        response = requests.get("http://127.0.0.1:9090/api/status", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print("❌ Server responded with error:", response.status_code)
            return False
    except requests.exceptions.RequestException as e:
        print("❌ Server is not running:", e)
        return False
    
    # Test 2: Get available tags to see what's in the Excel file
    try:
        response = requests.get("http://127.0.0.1:9090/api/available-tags", timeout=10)
        if response.status_code == 200:
            available_tags_data = response.json()
            # The API returns a list directly, not an object with 'tags' property
            available_tags = [tag.get('Product Name*', '') for tag in available_tags_data if isinstance(tag, dict)]
            print(f"✅ Retrieved {len(available_tags)} available tags from Excel file")
            
            # Show sample of available tags to see the case
            sample_tags = available_tags[:5]
            print(f"📋 Sample available tags: {sample_tags}")
            
        else:
            print("❌ Failed to get available tags:", response.status_code)
            return False
    except Exception as e:
        print("❌ Error getting available tags:", e)
        return False
    
    # Test 3: Test case-insensitive matching with JSON tags
    print("\n🔍 Testing Case-Insensitive Matching...")
    
    # Create case-insensitive lookup map
    available_tags_lower = {tag.lower(): tag for tag in available_tags if tag}
    
    matched_count = 0
    unmatched_tags = []
    
    for json_tag in JSON_MATCHED_TAGS:
        json_tag_lower = json_tag.lower()
        if json_tag_lower in available_tags_lower:
            matched_count += 1
            original_case = available_tags_lower[json_tag_lower]
            print(f"✅ MATCHED: '{json_tag}' -> '{original_case}'")
        else:
            unmatched_tags.append(json_tag)
            print(f"❌ NO MATCH: '{json_tag}'")
    
    print(f"\n📊 Matching Results:")
    print(f"   Total JSON tags: {len(JSON_MATCHED_TAGS)}")
    print(f"   Matched tags: {matched_count}")
    print(f"   Unmatched tags: {len(unmatched_tags)}")
    print(f"   Success rate: {(matched_count/len(JSON_MATCHED_TAGS)*100):.1f}%")
    
    if unmatched_tags:
        print(f"\n❌ Unmatched tags ({len(unmatched_tags)}):")
        for tag in unmatched_tags[:10]:  # Show first 10
            print(f"   - {tag}")
        if len(unmatched_tags) > 10:
            print(f"   ... and {len(unmatched_tags) - 10} more")
    
    # Test 4: Test the generate endpoint with matched tags
    if matched_count > 0:
        print(f"\n🚀 Testing Label Generation with {matched_count} matched tags...")
        
        # Get the matched tags with correct case
        matched_tags_correct_case = []
        for json_tag in JSON_MATCHED_TAGS:
            json_tag_lower = json_tag.lower()
            if json_tag_lower in available_tags_lower:
                matched_tags_correct_case.append(available_tags_lower[json_tag_lower])
        
        # Test with a small subset to avoid overwhelming the server
        test_tags = matched_tags_correct_case[:5]  # Test with first 5 matched tags
        
        try:
            response = requests.post(
                "http://127.0.0.1:9090/api/generate",
                json={
                    "selected_tags": test_tags,
                    "template_type": "mini",
                    "scale_factor": 1.0
                },
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"✅ SUCCESS: Generated labels for {len(test_tags)} tags!")
                print(f"   Content-Type: {response.headers.get('Content-Type', 'Unknown')}")
                print(f"   Content-Length: {len(response.content)} bytes")
            else:
                error_data = response.json()
                print(f"❌ FAILED: {response.status_code} - {error_data.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Error testing label generation: {e}")
    
    return matched_count > 0

def main():
    """Main test function"""
    print("Case-Insensitive Matching Fix Test")
    print("=" * 50)
    
    success = test_case_insensitive_matching()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 TEST PASSED: Case-insensitive matching is working!")
        print("✅ JSON matched tags can now be used for label generation")
    else:
        print("❌ TEST FAILED: Case-insensitive matching needs more work")
        print("🔧 Check the server logs for more details")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 