#!/usr/bin/env python3
"""
Warm up caches after upload to prevent disappearing data
"""
import requests
import time

def warmup_caches():
    """Warm up application caches"""
    print("🔥 WARMING UP CACHES")
    print("=" * 30)
    
    base_url = "https://www.agtpricetags.com"
    
    endpoints_to_warm = [
        "/api/initial-data",
        "/api/available-tags",
        "/api/filter-options"
    ]
    
    for endpoint in endpoints_to_warm:
        try:
            url = f"{base_url}{endpoint}"
            print(f"📡 Warming: {endpoint}")
            
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ {endpoint}: OK")
            else:
                print(f"⚠️ {endpoint}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ {endpoint}: {e}")
        
        time.sleep(0.5)
    
    print("
✅ Cache warmup complete!")

if __name__ == "__main__":
    warmup_caches()
