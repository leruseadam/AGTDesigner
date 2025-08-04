#!/usr/bin/env python3
"""
Test script to verify strain matching functionality
"""

import requests
import json
import time
import os

def test_strain_matching():
    """Test strain matching functionality"""
    base_url = "http://127.0.0.1:9090"
    
    print("=== Testing Strain Matching ===")
    
    # Test 1: Check if product database is enabled
    print("\n1. Checking product database status...")
    try:
        response = requests.get(f"{base_url}/api/product-db/status")
        if response.status_code == 200:
            status = response.json()
            print(f"   Product DB enabled: {status.get('enabled', False)}")
            print(f"   Stats: {status.get('stats', {})}")
        else:
            print(f"   Error: {response.status_code}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Check if we can get available tags (should be empty without upload)
    print("\n2. Checking available tags (should be empty)...")
    try:
        response = requests.get(f"{base_url}/api/available-tags")
        if response.status_code == 200:
            tags = response.json()
            print(f"   Available tags: {len(tags)} tags")
            if tags:
                print(f"   Sample tags: {tags[:3]}")
        else:
            print(f"   Error: {response.status_code}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: Check database stats
    print("\n3. Checking database stats...")
    try:
        response = requests.get(f"{base_url}/api/database-stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"   Total strains: {stats.get('total_strains', 0)}")
            print(f"   Lineage counts: {stats.get('lineage_counts', {})}")
            print(f"   Top strains: {len(stats.get('top_strains', []))}")
        else:
            print(f"   Error: {response.status_code}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 4: Check database view
    print("\n4. Checking database view...")
    try:
        response = requests.get(f"{base_url}/api/database-view")
        if response.status_code == 200:
            data = response.json()
            print(f"   Total strains in view: {data.get('total_strains', 0)}")
            print(f"   Total products in view: {data.get('total_products', 0)}")
            if data.get('strains'):
                print(f"   Sample strains: {[s['strain_name'] for s in data['strains'][:3]]}")
        else:
            print(f"   Error: {response.status_code}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 5: Try to upload a test file
    print("\n5. Testing file upload...")
    test_file = "uploads/test_products.xlsx"
    if os.path.exists(test_file):
        try:
            with open(test_file, 'rb') as f:
                files = {'file': f}
                response = requests.post(f"{base_url}/upload", files=files)
                
            if response.status_code == 200:
                result = response.json()
                filename = result.get('filename', '')
                print(f"   Upload successful: {filename}")
                
                # Wait for processing
                print("   Waiting for processing...")
                time.sleep(2)
                
                # Check upload status
                status_response = requests.get(f"{base_url}/api/upload-status?filename={filename}")
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    print(f"   Upload status: {status_data.get('status', 'unknown')}")
                
                # Check available tags after upload
                tags_response = requests.get(f"{base_url}/api/available-tags")
                if tags_response.status_code == 200:
                    tags = tags_response.json()
                    print(f"   Available tags after upload: {len(tags)} tags")
                    if tags:
                        print(f"   Sample tags: {[t.get('displayName', 'Unknown') for t in tags[:3]]}")
                        # Check for canonical_lineage in tags
                        for tag in tags[:3]:
                            canonical = tag.get('canonical_lineage', 'None')
                            strain = tag.get('Product Strain', 'None')
                            print(f"     - {tag.get('displayName', 'Unknown')}: Strain='{strain}', Canonical='{canonical}'")
            else:
                print(f"   Upload failed: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"   Upload error: {e}")
    else:
        print(f"   Test file not found: {test_file}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_strain_matching() 