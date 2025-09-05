#!/usr/bin/env python3
"""
Debug script to test the generation endpoint and understand the tag validation issue
"""

import requests
import json

def test_generation_endpoint():
    """Test the generation endpoint with sample data"""
    
    # Test data - simulate what the frontend might send
    test_data = {
        "template_type": "vertical",
        "scale_factor": 1.0,
        "selected_tags": [
            "Blue Dream",
            "OG Kush", 
            "Girl Scout Cookies",
            "Sour Diesel",
            "Granddaddy Purple"
        ],
        "filters": None
    }
    
    print("Testing generation endpoint...")
    print(f"Request data: {json.dumps(test_data, indent=2)}")
    
    try:
        response = requests.post(
            "http://127.0.0.1:5004/api/generate",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ Generation successful!")
            # For successful generation, the response is a file download, not JSON
            content_length = response.headers.get('Content-Length', 'Unknown')
            content_type = response.headers.get('Content-Type', 'Unknown')
            print(f"Generated file: {content_length} bytes, type: {content_type}")
            
            # Save the file to see what was generated
            filename = "test_generated_labels.docx"
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"✅ Saved generated file as: {filename}")
            
        else:
            print("❌ Generation failed!")
            try:
                error_data = response.json()
                print(f"Error: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Error text: {response.text}")
                
    except Exception as e:
        print(f"❌ Request failed: {e}")

def test_available_tags():
    """Test the available tags endpoint to see what tags are available"""
    
    print("\nTesting available tags endpoint...")
    
    try:
        response = requests.get("http://127.0.0.1:5004/api/available-tags")
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Handle both list and dict responses
            if isinstance(data, list):
                available_tags = data
            else:
                available_tags = data.get('available_tags', [])
                
            print(f"✅ Available tags count: {len(available_tags)}")
            
            # Show first 10 tags
            print("First 10 available tags:")
            for i, tag in enumerate(available_tags[:10]):
                if isinstance(tag, dict):
                    product_name = tag.get('Product Name*', tag.get('ProductName', tag.get('displayName', 'Unknown')))
                    print(f"  {i+1}. {product_name}")
                else:
                    print(f"  {i+1}. {tag}")
                
        else:
            print("❌ Failed to get available tags!")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

def test_with_real_product_names():
    """Test with actual product names from the data"""
    
    print("\nTesting with real product names from the data...")
    
    # First get available tags
    try:
        response = requests.get("http://127.0.0.1:5004/api/available-tags")
        if response.status_code == 200:
            data = response.json()
            
            # Handle both list and dict responses
            if isinstance(data, list):
                available_tags = data
            else:
                available_tags = data.get('available_tags', [])
            
            if available_tags:
                # Extract product names from the first 5 tags
                product_names = []
                for tag in available_tags[:5]:
                    if isinstance(tag, dict):
                        product_name = tag.get('Product Name*', tag.get('ProductName', tag.get('displayName', '')))
                        if product_name:
                            product_names.append(product_name)
                    else:
                        product_names.append(str(tag))
                
                if product_names:
                    test_data = {
                        "template_type": "vertical",
                        "scale_factor": 1.0,
                        "selected_tags": product_names,
                        "filters": None
                    }
                    
                    print(f"Testing with real product names: {product_names}")
                    
                    response = requests.post(
                        "http://127.0.0.1:5004/api/generate",
                        json=test_data,
                        headers={"Content-Type": "application/json"}
                    )
                    
                    print(f"Response status: {response.status_code}")
                    
                    if response.status_code == 200:
                        print("✅ Generation successful with real product names!")
                        content_length = response.headers.get('Content-Length', 'Unknown')
                        print(f"Generated file: {content_length} bytes")
                    else:
                        print("❌ Generation failed with real product names!")
                        try:
                            error_data = response.json()
                            print(f"Error: {json.dumps(error_data, indent=2)}")
                        except:
                            print(f"Error text: {response.text}")
                        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_available_tags()
    test_generation_endpoint()
    test_with_real_product_names()
