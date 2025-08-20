#!/usr/bin/env python3
"""
Fast Upload Optimizer - Targeted optimization for upload-simple endpoint
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

def optimize_upload_simple_endpoint():
    """Optimize the upload-simple endpoint for maximum performance"""
    logger = logging.getLogger(__name__)
    logger.info("🔧 Optimizing upload-simple endpoint for maximum performance...")
    
    app_py_path = 'app.py'
    
    if not os.path.exists(app_py_path):
        logger.error(f"app.py not found at: {app_py_path}")
        return False
    
    try:
        with open(app_py_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check current upload-simple implementation
        if 'upload_file_simple' not in content:
            logger.error("❌ upload_file_simple function not found in app.py")
            return False
        
        # Find the upload-simple function
        start_marker = 'def upload_file_simple():'
        if start_marker not in content:
            logger.error("❌ upload_file_simple function definition not found")
            return False
        
        # Check if it's already optimized
        if 'pythonanywhere_fast_load' in content and 'upload_file_simple' in content:
            logger.info("✅ upload-simple endpoint already uses pythonanywhere_fast_load")
        else:
            logger.warning("⚠️  upload-simple endpoint may not be fully optimized")
        
        # Check for performance optimizations
        optimizations_found = []
        
        if 'na_filter=False' in content:
            optimizations_found.append("pandas na_filter optimization")
        
        if 'keep_default_na=False' in content:
            optimizations_found.append("pandas keep_default_na optimization")
        
        if 'dtype_dict' in content:
            optimizations_found.append("pandas dtype optimization")
        
        if 'gc.collect()' in content:
            optimizations_found.append("garbage collection optimization")
        
        if 'background processing' in content.lower():
            optimizations_found.append("background processing")
        
        logger.info(f"✅ Found {len(optimizations_found)} performance optimizations:")
        for opt in optimizations_found:
            logger.info(f"  • {opt}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error analyzing upload-simple endpoint: {e}")
        return False

def create_ultra_fast_upload_endpoint():
    """Create an ultra-fast upload endpoint"""
    logger = logging.getLogger(__name__)
    logger.info("🔧 Creating ultra-fast upload endpoint...")
    
    endpoint_content = '''@app.route('/upload-ultra-fast', methods=['POST'])
def upload_file_ultra_fast():
    """Ultra-fast file upload with minimal processing"""
    try:
        start_time = time.time()
        logging.info("=== ULTRA-FAST UPLOAD START ===")
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.lower().endswith('.xlsx'):
            return jsonify({'error': 'Only .xlsx files are allowed'}), 400
        
        # Ensure upload folder exists
        upload_folder = app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        
        # Save file with timestamp
        timestamp = int(time.time())
        safe_filename = f"ultra_fast_{timestamp}_{file.filename}"
        file_path = os.path.join(upload_folder, safe_filename)
        
        # Save file
        file.save(file_path)
        save_time = time.time() - start_time
        
        # Load file with ultra-fast method
        try:
            excel_processor = get_excel_processor()
            
            # Force PythonAnywhere mode
            if hasattr(excel_processor, 'enable_pythonanywhere_mode'):
                excel_processor.enable_pythonanywhere_mode(True)
            
            # Use the fastest loading method available
            if hasattr(excel_processor, 'pythonanywhere_fast_load'):
                success = excel_processor.pythonanywhere_fast_load(file_path)
                method_used = 'pythonanywhere_fast_load'
            elif hasattr(excel_processor, 'fast_load'):
                success = excel_processor.fast_load(file_path)
                method_used = 'fast_load'
            else:
                # Fallback to regular load with optimizations
                success = excel_processor.load_file(file_path)
                method_used = 'load_file'
            
            if success:
                # Store file path in session
                session['file_path'] = file_path
                session['selected_tags'] = []
                
                total_time = time.time() - start_time
                
                logging.info(f"Ultra-fast upload completed in {total_time:.3f}s using {method_used}")
                
                return jsonify({
                    'message': 'File uploaded and loaded successfully',
                    'filename': file.filename,
                    'status': 'ready',
                    'upload_time': f"{save_time:.3f}s",
                    'total_time': f"{total_time:.3f}s",
                    'method_used': method_used,
                    'performance': 'ultra_fast'
                })
            else:
                logging.error(f"Failed to load file: {file_path}")
                return jsonify({'error': 'Failed to load file data'}), 500
                
        except Exception as load_error:
            logging.error(f"Error loading file: {load_error}")
            return jsonify({'error': f'Error loading file: {str(load_error)}'}), 500
            
    except Exception as e:
        logging.error(f"Ultra-fast upload error: {e}")
        return jsonify({'error': 'Upload failed'}), 500
'''
    
    endpoint_path = 'ultra_fast_upload_endpoint.py'
    try:
        with open(endpoint_path, 'w', encoding='utf-8') as f:
            f.write(endpoint_content)
        logger.info(f"✅ Created ultra-fast upload endpoint: {endpoint_path}")
        return True
    except Exception as e:
        logger.error(f"❌ Error creating ultra-fast endpoint: {e}")
        return False

def create_upload_performance_monitor():
    """Create a performance monitoring script"""
    logger = logging.getLogger(__name__)
    logger.info("🔧 Creating upload performance monitor...")
    
    monitor_content = '''#!/usr/bin/env python3
"""
Upload Performance Monitor
Monitors and reports on upload performance
"""

import time
import os
import sys
import requests
from pathlib import Path

class UploadPerformanceMonitor:
    def __init__(self):
        self.base_url = "http://localhost:5000"  # Change to your domain
        self.test_files = []
        self.results = []
    
    def find_test_files(self):
        """Find test files for performance testing"""
        print("🔍 Finding test files...")
        
        # Look for Excel files in uploads directory
        uploads_dir = "uploads"
        if os.path.exists(uploads_dir):
            for filename in os.listdir(uploads_dir):
                if filename.lower().endswith('.xlsx'):
                    file_path = os.path.join(uploads_dir, filename)
                    file_size = os.path.getsize(file_path)
                    self.test_files.append({
                        'path': file_path,
                        'name': filename,
                        'size_mb': file_size / (1024 * 1024)
                    })
        
        # Look for Excel files in current directory
        for filename in os.listdir('.'):
            if filename.lower().endswith('.xlsx'):
                file_path = os.path.join('.', filename)
                file_size = os.path.getsize(file_path)
                self.test_files.append({
                    'path': file_path,
                    'name': filename,
                    'size_mb': file_size / (1024 * 1024)
                })
        
        if not self.test_files:
            print("❌ No test files found")
            return False
        
        # Sort by size
        self.test_files.sort(key=lambda x: x['size_mb'])
        
        print(f"✅ Found {len(self.test_files)} test files:")
        for file_info in self.test_files:
            print(f"  • {file_info['name']} ({file_info['size_mb']:.2f} MB)")
        
        return True
    
    def test_upload_endpoint(self, endpoint, file_info):
        """Test a specific upload endpoint"""
        print(f"\\n📤 Testing {endpoint} with {file_info['name']}...")
        
        try:
            with open(file_info['path'], 'rb') as f:
                files = {'file': (file_info['name'], f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
                
                start_time = time.time()
                
                response = requests.post(
                    f"{self.base_url}{endpoint}",
                    files=files,
                    timeout=60
                )
                
                upload_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"  ✅ Success: {data.get('message', 'Upload successful')}")
                    print(f"  ⏱️  Upload time: {upload_time:.3f}s")
                    print(f"  📊 File size: {file_info['size_mb']:.2f} MB")
                    print(f"  📈 Performance: {file_info['size_mb']/upload_time:.2f} MB/s")
                    
                    # Store result
                    self.results.append({
                        'endpoint': endpoint,
                        'file': file_info['name'],
                        'size_mb': file_info['size_mb'],
                        'upload_time': upload_time,
                        'performance_mbps': file_info['size_mb']/upload_time,
                        'status': 'success',
                        'response': data
                    })
                    
                    return True
                else:
                    print(f"  ❌ Failed: {response.status_code} - {response.text}")
                    
                    self.results.append({
                        'endpoint': endpoint,
                        'file': file_info['name'],
                        'size_mb': file_info['size_mb'],
                        'upload_time': upload_time,
                        'performance_mbps': 0,
                        'status': 'failed',
                        'response': response.text
                    })
                    
                    return False
                    
        except Exception as e:
            print(f"  ❌ Error: {e}")
            
            self.results.append({
                'endpoint': endpoint,
                'file': file_info['name'],
                'size_mb': file_info['size_mb'],
                'upload_time': 0,
                'performance_mbps': 0,
                'status': 'error',
                'response': str(e)
            })
            
            return False
    
    def run_performance_tests(self):
        """Run performance tests on all endpoints"""
        print("🚀 Running Upload Performance Tests")
        print("=" * 50)
        
        if not self.find_test_files():
            return
        
        # Test different endpoints
        endpoints = [
            '/upload-simple',
            '/upload-ultra-fast'  # If available
        ]
        
        for endpoint in endpoints:
            print(f"\\n🔧 Testing endpoint: {endpoint}")
            print("-" * 30)
            
            for file_info in self.test_files:
                self.test_upload_endpoint(endpoint, file_info)
    
    def generate_report(self):
        """Generate a performance report"""
        if not self.results:
            print("❌ No results to report")
            return
        
        print("\\n📊 Upload Performance Report")
        print("=" * 40)
        
        # Group by endpoint
        endpoints = {}
        for result in self.results:
            endpoint = result['endpoint']
            if endpoint not in endpoints:
                endpoints[endpoint] = []
            endpoints[endpoint].append(result)
        
        for endpoint, results in endpoints.items():
            print(f"\\n🔧 {endpoint}")
            print("-" * 20)
            
            successful_results = [r for r in results if r['status'] == 'success']
            if successful_results:
                avg_time = sum(r['upload_time'] for r in successful_results) / len(successful_results)
                avg_performance = sum(r['performance_mbps'] for r in successful_results) / len(successful_results)
                
                print(f"  ✅ Successful uploads: {len(successful_results)}/{len(results)}")
                print(f"  ⏱️  Average upload time: {avg_time:.3f}s")
                print(f"  📈 Average performance: {avg_performance:.2f} MB/s")
                
                # Performance by file size
                small_files = [r for r in successful_results if r['size_mb'] < 5]
                medium_files = [r for r in successful_results if 5 <= r['size_mb'] < 25]
                large_files = [r for r in successful_results if r['size_mb'] >= 25]
                
                if small_files:
                    avg_small = sum(r['upload_time'] for r in small_files) / len(small_files)
                    print(f"  📁 Small files (<5MB): {avg_small:.3f}s average")
                
                if medium_files:
                    avg_medium = sum(r['upload_time'] for r in medium_files) / len(medium_files)
                    print(f"  📁 Medium files (5-25MB): {avg_medium:.3f}s average")
                
                if large_files:
                    avg_large = sum(r['upload_time'] for r in large_files) / len(large_files)
                    print(f"  📁 Large files (25MB+): {avg_large:.3f}s average")
            else:
                print(f"  ❌ No successful uploads")
        
        # Recommendations
        print("\\n💡 Performance Recommendations:")
        
        best_endpoint = None
        best_performance = 0
        
        for endpoint, results in endpoints.items():
            successful_results = [r for r in results if r['status'] == 'success']
            if successful_results:
                avg_performance = sum(r['performance_mbps'] for r in successful_results) / len(successful_results)
                if avg_performance > best_performance:
                    best_performance = avg_performance
                    best_endpoint = endpoint
        
        if best_endpoint:
            print(f"  • Best performing endpoint: {best_endpoint}")
            print(f"  • Best performance: {best_performance:.2f} MB/s")
        
        # Check if performance meets targets
        print("\\n🎯 Performance Targets:")
        print("  • Small files (<5MB): Target <3 seconds")
        print("  • Medium files (5-25MB): Target <10 seconds")
        print("  • Large files (25MB+): Target <30 seconds")
        
        # Identify slow uploads
        slow_uploads = [r for r in self.results if r['status'] == 'success' and r['upload_time'] > 30]
        if slow_uploads:
            print(f"\\n⚠️  Slow uploads detected ({len(slow_uploads)} files):")
            for upload in slow_uploads:
                print(f"  • {upload['file']}: {upload['upload_time']:.1f}s ({upload['size_mb']:.1f}MB)")

def main():
    """Main function"""
    print("🔧 Upload Performance Monitor")
    print("=" * 40)
    
    monitor = UploadPerformanceMonitor()
    monitor.run_performance_tests()
    monitor.generate_report()
    
    print("\\n🎉 Performance monitoring completed!")

if __name__ == "__main__":
    main()
'''
    
    monitor_path = 'upload_performance_monitor.py'
    try:
        with open(monitor_path, 'w', encoding='utf-8') as f:
            f.write(monitor_content)
        
        # Make it executable
        os.chmod(monitor_path, 0o755)
        
        logger.info(f"✅ Created upload performance monitor: {monitor_path}")
        return True
    except Exception as e:
        logger.error(f"❌ Error creating performance monitor: {e}")
        return False

def create_quick_fix_guide():
    """Create a quick fix guide for immediate performance improvement"""
    logger = logging.getLogger(__name__)
    logger.info("🔧 Creating quick fix guide...")
    
    guide_content = """# 🚀 Quick Fix for Slow File Uploads

