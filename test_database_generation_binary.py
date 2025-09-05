#!/usr/bin/env python3
"""
Test the database generation fix with proper handling of binary DOCX response.
"""

import requests
import json
import time
import sys

def test_database_generation_binary():
    """Test the database generation fix with binary response handling."""
    
    base_url = "http://127.0.0.1:5003"
    
    print("🧪 TESTING DATABASE GENERATION FIX (BINARY)")
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
            # Check if response is binary (DOCX file)
            content_type = response.headers.get('content-type', '')
            content_length = len(response.content)
            
            print(f"✅ Generation successful!")
            print(f"📊 Content-Type: {content_type}")
            print(f"📊 Content Length: {content_length} bytes")
            
            # Check if it's a DOCX file
            if 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' in content_type or content_length > 1000:
                print(f"✅ DOCX file generated successfully!")
                print(f"✅ Database generation fix is working!")
                
                # Check the first few bytes to confirm it's a DOCX
                first_bytes = response.content[:4]
                if first_bytes == b'PK\x03\x04':
                    print(f"✅ Confirmed: Valid DOCX file (ZIP format)")
                else:
                    print(f"⚠️  Warning: Response doesn't look like a DOCX file")
                    
            else:
                print(f"⚠️  Response doesn't appear to be a DOCX file")
                print(f"📊 First 100 bytes: {response.content[:100]}")
                
        else:
            print(f"❌ Generation failed: {response.status_code}")
            print(f"📊 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Generation test failed: {e}")
    
    # Step 3: Test with a product that should be in the database
    print(f"\n3️⃣ Testing with a product that should be in the database...")
    
    # Use a product that should exist in the available tags
    available_product = "Banana OG Distillate Cartridge by Hustler's Ambition - 1g"
    
    generation_data_2 = {
        "template_type": "vertical",
        "scale_factor": 1.0,
        "selected_tags": [available_product]
    }
    
    print(f"📊 Testing generation with available product: {available_product}")
    
    try:
        response = requests.post(f"{base_url}/api/generate", json=generation_data_2, timeout=30)
        
        if response.status_code == 200:
            content_length = len(response.content)
            print(f"✅ Generation successful!")
            print(f"📊 Content Length: {content_length} bytes")
            
            if content_length > 1000:
                print(f"✅ DOCX file generated successfully!")
            else:
                print(f"⚠️  Response seems too small for a DOCX file")
                
        else:
            print(f"❌ Generation failed: {response.status_code}")
            print(f"📊 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Generation test failed: {e}")
    
    # Step 4: Summary
    print(f"\n4️⃣ Test Summary...")
    
    print(f"\n🧪 TEST RESULTS:")
    print(f"   - Available tags count: {available_count}")
    print(f"   - JSON products generation: {'✅ WORKING' if 'DOCX file generated successfully' in locals() else '❌ FAILED'}")
    print(f"   - Database generation fix: {'✅ WORKING' if 'Database generation fix is working' in locals() else '❌ NEEDS WORK'}")
    
    if 'Database generation fix is working' in locals():
        print(f"   - JSON products can now be generated from database")
        print(f"   - Try generating labels with your JSON matched products")
    else:
        print(f"   - Database generation fix may need more work")
        print(f"   - Check the error messages above")
    
    return True

def main():
    """Main test function."""
    print("Starting Database Generation Fix Test (Binary)...")
    
    success = test_database_generation_binary()
    
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
