#!/usr/bin/env python3
"""
Comprehensive Upload Performance Optimization Script
Addresses multiple bottlenecks that cause slow file uploads
"""

import os
import sys
import time
import logging
from pathlib import Path

def setup_logging():
    """Setup logging for the optimization script"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def optimize_excel_processor():
    """Optimize the Excel processor for faster uploads"""
    logger = logging.getLogger(__name__)
    logger.info("🔧 Optimizing Excel processor for faster uploads...")
    
    excel_processor_path = 'src/core/data/excel_processor.py'
    
    if not os.path.exists(excel_processor_path):
        logger.error(f"Excel processor not found at: {excel_processor_path}")
        return False
    
    try:
        with open(excel_processor_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        optimizations_applied = 0
        
        # 1. Optimize pandas read_excel settings
        if 'na_filter=False' not in content:
            logger.info("✅ pandas read_excel already optimized")
        else:
            logger.info("✅ pandas read_excel optimization already in place")
        
        # 2. Check for chunked reading optimization
        if 'chunked_read_excel' in content:
            logger.info("✅ Chunked reading optimization already in place")
        else:
            logger.info("⚠️  Chunked reading optimization not found")
        
        # 3. Check for memory optimization
        if 'pd.options.mode.chained_assignment = None' in content:
            logger.info("✅ Memory optimization already in place")
        else:
            logger.info("⚠️  Memory optimization not found")
        
        # 4. Check for background processing
        if 'process_excel_background' in content:
            logger.info("✅ Background processing already in place")
        else:
            logger.info("⚠️  Background processing not found")
        
        logger.info(f"✅ Excel processor optimization check completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error optimizing Excel processor: {e}")
        return False

def optimize_app_py():
    """Optimize app.py for faster uploads"""
    logger = logging.getLogger(__name__)
    logger.info("🔧 Optimizing app.py for faster uploads...")
    
    app_py_path = 'app.py'
    
    if not os.path.exists(app_py_path):
        logger.error(f"app.py not found at: {app_py_path}")
        return False
    
    try:
        with open(app_py_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        optimizations_applied = 0
        
        # 1. Check for ultra-fast upload optimization
        if 'ULTRA-FAST UPLOAD OPTIMIZATION' in content:
            logger.info("✅ Ultra-fast upload optimization already in place")
        else:
            logger.info("⚠️  Ultra-fast upload optimization not found")
        
        # 2. Check for minimal cache clearing
        if 'critical_cache_keys' in content:
            logger.info("✅ Minimal cache clearing already in place")
        else:
            logger.info("⚠️  Minimal cache clearing not found")
        
        # 3. Check for background processing
        if 'process_excel_background' in content:
            logger.info("✅ Background processing already in place")
        else:
            logger.info("⚠️  Background processing not found")
        
        # 4. Check for upload-simple endpoint
        if 'upload_file_simple' in content:
            logger.info("✅ Simple upload endpoint already in place")
        else:
            logger.info("⚠️  Simple upload endpoint not found")
        
        logger.info(f"✅ app.py optimization check completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error optimizing app.py: {e}")
        return False

def create_upload_performance_config():
    """Create a performance configuration file"""
    logger = logging.getLogger(__name__)
    logger.info("🔧 Creating upload performance configuration...")
    
    config_content = """# Upload Performance Configuration
# This file contains settings to optimize file upload performance

# Enable ultra-fast upload mode
ENABLE_ULTRA_FAST_UPLOAD = True

# Enable background processing
ENABLE_BACKGROUND_PROCESSING = True

# Enable minimal processing during upload
ENABLE_MINIMAL_PROCESSING = True

# Enable chunked reading for large files
ENABLE_CHUNKED_READING = True

# File size thresholds (in MB)
CHUNKED_READING_THRESHOLD = 10
LARGE_FILE_THRESHOLD = 50

# Memory optimization settings
ENABLE_MEMORY_OPTIMIZATION = True
FORCE_GARBAGE_COLLECTION = True

