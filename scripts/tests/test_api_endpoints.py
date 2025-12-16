#!/usr/bin/env python3
"""
Test script to verify the fixed API endpoints work correctly.
"""

import requests
import json

def test_api_endpoint(url, endpoint_name):
    """Test a single API endpoint."""
    print(f"\n🔍 Testing {endpoint_name}...")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {endpoint_name} - SUCCESS")
            print(f"Response keys: {list(data.keys())}")
            
            # Check for expected data structure
            if endpoint_name == "database-analytics":
                expected_keys = ['product_type_distribution', 'lineage_distribution', 'vendor_performance', 'recent_activity']
                for key in expected_keys:
                    if key in data:
                        print(f"  ✅ {key}: Found")
                    else:
                        print(f"  ❌ {key}: Missing")
                        
            elif endpoint_name == "database-vendor-stats":
                expected_keys = ['vendors', 'brands', 'total_vendors', 'total_brands']
                for key in expected_keys:
                    if key in data:
                        print(f"  ✅ {key}: Found")
                    else:
                        print(f"  ❌ {key}: Missing")
                        
        else:
            print(f"❌ {endpoint_name} - FAILED")
            print(f"Error: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ {endpoint_name} - REQUEST FAILED")
        print(f"Error: {e}")
    except json.JSONDecodeError as e:
        print(f"❌ {endpoint_name} - JSON DECODE FAILED")
        print(f"Error: {e}")
    except Exception as e:
        print(f"❌ {endpoint_name} - UNEXPECTED ERROR")
        print(f"Error: {e}")

def main():
    """Test all API endpoints."""
    base_url = "https://www.agtpricetags.com"
    
    endpoints = [
        ("/api/database-analytics", "database-analytics"),
        ("/api/database-vendor-stats", "database-vendor-stats"),
        ("/api/database-stats", "database-stats"),  # This should work
        ("/api/database-health", "database-health")  # This should work
    ]
    
    print("🚀 Testing API Endpoints")
    print("=" * 50)
    
    for endpoint, name in endpoints:
        url = base_url + endpoint
        test_api_endpoint(url, name)
    
    print("\n" + "=" * 50)
    print("🏁 API Testing Complete")

if __name__ == "__main__":
    main()
