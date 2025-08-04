#!/usr/bin/env python3
"""
Test script to verify product database integration with vendor, brand, and product type data.
"""

import requests
import json
import time
import os

def test_product_database_integration():
    """Test the product database integration functionality."""
    
    base_url = "http://localhost:9090"
    
    print("=== Product Database Integration Test ===\n")
    
    # Test 1: Check if the app is running
    print("1. Testing app connectivity...")
    try:
        response = requests.get(f"{base_url}/api/status")
        if response.status_code == 200:
            print("✅ App is running")
        else:
            print(f"❌ App returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to app: {e}")
        return False
    
    # Test 2: Check product database status
    print("\n2. Testing product database status...")
    try:
        response = requests.get(f"{base_url}/api/product-db/status")
        if response.status_code == 200:
            status = response.json()
            print(f"✅ Product DB Status: {status}")
        else:
            print(f"❌ Product DB status returned {response.status_code}")
    except Exception as e:
        print(f"❌ Error checking product DB status: {e}")
    
    # Test 3: Check database statistics
    print("\n3. Testing database statistics...")
    try:
        response = requests.get(f"{base_url}/api/database-stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Database Stats:")
            print(f"   - Total strains: {stats.get('total_strains', 0)}")
            print(f"   - Total products: {stats.get('total_products', 0)}")
            print(f"   - Top vendors: {len(stats.get('vendor_statistics', []))}")
            print(f"   - Top brands: {len(stats.get('brand_statistics', []))}")
            print(f"   - Product types: {len(stats.get('product_type_statistics', []))}")
        else:
            print(f"❌ Database stats returned {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting database stats: {e}")
    
    # Test 4: Check detailed vendor statistics
    print("\n4. Testing detailed vendor statistics...")
    try:
        response = requests.get(f"{base_url}/api/database-vendor-stats")
        if response.status_code == 200:
            vendor_stats = response.json()
            summary = vendor_stats.get('summary', {})
            print(f"✅ Vendor Stats:")
            print(f"   - Total vendors: {summary.get('total_vendors', 0)}")
            print(f"   - Total brands: {summary.get('total_brands', 0)}")
            print(f"   - Total product types: {summary.get('total_product_types', 0)}")
            print(f"   - Vendor-brand combinations: {summary.get('total_vendor_brand_combinations', 0)}")
            
            # Show top 5 vendors
            vendors = vendor_stats.get('vendors', [])
            if vendors:
                print(f"   - Top 5 vendors:")
                for i, vendor in enumerate(vendors[:5], 1):
                    print(f"     {i}. {vendor['vendor']} ({vendor['product_count']} products)")
        else:
            print(f"❌ Vendor stats returned {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting vendor stats: {e}")
    
    # Test 5: Check if there's a default file to test with
    print("\n5. Testing with default file...")
    default_file = "data/default_upload.xlsx"
    if os.path.exists(default_file):
        print(f"✅ Found default file: {default_file}")
        
        # Test file upload
        try:
            with open(default_file, 'rb') as f:
                files = {'file': (os.path.basename(default_file), f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
                response = requests.post(f"{base_url}/upload", files=files)
                
                if response.status_code == 200:
                    print("✅ File uploaded successfully")
                    
                    # Wait a moment for background processing
                    print("   Waiting for background processing...")
                    time.sleep(2)
                    
                    # Check updated stats
                    response = requests.get(f"{base_url}/api/database-stats")
                    if response.status_code == 200:
                        updated_stats = response.json()
                        print(f"   Updated stats after upload:")
                        print(f"   - Total products: {updated_stats.get('total_products', 0)}")
                        print(f"   - Top vendors: {len(updated_stats.get('vendor_statistics', []))}")
                else:
                    print(f"❌ File upload failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Error uploading file: {e}")
    else:
        print(f"⚠️  No default file found at {default_file}")
        print("   You can upload a file manually to test the integration")
    
    # Test 6: Check performance stats
    print("\n6. Testing performance statistics...")
    try:
        response = requests.get(f"{base_url}/api/performance")
        if response.status_code == 200:
            perf_stats = response.json()
            print(f"✅ Performance Stats:")
            print(f"   - Product DB queries: {perf_stats.get('product_db', {}).get('total_queries', 0)}")
            print(f"   - Cache hit rate: {perf_stats.get('product_db', {}).get('cache_hit_rate', 0):.2%}")
        else:
            print(f"❌ Performance stats returned {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting performance stats: {e}")
    
    print("\n=== Test Complete ===")
    print("\nTo test the integration:")
    print("1. Upload an Excel file through the web interface")
    print("2. Check the database statistics at /api/database-stats")
    print("3. View detailed vendor stats at /api/database-vendor-stats")
    print("4. Export the database at /api/database-export")
    
    return True

if __name__ == "__main__":
    test_product_database_integration() 