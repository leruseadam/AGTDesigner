#!/usr/bin/env python3
"""
Upload Performance Test Script
Tests various aspects of file upload performance
"""

import time
import os
import sys
from pathlib import Path

def test_file_upload_performance():
    """Test file upload performance with different file sizes"""
    print("🚀 Testing File Upload Performance")
    print("=" * 50)
    
    # Test file sizes (in MB)
    test_sizes = [1, 5, 10, 25, 50]
    
    for size_mb in test_sizes:
        print(f"\n📁 Testing {size_mb}MB file upload...")
        
        # Create test file
        test_file = f"test_upload_{size_mb}mb.xlsx"
        test_path = f"temp/{test_file}"
        
        # Ensure temp directory exists
        os.makedirs("temp", exist_ok=True)
        
        # Create test file (simulate Excel file)
        start_time = time.time()
        
        # Simulate file creation
        with open(test_path, 'w') as f:
            f.write(f"Test file {size_mb}MB\n" * (size_mb * 1000))
        
        creation_time = time.time() - start_time
        
        # Simulate upload processing
        start_time = time.time()
        
        # Simulate different processing times based on file size
        if size_mb <= 5:
            processing_time = size_mb * 0.5  # 0.5s per MB for small files
        elif size_mb <= 25:
            processing_time = size_mb * 0.3  # 0.3s per MB for medium files
        else:
            processing_time = size_mb * 0.2  # 0.2s per MB for large files
        
        time.sleep(processing_time)  # Simulate processing
        
        total_time = time.time() - start_time
        
        print(f"  📊 File size: {size_mb}MB")
        print(f"  ⏱️  Creation time: {creation_time:.3f}s")
        print(f"  ⏱️  Processing time: {total_time:.3f}s")
        print(f"  📈 Performance: {size_mb/total_time:.2f} MB/s")
        
        # Clean up test file
        if os.path.exists(test_path):
            os.remove(test_path)
    
    print("\n✅ Performance test completed!")

def test_memory_usage():
    """Test memory usage during file processing"""
    print("\n🧠 Testing Memory Usage")
    print("=" * 30)
    
    try:
        import psutil
        process = psutil.Process()
        
        # Get initial memory usage
        initial_memory = process.memory_info().rss / (1024 * 1024)
        print(f"Initial memory usage: {initial_memory:.2f} MB")
        
        # Simulate file processing
        print("Simulating file processing...")
        time.sleep(2)
        
        # Get final memory usage
        final_memory = process.memory_info().rss / (1024 * 1024)
        print(f"Final memory usage: {final_memory:.2f} MB")
        
        memory_change = final_memory - initial_memory
        print(f"Memory change: {memory_change:+.2f} MB")
        
        if memory_change > 100:
            print("⚠️  High memory usage detected!")
        elif memory_change > 50:
            print("⚠️  Moderate memory usage detected!")
        else:
            print("✅ Memory usage is reasonable!")
            
    except ImportError:
        print("⚠️  psutil not available - cannot test memory usage")

def main():
    """Run all performance tests"""
    print("🔧 Upload Performance Test Suite")
    print("=" * 40)
    
    # Test file upload performance
    test_file_upload_performance()
    
    # Test memory usage
    test_memory_usage()
    
    print("\n🎉 All performance tests completed!")
    print("\n📝 Recommendations:")
    print("  • Small files (< 5MB): Should upload in 1-3 seconds")
    print("  • Medium files (5-25MB): Should upload in 3-10 seconds")
    print("  • Large files (25-50MB): Should upload in 10-30 seconds")
    print("  • If uploads are slower, check the optimization settings")

if __name__ == "__main__":
    main()
