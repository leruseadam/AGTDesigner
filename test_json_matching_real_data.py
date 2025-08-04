#!/usr/bin/env python3
"""
Test script with real JSON data to verify JSON matching functionality.
This test uses a real JSON URL to demonstrate the matching process.
"""

import requests
import json
import time

def test_json_matching_with_real_data():
    """Test JSON matching with real JSON data."""
    
    print("=== JSON MATCHING WITH REAL DATA TEST ===")
    
    # Real JSON URL for testing - this is a sample cannabis product data
    # You can replace this with your actual JSON URL
    test_url = "https://raw.githubusercontent.com/example/cannabis-data/main/sample_products.json"
    
    # Alternative: Create a local test JSON file
    create_test_json_file()
    test_url = "http://localhost:5000/test_products.json"
    
    try:
        print(f"1. Making JSON matching request to: {test_url}")
        
        # Make the JSON matching request
        response = requests.post(
            'http://localhost:5000/api/json-match',
            json={'url': test_url},
            timeout=60  # Increased timeout for real data
        )
        
        print(f"2. Response status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"3. JSON matching response keys: {list(data.keys())}")
            print(f"4. Matched count: {data.get('matched_count', 0)}")
            print(f"5. Available tags count: {len(data.get('available_tags', []))}")
            print(f"6. Selected tags count: {len(data.get('selected_tags', []))}")
            
            # Check if selected_tags is populated
            selected_tags = data.get('selected_tags', [])
            if selected_tags:
                print(f"7. ✅ Selected tags are populated with {len(selected_tags)} items")
                print(f"   Sample selected tags:")
                for i, tag in enumerate(selected_tags[:3]):
                    if isinstance(tag, dict):
                        name = tag.get('Product Name*', 'Unknown')
                        print(f"     {i+1}. {name}")
                    else:
                        print(f"     {i+1}. {tag}")
            else:
                print("7. ❌ Selected tags are empty")
            
            # Check available tags
            available_tags = data.get('available_tags', [])
            if available_tags:
                print(f"8. Available tags sample:")
                for i, tag in enumerate(available_tags[:3]):
                    if isinstance(tag, dict):
                        name = tag.get('Product Name*', 'Unknown')
                        print(f"     {i+1}. {name}")
                    else:
                        print(f"     {i+1}. {tag}")
            
            # Check if there are any error messages
            if 'error' in data:
                print(f"9. ❌ Error in response: {data['error']}")
            
            # Test the selected tags endpoint after JSON matching
            print("\n10. Testing selected tags endpoint after JSON matching...")
            time.sleep(2)  # Give the server time to process
            
            selected_response = requests.get('http://localhost:5000/api/selected-tags')
            if selected_response.status_code == 200:
                selected_data = selected_response.json()
                print(f"    Selected tags endpoint returned: {len(selected_data.get('selected_tags', []))} items")
                
                if selected_data.get('selected_tags'):
                    print("    ✅ Selected tags endpoint is returning data")
                else:
                    print("    ❌ Selected tags endpoint is not returning data")
            else:
                print(f"    ❌ Selected tags endpoint failed: {selected_response.status_code}")
            
        else:
            print(f"3. ❌ JSON matching failed with status code: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out - the JSON URL may be slow or unavailable")
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - make sure the server is running on localhost:5000")
    except Exception as e:
        print(f"❌ Error during test: {e}")

def create_test_json_file():
    """Create a test JSON file with sample cannabis product data."""
    
    print("Creating test JSON file with sample data...")
    
    # Sample cannabis product data
    test_products = [
        {
            "product_name": "Blue Dream Flower",
            "strain_name": "Blue Dream",
            "vendor": "Sample Vendor",
            "brand": "Sample Brand",
            "product_type": "flower",
            "weight": "3.5g",
            "thc_content": "18.5%",
            "cbd_content": "0.1%"
        },
        {
            "product_name": "OG Kush Pre-Roll",
            "strain_name": "OG Kush",
            "vendor": "Sample Vendor",
            "brand": "Sample Brand",
            "product_type": "pre-roll",
            "weight": "1g",
            "thc_content": "22.3%",
            "cbd_content": "0.2%"
        },
        {
            "product_name": "Sour Diesel Concentrate",
            "strain_name": "Sour Diesel",
            "vendor": "Sample Vendor",
            "brand": "Sample Brand",
            "product_type": "concentrate",
            "weight": "1g",
            "thc_content": "85.2%",
            "cbd_content": "0.5%"
        },
        {
            "product_name": "Girl Scout Cookies Vape Cartridge",
            "strain_name": "Girl Scout Cookies",
            "vendor": "Sample Vendor",
            "brand": "Sample Brand",
            "product_type": "vape cartridge",
            "weight": "1g",
            "thc_content": "78.9%",
            "cbd_content": "0.3%"
        },
        {
            "product_name": "Purple Haze Edible Gummies",
            "strain_name": "Purple Haze",
            "vendor": "Sample Vendor",
            "brand": "Sample Brand",
            "product_type": "edible",
            "weight": "100mg",
            "thc_content": "10mg per gummy",
            "cbd_content": "2mg per gummy"
        }
    ]
    
    # Save to a local file
    with open('test_products.json', 'w') as f:
        json.dump(test_products, f, indent=2)
    
    print("✅ Test JSON file created: test_products.json")
    print(f"   Contains {len(test_products)} sample products")

def check_server_status():
    """Check if the server is running and accessible."""
    
    print("=== SERVER STATUS CHECK ===")
    
    try:
        response = requests.get('http://localhost:5000/api/status', timeout=5)
        if response.status_code == 200:
            print("✅ Server is running and accessible")
            return True
        else:
            print(f"❌ Server returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running on localhost:5000")
        print("   Please start the server with: python app.py")
        return False
    except Exception as e:
        print(f"❌ Error checking server status: {e}")
        return False

def test_with_default_file():
    """Test JSON matching with default file enabled."""
    
    print("\n=== TESTING WITH DEFAULT FILE ENABLED ===")
    
    # First, enable default file loading
    print("1. Enabling default file loading...")
    
    # You can manually enable default file loading by setting DISABLE_DEFAULT_FOR_TESTING = False
    # in src/core/data/excel_processor.py
    
    print("2. Restart the server to load default file")
    print("3. Then run JSON matching to see if it works with default data")
    
    print("\nTo enable default file loading:")
    print("1. Edit src/core/data/excel_processor.py")
    print("2. Set DISABLE_DEFAULT_FOR_TESTING = True")
    print("3. Restart the server")
    print("4. Run JSON matching")

if __name__ == "__main__":
    print("JSON MATCHING WITH REAL DATA TEST")
    print("=" * 50)
    
    # Check if server is running
    if not check_server_status():
        print("\nPlease start the server first:")
        print("1. Open a terminal in the project directory")
        print("2. Run: python app.py")
        print("3. Wait for the server to start")
        print("4. Run this test again")
        exit(1)
    
    print("\nTesting JSON matching with real data...")
    test_json_matching_with_real_data()
    
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print("This test:")
    print("1. Creates a test JSON file with sample cannabis products")
    print("2. Tests JSON matching with real data")
    print("3. Verifies that selected tags are populated")
    print("\nIf you want to test with default file loading:")
    test_with_default_file()
    
    print("\nTo test with your own JSON URL:")
    print("1. Replace the test_url in test_json_matching_with_real_data()")
    print("2. Run the function: test_json_matching_with_real_data()") 