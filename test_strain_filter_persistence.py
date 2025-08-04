#!/usr/bin/env python3
"""
Test script to verify strain filter persistence functionality
"""

import requests
import json
import time
import os

def test_strain_filter_persistence():
    """Test strain filter persistence functionality"""
    base_url = "http://127.0.0.1:9090"
    
    print("=== Testing Strain Filter Persistence ===")
    
    # Test 1: Check if server is running
    print("\n1. Checking server status...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("   Server is running")
        else:
            print(f"   Server error: {response.status_code}")
            return
    except Exception as e:
        print(f"   Server connection error: {e}")
        return
    
    # Test 2: Upload a test file
    print("\n2. Uploading test file...")
    test_file = "data/default_inventory.xlsx"
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
                time.sleep(5)
                
                # Check upload status
                status_response = requests.get(f"{base_url}/api/upload-status?filename={filename}")
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    print(f"   Upload status: {status_data.get('status', 'unknown')}")
                
                # Test 3: Get available tags and check for strain data
                print("\n3. Checking available tags for strain data...")
                tags_response = requests.get(f"{base_url}/api/available-tags")
                if tags_response.status_code == 200:
                    tags = tags_response.json()
                    print(f"   Available tags: {len(tags)} tags")
                    
                    if tags:
                        # Check for strain data in tags
                        strains_found = set()
                        for tag in tags[:10]:  # Check first 10 tags
                            strain = tag.get('Product Strain', '')
                            if strain and strain.strip():
                                strains_found.add(strain.strip())
                        
                        print(f"   Unique strains found: {len(strains_found)}")
                        if strains_found:
                            print(f"   Sample strains: {list(strains_found)[:5]}")
                        
                        # Test 4: Check filter options
                        print("\n4. Checking filter options...")
                        filter_response = requests.get(f"{base_url}/api/filter-options")
                        if filter_response.status_code == 200:
                            filter_options = filter_response.json()
                            strain_options = filter_options.get('strain', [])
                            print(f"   Strain filter options: {len(strain_options)} options")
                            if strain_options:
                                print(f"   Sample strain options: {strain_options[:5]}")
                        
                        # Test 5: Test strain filtering
                        if strain_options:
                            # Find a good test strain (not 'nan' or 'Mixed')
                            test_strain = None
                            for strain in strain_options:
                                if strain and strain != 'nan' and strain != 'Mixed' and strain.strip():
                                    test_strain = strain
                                    break
                            
                            if test_strain:
                                print(f"\n5. Testing strain filtering with: {test_strain}")
                            else:
                                print(f"\n5. No suitable test strain found, using first option: {strain_options[0]}")
                                test_strain = strain_options[0]
                            
                            # Apply strain filter
                            filter_data = {
                                'filters': {
                                    'strain': test_strain
                                }
                            }
                            
                            filter_response = requests.post(f"{base_url}/api/filter-options", 
                                                          json=filter_data)
                            if filter_response.status_code == 200:
                                filtered_options = filter_response.json()
                                print(f"   Filter applied successfully")
                                print(f"   Filtered strain options: {len(filtered_options.get('strain', []))}")
                            else:
                                print(f"   Filter application failed: {filter_response.status_code}")
                        
                        # Test 6: Test download with strain filter
                        print(f"\n6. Testing download with strain filter...")
                        download_data = {
                            'filters': {
                                'strain': test_strain
                            },
                            'selected_tags': []
                        }
                        
                        download_response = requests.post(f"{base_url}/api/download-processed-excel", 
                                                        json=download_data)
                        if download_response.status_code == 200:
                            print(f"   Download with strain filter successful")
                        else:
                            print(f"   Download with strain filter failed: {download_response.status_code}")
                            print(f"   Response: {download_response.text}")
                    else:
                        print("   No tags found")
                else:
                    print(f"   Failed to get available tags: {tags_response.status_code}")
            else:
                print(f"   Upload failed: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"   Upload error: {e}")
    else:
        print(f"   Test file not found: {test_file}")
    
    print("\n=== Test Complete ===")
    print("To test persistence manually:")
    print("1. Open http://localhost:9090 in your browser")
    print("2. Upload the default_inventory.xlsx file")
    print("3. Change the strain filter to a specific strain")
    print("4. Reload the page - the strain filter should remain selected")
    print("5. Upload a different file - the strain filter should still be applied")

if __name__ == "__main__":
    test_strain_filter_persistence() 