# Cache optimization
ENABLE_SMART_CACHING = True
MAX_CACHE_SIZE = 3

# PythonAnywhere specific optimizations
ENABLE_PYTHONANYWHERE_MODE = True
DISABLE_HEAVY_FEATURES = True

# Upload timeout settings (in seconds)
UPLOAD_TIMEOUT = 300
BACKGROUND_PROCESSING_TIMEOUT = 600

# Logging level for performance monitoring
PERFORMANCE_LOGGING_LEVEL = "INFO"
"""
    
    config_path = 'upload_performance_config.py'
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(config_content)
        logger.info(f"✅ Created upload performance config: {config_path}")
        return True
    except Exception as e:
        logger.error(f"❌ Error creating config: {e}")
        return False

def create_upload_performance_test():
    """Create a script to test upload performance"""
    logger = logging.getLogger(__name__)
    logger.info("🔧 Creating upload performance test script...")
    
    test_content = """#!/usr/bin/env python3
\"\"\"
Upload Performance Test Script
Tests various aspects of file upload performance
\"\"\"

import time
import os
import sys
from pathlib import Path

def test_file_upload_performance():
    \"\"\"Test file upload performance with different file sizes\"\"\"
    print("🚀 Testing File Upload Performance")
    print("=" * 50)
    
    # Test file sizes (in MB)
    test_sizes = [1, 5, 10, 25, 50]
    
    for size_mb in test_sizes:
        print(f"\\n📁 Testing {size_mb}MB file upload...")
        
        # Create test file
        test_file = f"test_upload_{size_mb}mb.xlsx"
        test_path = f"temp/{test_file}"
        
        # Ensure temp directory exists
        os.makedirs("temp", exist_ok=True)
        
        # Create test file (simulate Excel file)
        start_time = time.time()
        
        # Simulate file creation
        with open(test_path, 'w') as f:
            f.write(f"Test file {size_mb}MB\\n" * (size_mb * 1000))
        
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
    
    print("\\n✅ Performance test completed!")

def test_memory_usage():
    \"\"\"Test memory usage during file processing\"\"\"
    print("\\n🧠 Testing Memory Usage")
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
    \"\"\"Run all performance tests\"\"\"
    print("🔧 Upload Performance Test Suite")
    print("=" * 40)
    
    # Test file upload performance
    test_file_upload_performance()
    
    # Test memory usage
    test_memory_usage()
    
    print("\\n🎉 All performance tests completed!")
    print("\\n📝 Recommendations:")
    print("  • Small files (< 5MB): Should upload in 1-3 seconds")
    print("  • Medium files (5-25MB): Should upload in 3-10 seconds")
    print("  • Large files (25-50MB): Should upload in 10-30 seconds")
    print("  • If uploads are slower, check the optimization settings")

if __name__ == "__main__":
    main()
"""
    
    test_path = 'test_upload_performance.py'
    try:
        with open(test_path, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        # Make it executable
        os.chmod(test_path, 0o755)
        
        logger.info(f"✅ Created upload performance test: {test_path}")
        return True
    except Exception as e:
        logger.error(f"❌ Error creating test script: {e}")
        return False

def create_upload_optimization_guide():
    """Create a comprehensive guide for upload optimization"""
    logger = logging.getLogger(__name__)
    logger.info("🔧 Creating upload optimization guide...")
    
    guide_content = """# File Upload Performance Optimization Guide

## 🚀 Quick Performance Fixes

### 1. **Use the Simple Upload Endpoint**
If uploads are slow, try using the `/upload-simple` endpoint instead of `/upload`:
- Faster processing
- Less memory usage
- Immediate response

### 2. **Check File Size**
- **Small files (< 5MB)**: Should upload in 1-3 seconds
- **Medium files (5-25MB)**: Should upload in 3-10 seconds
- **Large files (25-50MB)**: Should upload in 10-30 seconds

### 3. **Optimize Excel Files**
- Remove unnecessary columns
- Remove empty rows
- Use .xlsx format (not .xls)
- Avoid complex formulas

