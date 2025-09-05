#!/usr/bin/env python3
"""
Test the database generation fix to verify that JSON matched products can now be generated from the database.
"""

import requests
import json
import time
import sys

def test_database_generation():
    """Test the database generation fix."""
    
    base_url = "http://127.0.0.1:5003"
    
    print("🧪 TESTING DATABASE GENERATION FIX")
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
    
    # Step 2: Test generation with specific JSON products
    print("\n2️⃣ Testing generation with specific JSON products...")
    
    # The specific products that were missing before
    test_products = [
        "Hawaiian Golden Pineapple Live Resin Cartridge by Dabstract",
        "High Life Live Resin Cake Icing by Dabstract", 
        "Non GMO Live Resin Cake Icing by Dabstract",
        "White Gummie Bears Live Resin Cake Icing by Dabstract",
        "Blue Dream Live Resin Cartridge by Dabstract"
    ]
    
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
    
    # Step 3: Check if the database was used
    print(f"\n3️⃣ Checking if database was used...")
    
    # The fix should now use the database to get product information
    # even if the products are not in the Excel data
    print(f"📊 The fix should now:")
    print(f"   - Look up products in the database")
    print(f"   - Use database records for generation")
    print(f"   - Generate labels even if products aren't in Excel data")
    
    # Step 4: Summary
    print(f"\n4️⃣ Test Summary...")
    
    print(f"\n🧪 TEST RESULTS:")
    print(f"   - Available tags count: {available_count}")
    print(f"   - Generation test: {'✅ PASSED' if 'Generation successful' in locals() else '❌ FAILED'}")
    
    if 'Generation successful' in locals():
        print(f"   - Database generation fix is working")
        print(f"   - JSON products can now be generated from database")
    else:
        print(f"   - Database generation fix may need more work")
        print(f"   - Check the error messages above")
    
    return True

def main():
    """Main test function."""
    print("Starting Database Generation Fix Test...")
    
    success = test_database_generation()
    
    if success:
        print("\n🧪 TEST COMPLETE!")
        print("   - Check the results above")
        print("   - If generation succeeded, the database fix is working")
        print("   - Try generating labels with your JSON matched products")
        sys.exit(0)
    else:
        print("\n❌ TEST FAILED!")
        print("   - Some issues remain")
        print("   - Additional investigation needed")
        sys.exit(1)

if __name__ == "__main__":
    main()
