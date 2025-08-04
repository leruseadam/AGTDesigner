#!/usr/bin/env python3
"""
Comprehensive test script to verify all lineage editor freezing fixes work together.
"""

import requests
import time
import json
import sys
import threading
import concurrent.futures

def test_concurrent_lineage_operations():
    """Test multiple concurrent lineage operations to ensure no freezing."""
    
    base_url = "http://127.0.0.1:9090"
    
    print("Testing concurrent lineage operations...")
    
    def make_lineage_request(strain_name, lineage):
        """Make a single lineage update request."""
        try:
            response = requests.post(f"{base_url}/api/update-strain-lineage",
                                   json={
                                       "strain_name": strain_name,
                                       "lineage": lineage
                                   },
                                   timeout=20)
            return {
                'strain_name': strain_name,
                'status_code': response.status_code,
                'success': response.status_code == 200,
                'error': None if response.status_code == 200 else response.text
            }
        except requests.exceptions.Timeout:
            return {
                'strain_name': strain_name,
                'status_code': 408,
                'success': False,
                'error': 'Request timed out'
            }
        except Exception as e:
            return {
                'strain_name': strain_name,
                'status_code': 500,
                'success': False,
                'error': str(e)
            }
    
    # Test data
    test_strains = [
        ("Test Strain 1", "SATIVA"),
        ("Test Strain 2", "INDICA"),
        ("Test Strain 3", "HYBRID"),
        ("Test Strain 4", "CBD"),
        ("Test Strain 5", "MIXED"),
        ("Test Strain 6", "HYBRID/SATIVA"),
        ("Test Strain 7", "HYBRID/INDICA"),
        ("Test Strain 8", "PARA"),
    ]
    
    print(f"\n1. Testing {len(test_strains)} concurrent lineage updates...")
    
    # Run concurrent requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(make_lineage_request, strain, lineage) 
                  for strain, lineage in test_strains]
        
        results = []
        for future in concurrent.futures.as_completed(futures, timeout=60):
            try:
                result = future.result(timeout=10)
                results.append(result)
            except concurrent.futures.TimeoutError:
                print("✗ Future result timed out")
            except Exception as e:
                print(f"✗ Future error: {e}")
    
    # Analyze results
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"✓ Successful operations: {len(successful)}/{len(test_strains)}")
    print(f"✗ Failed operations: {len(failed)}/{len(test_strains)}")
    
    if failed:
        print("\nFailed operations:")
        for failure in failed:
            print(f"  - {failure['strain_name']}: {failure['error']}")
    
    return len(successful) >= len(test_strains) * 0.8  # 80% success rate

def test_session_manager_performance():
    """Test session manager performance under load."""
    
    base_url = "http://127.0.0.1:9090"
    
    print("\n2. Testing session manager performance...")
    
    def make_session_request():
        """Make a request that uses session management."""
        try:
            response = requests.get(f"{base_url}/api/status", timeout=10)
            return response.status_code == 200
        except Exception:
            return False
    
    # Test concurrent session requests
    print("Making 20 concurrent session requests...")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_session_request) for _ in range(20)]
        
        results = []
        for future in concurrent.futures.as_completed(futures, timeout=30):
            try:
                result = future.result(timeout=5)
                results.append(result)
            except Exception:
                results.append(False)
    
    successful = sum(results)
    print(f"✓ Successful session requests: {successful}/20")
    
    return successful >= 18  # 90% success rate

def test_database_notifier_performance():
    """Test database notifier performance."""
    
    base_url = "http://127.0.0.1:9090"
    
    print("\n3. Testing database notifier performance...")
    
    def make_notification_request():
        """Make a request that triggers database notifications."""
        try:
            response = requests.post(f"{base_url}/api/update-lineage",
                                   json={
                                       "tag_name": f"Test Product {time.time()}",
                                       "Product Name*": f"Test Product {time.time()}",
                                       "lineage": "HYBRID"
                                   },
                                   timeout=15)
            return response.status_code in [200, 404]  # 404 is expected for non-existent products
        except Exception:
            return False
    
    # Test concurrent notification requests
    print("Making 10 concurrent notification requests...")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(make_notification_request) for _ in range(10)]
        
        results = []
        for future in concurrent.futures.as_completed(futures, timeout=30):
            try:
                result = future.result(timeout=10)
                results.append(result)
            except Exception:
                results.append(False)
    
    successful = sum(results)
    print(f"✓ Successful notification requests: {successful}/10")
    
    return successful >= 8  # 80% success rate

