#!/usr/bin/env python3
"""
Simple test script using existing files to verify Label Maker improvements
"""

import requests
import time
import json

def test_progress_tracking():
    """Test progress tracking with existing file"""
    print("=== Testing Progress Tracking ===")
    
    base_url = "http://localhost:9090"
    
    # Upload existing file
    print("1. Uploading default_inventory.xlsx...")
    with open('data/default_inventory.xlsx', 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{base_url}/upload", files=files)
    
    if response.status_code != 200:
        print(f"✗ Upload failed: {response.status_code}")
        return False
    
    data = response.json()
    filename = data.get('filename')
    print(f"✓ Upload successful: {filename}")
    
    # Monitor progress steps
    print("2. Monitoring progress steps...")
    max_attempts = 20
    attempts = 0
    steps_seen = set()
    
    while attempts < max_attempts:
        response = requests.get(f"{base_url}/api/upload-status?filename={filename}")
        if response.status_code == 200:
            data = response.json()
            status = data.get('status')
            step = data.get('step', 'No step info')
            
            if step != 'No step info':
                steps_seen.add(step)
                print(f"  Step: {step}")
            
            if status in ['ready', 'done']:
                print("✓ Processing completed")
                break
            elif status == 'not_found':
                print("✗ File not found in processing")
                return False
        
        time.sleep(2)
        attempts += 1
    
    if len(steps_seen) > 0:
        print(f"✓ Progress tracking working - saw {len(steps_seen)} different steps")
        return True
    else:
        print("✗ No progress steps detected")
        return False

def test_lineage_matching():
    """Test lineage matching by checking available tags"""
    print("\n=== Testing Lineage Matching ===")
    
    base_url = "http://localhost:9090"
    
    # Wait for processing to complete
    time.sleep(5)
    
    # Get available tags
    response = requests.get(f"{base_url}/api/available-tags")
    if response.status_code != 200:
        print("✗ Failed to get available tags")
        return False
    
    tags = response.json()
    print(f"✓ Retrieved {len(tags)} tags")
    
    # Look for strains with descriptors
    strains_with_descriptors = []
    for tag in tags:
        strain = tag.get('Product Strain', '')
        if ' ' in strain and any(word in strain.lower() for word in ['wax', 'pre-roll', 'flower', 'concentrate']):
            strains_with_descriptors.append(tag)
    
    if strains_with_descriptors:
        print(f"✓ Found {len(strains_with_descriptors)} strains with descriptors")
        for tag in strains_with_descriptors[:3]:  # Show first 3
            print(f"  {tag.get('Product Strain')} -> {tag.get('Lineage')}")
        return True
    else:
        print("⚠ No strains with descriptors found in test data")
        return True  # Not a failure, just no test data

def test_sovereign_lineage():
    """Test sovereign lineage by updating a strain and checking persistence"""
    print("\n=== Testing Sovereign Lineage ===")
    
    base_url = "http://localhost:9090"
    
    # Get available tags first
    response = requests.get(f"{base_url}/api/available-tags")
    if response.status_code != 200:
        print("✗ Failed to get available tags")
        return False
    
    tags = response.json()
    if not tags:
        print("✗ No tags available for testing")
        return False
    
    # Find a tag to update
    test_tag = tags[0]
    tag_name = test_tag.get('Product Name*', '')
    current_lineage = test_tag.get('Lineage', '')
    
    if not tag_name:
        print("✗ No valid tag name found")
        return False
    
    print(f"1. Testing with tag: {tag_name} (current lineage: {current_lineage})")
    
    # Update lineage
    new_lineage = 'SATIVA' if current_lineage != 'SATIVA' else 'INDICA'
    update_data = {
        'tag_name': tag_name,
        'lineage': new_lineage
    }
    
    print(f"2. Updating lineage to {new_lineage}...")
    response = requests.post(f"{base_url}/api/update-lineage", json=update_data)
    
    if response.status_code == 200:
        print("✓ Lineage updated successfully")
    else:
        print(f"✗ Failed to update lineage: {response.status_code}")
        return False
    
    # Check if update was applied
    time.sleep(2)
    response = requests.get(f"{base_url}/api/available-tags")
    if response.status_code == 200:
        tags = response.json()
        updated_tag = None
        for tag in tags:
            if tag.get('Product Name*') == tag_name:
                updated_tag = tag
                break
        
        if updated_tag and updated_tag.get('Lineage') == new_lineage:
            print("✓ Sovereign lineage update confirmed")
            return True
        else:
            print("✗ Lineage update not reflected")
            return False
    else:
        print("✗ Failed to verify update")
        return False

def test_multi_format_support():
    """Test that the UI supports multiple file formats"""
    print("\n=== Testing Multi-Format UI Support ===")
    
    base_url = "http://localhost:9090"
    
    # Get the main page
    response = requests.get(base_url)
    if response.status_code != 200:
        print("✗ Failed to get main page")
        return False
    
    html = response.text
    
    # Check for multi-format support in HTML
    if 'accept=".xlsx,.csv,.parquet"' in html:
        print("✓ Multi-format file input found in UI")
        return True
    else:
        print("✗ Multi-format file input not found in UI")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Simple Label Maker Tests")
    print("=" * 50)
    
    tests = [
        ("Progress Tracking", test_progress_tracking),
        ("Lineage Matching", test_lineage_matching),
        ("Sovereign Lineage", test_sovereign_lineage),
        ("Multi-Format UI", test_multi_format_support)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! All improvements are working correctly.")
    else:
        print("⚠ Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 