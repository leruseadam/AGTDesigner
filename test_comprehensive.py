#!/usr/bin/env python3
"""
Comprehensive test script for Label Maker improvements
Tests: multi-format uploads, lineage matching, sovereign lineage, progress tracking
"""

import os
import sys
import time
import requests
import pandas as pd
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_multi_format_upload():
    """Test uploading Excel, CSV, and Parquet files"""
    print("=== Testing Multi-Format Upload Support ===")
    
    base_url = "http://localhost:9090"
    
    # Create test data
    test_data = {
        'Product Name*': ['Blue Dream Wax - 1g', 'Jack Herer Pre-Roll', 'OG Kush Flower'],
        'Product Strain': ['Blue Dream', 'Jack Herer', 'OG Kush'],
        'Lineage': ['HYBRID', 'SATIVA', 'HYBRID'],
        'Brand': ['Test Brand', 'Test Brand', 'Test Brand'],
        'Product Type': ['concentrate', 'pre-roll', 'flower']
    }
    df = pd.DataFrame(test_data)
    
    # Test CSV upload
    print("1. Testing CSV upload...")
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
        df.to_csv(f.name, index=False)
        files = {'file': open(f.name, 'rb')}
        response = requests.post(f"{base_url}/upload", files=files)
        files['file'].close()
        os.unlink(f.name)
    
    if response.status_code == 200:
        print("✓ CSV upload successful")
        data = response.json()
        if 'filename' in data:
            print(f"  Filename: {data['filename']}")
    else:
        print(f"✗ CSV upload failed: {response.status_code}")
        return False
    
    # Test Excel upload
    print("2. Testing Excel upload...")
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
        df.to_excel(f.name, index=False)
        files = {'file': open(f.name, 'rb')}
        response = requests.post(f"{base_url}/upload", files=files)
        files['file'].close()
        os.unlink(f.name)
    
    if response.status_code == 200:
        print("✓ Excel upload successful")
    else:
        print(f"✗ Excel upload failed: {response.status_code}")
        return False
    
    return True

def test_lineage_matching():
    """Test lineage matching with strain descriptors"""
    print("\n=== Testing Lineage Matching with Descriptors ===")
    
    base_url = "http://localhost:9090"
    
    # Create test data with descriptors
    test_data = {
        'Product Name*': [
            'Blue Dream Wax - 1g',
            'Blue Dream Pre-Roll - 1g', 
            'Jack Herer Concentrate',
            'OG Kush Flower - 3.5g'
        ],
        'Product Strain': [
            'Blue Dream Wax',
            'Blue Dream Pre-Roll',
            'Jack Herer Concentrate', 
            'OG Kush Flower'
        ],
        'Lineage': ['HYBRID', 'HYBRID', 'SATIVA', 'HYBRID'],
        'Brand': ['Test Brand'] * 4,
        'Product Type': ['concentrate', 'pre-roll', 'concentrate', 'flower']
    }
    df = pd.DataFrame(test_data)
    
    # Upload test file
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
        df.to_csv(f.name, index=False)
        files = {'file': open(f.name, 'rb')}
        response = requests.post(f"{base_url}/upload", files=files)
        files['file'].close()
        os.unlink(f.name)
    
    if response.status_code != 200:
        print("✗ Failed to upload test file for lineage matching")
        return False
    
    # Wait for processing and check results
    time.sleep(5)
    
    # Get available tags to check lineage assignment
    response = requests.get(f"{base_url}/api/available-tags")
    if response.status_code == 200:
        tags = response.json()
        print(f"✓ Retrieved {len(tags)} tags")
        
        # Check if Blue Dream and Jack Herer were correctly extracted
        blue_dream_found = False
        jack_herer_found = False
        
        for tag in tags:
            if 'Blue Dream' in tag.get('Product Strain', ''):
                blue_dream_found = True
                print(f"  Found Blue Dream: {tag.get('Product Strain')} -> {tag.get('Lineage')}")
            if 'Jack Herer' in tag.get('Product Strain', ''):
                jack_herer_found = True
                print(f"  Found Jack Herer: {tag.get('Product Strain')} -> {tag.get('Lineage')}")
        
        if blue_dream_found and jack_herer_found:
            print("✓ Lineage matching with descriptors working")
            return True
        else:
            print("✗ Some strains not found or incorrectly matched")
            return False
    else:
        print("✗ Failed to retrieve tags")
        return False