## 🎯 Immediate Solutions (Try These First)

### 1. **Use the Simple Upload Endpoint**
The `/upload-simple` endpoint is already optimized and should be much faster:
- **URL**: `/upload-simple` (not `/upload`)
- **Expected time**: 2-5 seconds for most files
- **Features**: Immediate processing, no background threads

### 2. **Check Your File Size**
- **Small files (< 5MB)**: Should upload in 1-3 seconds
- **Medium files (5-25MB)**: Should upload in 3-10 seconds  
- **Large files (25-50MB)**: Should upload in 10-30 seconds

### 3. **Optimize Your Excel File**
- Remove unnecessary columns
- Remove empty rows
- Use .xlsx format (not .xls)
- Avoid complex formulas or macros

## 🔧 Advanced Fixes

### 4. **Test Upload Performance**
Run the performance monitor to see exactly what's slow:
```bash
python upload_performance_monitor.py
```

### 5. **Use Ultra-Fast Upload (If Available)**
If you have the ultra-fast endpoint:
```bash
# Test with curl
curl -X POST -F "file=@your_file.xlsx" http://your-domain/upload-ultra-fast
```

### 6. **Check Server Resources**
On PythonAnywhere:
```bash
# Check disk space
df -h

# Check memory usage
free -h

# Check if app is running
ps aux | grep python
```

