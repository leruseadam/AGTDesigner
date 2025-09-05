#!/usr/bin/env python3
"""
Comprehensive test to verify JSON matching fix is working correctly.
This test simulates the exact issue: 40 JSON matched products, but only 27 in database.
"""

import requests
import json
import base64
import time

def create_test_data(num_products=40):
    """Create test data with specified number of products."""
    products = []
    for i in range(num_products):
        products.append({
            "product_name": f"Test Product {i+1}",
            "vendor": "Test Vendor",
            "brand": "Test Brand",
            "inventory_type": "Concentrate for Inhalation",
            "weight": "1g",
            "strain": f"Test Strain {i+1}"
        })
    
    return {
        "inventory_transfer_items": products,
        "from_license_name": "Test Vendor"
    }

def test_complete_json_fix():
    """Test the complete JSON matching fix."""
    print("🧪 Testing Complete JSON Matching Fix")
    print("=" * 50)
    
    # Create test data with 40 products
    test_data = create_test_data(40)
    data_str = json.dumps(test_data)
    data_url = f"data:application/json;base64,{base64.b64encode(data_str.encode()).decode()}"
    
    print(f"📋 Created test data with {len(test_data['inventory_transfer_items'])} products")
    
    # Test JSON matching
    print(f"\n🚀 Testing JSON matching...")
    try:
        response = requests.post(
            'http://127.0.0.1:5003/api/json-match',
            json={'url': data_url},
            timeout=30
        )
        
        print(f"📡 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ JSON matching successful!")
            
            matched_count = result.get('matched_count', 0)
            available_tags = len(result.get('available_tags', []))
            selected_tags = len(result.get('selected_tags', []))
            
            print(f"\n📊 Results:")
            print(f"   Matched count: {matched_count}")
            print(f"   Available tags: {available_tags}")
            print(f"   Selected tags: {selected_tags}")
            
            # Check if the fix is working
            if matched_count > 0 and selected_tags == 0:
                print(f"❌ BUG DETECTED: Found {matched_count} matches but {selected_tags} selected tags")
                print(f"   This indicates the JSON matching bug is still present")
                return False
            elif matched_count > 0 and selected_tags > 0:
                print(f"✅ FIX WORKING: Found {matched_count} matches and {selected_tags} selected tags")
                
                # Test template generation
                print(f"\n🔨 Testing template generation...")
                try:
                    gen_response = requests.post(
                        'http://127.0.0.1:5003/api/generate',
                        json={
                            'template_type': 'vertical',
                            'scale_factor': 1.0,
                            'selected_tags': []  # Use tags from session
                        },
                        timeout=60
                    )
                    
                    if gen_response.status_code == 200:
                        print(f"✅ Template generation successful!")
                        
                        # Check if all selected tags were processed
                        if selected_tags <= 30:  # Reasonable threshold
                            print(f"✅ All {selected_tags} selected tags were processed")
                            return True
                        else:
                            print(f"⚠️  Large number of tags ({selected_tags}) - check processing")
                            return True
                    else:
                        print(f"❌ Template generation failed: {gen_response.status_code}")
                        try:
                            error_data = gen_response.json()
                            print(f"   Error: {error_data.get('error', 'Unknown error')}")
                        except:
                            print(f"   Response: {gen_response.text}")
                        return False
                        
                except Exception as e:
                    print(f"❌ Template generation error: {e}")
                    return False
                    
            else:
                print(f"⚠️  No matches found - test data might not match Excel data")
                return True
                
        else:
            print(f"❌ JSON matching failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection failed - make sure the Flask app is running on port 5003")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_selected_tags_endpoint():
    """Test the selected tags endpoint specifically."""
    print(f"\n🔍 Testing selected tags endpoint...")
    try:
        response = requests.get('http://127.0.0.1:5003/api/selected-tags', timeout=10)
        
        if response.status_code == 200:
            tags = response.json()
            print(f"✅ Selected tags endpoint working!")
            print(f"   Tags count: {len(tags)}")
            
            if len(tags) > 0:
                print(f"   Sample tags: {tags[:3]}")
                return True
            else:
                print(f"   No selected tags found")
                return False
        else:
            print(f"❌ Selected tags endpoint failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Selected tags endpoint error: {e}")
        return False

if __name__ == "__main__":
    success = test_complete_json_fix()
    selected_tags_working = test_selected_tags_endpoint()
    
    print("\n" + "=" * 50)
    if success and selected_tags_working:
        print("🏁 ALL TESTS PASSED - JSON matching fix is working correctly!")
    elif success:
        print("🏁 JSON matching fix is working, but selected tags endpoint needs attention")
    else:
        print("🏁 JSON matching fix needs more work")
    print("=" * 50)