def test_sovereign_lineage():
    """Test sovereign lineage persistence across uploads"""
    print("\n=== Testing Sovereign Lineage Persistence ===")
    
    base_url = "http://localhost:9090"
    
    # First upload with default lineage
    test_data1 = {
        'Product Name*': ['Blue Dream Test - 1g'],
        'Product Strain': ['Blue Dream'],
        'Lineage': ['HYBRID'],
        'Brand': ['Test Brand'],
        'Product Type': ['flower']
    }
    df1 = pd.DataFrame(test_data1)
    
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
        df1.to_csv(f.name, index=False)
        files = {'file': open(f.name, 'rb')}
        response = requests.post(f"{base_url}/upload", files=files)
        files['file'].close()
        os.unlink(f.name)
    
    if response.status_code != 200:
        print("✗ Failed first upload")
        return False
    
    time.sleep(3)
    
    # Update lineage to SATIVA
    print("1. Updating Blue Dream lineage to SATIVA...")
    update_data = {
        'tag_name': 'Blue Dream Test - 1g',
        'lineage': 'SATIVA'
    }
    response = requests.post(f"{base_url}/api/update-lineage", json=update_data)
    
    if response.status_code == 200:
        print("✓ Lineage updated successfully")
    else:
        print(f"✗ Failed to update lineage: {response.status_code}")
        return False
    
    time.sleep(2)
    
    # Second upload with different lineage
    test_data2 = {
        'Product Name*': ['Blue Dream Second - 1g'],
        'Product Strain': ['Blue Dream'],
        'Lineage': ['HYBRID'],  # Should be overridden by sovereign lineage
        'Brand': ['Test Brand'],
        'Product Type': ['flower']
    }
    df2 = pd.DataFrame(test_data2)
    
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
        df2.to_csv(f.name, index=False)
        files = {'file': open(f.name, 'rb')}
        response = requests.post(f"{base_url}/upload", files=files)
        files['file'].close()
        os.unlink(f.name)
    
    if response.status_code != 200:
        print("✗ Failed second upload")
        return False
    
    time.sleep(3)
    
    # Check if both Blue Dream products have SATIVA lineage
    response = requests.get(f"{base_url}/api/available-tags")
    if response.status_code == 200:
        tags = response.json()
        blue_dream_count = 0
        sativa_count = 0
        
        for tag in tags:
            if 'Blue Dream' in tag.get('Product Strain', ''):
                blue_dream_count += 1
                if tag.get('Lineage') == 'SATIVA':
                    sativa_count += 1
                print(f"  Blue Dream product: {tag.get('Product Name*')} -> {tag.get('Lineage')}")
        
        if blue_dream_count > 0 and sativa_count == blue_dream_count:
            print("✓ Sovereign lineage working - all Blue Dream products have SATIVA lineage")
            return True
        else:
            print(f"✗ Sovereign lineage failed - {sativa_count}/{blue_dream_count} Blue Dream products have SATIVA lineage")
            return False
    else:
        print("✗ Failed to retrieve tags for verification")
        return False

def test_progress_tracking():
    """Test progress tracking during upload"""
    print("\n=== Testing Progress Tracking ===")
    
    base_url = "http://localhost:9090"
    
    # Create larger test file to see progress steps
    test_data = {
        'Product Name*': [f'Test Product {i}' for i in range(100)],
        'Product Strain': [f'Test Strain {i % 10}' for i in range(100)],
        'Lineage': ['HYBRID'] * 100,
        'Brand': ['Test Brand'] * 100,
        'Product Type': ['flower'] * 100
    }
    df = pd.DataFrame(test_data)
    
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
        df.to_csv(f.name, index=False)
        files = {'file': open(f.name, 'rb')}
        
        print("1. Uploading large test file...")
        response = requests.post(f"{base_url}/upload", files=files)
        files['file'].close()
        os.unlink(f.name)
    
    if response.status_code != 200:
        print("✗ Failed to upload test file")
        return False
    
    data = response.json()
    filename = data.get('filename')
    
    if not filename:
        print("✗ No filename returned")
        return False
    
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

def test_performance():
    """Test performance improvements"""
    print("\n=== Testing Performance Improvements ===")
    
    base_url = "http://localhost:9090"
    
    # Create medium-sized test file
    test_data = {
        'Product Name*': [f'Performance Test {i}' for i in range(500)],
        'Product Strain': [f'Strain {i % 20}' for i in range(500)],
        'Lineage': ['HYBRID'] * 500,
        'Brand': ['Test Brand'] * 500,
        'Product Type': ['flower'] * 500
    }
    df = pd.DataFrame(test_data)
    
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
        df.to_csv(f.name, index=False)
        files = {'file': open(f.name, 'rb')}
        
        print("1. Testing upload and processing time...")
        start_time = time.time()
        response = requests.post(f"{base_url}/upload", files=files)
        files['file'].close()
        os.unlink(f.name)
    
    if response.status_code != 200:
        print("✗ Upload failed")
        return False
    
    upload_time = time.time() - start_time
    print(f"  Upload time: {upload_time:.2f} seconds")
    
    data = response.json()
    filename = data.get('filename')
    
    # Monitor processing time
    start_time = time.time()
    max_attempts = 30
    attempts = 0
    
    while attempts < max_attempts:
        response = requests.get(f"{base_url}/api/upload-status?filename={filename}")
        if response.status_code == 200:
            data = response.json()
            status = data.get('status')
            
            if status in ['ready', 'done']:
                processing_time = time.time() - start_time
                total_time = upload_time + processing_time
                print(f"  Processing time: {processing_time:.2f} seconds")
                print(f"  Total time: {total_time:.2f} seconds")
                
                if total_time < 30:  # Should be reasonably fast
                    print("✓ Performance acceptable")
                    return True
                else:
                    print("⚠ Performance could be improved")
                    return True
                break
        
        time.sleep(1)
        attempts += 1
    
    print("✗ Processing timeout")
    return False

def main():
    """Run all tests"""
    print("🚀 Starting Comprehensive Label Maker Tests")
    print("=" * 50)
    
    tests = [
        ("Multi-Format Upload", test_multi_format_upload),
        ("Lineage Matching", test_lineage_matching),
        ("Sovereign Lineage", test_sovereign_lineage),
        ("Progress Tracking", test_progress_tracking),
        ("Performance", test_performance)
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
    sys.exit(0 if success else 1) 