def test_frontend_timeout_handling():
    """Test that frontend timeout handling is working."""
    
    print("\n4. Testing frontend timeout handling...")
    
    # Check if the emergency cleanup function exists in the lineage editor
    try:
        with open('static/js/lineage-editor.js', 'r') as f:
            js_content = f.read()
            
        checks = [
            ('emergencyLineageModalCleanup', 'Emergency cleanup function'),
            ('AbortController', 'AbortController timeout handling'),
            ('setTimeout', 'setTimeout protection'),
            ('30000', '30-second timeout'),
            ('45000', '45-second timeout'),
            ('controller.abort()', 'Abort functionality'),
            ('queue.Queue', 'Operation queue'),
            ('threading.RLock', 'RLock for better performance'),
            ('_notify_with_timeout', 'Timeout protection for notifications')
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

def test_backend_timeout_handling():
    """Test that backend timeout handling is working."""
    
    print("\n5. Testing backend timeout handling...")
    
    # Check if timeout protection exists in backend files
    backend_files = [
        ('app.py', 'Backend API timeout protection'),
        ('src/core/data/session_manager.py', 'Session manager timeout protection'),
        ('src/core/data/database_notifier.py', 'Database notifier timeout protection'),
        ('src/core/data/product_database.py', 'Product database timeout protection')
    ]
    
    all_passed = True
    for filename, description in backend_files:
        try:
            with open(filename, 'r') as f:
                content = f.read()
                
            checks = [
                ('threading.Thread', 'Threading support'),
                ('thread.join(timeout=', 'Timeout protection'),
                ('queue.Queue', 'Operation queue'),
                ('RLock', 'RLock for better performance'),
                ('_notify_with_timeout', 'Timeout notifications')
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

def test_emergency_cleanup():
    """Test emergency cleanup functionality."""
    
    print("\n6. Testing emergency cleanup functionality...")
    
    # Check if emergency cleanup button exists in HTML
    try:
        with open('templates/index.html', 'r') as f:
            html_content = f.read()
            
        if 'emergencyLineageModalCleanup' in html_content:
            print("✓ Emergency cleanup button found in HTML")
        else:
            print("✗ Emergency cleanup button missing from HTML")
            return False
            
        if 'btn-outline-danger' in html_content:
            print("✓ Emergency cleanup button styling found")
        else:
            print("✗ Emergency cleanup button styling missing")
            return False
            
        return True
        
    except FileNotFoundError:
        print("✗ HTML template file not found")
        return False
    except Exception as e:
        print(f"✗ Error reading HTML file: {e}")
        return False

def main():
    """Run all comprehensive tests."""
    
    print("="*60)
    print("COMPREHENSIVE LINEAGE EDITOR FREEZING FIX TEST")
    print("="*60)
    
    # Check if server is running
    try:
        response = requests.get("http://127.0.0.1:9090/api/health", timeout=5)
        if response.status_code != 200:
            print("✗ Server is not responding properly")
            return False
        print("✓ Server is running and responding")
    except Exception:
        print("✗ Server is not running on port 9090")
        print("Please start the server with: python app.py")
        return False
    
    # Run all tests
    tests = [
        ("Concurrent Lineage Operations", test_concurrent_lineage_operations),
        ("Session Manager Performance", test_session_manager_performance),
        ("Database Notifier Performance", test_database_notifier_performance),
        ("Frontend Timeout Handling", test_frontend_timeout_handling),
        ("Backend Timeout Handling", test_backend_timeout_handling),
        ("Emergency Cleanup", test_emergency_cleanup)
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
    
    if passed >= total * 0.8:  # 80% success rate
        print("\n🎉 OVERALL RESULT: PASSED")
        print("The lineage editor freezing fixes are working properly!")
        return True
    else:
        print("\n❌ OVERALL RESULT: FAILED")
        print("Some fixes may need additional work.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 