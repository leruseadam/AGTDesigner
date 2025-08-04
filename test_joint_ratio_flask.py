#!/usr/bin/env python3
"""
Test script to verify joint ratio fix works in Flask app
"""

import sys
import os
import requests
import json

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_joint_ratio_flask():
    """Test the joint ratio fix in Flask app"""
    print("🧪 Testing Joint Ratio Fix in Flask App")
    print("=" * 60)
    
    # Check Flask app status
    try:
        response = requests.get('http://127.0.0.1:9090/api/status')
        if response.status_code == 200:
            status = response.json()
            print(f"📊 Flask app status: {status}")
        else:
            print("❌ Flask app not responding")
            return
    except Exception as e:
        print(f"❌ Error connecting to Flask app: {e}")
        return
    
    print()
    
    # Test with a sample pre-roll product to see if JointRatio is extracted correctly
    print("1. Testing with sample pre-roll data:")
    print("-" * 40)
    
    # Create a test record with joint ratio in the product name
    test_record = {
        'Product Name*': 'Test Pre-Roll - 0.5g x 2 Pack',
        'Product Type*': 'pre-roll',
        'Product Brand': 'Test Brand',
        'Product Strain': 'Test Strain',
        'Lineage': 'HYBRID',
        'Weight*': '1',
        'Price': '10',
        'THC test result': '20.5',
        'CBD test result': '0.1'
    }
    
    try:
        # Test the template generation with this record
        response = requests.post('http://127.0.0.1:9090/api/generate-labels', 
                               json={
                                   'template_type': 'vertical',
                                   'records': [test_record],
                                   'count': 1
                               })
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Template generation successful")
            print(f"   Generated filename: {result.get('filename', 'Unknown')}")
            
            # Check if the generated content contains the correct joint ratio
            if 'content' in result:
                content = result['content']
                if '0.5g x 2 Pack' in content:
                    print("✅ JointRatio correctly extracted and used: '0.5g x 2 Pack'")
                else:
                    print("❌ JointRatio not found in generated content")
                    print(f"   Content preview: {content[:200]}...")
        else:
            print(f"❌ Template generation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing template generation: {e}")
    
    print()
    
    # Test with actual Excel file data if available
    print("2. Testing with actual Excel file:")
    print("-" * 40)
    
    try:
        # Try to get available tags to see if data is loaded
        response = requests.get('http://127.0.0.1:9090/api/available-tags')
        if response.status_code == 200:
            tags = response.json()
            print(f"✅ Available tags: {len(tags)} tags found")
            
            # Look for pre-roll products
            preroll_tags = [tag for tag in tags if 'pre-roll' in tag.get('product_type', '').lower()]
            print(f"   Pre-roll products: {len(preroll_tags)} found")
            
            if preroll_tags:
                # Test with the first pre-roll product
                test_tag = preroll_tags[0]
                print(f"   Testing with: {test_tag.get('product_name', 'Unknown')}")
                
                # Check if it has joint ratio information
                product_name = test_tag.get('product_name', '')
                if 'g' in product_name and ('x' in product_name or 'pack' in product_name.lower()):
                    print(f"   ✅ Product name contains joint ratio info: '{product_name}'")
                else:
                    print(f"   ⚠️  Product name doesn't contain obvious joint ratio info: '{product_name}'")
            else:
                print("   ⚠️  No pre-roll products found in available tags")
        else:
            print(f"❌ Could not get available tags: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing with actual data: {e}")

if __name__ == "__main__":
    test_joint_ratio_flask() 