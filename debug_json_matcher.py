#!/usr/bin/env python3
"""
Debug script to identify JSON matcher processing issues
"""

import requests
import json
import time
import logging
import traceback
from urllib.parse import urlparse

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_json_url(url):
    """Test a JSON URL to identify potential issues"""
    print(f"🔍 Testing JSON URL: {url}")
    print("=" * 60)
    
    # Step 1: Test URL accessibility
    print("\n1. Testing URL accessibility...")
    try:
        start_time = time.time()
        response = requests.get(url, timeout=30)
        load_time = time.time() - start_time
        
        print(f"✅ URL accessible (Status: {response.status_code})")
        print(f"   Load time: {load_time:.2f} seconds")
        print(f"   Content length: {len(response.content)} bytes")
        
        if response.status_code != 200:
            print(f"❌ Warning: Non-200 status code: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ URL timeout - server is too slow to respond")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - cannot reach the URL")
        return False
    except Exception as e:
        print(f"❌ Error accessing URL: {e}")
        return False
    
    # Step 2: Test JSON parsing
    print("\n2. Testing JSON parsing...")
    try:
        start_time = time.time()
        data = response.json()
        parse_time = time.time() - start_time
        
        print(f"✅ JSON parsed successfully")
        print(f"   Parse time: {parse_time:.2f} seconds")
        
        # Check for expected structure
        if isinstance(data, dict):
            print(f"   Root type: dictionary with {len(data)} keys")
            if 'inventory_transfer_items' in data:
                items = data['inventory_transfer_items']
                print(f"   Found 'inventory_transfer_items' with {len(items)} items")
                
                if items:
                    # Sample first item
                    first_item = items[0]
                    print(f"   First item keys: {list(first_item.keys())}")
                    
                    # Check for required fields
                    required_fields = ['product_name', 'vendor', 'brand']
                    missing_fields = [field for field in required_fields if field not in first_item]
                    if missing_fields:
                        print(f"   ⚠️  Missing fields in first item: {missing_fields}")
                    else:
                        print(f"   ✅ All required fields present")
                        
                    # Check data types
                    for field in required_fields:
                        if field in first_item:
                            value = first_item[field]
                            print(f"   {field}: {type(value).__name__} = '{value}'")
                else:
                    print("   ⚠️  No items found in inventory_transfer_items")
            else:
                print("   ⚠️  No 'inventory_transfer_items' key found")
                print(f"   Available keys: {list(data.keys())}")
        else:
            print(f"   ⚠️  Root is not a dictionary (type: {type(data).__name__})")
            
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Error parsing JSON: {e}")
        return False
    
    # Step 3: Test with Flask endpoint
    print("\n3. Testing with Flask JSON matcher...")
    try:
        flask_data = {'url': url}
        start_time = time.time()
        
        response = requests.post('http://127.0.0.1:9090/api/json-match',
                               json=flask_data,
                               headers={'Content-Type': 'application/json'},
                               timeout=120)  # 2 minute timeout
        
        process_time = time.time() - start_time
        print(f"   Processing time: {process_time:.2f} seconds")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Flask JSON matching completed successfully")
            print(f"   Matched count: {result.get('matched_count', 0)}")
            print(f"   Cache status: {result.get('cache_status', 'Unknown')}")
            print(f"   Success: {result.get('success', False)}")
        else:
            error_data = response.json()
            print(f"❌ Flask JSON matching failed: {error_data.get('error', 'Unknown error')}")
            print(f"   Full error response: {error_data}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Flask processing timeout - the JSON dataset might be too large")
        return False
    except Exception as e:
        print(f"❌ Error with Flask processing: {e}")
        print(f"   Full traceback:")
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 60)
    print("✅ JSON URL test completed successfully")
    return True

def analyze_json_structure(url):
    """Analyze the JSON structure to identify potential issues"""
    print(f"\n🔬 Analyzing JSON structure...")
    
    try:
        response = requests.get(url, timeout=30)
        data = response.json()
        
        if 'inventory_transfer_items' not in data:
            print("❌ No 'inventory_transfer_items' found - this is required")
            return
            
        items = data['inventory_transfer_items']
        print(f"📊 Found {len(items)} items to process")
        
        # Analyze item structure
        if items:
            first_item = items[0]
            print(f"📋 Item structure analysis:")
            print(f"   Total fields: {len(first_item)}")
            
            # Check field types and values
            field_analysis = {}
            for key, value in first_item.items():
                field_analysis[key] = {
                    'type': type(value).__name__,
                    'value_length': len(str(value)) if value else 0,
                    'is_empty': not value if value is not None else True
                }
            
            # Show problematic fields
            print(f"   Field analysis:")
            for field, analysis in field_analysis.items():
                status = "✅"
                if analysis['is_empty']:
                    status = "⚠️"
                if analysis['value_length'] > 100:
                    status = "🔍"
                print(f"     {status} {field}: {analysis['type']} (length: {analysis['value_length']})")
        
        # Check for potential performance issues
        print(f"\n⚡ Performance analysis:")
        print(f"   Total items: {len(items)}")
        
        if len(items) > 1000:
            print(f"   ⚠️  Large dataset detected ({len(items)} items)")
            print(f"   💡 Consider processing in smaller batches")
        
        # Check for memory-intensive fields
        large_fields = []
        if items:
            for key, value in items[0].items():
                if isinstance(value, str) and len(value) > 500:
                    large_fields.append(key)
        
        if large_fields:
            print(f"   ⚠️  Large text fields detected: {large_fields}")
            print(f"   💡 These might cause memory issues")
        
    except Exception as e:
        print(f"❌ Error analyzing JSON structure: {e}")

def main():
    """Main function to run diagnostics"""
    print("🔧 JSON Matcher Diagnostic Tool")
    print("=" * 60)
    
    # Get URL from user
    url = input("Enter the JSON URL to test: ").strip()
    
    if not url:
        print("❌ No URL provided")
        return
    
    # Validate URL format
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            print("❌ Invalid URL format")
            return
    except Exception:
        print("❌ Invalid URL format")
        return
    
    # Run tests
    success = test_json_url(url)
    
    if success:
        analyze_json_structure(url)
    
    print("\n" + "=" * 60)
    print("📋 Diagnostic Summary:")
    if success:
        print("✅ All tests passed - JSON matcher should work")
        print("💡 If it still stops, check:")
        print("   - Browser console for JavaScript errors")
        print("   - Server logs for Python errors")
        print("   - Network tab for request/response issues")
    else:
        print("❌ Issues detected - see above for details")
        print("💡 Common solutions:")
        print("   - Check URL accessibility")
        print("   - Verify JSON format")
        print("   - Try with a smaller dataset")

if __name__ == "__main__":
    main() 