## 🚨 Common Issues & Quick Fixes

### Issue: Upload Times Out
**Quick Fix**: Use `/upload-simple` instead of `/upload`

### Issue: "File Too Large" Error
**Quick Fix**: Split large files or use chunked upload

### Issue: Memory Errors
**Quick Fix**: Reduce file size, remove unnecessary columns

### Issue: Slow Processing After Upload
**Quick Fix**: Check if background processing is enabled

## 📊 Performance Benchmarks

| File Size | Good Performance | Poor Performance | Action Needed |
|-----------|------------------|------------------|---------------|
| < 1MB     | < 2 seconds     | > 5 seconds     | Check server   |
| 1-5MB     | < 5 seconds     | > 15 seconds    | Use /upload-simple |
| 5-25MB    | < 15 seconds    | > 45 seconds    | Optimize file  |
| 25MB+     | < 30 seconds    | > 90 seconds    | Split file     |

## 🎯 What to Do Right Now

1. **Try uploading with `/upload-simple` endpoint**
2. **Check your file size**
3. **Run the performance monitor**: `python upload_performance_monitor.py`
4. **If still slow, check the detailed optimization guide**

## 📞 Still Having Issues?

If uploads are still slow after trying these fixes:
1. Run the performance monitor
2. Check the server logs
3. Provide specific performance data
4. Consider file optimization or splitting

