#!/usr/bin/env python3
"""
Test CBD text visibility in generated Word documents
"""

import requests
import json
import tempfile
import pandas as pd
import time

def test_cbd_text_in_word_document():
    """Test that CBD text appears correctly in generated Word documents."""
    print("=== CBD TEXT VISIBILITY TEST ===")
    
    # Create test data with CBD products
    test_data = {
        'Product Name*': ['CBD Huckleberry Web - 1g', 'Regular Product - 1g'],
        'Product Type*': ['Flower', 'Flower'],
        'Product Strain': ['', ''],
        'Lineage': ['CBD', 'HYBRID'],
        'Vendor': ['Test Vendor', 'Test Vendor'],
        'Price': ['$10', '$10'],
        'Weight*': ['1g', '1g'],
        'Ratio': ['', ''],
        'Units': ['', ''],
        'Quantity*': [1, 1],
        'THC test result': ['', ''],
        'CBD test result': ['', ''],
        'Test result unit (% or mg)': ['', '']
    }
    
    # Create Excel file
    df = pd.DataFrame(test_data)
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as temp_file:
        df.to_excel(temp_file.name, index=False)
        temp_file_path = temp_file.name
    
    try:
        print(f"Created test Excel file: {temp_file_path}")
        
        # Test URL (assuming Flask is running on default port)
        base_url = "http://127.0.0.1:8001"
        
        # Step 1: Upload the file
        print("\n1. Uploading test file to Flask app...")
        with open(temp_file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{base_url}/upload", files=files)
        
        if response.status_code == 200:
            print(f"✅ File uploaded successfully")
            
            # Step 2: Get available tags to find our CBD product
            print("\n2. Getting available tags...")
            tags_response = requests.get(f"{base_url}/api/available-tags")
            
            if tags_response.status_code == 200:
                tags_data = tags_response.json()
                tags = tags_data.get('tags', [])
                
                # Find CBD product
                cbd_tag = None
                for tag in tags:
                    if 'CBD Huckleberry' in tag.get('ProductName', ''):
                        cbd_tag = tag
                        break
                
                if cbd_tag:
                    print(f"✅ Found CBD product: {cbd_tag['ProductName']}")
                    print(f"   Lineage: '{cbd_tag.get('Lineage', 'N/A')}'")
                    
                    # Step 3: Select the CBD tag and generate document
                    print("\n3. Selecting CBD tag and generating Word document...")
                    
                    # Select the tag
                    select_response = requests.post(f"{base_url}/api/select-tag", 
                                                  json={'tagName': cbd_tag['ProductName']})
                    
                    if select_response.status_code == 200:
                        print(f"✅ CBD tag selected successfully")
                        
                        # Generate Word document
                        generate_response = requests.post(f"{base_url}/generate")
                        
                        if generate_response.status_code == 200:
                            print(f"✅ Word document generated successfully!")
                            
                            # Save the document
                            output_path = "/Users/adamcordova/Desktop/labelMaker_ QR copy final copy 10/test_cbd_text_fix.docx"
                            with open(output_path, 'wb') as f:
                                f.write(generate_response.content)
                            
                            print(f"📄 Word document saved: {output_path}")
                            print(f"🎯 Please open the document to verify CBD text is visible!")
                            
                        else:
                            print(f"❌ Word generation failed: {generate_response.status_code}")
                            print(f"   Response: {generate_response.text}")
                    else:
                        print(f"❌ Tag selection failed: {select_response.status_code}")
                        print(f"   Response: {select_response.text}")
                        
                else:
                    print(f"❌ CBD product not found in available tags")
                    print(f"Available tags: {[tag.get('ProductName', 'N/A') for tag in tags[:5]]}")
                    
            else:
                print(f"❌ Failed to get available tags: {tags_response.status_code}")
                
        else:
            print(f"❌ File upload failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Could not connect to Flask app at {base_url}")
        print(f"   Make sure the app is running on port 8001")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_cbd_text_in_word_document()