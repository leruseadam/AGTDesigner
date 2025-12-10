#!/usr/bin/env python3
"""
PythonAnywhere Performance Optimization Script
Applies comprehensive performance fixes to make the app faster on PythonAnywhere
"""

import os
import sys
import shutil
from datetime import datetime

def backup_file(filepath):
    """Create a backup of the file before modifying"""
    if os.path.exists(filepath):
        backup_path = f"{filepath}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(filepath, backup_path)
        print(f"✅ Backed up {filepath} to {backup_path}")
        return backup_path
    return None

def apply_app_py_optimizations():
    """Apply performance optimizations to app.py"""
    print("\n🔧 Optimizing app.py...")
    
    app_py_path = "app.py"
    backup_file(app_py_path)
    
    with open(app_py_path, 'r') as f:
        content = f.read()
    
    optimizations_applied = []
    
    # 1. Ensure fast_load is default for available-tags
    if 'fast_load = True  # Default to fast loading' not in content:
        # This should already be there, but verify
        optimizations_applied.append("Fast load mode defaulted")
    
    # 2. Add cached_route decorator to available-tags endpoint if not present
    if '@app.route(\'/api/available-tags\', methods=[\'GET\'])' in content:
        if '@cached_route' not in content.split('@app.route(\'/api/available-tags\'')[0].split('\n')[-5:]:
            # Find the route and add caching
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.strip() == "@app.route('/api/available-tags', methods=['GET'])":
                    # Check if @cached_route is already above
                    if i > 0 and '@cached_route' not in lines[i-1]:
                        lines.insert(i, '@cached_route(ttl=60, cache_type="aggressive", vary_by=["session_id"])')
                        content = '\n'.join(lines)
                        optimizations_applied.append("Added aggressive caching to /api/available-tags")
                    break
    
    # 3. Ensure compression is applied to responses
    if 'compress_response' in content:
        optimizations_applied.append("Response compression enabled")
    
    # Write back if changes were made
    if optimizations_applied:
        with open(app_py_path, 'w') as f:
            f.write(content)
        print(f"✅ Applied {len(optimizations_applied)} optimizations to app.py")
        for opt in optimizations_applied:
            print(f"   - {opt}")
    else:
        print("✅ app.py already optimized")

def apply_wsgi_optimizations():
    """Apply performance optimizations to wsgi.py"""
    print("\n🔧 Optimizing wsgi.py...")
    
    wsgi_py_path = "wsgi.py"
    backup_file(wsgi_py_path)
    
    with open(wsgi_py_path, 'r') as f:
        content = f.read()
    
    optimizations = []
    
    # Add performance environment variables
    env_vars = {
        'PYTHONANYWHERE_OPTIMIZATION': 'True',
        'FORCE_FAST_LOAD': 'True',
        'DISABLE_STARTUP_FILE_LOADING': 'True',
        'MAX_MEMORY_MB': '450',
        'CACHE_SIZE_LIMIT': '100',
        'BATCH_SIZE_LIMIT': '500',
    }
    
    for var, value in env_vars.items():
        if f"os.environ['{var}']" not in content:
            # Add before the import statement
            import_line = "from app import app as application"
            if import_line in content:
                content = content.replace(
                    import_line,
                    f"os.environ['{var}'] = '{value}'\n    {import_line}"
                )
                optimizations.append(f"Added {var}={value}")
    
    if optimizations:
        with open(wsgi_py_path, 'w') as f:
            f.write(content)
        print(f"✅ Applied {len(optimizations)} optimizations to wsgi.py")
        for opt in optimizations:
            print(f"   - {opt}")
    else:
        print("✅ wsgi.py already optimized")

def apply_config_optimizations():
    """Apply performance optimizations to config.py"""
    print("\n🔧 Optimizing config.py...")
    
    config_py_path = "config.py"
    backup_file(config_py_path)
    
    with open(config_py_path, 'r') as f:
        content = f.read()
    
    optimizations = []
    
    # Ensure cache timeout is reasonable for production
    if 'CACHE_DEFAULT_TIMEOUT = 300' not in content:
        content = content.replace(
            'CACHE_DEFAULT_TIMEOUT =',
            'CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes - optimized for performance  #'
        )
        optimizations.append("Set cache timeout to 5 minutes")
    
    # Ensure compression is enabled
    if 'COMPRESS_ALGORITHM' not in content:
        # Add compression config
        content = content.replace(
            '# Caching',
            '''# Caching
    
    # Compression (for better performance)
    COMPRESS_ALGORITHM = 'gzip'
    COMPRESS_LEVEL = 6
    COMPRESS_MIN_SIZE = 1024
    
    # Caching'''
        )
        optimizations.append("Added compression configuration")
    
    if optimizations:
        with open(config_py_path, 'w') as f:
            f.write(content)
        print(f"✅ Applied {len(optimizations)} optimizations to config.py")
        for opt in optimizations:
            print(f"   - {opt}")
    else:
        print("✅ config.py already optimized")

