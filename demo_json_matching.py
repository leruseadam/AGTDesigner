#!/usr/bin/env python3
"""
Demonstration script showing how to use JSON matching functionality
"""

import requests
import json
import time

def demo_json_matching():
    """Demonstrate JSON matching functionality"""
    base_url = 'http://127.0.0.1:9090'
    
    print("🚀 JSON Matching Demonstration")
    print("=" * 50)
    
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
    
    # Step 2: Show JSON status
    print("\n2. Checking JSON matching status...")
    try:
        response = requests.get(f'{base_url}/api/json-status', timeout=5)
        if response.status_code == 200:
            json_status = response.json()
            print(f"✅ JSON matching ready")
            print(f"  Cache status: {json_status.get('cache_status', 'Unknown')}")
            print(f"  Current matches: {len(json_status.get('json_matched_names', []))}")
        else:
            print(f"❌ JSON status error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error checking JSON status: {e}")
    
    # Step 3: Demonstrate with a sample JSON URL
    print("\n3. Demonstrating JSON matching...")
    
    # Create a sample JSON URL (using httpbin for demonstration)
    # In real usage, this would be a URL containing inventory transfer data
    sample_url = "https://httpbin.org/json"
    
    print(f"   Using sample URL: {sample_url}")
    print("   Note: This is a demo URL. In real usage, use a URL with inventory_transfer_items")
    
    try:
        data = {'url': sample_url}
        print("   Sending JSON match request...")
        
        response = requests.post(f'{base_url}/api/json-match', 
                               json=data, 
                               headers={'Content-Type': 'application/json'},
                               timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ JSON matching completed successfully!")
            print(f"   Success: {result.get('success', False)}")
            print(f"   Matched count: {result.get('matched_count', 0)}")
            print(f"   Cache status: {result.get('cache_status', 'Unknown')}")
            
            if result.get('matched_names'):
                print(f"   Matched products:")
                for i, name in enumerate(result['matched_names'][:5], 1):  # Show first 5
                    print(f"     {i}. {name}")
                if len(result['matched_names']) > 5:
                    print(f"     ... and {len(result['matched_names']) - 5} more")
            
            if result.get('selected_tags'):
                print(f"   Selected tags created: {len(result['selected_tags'])}")
                
        else:
            error_data = response.json()
            print(f"❌ JSON matching failed: {error_data.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error during JSON matching: {e}")
    
    # Step 4: Show how to use with real inventory data
    print("\n4. How to use with real inventory data:")
    print("   a) Prepare a JSON URL with inventory_transfer_items array")
    print("   b) Ensure the URL is accessible via HTTP/HTTPS")
    print("   c) Use the web interface or API to match products")
    print("   d) Review matched products and selected tags")
    
    # Step 5: Show API usage example
    print("\n5. API Usage Example:")
    print("""
   # Python code example:
   import requests
   
   url = "https://your-inventory-api.com/transfer-data"
   data = {'url': url}
   
   response = requests.post('http://127.0.0.1:9090/api/json-match', 
                          json=data, 
                          headers={'Content-Type': 'application/json'})
   
   if response.status_code == 200:
       result = response.json()
       print(f"Matched {result['matched_count']} products")
       for name in result['matched_names']:
           print(f"  - {name}")
   """)
    
    print("\n" + "=" * 50)
    print("🎉 JSON matching is ready to use!")
    print("   Open http://127.0.0.1:9090 in your browser")
    print("   Click 'Match products from JSON URL' button")
    print("   Enter your inventory JSON URL and start matching!")

if __name__ == "__main__":
    demo_json_matching() 