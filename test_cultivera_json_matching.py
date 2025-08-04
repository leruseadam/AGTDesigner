#!/usr/bin/env python3
"""
Test script to demonstrate JSON matching with real Cultivera transfer data.
This shows how the system handles actual inventory transfer JSON files.
"""

import requests
import json
import base64

def test_cultivera_json_matching():
    """Test JSON matching with real Cultivera transfer data."""
    
    # Real Cultivera JSON URL provided by user
    cultivera_url = "https://files.cultivera.com/435553542D5753313030303438/Interop/25/28/0KMK8B1FTA5RZZ67/Cultivera_ORD-153392_422044.json"
    
    print("=== Testing with Real Cultivera Transfer Data ===")
    print(f"Source: {cultivera_url}")
    print()
    
    try:
        # Make request to the JSON matching endpoint with the real Cultivera URL
        response = requests.post('http://127.0.0.1:5001/api/json-match', 
                               json={'url': cultivera_url}, 
                               timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ JSON Matching Successful!")
            print(f"Matched count: {result.get('matched_count', 0)}")
            print(f"Available tags count: {len(result.get('available_tags', []))}")
            print(f"JSON matched tags count: {len(result.get('json_matched_tags', []))}")
            print()
            
            # Show the available tags (matched products)
            available_tags = result.get('available_tags', [])
            if available_tags:
                print("📋 Available Tags (Cultivera Transfer Items):")
                for i, tag in enumerate(available_tags[:10], 1):  # Show first 10 items
                    product_name = tag.get('Product Name*', tag.get('ProductName', 'Unknown'))
                    vendor = tag.get('Vendor', 'Unknown')
                    price = tag.get('Price', 'Unknown')
                    source = tag.get('Source', 'Unknown')
                    strain = tag.get('Product Strain', 'Unknown')
                    
                    print(f"  {i}. {product_name}")
                    print(f"     Source: {source}")
                    print(f"     Vendor: {vendor}")
                    print(f"     Strain: {strain}")
                    print(f"     Price: {price}")
                    print()
                
                if len(available_tags) > 10:
                    print(f"     ... and {len(available_tags) - 10} more items")
                    print()
            
            # Show sample JSON matched tags
            json_matched_tags = result.get('json_matched_tags', [])
            if json_matched_tags:
                print("🔍 Sample JSON Matched Tags:")
                for i, tag in enumerate(json_matched_tags[:5], 1):  # Show first 5
                    product_name = tag.get('Product Name*', tag.get('ProductName', 'Unknown'))
                    vendor = tag.get('Vendor', 'Unknown')
                    price = tag.get('Price', 'Unknown')
                    
                    print(f"  {i}. {product_name}")
                    print(f"     Vendor: {vendor}")
                    print(f"     Price: {price}")
                    print()
            
            # Show transfer details
            print("📊 Transfer Details:")
            print(f"  • Total items in transfer: {len(available_tags)}")
            print(f"  • Items matched in dataset: {result.get('matched_count', 0)}")
            print(f"  • Filter mode: {result.get('filter_mode', 'Unknown')}")
            print(f"  • Cache status: {result.get('cache_status', 'Unknown')}")
            print()
            
            # Show success message
            print("🎉 Success! The JSON matching system successfully processed the Cultivera transfer file.")
            print("   The Available Tags list now contains only the items from this transfer.")
            print("   You can now select which items to include in your labels.")
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network Error: {e}")
        print("Make sure the server is running on port 5001")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_cultivera_data_structure():
    """Test to show the structure of the Cultivera data."""
    
    print("=== Cultivera Data Structure Analysis ===")
    
    try:
        # Fetch the JSON data directly to analyze its structure
        response = requests.get("https://files.cultivera.com/435553542D5753313030303438/Interop/25/28/0KMK8B1FTA5RZZ67/Cultivera_ORD-153392_422044.json", 
                               timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            print("📋 Transfer Information:")
            print(f"  • Document Name: {data.get('document_name', 'Unknown')}")
            print(f"  • Schema Version: {data.get('document_schema_version', 'Unknown')}")
            print(f"  • From License: {data.get('from_license_name', 'Unknown')} ({data.get('from_license_number', 'Unknown')})")
            print(f"  • To License: {data.get('to_license_name', 'Unknown')} ({data.get('to_license_number', 'Unknown')})")
            print(f"  • Transfer ID: {data.get('transfer_id', 'Unknown')}")
            print(f"  • Transfer Date: {data.get('transferred_at', 'Unknown')}")
            print()
            
            # Analyze inventory items
            inventory_items = data.get('inventory_transfer_items', [])
            print(f"📦 Inventory Items ({len(inventory_items)} total):")
            
            for i, item in enumerate(inventory_items[:5], 1):  # Show first 5 items
                product_name = item.get('product_name', 'Unknown')
                qty = item.get('qty', 0)
                unit_weight = item.get('unit_weight', 0)
                line_price = item.get('line_price', 0)
                strain_name = item.get('strain_name', 'Unknown')
                inventory_type = item.get('inventory_type', 'Unknown')
                
                print(f"  {i}. {product_name}")
                print(f"     Quantity: {qty}")
                print(f"     Unit Weight: {unit_weight}g")
                print(f"     Line Price: ${line_price}")
                print(f"     Strain: {strain_name}")
                print(f"     Type: {inventory_type}")
                print()
            
            if len(inventory_items) > 5:
                print(f"     ... and {len(inventory_items) - 5} more items")
                print()
            
            print("✅ Data structure analysis complete!")
            print("   The JSON matching system will process these inventory items")
            print("   and match them against your Excel dataset.")
            
        else:
            print(f"❌ Error fetching data: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error analyzing data structure: {e}")

if __name__ == "__main__":
    print("🚀 Testing JSON Matching with Real Cultivera Data")
    print("=" * 60)
    print()
    
    # First analyze the data structure
    test_cultivera_data_structure()
    print()
    
    # Then test the JSON matching
    test_cultivera_json_matching() 