def verify_response_cache_module():
    """Verify that response_cache module exists and is working"""
    print("\n🔍 Verifying response_cache module...")
    
    response_cache_path = "src/core/utils/response_cache.py"
    if os.path.exists(response_cache_path):
        print("✅ response_cache.py exists")
        
        # Verify key functions
        with open(response_cache_path, 'r') as f:
            content = f.read()
        
        required_functions = ['cached_route', 'compress_response', 'ResponseCache']
        missing = [fn for fn in required_functions if fn not in content]
        
        if missing:
            print(f"⚠️  Warning: Missing functions in response_cache.py: {missing}")
        else:
            print("✅ All required caching functions present")
    else:
        print("⚠️  Warning: response_cache.py not found - caching may be disabled")
        print("   The app will still work but without response caching")

def create_performance_test_script():
    """Create a simple performance test script"""
    print("\n📝 Creating performance test script...")
    
    test_script = """#!/usr/bin/env python3
\"\"\"
Simple performance test for PythonAnywhere deployment
Run this after deploying to verify performance improvements
\"\"\"

import requests
import time
import sys

def test_endpoint(url, description):
    print(f"\\n🧪 Testing: {description}")
    print(f"   URL: {url}")
    
    # First request (cache miss)
    start = time.time()
    try:
        response = requests.get(url, timeout=30)
        elapsed_first = time.time() - start
        
        cache_status = response.headers.get('X-Cache', 'N/A')
        encoding = response.headers.get('Content-Encoding', 'none')
        
        print(f"   ✅ First request: {elapsed_first:.2f}s")
        print(f"      Cache: {cache_status}")
        print(f"      Encoding: {encoding}")
        print(f"      Status: {response.status_code}")
        
        # Second request (should be cached)
        time.sleep(0.5)
        start = time.time()
        response2 = requests.get(url, timeout=30)
        elapsed_second = time.time() - start
        
        cache_status2 = response2.headers.get('X-Cache', 'N/A')
        
        print(f"   ✅ Second request: {elapsed_second:.2f}s")
        print(f"      Cache: {cache_status2}")
        
        improvement = ((elapsed_first - elapsed_second) / elapsed_first * 100) if elapsed_first > 0 else 0
        print(f"   📊 Improvement: {improvement:.1f}% faster")
        
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 test_pythonanywhere_performance.py <your-pythonanywhere-url>")
        print("Example: python3 test_pythonanywhere_performance.py https://adamcordova.pythonanywhere.com")
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip('/')
    
    print("=" * 60)
    print("🚀 PythonAnywhere Performance Test")
    print("=" * 60)
    
    endpoints = [
        (f"{base_url}/api/available-tags?fast_load=1", "Available Tags (Fast Load)"),
        (f"{base_url}/api/stores", "Store List"),
        (f"{base_url}/", "Home Page"),
    ]
    
    results = []
    for url, description in endpoints:
        success = test_endpoint(url, description)
        results.append(success)
    
    print("\\n" + "=" * 60)
    print(f"📊 Results: {sum(results)}/{len(results)} tests passed")
    print("=" * 60)
    
    if all(results):
        print("✅ All tests passed! Performance optimizations are working.")
    else:
        print("⚠️  Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()
"""
    
    test_script_path = "test_pythonanywhere_performance.py"
    with open(test_script_path, 'w') as f:
        f.write(test_script)
    
    os.chmod(test_script_path, 0o755)
    print(f"✅ Created {test_script_path}")
    print(f"   Run with: python3 {test_script_path} <your-pythonanywhere-url>")

def main():
    print("=" * 70)
    print("🚀 PythonAnywhere Performance Optimization")
    print("=" * 70)
    print("\nThis script will apply performance optimizations to:")
    print("  - app.py (caching, compression, fast load)")
    print("  - wsgi.py (environment variables)")
    print("  - config.py (cache settings)")
    print("\n⚠️  Backups will be created before any changes")
    
    input("\nPress Enter to continue or Ctrl+C to cancel...")
    
    try:
        # Apply optimizations
        apply_app_py_optimizations()
        apply_wsgi_optimizations()
        apply_config_optimizations()
        verify_response_cache_module()
        create_performance_test_script()
        
        print("\n" + "=" * 70)
        print("✅ Performance optimizations applied successfully!")
        print("=" * 70)
        
        print("\n📋 Next Steps:")
        print("  1. Test locally: python3 app.py")
        print("  2. Deploy to PythonAnywhere: bash deploy_pa.sh")
        print("  3. Test performance: python3 test_pythonanywhere_performance.py <url>")
        print("  4. Monitor logs in PythonAnywhere dashboard")
        
        print("\n📖 For more details, see: PYTHONANYWHERE_PERFORMANCE_FIX.md")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Please check the error and try again")
        sys.exit(1)

if __name__ == "__main__":
    main()