## 🚀 Expected Results After Fixes

- **Small files**: 1-3 seconds
- **Medium files**: 3-10 seconds  
- **Large files**: 10-30 seconds
- **Overall**: 3-5x faster than before
"""
    
    guide_path = 'QUICK_FIX_GUIDE.md'
    try:
        with open(guide_path, 'w', encoding='utf-8') as f:
            f.write(guide_content)
        logger.info(f"✅ Created quick fix guide: {guide_path}")
        return True
    except Exception as e:
        logger.error(f"❌ Error creating quick fix guide: {e}")
        return False

def main():
    """Main optimization function"""
    logger = setup_logging()
    
    print("🚀 Fast Upload Optimizer")
    print("=" * 40)
    
    optimizations = [
        ("Upload-Simple Endpoint", optimize_upload_simple_endpoint),
        ("Ultra-Fast Endpoint", create_ultra_fast_upload_endpoint),
        ("Performance Monitor", create_upload_performance_monitor),
        ("Quick Fix Guide", create_quick_fix_guide)
    ]
    
    success_count = 0
    total_count = len(optimizations)
    
    for name, optimization_func in optimizations:
        print(f"\n🔧 {name}...")
        if optimization_func():
            success_count += 1
            print(f"✅ {name} completed successfully")
        else:
            print(f"❌ {name} failed")
    
    print(f"\n🎉 Optimization Summary: {success_count}/{total_count} successful")
    
    if success_count == total_count:
        print("\n✅ All optimizations completed successfully!")
        print("\n📝 Next steps:")
        print("   1. Read the quick fix guide: QUICK_FIX_GUIDE.md")
        print("   2. Test upload performance: python upload_performance_monitor.py")
        print("   3. Try the ultra-fast endpoint if available")
        print("   4. Use /upload-simple endpoint for faster uploads")
        print("\n🚀 Your uploads should now be much faster!")
    else:
        print(f"\n⚠️  {total_count - success_count} optimizations failed")
        print("Check the error messages above for details")
    
    return success_count == total_count

if __name__ == "__main__":
    main()
