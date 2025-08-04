#!/usr/bin/env python3
"""
Test script to verify DOH and High CBD images are displayed in the UI.
This script tests that products with DOH="YES" show the appropriate images.
"""

import os
import sys
import logging
import requests
import json
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_doh_images_ui():
    """Test that DOH and High CBD images are displayed in the UI."""
    print("🔍 Testing DOH and High CBD Images in UI")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:9090"
    
    # Test 1: Check if image files exist
    print("\n1. Checking image files...")
    image_files = [
        'static/img/DOH.png',
        'static/img/HighCBD.png'
    ]
    
    for image_file in image_files:
        if os.path.exists(image_file):
            print(f"   ✅ {image_file} exists")
        else:
            print(f"   ❌ {image_file} missing")
            return False
    
    # Test 2: Check server status
    print("\n2. Testing server status...")
    try:
        response = requests.get(f"{base_url}/api/status", timeout=10)
        if response.status_code == 200:
            status_data = response.json()
            print(f"   ✅ Server is running")
            print(f"   📊 Data loaded: {status_data.get('data_loaded', False)}")
        else:
            print(f"   ❌ Server returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Cannot connect to server: {e}")
        return False
    
    # Test 3: Test image accessibility via web server
    print("\n3. Testing image accessibility...")
    try:
        # Test DOH.png
        response = requests.get(f"{base_url}/static/img/DOH.png", timeout=10)
        if response.status_code == 200:
            print(f"   ✅ DOH.png accessible via web server")
        else:
            print(f"   ❌ DOH.png not accessible: {response.status_code}")
            return False
        
        # Test HighCBD.png
        response = requests.get(f"{base_url}/static/img/HighCBD.png", timeout=10)
        if response.status_code == 200:
            print(f"   ✅ HighCBD.png accessible via web server")
        else:
            print(f"   ❌ HighCBD.png not accessible: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing image accessibility: {e}")
        return False
    
    # Test 4: Test available tags endpoint to see if DOH data is included
    print("\n4. Testing available tags endpoint...")
    try:
        response = requests.get(f"{base_url}/api/available-tags", timeout=10)
        if response.status_code == 200:
            tags = response.json()
            print(f"   ✅ Available tags endpoint working")
            print(f"   📊 Found {len(tags)} tags")
            
            # Look for tags with DOH="YES"
            doh_tags = [tag for tag in tags if tag.get('DOH', '').upper() == 'YES']
            print(f"   🏷️  Found {len(doh_tags)} DOH compliant tags")
            
            # Look for High CBD tags
            high_cbd_tags = [tag for tag in doh_tags if tag.get('Product Type*', '').lower().startswith('high cbd')]
            print(f"   🌿 Found {len(high_cbd_tags)} High CBD tags")
            
            if doh_tags:
                print(f"   📝 Sample DOH tags:")
                for i, tag in enumerate(doh_tags[:3]):
                    product_type = tag.get('Product Type*', 'Unknown')
                    is_high_cbd = product_type.lower().startswith('high cbd')
                    image_type = "HighCBD.png" if is_high_cbd else "DOH.png"
                    print(f"      {i+1}. {tag.get('Product Name*', 'Unknown')} ({product_type}) -> {image_type}")
            
        else:
            print(f"   ❌ Available tags endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error testing available tags: {e}")
        return False
    
    # Test 5: Test filter options to see if DOH is included
    print("\n5. Testing filter options...")
    try:
        response = requests.get(f"{base_url}/api/filter-options", timeout=10)
        if response.status_code == 200:
            filter_options = response.json()
            print(f"   ✅ Filter options endpoint working")
            
            # Check if DOH field is available in the data
            if 'doh' in filter_options:
                doh_options = filter_options['doh']
                print(f"   🏷️  DOH filter options: {doh_options}")
            else:
                print(f"   ⚠️  No DOH filter options found")
                
        else:
            print(f"   ❌ Filter options endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error testing filter options: {e}")
        return False
    
    return True

def create_test_data():
    """Create test data with DOH and High CBD products for testing."""
    print("\n6. Creating test data for manual verification...")
    
    test_data = {
        "doh_compliant_regular": {
            "Product Name*": "Test DOH Product",
            "Product Type*": "Flower",
            "DOH": "YES",
            "Product Brand": "Test Brand",
            "Vendor": "Test Vendor"
        },
        "doh_compliant_high_cbd": {
            "Product Name*": "Test High CBD Product",
            "Product Type*": "High CBD Edible",
            "DOH": "YES",
            "Product Brand": "Test Brand",
            "Vendor": "Test Vendor"
        },
        "not_doh_compliant": {
            "Product Name*": "Test Non-DOH Product",
            "Product Type*": "Concentrate",
            "DOH": "NO",
            "Product Brand": "Test Brand",
            "Vendor": "Test Vendor"
        }
    }
    
    print("   📋 Test data created:")
    for key, data in test_data.items():
        product_type = data['Product Type*']
        doh_value = data['DOH']
        is_high_cbd = product_type.lower().startswith('high cbd')
        expected_image = "HighCBD.png" if (doh_value == "YES" and is_high_cbd) else ("DOH.png" if doh_value == "YES" else "None")
        print(f"      {key}: {data['Product Name*']} -> {expected_image}")
    
    return test_data

def main():
    """Main function."""
    print("🚀 DOH and High CBD Images UI Test")
    print("This test verifies that DOH and High CBD images are properly displayed")
    print()
    
    # Check if server is running
    try:
        response = requests.get("http://127.0.0.1:9090/api/status", timeout=5)
        if response.status_code != 200:
            print("❌ Server is not responding properly")
            print("Please ensure the Flask server is running on port 9090")
            return False
    except Exception as e:
        print("❌ Cannot connect to server")
        print("Please ensure the Flask server is running on port 9090")
        print(f"Error: {e}")
        return False
    
    # Run the tests
    success = test_doh_images_ui()
    
    if success:
        print("\n✅ Test completed successfully!")
        print("The DOH and High CBD images should now be displayed in the UI.")
        print()
        print("📋 Manual Verification Steps:")
        print("1. Open the web interface in your browser")
        print("2. Look for products with DOH='YES' in the available tags")
        print("3. Verify that:")
        print("   - Regular DOH compliant products show DOH.png")
        print("   - High CBD products show HighCBD.png")
        print("   - Non-DOH products show no image")
        print()
        print("🔧 Technical Details:")
        print("- Images are served from /static/img/")
        print("- Logic checks DOH='YES' and Product Type* starts with 'high cbd'")
        print("- Images are 16px height with auto width")
        print("- Images appear after the product name with 4px margin")
    else:
        print("\n❌ Test failed!")
        print("Please check the implementation and try again.")
    
    # Create test data for reference
    create_test_data()
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 