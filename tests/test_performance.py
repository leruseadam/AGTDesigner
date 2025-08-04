#!/usr/bin/env python3
"""
Performance test script for the Label Maker application.
Tests page refresh time improvements.
"""

import requests
import time
import json

def test_page_refresh_performance():
    """Test the performance of the main page route."""
    base_url = "http://127.0.0.1:5000"
    
    print("🚀 Testing page refresh performance...")
    print("=" * 50)
    
    # Test first load (should be slower)
    print("\n📄 First page load (cold start):")
    start_time = time.time()
    try:
        response = requests.get(f"{base_url}/")
        first_load_time = time.time() - start_time
        print(f"   Status: {response.status_code}")
        print(f"   Time: {first_load_time:.2f} seconds")
    except Exception as e:
        print(f"   Error: {e}")
        return
    
    # Test second load (should be faster due to cache)
    print("\n📄 Second page load (cached):")
    start_time = time.time()
    try:
        response = requests.get(f"{base_url}/")
        second_load_time = time.time() - start_time
        print(f"   Status: {response.status_code}")
        print(f"   Time: {second_load_time:.2f} seconds")
    except Exception as e:
        print(f"   Error: {e}")
        return
    
    # Test cache status
    print("\n📊 Cache status:")
    try:
        response = requests.get(f"{base_url}/api/cache-status")
        if response.status_code == 200:
            cache_info = response.json()
            print(f"   Cached: {cache_info.get('cached', False)}")
            if cache_info.get('cached'):
                print(f"   Age: {cache_info.get('age_seconds', 0):.1f} seconds")
                print(f"   Expires in: {cache_info.get('expires_in_seconds', 0):.1f} seconds")
    except Exception as e:
        print(f"   Error getting cache status: {e}")
    
    # Test performance stats
    print("\n📈 Performance stats:")
    try:
        response = requests.get(f"{base_url}/api/performance")
        if response.status_code == 200:
            stats = response.json()
            print(f"   CPU: {stats.get('system', {}).get('cpu_percent', 0):.1f}%")
            print(f"   Memory: {stats.get('system', {}).get('memory_percent', 0):.1f}%")
            print(f"   Excel cache size: {stats.get('excel_processor', {}).get('cache_size', 0)}")
    except Exception as e:
        print(f"   Error getting performance stats: {e}")
    
    # Calculate improvement
    if first_load_time > 0 and second_load_time > 0:
        improvement = ((first_load_time - second_load_time) / first_load_time) * 100
        print(f"\n🎯 Performance improvement: {improvement:.1f}%")
        print(f"   First load: {first_load_time:.2f}s")
        print(f"   Cached load: {second_load_time:.2f}s")
        print(f"   Time saved: {first_load_time - second_load_time:.2f}s")
    
    print("\n" + "=" * 50)
    print("✅ Performance test complete!")

if __name__ == "__main__":
    test_page_refresh_performance() 