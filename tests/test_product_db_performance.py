#!/usr/bin/env python3
"""
Performance test script for product database integration optimization.
Tests app load time improvements by disabling product database strain matching.
"""

import requests
import time
import json

def test_app_load_performance():
    """Test the performance of app loading with and without product DB integration."""
    base_url = "http://127.0.0.1:5000"
    
    print("🚀 Testing Product Database Performance Optimization...")
    print("=" * 60)
    
    # Test 1: Check current product DB status
    print("\n📊 Current Product Database Status:")
    try:
        response = requests.get(f"{base_url}/api/product-db/status")
        if response.status_code == 200:
            status = response.json()
            print(f"   Enabled: {status.get('enabled', 'Unknown')}")
            print(f"   Stats: {json.dumps(status.get('stats', {}), indent=2)}")
        else:
            print(f"   Error: {response.status_code}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Disable product DB integration
    print("\n🔧 Disabling Product Database Integration...")
    try:
        response = requests.post(f"{base_url}/api/product-db/disable")
        if response.status_code == 200:
            print("   ✅ Product DB integration disabled successfully")
        else:
            print(f"   ❌ Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Measure page load time with disabled integration
    print("\n📄 Testing Page Load Time (Product DB Disabled):")
    start_time = time.time()
    try:
        response = requests.get(f"{base_url}/")
        load_time_disabled = time.time() - start_time
        print(f"   Status: {response.status_code}")
        print(f"   Time: {load_time_disabled:.2f} seconds")
    except Exception as e:
        print(f"   Error: {e}")
        load_time_disabled = None
    
    # Test 4: Re-enable product DB integration
    print("\n🔧 Re-enabling Product Database Integration...")
    try:
        response = requests.post(f"{base_url}/api/product-db/enable")
        if response.status_code == 200:
            print("   ✅ Product DB integration enabled successfully")
        else:
            print(f"   ❌ Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 5: Measure page load time with enabled integration
    print("\n📄 Testing Page Load Time (Product DB Enabled):")
    start_time = time.time()
    try:
        response = requests.get(f"{base_url}/")
        load_time_enabled = time.time() - start_time
        print(f"   Status: {response.status_code}")
        print(f"   Time: {load_time_enabled:.2f} seconds")
    except Exception as e:
        print(f"   Error: {e}")
        load_time_enabled = None
    
    # Test 6: Performance comparison
    print("\n📈 Performance Comparison:")
    if load_time_disabled is not None and load_time_enabled is not None:
        improvement = ((load_time_enabled - load_time_disabled) / load_time_enabled) * 100
        time_saved = load_time_enabled - load_time_disabled
        print(f"   Enabled: {load_time_enabled:.2f} seconds")
        print(f"   Disabled: {load_time_disabled:.2f} seconds")
        print(f"   Time Saved: {time_saved:.2f} seconds")
        print(f"   Improvement: {improvement:.1f}%")
        
        if improvement > 0:
            print("   ✅ Performance improvement achieved!")
        else:
            print("   ⚠️  No significant improvement detected")
    else:
        print("   ⚠️  Could not complete performance comparison")
    
    # Test 7: Final status check
    print("\n📊 Final Product Database Status:")
    try:
        response = requests.get(f"{base_url}/api/product-db/status")
        if response.status_code == 200:
            status = response.json()
            print(f"   Enabled: {status.get('enabled', 'Unknown')}")
        else:
            print(f"   Error: {response.status_code}")
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    test_app_load_performance() 