#!/usr/bin/env python3
"""
Debug script to test JSON matching and see what's happening with matched_tags.
"""

import requests
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_json_matching():
    """Test JSON matching and check the response."""
    
    # Test with a working JSON URL or create mock data
    # For testing, let's use a simple JSON structure that should work
    test_data = {
        'url': 'https://jsonplaceholder.typicode.com/posts/1'  # This should work for testing
    }
    
    try:
        # Make request to the JSON matching endpoint
        response = requests.post('http://127.0.0.1:5001/api/json-match', 
                               json=test_data, 
                               timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            
            print("=== JSON Matching Response ===")
            print(f"Success: {result.get('success', False)}")
            print(f"Matched count: {result.get('matched_count', 0)}")
            print(f"Available tags count: {len(result.get('available_tags', []))}")
            print(f"JSON matched tags count: {len(result.get('json_matched_tags', []))}")
            print(f"Filter mode: {result.get('filter_mode', 'unknown')}")
            print(f"Has full Excel: {result.get('has_full_excel', False)}")
            print(f"Message: {result.get('message', 'No message')}")
            
            # Check if available_tags contains JSON matched items
            available_tags = result.get('available_tags', [])
            json_matched_in_available = [tag for tag in available_tags if tag.get('Source') == 'JSON Match']
            print(f"JSON matched items in available_tags: {len(json_matched_in_available)}")
            
            if json_matched_in_available:
                print("Sample JSON matched items in available_tags:")
                for i, tag in enumerate(json_matched_in_available[:3]):
                    print(f"  {i+1}. {tag.get('Product Name*', 'Unknown')} (Source: {tag.get('Source', 'None')})")
            
            # Check json_matched_tags separately
            json_matched_tags = result.get('json_matched_tags', [])
            if json_matched_tags:
                print("Sample JSON matched tags:")
                for i, tag in enumerate(json_matched_tags[:3]):
                    print(f"  {i+1}. {tag.get('Product Name*', 'Unknown')} (Source: {tag.get('Source', 'None')})")
            
            # Check if we're getting the full Excel list
            if len(available_tags) > 1000:  # Likely full Excel list
                print(f"⚠️  WARNING: Available tags count ({len(available_tags)}) suggests full Excel list, not JSON matched items")
                
                # Check if any items have Source field
                items_with_source = [tag for tag in available_tags if 'Source' in tag]
                print(f"Items with Source field: {len(items_with_source)}")
                
                if items_with_source:
                    sources = set(tag.get('Source') for tag in items_with_source)
                    print(f"Source values found: {sources}")
                else:
                    print("No items have Source field - this indicates full Excel list")
            
        else:
            print(f"Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Error testing JSON matching: {e}")

def test_with_mock_data():
    """Test JSON matching with mock data to bypass URL issues."""
    
    # Create mock JSON data that should match some products in the Excel file
    mock_json_data = {
        'inventory_transfer_items': [
            {
                'product_name': 'Core Reactor Quartz Banger',
                'brand': 'Test Brand',
                'vendor': 'Test Vendor',
                'quantity': 1,
                'unit_of_measure': 'each'
            },
            {
                'product_name': 'Terp Slurper Quartz Banger', 
                'brand': 'Test Brand',
                'vendor': 'Test Vendor',
                'quantity': 2,
                'unit_of_measure': 'each'
            }
        ]
    }
    
    try:
        # Make request to the JSON matching endpoint with mock data
        # We need to send a URL parameter, so let's use a data URL with our mock JSON
        import json
        import base64
        
        # Encode the mock data as a data URL
        json_str = json.dumps(mock_json_data)
        encoded_data = base64.b64encode(json_str.encode()).decode()
        data_url = f"data:application/json;base64,{encoded_data}"
        
        response = requests.post('http://127.0.0.1:5001/api/json-match', 
                               json={'url': data_url}, 
                               timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            print("=== Mock Data JSON Matching Response ===")
            print(f"Success: {result.get('success', False)}")
            print(f"Matched count: {result.get('matched_count', 0)}")
            print(f"Available tags count: {len(result.get('available_tags', []))}")
            print(f"JSON matched tags count: {len(result.get('json_matched_tags', []))}")
            
        else:
            print(f"Mock data test error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Error testing with mock data: {e}")

if __name__ == "__main__":
    print("Testing with real URL...")
    test_json_matching()
    print("\n" + "="*50 + "\n")
    print("Testing with mock data...")
    test_with_mock_data() 