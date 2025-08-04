#!/usr/bin/env python3
"""
Test script to check cache building process for JSON matcher
"""

import sys
import os
import time
import logging

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.data.json_matcher import JSONMatcher
from src.core.data.excel_processor import ExcelProcessor

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_cache_building():
    """Test the cache building process"""
    print("🔧 Testing JSON Matcher Cache Building")
    print("=" * 50)
    
    try:
        # Step 1: Initialize Excel processor
        print("\n1. Initializing Excel processor...")
        start_time = time.time()
        excel_processor = ExcelProcessor()
        init_time = time.time() - start_time
        print(f"✅ Excel processor initialized in {init_time:.2f} seconds")
        
        # Check if data is loaded
        if excel_processor.df is None:
            print("❌ No data loaded in Excel processor")
            return False
        
        print(f"   Data shape: {excel_processor.df.shape}")
        print(f"   Columns: {len(excel_processor.df.columns)}")
        
        # Step 2: Initialize JSON matcher
        print("\n2. Initializing JSON matcher...")
        start_time = time.time()
        matcher = JSONMatcher(excel_processor)
        init_time = time.time() - start_time
        print(f"✅ JSON matcher initialized in {init_time:.2f} seconds")
        
        # Step 3: Check initial cache status
        print("\n3. Checking initial cache status...")
        cache_status = matcher.get_sheet_cache_status()
        print(f"   Initial cache status: {cache_status}")
        
        # Step 4: Build cache manually
        print("\n4. Building cache manually...")
        start_time = time.time()
        matcher._build_sheet_cache()
        build_time = time.time() - start_time
        print(f"✅ Cache built in {build_time:.2f} seconds")
        
        # Step 5: Check cache after building
        print("\n5. Checking cache after building...")
        cache_status = matcher.get_sheet_cache_status()
        print(f"   Cache status: {cache_status}")
        
        if matcher._sheet_cache is not None:
            print(f"   Sheet cache entries: {len(matcher._sheet_cache)}")
        else:
            print("   ❌ Sheet cache is None")
            return False
            
        if matcher._indexed_cache is not None:
            indexed = matcher._indexed_cache
            print(f"   Indexed cache:")
            print(f"     Exact names: {len(indexed.get('exact_names', {}))}")
            print(f"     Vendors: {len(indexed.get('vendor_groups', {}))}")
            print(f"     Key terms: {len(indexed.get('key_terms', {}))}")
            print(f"     Normalized names: {len(indexed.get('normalized_names', {}))}")
        else:
            print("   ❌ Indexed cache is None")
            return False
        
        # Step 6: Test cache rebuilding
        print("\n6. Testing cache rebuilding...")
        start_time = time.time()
        matcher.rebuild_sheet_cache()
        rebuild_time = time.time() - start_time
        print(f"✅ Cache rebuilt in {rebuild_time:.2f} seconds")
        
        # Step 7: Test a simple matching operation
        print("\n7. Testing simple matching operation...")
        test_item = {
            'product_name': 'Test Product',
            'vendor': 'Test Vendor',
            'brand': 'Test Brand'
        }
        
        start_time = time.time()
        candidates = matcher._find_candidates_optimized(test_item)
        match_time = time.time() - start_time
        print(f"✅ Matching test completed in {match_time:.2f} seconds")
        print(f"   Found {len(candidates)} candidates")
        
        # Step 8: Test strain cache building
        print("\n8. Testing strain cache building...")
        start_time = time.time()
        matcher._build_strain_cache()
        strain_time = time.time() - start_time
        print(f"✅ Strain cache built in {strain_time:.2f} seconds")
        
        strain_status = matcher.get_strain_cache_status()
        print(f"   Strain cache status: {strain_status}")
        
        print("\n" + "=" * 50)
        print("✅ All cache building tests passed!")
        print("💡 The JSON matcher should work correctly")
        return True
        
    except Exception as e:
        print(f"\n❌ Error during cache building test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_memory_usage():
    """Test memory usage during cache building"""
    print("\n🧠 Testing memory usage...")
    
    try:
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        print(f"   Initial memory usage: {initial_memory:.1f} MB")
        
        # Build cache
        excel_processor = ExcelProcessor()
        matcher = JSONMatcher(excel_processor)
        matcher._build_sheet_cache()
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        print(f"   Final memory usage: {final_memory:.1f} MB")
        print(f"   Memory increase: {memory_increase:.1f} MB")
        
        if memory_increase > 500:  # More than 500MB increase
            print("   ⚠️  Large memory increase detected")
        else:
            print("   ✅ Memory usage is reasonable")
            
    except ImportError:
        print("   ℹ️  psutil not available - skipping memory test")
    except Exception as e:
        print(f"   ❌ Error testing memory usage: {e}")

def main():
    """Main function"""
    print("🔧 JSON Matcher Cache Building Diagnostic")
    print("=" * 60)
    
    # Run cache building test
    success = test_cache_building()
    
    # Run memory test
    test_memory_usage()
    
    print("\n" + "=" * 60)
    print("📋 Summary:")
    if success:
        print("✅ Cache building is working correctly")
        print("💡 If JSON matcher still stops, the issue might be:")
        print("   - Large JSON datasets causing timeouts")
        print("   - Network connectivity issues")
        print("   - Specific JSON format problems")
        print("   - Browser JavaScript errors")
    else:
        print("❌ Cache building has issues")
        print("💡 Check the error messages above for details")

if __name__ == "__main__":
    main() 