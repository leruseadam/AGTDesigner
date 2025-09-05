#!/usr/bin/env python3
"""
Test the JSON matching data to see what's actually being returned and why it's not found.
"""

import requests
import json
import time
import sys

def test_json_matching_data():
    """Test the JSON matching data."""
    
    base_url = "http://127.0.0.1:5003"
    
    print("🧪 TESTING JSON MATCHING DATA")
    print("=" * 60)
    
    # Step 1: Check what JSON matched tags are available
    print("\n1️⃣ Checking JSON matched tags...")
    try:
        response = requests.get(f"{base_url}/api/available-tags?filter=json_matched", timeout=10)
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, dict):
                json_tags = result.get('tags', [])
            elif isinstance(result, list):
                json_tags = result
            else:
                json_tags = []
            
            print(f"📊 JSON matched tags count: {len(json_tags)}")
            
            if json_tags:
                print(f"📋 Sample JSON tags:")
                for i, tag in enumerate(json_tags[:5]):
                    if isinstance(tag, dict):
                        name = tag.get('Product Name*', tag.get('ProductName', tag.get('displayName', 'Unknown')))
                        vendor = tag.get('Product Brand', tag.get('Vendor/Supplier*', 'Unknown'))
                        product_type = tag.get('Product Type*', 'Unknown')
                        print(f"   {i+1}. {name}")
                        print(f"      Vendor: {vendor}")
                        print(f"      Type: {product_type}")
                        print(f"      Keys: {list(tag.keys())}")
                    else:
                        print(f"   {i+1}. {tag}")
            else:
                print(f"❌ No JSON matched tags found")
                
        else:
            print(f"❌ JSON matched tags check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error checking JSON matched tags: {e}")
        return False
    
    # Step 2: Check if these JSON tags are in the main available tags
    print("\n2️⃣ Checking if JSON tags are in main available tags...")
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
            
            print(f"📊 Main available tags count: {len(available_tags)}")
            
            # Extract available tag names
            available_names = []
            for tag in available_tags:
                if isinstance(tag, dict):
                    name = tag.get('Product Name*', tag.get('displayName', ''))
                else:
                    name = str(tag)
                available_names.append(name)
            
            # Check which JSON tags are found
            found_count = 0
            missing_count = 0
            
            for tag in json_tags:
                if isinstance(tag, dict):
                    json_name = tag.get('Product Name*', tag.get('ProductName', tag.get('displayName', '')))
                else:
                    json_name = str(tag)
                
                if json_name in available_names:
                    found_count += 1
                else:
                    missing_count += 1
            
            print(f"📊 JSON tags found in main available tags: {found_count}")
            print(f"📊 JSON tags missing from main available tags: {missing_count}")
            
            if missing_count > 0:
                print(f"❌ Most JSON tags are not in the main available tags")
                print(f"❌ This explains why generation fails")
            else:
                print(f"✅ All JSON tags are in the main available tags")
                
        else:
            print(f"❌ Available tags check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error checking available tags: {e}")
        return False
    
    # Step 3: Check the actual JSON matching process
    print("\n3️⃣ Checking JSON matching process...")
    
    # The issue might be that JSON matching creates products that don't get added to the main available tags
    print(f"📊 The problem might be:")
    print(f"   1. JSON matching creates products but doesn't add them to main available tags")
    print(f"   2. JSON products are stored separately and not integrated")
    print(f"   3. The generation process only looks in main available tags")
    
    # Step 4: Test generation with JSON matched tags directly
    print("\n4️⃣ Testing generation with JSON matched tags directly...")
    
    if json_tags:
        # Use the actual JSON tags for generation
        test_products = []
        for tag in json_tags[:5]:  # Test with first 5
            if isinstance(tag, dict):
                name = tag.get('Product Name*', tag.get('ProductName', tag.get('displayName', '')))
                if name:
                    test_products.append(name)
        
        if test_products:
            generation_data = {
                "template_type": "vertical",
                "scale_factor": 1.0,
                "selected_tags": test_products
            }
            
            print(f"📊 Testing generation with {len(test_products)} JSON products")
            print(f"📋 Test products: {test_products}")
            
            try:
                response = requests.post(f"{base_url}/api/generate", json=generation_data, timeout=30)
                
                if response.status_code == 200:
                    content_length = len(response.content)
                    print(f"✅ Generation successful!")
                    print(f"📊 Content Length: {content_length} bytes")
                    
                    if content_length > 1000:
                        print(f"✅ DOCX file generated successfully!")
                        print(f"✅ JSON products can be generated directly")
                    else:
                        print(f"⚠️  Response seems too small for a DOCX file")
                        
                else:
                    print(f"❌ Generation failed: {response.status_code}")
                    print(f"📊 Response: {response.text}")
                    
            except Exception as e:
                print(f"❌ Generation test failed: {e}")
        else:
            print(f"❌ No valid product names found in JSON tags")
    else:
        print(f"❌ No JSON tags available for testing")
    
    # Step 5: Summary
    print(f"\n5️⃣ Summary...")
    
    print(f"\n🧪 TEST RESULTS:")
    print(f"   - JSON matched tags: {len(json_tags) if 'json_tags' in locals() else 'Unknown'}")
    print(f"   - Found in main available tags: {found_count if 'found_count' in locals() else 'Unknown'}")
    print(f"   - Missing from main available tags: {missing_count if 'missing_count' in locals() else 'Unknown'}")
    print(f"   - Direct generation test: {'✅ WORKING' if 'DOCX file generated successfully' in locals() else '❌ FAILED'}")
    
    print(f"\n🔍 ROOT CAUSE:")
    if 'missing_count' in locals() and missing_count > 0:
        print(f"   - JSON matched products are not being added to the main available tags")
        print(f"   - The generation process only looks in main available tags")
        print(f"   - JSON products need to be integrated with the main data source")
    else:
        print(f"   - JSON products are properly integrated")
        print(f"   - The issue might be elsewhere")
    
    return True

def main():
    """Main test function."""
    print("Starting JSON Matching Data Test...")
    
    success = test_json_matching_data()
    
    if success:
        print("\n🧪 TEST COMPLETE!")
        print("   - Check the results above for detailed analysis")
        print("   - The root cause should be clear now")
        sys.exit(0)
    else:
        print("\n❌ TEST FAILED!")
        print("   - Some issues remain")
        print("   - Additional investigation needed")
        sys.exit(1)

if __name__ == "__main__":
    main()
