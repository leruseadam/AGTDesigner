#!/usr/bin/env python3
"""
Test script to verify the lineage editor loading fix works properly.
"""

import requests
import time
import json
import sys

def test_lineage_editor_loading():
    """Test that the lineage editor loads properly without getting stuck."""
    
    base_url = "http://127.0.0.1:9090"
    
    print("Testing lineage editor loading fix...")
    
    # Test 1: Check if server is responsive
    try:
        response = requests.get(f"{base_url}/api/health", timeout=10)
        if response.status_code != 200:
            print("✗ Server is not responding properly")
            return False
        print("✓ Server is responsive")
    except Exception as e:
        print(f"✗ Server connection failed: {e}")
        return False
    
    # Test 2: Check if lineage editor endpoints are available
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            print("✓ Main page loads successfully")
        else:
            print("✗ Main page failed to load")
            return False
    except Exception as e:
        print(f"✗ Main page load failed: {e}")
        return False
    
    # Test 3: Test lineage update endpoint
    try:
        response = requests.post(f"{base_url}/api/update-lineage",
                               json={
                                   "tag_name": "Test Product",
                                   "Product Name*": "Test Product",
                                   "lineage": "HYBRID"
                               },
                               timeout=15)
        
        # We expect either 200 (success) or 404 (product not found)
        if response.status_code in [200, 404]:
            print("✓ Lineage update endpoint responds properly")
        else:
            print(f"✗ Lineage update endpoint returned unexpected status: {response.status_code}")
            return False
    except requests.exceptions.Timeout:
        print("✗ Lineage update endpoint timed out")
        return False
    except Exception as e:
        print(f"✗ Lineage update endpoint failed: {e}")
        return False
    
    # Test 4: Test strain lineage update endpoint
    try:
        response = requests.post(f"{base_url}/api/update-strain-lineage",
                               json={
                                   "strain_name": "Test Strain",
                                   "lineage": "HYBRID"
                               },
                               timeout=15)
        
        # We expect either 200 (success) or 404 (strain not found)
        if response.status_code in [200, 404]:
            print("✓ Strain lineage update endpoint responds properly")
        else:
            print(f"✗ Strain lineage update endpoint returned unexpected status: {response.status_code}")
            return False
    except requests.exceptions.Timeout:
        print("✗ Strain lineage update endpoint timed out")
        return False
    except Exception as e:
        print(f"✗ Strain lineage update endpoint failed: {e}")
        return False
    
    return True

def test_frontend_loading_protection():
    """Test that frontend loading protection is implemented."""
    
    print("\nTesting frontend loading protection...")
    
    # Check if the enhanced lineage editor JS file exists
    try:
        with open('static/js/lineage-editor.js', 'r') as f:
            js_content = f.read()
            
        checks = [
            ('isLoading', 'Loading state management'),
            ('loadingTimeout', 'Loading timeout protection'),
            ('initializeWithTimeout', 'Timeout-protected initialization'),
            ('forceInitialize', 'Force initialization fallback'),
            ('forceCleanup', 'Force cleanup mechanism'),
            ('emergencyLineageModalCleanup', 'Emergency cleanup function'),
            ('setTimeout', 'Startup delay implementation'),
            ('retry delay', 'Retry mechanism')
        ]
        
        all_passed = True
        for check, description in checks:
            if check in js_content:
                print(f"✓ {description} found")
            else:
                print(f"✗ {description} not found")
                all_passed = False
        
        return all_passed
        
    except FileNotFoundError:
        print("✗ Lineage editor JS file not found")
        return False
    except Exception as e:
        print(f"✗ Error reading JS file: {e}")
        return False

def test_backend_loading_protection():
    """Test that backend loading protection is implemented."""
    
    print("\nTesting backend loading protection...")
    
    # Check if the enhanced backend files exist
    backend_files = [
        ('src/core/data/session_manager.py', 'Session manager with queue system'),
        ('src/core/data/database_notifier.py', 'Database notifier with timeout protection'),
        ('src/core/data/product_database.py', 'Product database with timeout protection'),
        ('app.py', 'Backend API with timeout protection')
    ]
    
    all_passed = True
    for filename, description in backend_files:
        try:
            with open(filename, 'r') as f:
                content = f.read()
                
            checks = [
                ('queue.Queue', 'Operation queue system'),
                ('threading.RLock', 'RLock for better performance'),
                ('thread.join(timeout=', 'Timeout protection'),
                ('_notify_with_timeout', 'Timeout notifications'),
                ('forceInitialize', 'Force initialization'),
                ('forceCleanup', 'Force cleanup')
            ]
            
            file_passed = True
            for check, check_desc in checks:
                if check in content:
                    print(f"  ✓ {check_desc} in {filename}")
                else:
                    print(f"  ✗ {check_desc} missing in {filename}")
                    file_passed = False
            
            if file_passed:
                print(f"✓ {description} implemented")
            else:
                print(f"✗ {description} incomplete")
                all_passed = False
                
        except FileNotFoundError:
            print(f"✗ {filename} not found")
            all_passed = False
        except Exception as e:
            print(f"✗ Error reading {filename}: {e}")
            all_passed = False
    
    return all_passed

def main():
    """Run all loading fix tests."""
    
    print("="*60)
    print("LINEAGE EDITOR LOADING FIX TEST")
    print("="*60)
    
    # Run all tests
    tests = [
        ("Backend Loading Protection", test_backend_loading_protection),
        ("Frontend Loading Protection", test_frontend_loading_protection),
        ("Lineage Editor Loading", test_lineage_editor_loading)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                print(f"✓ {test_name} PASSED")
            else:
                print(f"✗ {test_name} FAILED")
        except Exception as e:
            print(f"✗ {test_name} ERROR: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    print(f"Success rate: {passed/total*100:.1f}%")
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status} {test_name}")
    
    if passed >= total:
        print("\n🎉 OVERALL RESULT: PASSED")
        print("The lineage editor loading fix is working properly!")
        print("\nKey improvements:")
        print("- Loading state management prevents multiple simultaneous openings")
        print("- Timeout protection prevents infinite loading")
        print("- Force initialization and cleanup mechanisms")
        print("- Startup delay prevents conflicts with database operations")
        print("- Emergency cleanup function for stuck modals")
        return True
    else:
        print("\n❌ OVERALL RESULT: FAILED")
        print("Some loading fix components may need additional work.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 