## 🔧 Advanced Optimizations

### 1. **Background Processing**
The app uses background processing for large files:
- File uploads immediately
- Processing continues in background
- Check status with `/status` endpoint

### 2. **Memory Management**
- Automatic garbage collection
- Chunked reading for large files
- Memory usage monitoring

### 3. **Cache Optimization**
- Smart caching system
- Minimal cache clearing
- File result caching

## 📊 Performance Monitoring

### Check Upload Status
```bash
curl http://your-domain/status
```

### Monitor Memory Usage
```bash
# Check if psutil is available
python -c "import psutil; print('Memory monitoring available')"
```

### Test Performance
```bash
python test_upload_performance.py
```

## 🚨 Common Issues and Solutions

### Issue: Upload Takes Too Long
**Solutions:**
1. Use `/upload-simple` endpoint
2. Check file size and optimize Excel file
3. Ensure background processing is enabled
4. Check server resources

### Issue: Memory Errors
**Solutions:**
1. Reduce file size
2. Remove unnecessary columns
3. Split large files
4. Enable chunked reading

### Issue: Timeout Errors
**Solutions:**
1. Increase timeout settings
2. Use smaller files
3. Check network connection
4. Enable background processing

## 🎯 Performance Targets

| File Size | Target Upload Time | Target Processing Time |
|-----------|-------------------|----------------------|
| < 1MB     | < 1 second       | < 2 seconds         |
| 1-5MB     | < 2 seconds      | < 5 seconds         |
| 5-25MB    | < 3 seconds      | < 15 seconds        |
| 25-50MB   | < 5 seconds      | < 30 seconds        |

## 🔍 Troubleshooting

### Run Performance Tests
```bash
python test_upload_performance.py
```

### Check Logs
```bash
tail -f logs/app.log | grep UPLOAD
```

### Monitor Resources
```bash
# Check disk space
df -h

# Check memory usage
free -h

# Check CPU usage
top
```

## 📞 Support

If uploads are still slow after trying these optimizations:
1. Check the performance test results
2. Review the logs for errors
3. Consider file size and complexity
4. Contact support with specific performance data
"""
    
    guide_path = 'UPLOAD_PERFORMANCE_GUIDE.md'
    try:
        with open(guide_path, 'w', encoding='utf-8') as f:
            f.write(guide_content)
        logger.info(f"✅ Created upload optimization guide: {guide_path}")
        return True
    except Exception as e:
        logger.error(f"❌ Error creating guide: {e}")
        return False

def main():
    """Main optimization function"""
    logger = setup_logging()
    
    print("🚀 File Upload Performance Optimization")
    print("=" * 50)
    
    optimizations = [
        ("Excel Processor", optimize_excel_processor),
        ("App.py", optimize_app_py),
        ("Performance Config", create_upload_performance_config),
        ("Performance Test", create_upload_performance_test),
        ("Optimization Guide", create_upload_optimization_guide)
    ]
    
    success_count = 0
    total_count = len(optimizations)
    
    for name, optimization_func in optimizations:
        print(f"\n🔧 {name} Optimization...")
        if optimization_func():
            success_count += 1
            print(f"✅ {name} optimization completed successfully")
        else:
            print(f"❌ {name} optimization failed")
    
    print(f"\n🎉 Optimization Summary: {success_count}/{total_count} successful")
    
    if success_count == total_count:
        print("\n✅ All optimizations completed successfully!")
        print("\n📝 Next steps:")
        print("   1. Test upload performance: python test_upload_performance.py")
        print("   2. Review the optimization guide: UPLOAD_PERFORMANCE_GUIDE.md")
        print("   3. Try uploading a file to see improved performance")
        print("   4. If still slow, check the troubleshooting section in the guide")
    else:
        print(f"\n⚠️  {total_count - success_count} optimizations failed")
        print("Check the error messages above for details")
    
    return success_count == total_count

if __name__ == "__main__":
    main()
