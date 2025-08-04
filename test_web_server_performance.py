#!/usr/bin/env python3
"""
Test script for web server performance optimizations.
"""

import requests
import time
import json
import os

def test_web_server_endpoints(base_url="http://127.0.0.1:5001"):
    """Test web server optimized endpoints."""
    
    print("=== Web Server Performance Test ===")
    
    # Test 1: Health check
    print("\n1. Testing health check...")
    start_time = time.time()
    try:
        response = requests.get(f"{base_url}/api/health", timeout=30)
        health_time = time.time() - start_time
        print(f"   Health check: {response.status_code} in {health_time:.3f}s")
    except Exception as e:
        print(f"   Health check failed: {e}")
    
    # Test 2: Available tags (should be fast now)
    print("\n2. Testing available tags...")
    start_time = time.time()
    try:
        response = requests.get(f"{base_url}/api/available-tags", timeout=30)
        tags_time = time.time() - start_time
        print(f"   Available tags: {response.status_code} in {tags_time:.3f}s")
    except Exception as e:
        print(f"   Available tags failed: {e}")
    
    # Test 3: Initial data (should be fast with optimizations)
    print("\n3. Testing initial data...")
    start_time = time.time()
    try:
        response = requests.get(f"{base_url}/api/initial-data", timeout=60)
        initial_time = time.time() - start_time
        print(f"   Initial data: {response.status_code} in {initial_time:.3f}s")
    except Exception as e:
        print(f"   Initial data failed: {e}")
    
    # Test 4: Performance stats
    print("\n4. Testing performance stats...")
    start_time = time.time()
    try:
        response = requests.get(f"{base_url}/api/performance", timeout=30)
        perf_time = time.time() - start_time
        print(f"   Performance stats: {response.status_code} in {perf_time:.3f}s")
        if response.status_code == 200:
            data = response.json()
            print(f"   Memory usage: {data.get('memory_usage', 'N/A')}")
            print(f"   Cache status: {data.get('cache_status', 'N/A')}")
    except Exception as e:
        print(f"   Performance stats failed: {e}")
    
    # Test 5: Upload status (should be fast)
    print("\n5. Testing upload status...")
    start_time = time.time()
    try:
        response = requests.get(f"{base_url}/api/upload-status", timeout=30)
        status_time = time.time() - start_time
        print(f"   Upload status: {response.status_code} in {status_time:.3f}s")
    except Exception as e:
        print(f"   Upload status failed: {e}")

def test_default_file_loading():
    """Test default file loading functionality."""
    print("\n=== Default File Loading Test ===")
    
    # Test the get_default_upload_file function
    try:
        from src.core.data.excel_processor import get_default_upload_file
        
        print("Testing get_default_upload_file()...")
        start_time = time.time()
        default_file = get_default_upload_file()
        load_time = time.time() - start_time
        
        if default_file:
            print(f"   Default file found: {default_file}")
            print(f"   Load time: {load_time:.3f}s")
        else:
            print("   No default file found (expected for web server)")
            print(f"   Check time: {load_time:.3f}s")
            
    except Exception as e:
        print(f"   Default file loading test failed: {e}")

def test_web_server_config():
    """Test web server configuration."""
    print("\n=== Web Server Configuration Test ===")
    
    try:
        from config_web_server import get_web_server_config, is_web_server
        
        config = get_web_server_config()
        print("Web server configuration:")
        print(f"   Web server mode: {config.get('web_server_mode', 'N/A')}")
        print(f"   Development mode: {config.get('development_mode', 'N/A')}")
        print(f"   Upload folder: {config.get('upload_folder', 'N/A')}")
        print(f"   Max content length: {config.get('max_content_length', 'N/A')} bytes")
        print(f"   Cache size limit: {config.get('cache_size_limit', 'N/A')}")
        print(f"   Product DB integration: {config.get('enable_product_db_integration', 'N/A')}")
        
        is_ws = is_web_server()
        print(f"   Running on web server: {is_ws}")
        
    except Exception as e:
        print(f"   Web server config test failed: {e}")

def test_environment_variables():
    """Test environment variables for web server mode."""
    print("\n=== Environment Variables Test ===")
    
    env_vars = [
        'WEB_SERVER_MODE',
        'DEVELOPMENT_MODE', 
        'DISABLE_DEFAULT_FILE_LOADING'
    ]
    
    for var in env_vars:
        value = os.environ.get(var, 'Not set')
        print(f"   {var}: {value}")

def main():
    """Main test function."""
    print("Web Server Performance Test Suite")
    print("=" * 50)
    
    # Test environment variables
    test_environment_variables()
    
    # Test web server configuration
    test_web_server_config()
    
    # Test default file loading
    test_default_file_loading()
    
    # Test endpoints (if server is running)
    print("\n" + "=" * 50)
    print("Testing endpoints (requires server to be running)...")
    test_web_server_endpoints()
    
    print("\n" + "=" * 50)
    print("Test completed!")
    print("\nNext steps for web server deployment:")
    print("1. Upload files to PythonAnywhere")
    print("2. Follow WEB_SERVER_DEPLOYMENT_GUIDE.md")
    print("3. Use /upload-web-optimized endpoint for faster uploads")
    print("4. Monitor performance via /api/performance")

if __name__ == "__main__":
    main() 