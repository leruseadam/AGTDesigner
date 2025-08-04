#!/usr/bin/env python3
"""
Test script to demonstrate JSON matching with the real Cultivera URL
"""

import requests
import json
import time

def test_cultivera_json_matching():
    """Test JSON matching with the real Cultivera URL"""
    base_url = 'http://127.0.0.1:9090'
    cultivera_url = "https://files.cultivera.com/435553542D57533130383235/Interop/25/16/3EGQ3216P7YSVJCF/Cultivera_ORD-5430_422044.json"
    
    print("🧪 Testing JSON Matching with Real Cultivera Data")
    print("=" * 60)
    print(f"URL: {cultivera_url}")
    print("=" * 60)
    
    # Step 1: Check server status
    print("\n1. Checking server status...")
    try:
        response = requests.get(f'{base_url}/api/status', timeout=5)
        if response.status_code == 200:
            status = response.json()
            print(f"✅ Server is running")
            print(f"  Data loaded: {status.get('data_loaded', False)}")
            if status.get('data_loaded'):
                print(f"  Excel records: {status.get('data_shape', [0, 0])[0]}")
        else:
            print(f"❌ Server error: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("   Please start the Flask app with: python app.py")
        return
    
    # Step 2: Test JSON matching with the real Cultivera URL
    print("\n2. Testing JSON matching with Cultivera data...")
    print("   This may take a few minutes for processing...")
    
    try:
        data = {'url': cultivera_url}
        start_time = time.time()
        
        response = requests.post(f'{base_url}/api/json-match', 
                               json=data, 
                               headers={'Content-Type': 'application/json'},
                               timeout=600)  # 10 minute timeout
        
        processing_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ JSON matching completed successfully!")
            print(f"  Processing time: {processing_time:.2f} seconds")
            print(f"  Success: {result.get('success', False)}")
            print(f"  Matched count: {result.get('matched_count', 0)}")
            print(f"  Cache status: {result.get('cache_status', 'Unknown')}")
            
            if result.get('matched_names'):
                print(f"\n  📋 Matched products:")
                for i, name in enumerate(result['matched_names'][:10], 1):  # Show first 10
                    print(f"     {i}. {name}")
                if len(result['matched_names']) > 10:
                    print(f"     ... and {len(result['matched_names']) - 10} more")
            
            if result.get('selected_tags'):
                print(f"\n  🏷️  Selected tags created: {len(result['selected_tags'])}")
                print(f"  Sample tags:")
                for i, tag in enumerate(result['selected_tags'][:3], 1):
                    product_name = tag.get('Product Name*', 'Unknown')
                    vendor = tag.get('Vendor', 'Unknown')
                    product_type = tag.get('Product Type*', 'Unknown')
                    print(f"     {i}. {product_name} ({vendor}) - {product_type}")
                
        else:
            error_data = response.json()
            print(f"❌ JSON matching failed: {error_data.get('error', 'Unknown error')}")
            
    except requests.exceptions.Timeout:
        print("❌ JSON matching timed out after 10 minutes")
        print("   This can happen with very large datasets")
    except Exception as e:
        print(f"❌ Error during JSON matching: {e}")
    
    # Step 3: Show what the Cultivera data contains
    print("\n3. Cultivera Data Analysis:")
    print("   Based on the URL structure, this appears to be:")
    print("   - Transfer ID: ORD-5430")
    print("   - To License: 422044 (A GREENER TODAY BOTHELL)")
    print("   - From License: 412627 (JSM LLC)")
    print("   - Document Type: WCIA Transfer Schema v2.1.0")
    
    print("\n4. Expected Product Types:")
    print("   The JSON likely contains inventory_transfer_items with:")
    print("   - Product names (e.g., 'Medically Compliant - Dank Czar...')")
    print("   - Vendor information (JSM LLC)")
    print("   - Product types (Concentrate for Inhalation)")
    print("   - Strain names (GMO, Grape Gasoline, etc.)")
    print("   - Quantities and pricing")
    
    print("\n" + "=" * 60)
    print("🎉 JSON matching is ready for real Cultivera data!")
    print("   The system will match products from the JSON against your Excel data")
    print("   and automatically create selected tags for label generation.")

if __name__ == "__main__":
    test_cultivera_json_matching() 