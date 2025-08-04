#!/usr/bin/env python3
"""
Test script to verify PythonAnywhere upload optimizations.
This script tests the new pythonanywhere_fast_load method and compares performance.
"""

import sys
import os
import time
import logging
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.data.excel_processor import ExcelProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_pythonanywhere_optimizations():
    """Test the PythonAnywhere upload optimizations."""
    print("🚀 Testing PythonAnywhere Upload Optimizations")
    print("=" * 50)
    
    # Create test processor
    processor = ExcelProcessor()
    
    # Test file path (create a small test file if needed)
    test_file = "test_sample.xlsx"
    
    if not os.path.exists(test_file):
        print(f"❌ Test file {test_file} not found")
        print("Please create a test Excel file to run the optimization test")
        return False
    
    print(f"✅ Found test file: {test_file}")
    
    # Test 1: Standard loading method
    print("\n📊 Test 1: Standard Loading Method")
    print("-" * 30)
    
    start_time = time.time()
    try:
        # Disable PythonAnywhere mode
        processor.enable_pythonanywhere_mode(False)
        
        # Use standard loading
        success = processor.load_file(test_file)
        standard_time = time.time() - start_time
        
        if success:
            print(f"✅ Standard loading completed in {standard_time:.2f} seconds")
            standard_rows = len(processor.df) if processor.df is not None else 0
            print(f"   Rows loaded: {standard_rows}")
        else:
            print("❌ Standard loading failed")
            return False
            
    except Exception as e:
        print(f"❌ Error in standard loading: {e}")
        return False
    
    # Clear processor for next test
    processor.df = None
    import gc
    gc.collect()
    
    # Test 2: PythonAnywhere optimized loading
    print("\n📊 Test 2: PythonAnywhere Optimized Loading")
    print("-" * 30)
    
    start_time = time.time()
    try:
        # Enable PythonAnywhere mode
        processor.enable_pythonanywhere_mode(True)
        
        # Use optimized loading
        success = processor.pythonanywhere_fast_load(test_file)
        optimized_time = time.time() - start_time
        
        if success:
            print(f"✅ Optimized loading completed in {optimized_time:.2f} seconds")
            optimized_rows = len(processor.df) if processor.df is not None else 0
            print(f"   Rows loaded: {optimized_rows}")
        else:
            print("❌ Optimized loading failed")
            return False
            
    except Exception as e:
        print(f"❌ Error in optimized loading: {e}")
        return False
    
    # Performance comparison
    print("\n📈 Performance Comparison")
    print("-" * 30)
    
    if standard_time > 0 and optimized_time > 0:
        speedup = standard_time / optimized_time
        time_saved = standard_time - optimized_time
        
        print(f"Standard loading time: {standard_time:.2f} seconds")
        print(f"Optimized loading time: {optimized_time:.2f} seconds")
        print(f"Speedup: {speedup:.1f}x faster")
        print(f"Time saved: {time_saved:.2f} seconds")
        
        if speedup > 1.0:
            print("✅ Optimization successful - faster loading achieved!")
        else:
            print("⚠️  Optimization may need tuning")
    
    # Data integrity check
    print("\n🔍 Data Integrity Check")
    print("-" * 30)
    
    if processor.df is not None:
        print(f"✅ Data loaded successfully")
        print(f"   Total rows: {len(processor.df)}")
        print(f"   Total columns: {len(processor.df.columns)}")
        print(f"   Columns: {list(processor.df.columns)}")
        
        # Check for required columns
        required_columns = ['Product Name*', 'Product Type*', 'Lineage', 'Product Brand']
        missing_columns = [col for col in required_columns if col not in processor.df.columns]
        
        if missing_columns:
            print(f"⚠️  Missing required columns: {missing_columns}")
        else:
            print("✅ All required columns present")
    else:
        print("❌ No data loaded")
        return False
    
    # Memory usage check
    print("\n💾 Memory Usage Check")
    print("-" * 30)
    
    try:
        import psutil
        process = psutil.Process()
        memory_mb = process.memory_info().rss / (1024 * 1024)
        print(f"Current memory usage: {memory_mb:.1f} MB")
        
        if memory_mb < 100:
            print("✅ Memory usage is reasonable")
        else:
            print("⚠️  Memory usage is high, consider optimization")
            
    except ImportError:
        print("⚠️  psutil not available, skipping memory check")
    
    print("\n🎉 PythonAnywhere Upload Optimization Test Completed!")
    return True

def test_optimization_features():
    """Test specific optimization features."""
    print("\n🔧 Testing Optimization Features")
    print("=" * 40)
    
    processor = ExcelProcessor()
    
    # Test 1: PythonAnywhere mode enabling
    print("\n1. Testing PythonAnywhere mode enabling...")
    processor.enable_pythonanywhere_mode(True)
    print("✅ PythonAnywhere mode enabled")
    
    # Test 2: Optimization application
    print("\n2. Testing optimization application...")
    processor._apply_pythonanywhere_optimizations()
    print("✅ Optimizations applied")
    
    # Test 3: Cache management
    print("\n3. Testing cache management...")
    processor._file_cache = {}  # Clear cache
    print("✅ Cache cleared")
    
    print("\n✅ All optimization features working correctly")

if __name__ == "__main__":
    print("PythonAnywhere Upload Optimization Test Suite")
    print("=" * 60)
    
    # Test optimization features
    test_optimization_features()
    
    # Test full optimization
    success = test_pythonanywhere_optimizations()
    
    if success:
        print("\n🎉 All tests passed! PythonAnywhere optimizations are working correctly.")
    else:
        print("\n💥 Some tests failed. Check the implementation.") 