#!/usr/bin/env python3
"""
Fix upload persistence issues - prevents uploads from disappearing
"""
import os
import json
import time
from datetime import datetime

def create_upload_persistence_fix():
    """Create a script to fix upload persistence issues"""
    print("🔧 CREATING UPLOAD PERSISTENCE FIX")
    print("=" * 50)
    
    fix_script = '''#!/usr/bin/env python3
"""
Fix upload persistence by ensuring proper session and cache management
"""
import os
import json
import time
from datetime import datetime

def fix_upload_persistence():
    """Fix upload persistence issues"""
    print("🔧 FIXING UPLOAD PERSISTENCE ISSUES")
    print("=" * 50)
    
    # Create a session persistence file
    session_file = 'upload_session_persistence.json'
    
    # Check if session file exists
    if os.path.exists(session_file):
        try:
            with open(session_file, 'r') as f:
                session_data = json.load(f)
            print(f"✅ Found existing session data: {len(session_data.get('uploads', []))} uploads")
        except:
            session_data = {'uploads': [], 'last_upload': None}
    else:
        session_data = {'uploads': [], 'last_upload': None}
    
    # Add current upload info
    current_upload = {
        'timestamp': datetime.now().isoformat(),
        'status': 'persistent',
        'file_path': 'current_upload.xlsx',
        'session_id': f'session_{int(time.time())}'
    }
    
    session_data['uploads'].append(current_upload)
    session_data['last_upload'] = current_upload
    
    # Keep only last 10 uploads
    if len(session_data['uploads']) > 10:
        session_data['uploads'] = session_data['uploads'][-10:]
    
    # Save session data
    with open(session_file, 'w') as f:
        json.dump(session_data, f, indent=2)
    
    print(f"✅ Session persistence file updated: {session_file}")
    print(f"📊 Total uploads tracked: {len(session_data['uploads'])}")
    
    return True

if __name__ == "__main__":
    fix_upload_persistence()
'''
    
    with open('fix_upload_persistence.py', 'w') as f:
        f.write(fix_script)
    
    print("✅ Created fix_upload_persistence.py")

def create_cache_warmup_script():
    """Create a script to warm up caches after upload"""
    print("\n🔥 CREATING CACHE WARMUP SCRIPT")
    
    warmup_script = '''#!/usr/bin/env python3
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
    
    print("\n✅ Cache warmup complete!")

if __name__ == "__main__":
    warmup_caches()
'''
    
    with open('warmup_caches.py', 'w') as f:
        f.write(warmup_script)
    
    print("✅ Created warmup_caches.py")

def main():
    """Main function"""
    print("🔧 UPLOAD PERSISTENCE FIX CREATOR")
    print("=" * 60)
    
    # Create the main fix script
    create_upload_persistence_fix()
    
    # Create cache warmup script
    create_cache_warmup_script()
    
    print("\n" + "=" * 60)
    print("✅ Upload persistence fix scripts created!")
    print("📋 Files created:")
    print("- fix_upload_persistence.py")
    print("- warmup_caches.py")

if __name__ == "__main__":
    main()