#!/usr/bin/env python3
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
        print(f"\n📤 Testing {endpoint} with {file_info['name']}...")
        
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
            print(f"\n🔧 Testing endpoint: {endpoint}")
            print("-" * 30)
            
            for file_info in self.test_files:
                self.test_upload_endpoint(endpoint, file_info)
    
    def generate_report(self):
        """Generate a performance report"""
        if not self.results:
            print("❌ No results to report")
            return
        
        print("\n📊 Upload Performance Report")
        print("=" * 40)
        
        # Group by endpoint
        endpoints = {}
        for result in self.results:
            endpoint = result['endpoint']
            if endpoint not in endpoints:
                endpoints[endpoint] = []
            endpoints[endpoint].append(result)
        
        for endpoint, results in endpoints.items():
            print(f"\n🔧 {endpoint}")
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
        print("\n💡 Performance Recommendations:")
        
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
        print("\n🎯 Performance Targets:")
        print("  • Small files (<5MB): Target <3 seconds")
        print("  • Medium files (5-25MB): Target <10 seconds")
        print("  • Large files (25MB+): Target <30 seconds")
        
        # Identify slow uploads
        slow_uploads = [r for r in self.results if r['status'] == 'success' and r['upload_time'] > 30]
        if slow_uploads:
            print(f"\n⚠️  Slow uploads detected ({len(slow_uploads)} files):")
            for upload in slow_uploads:
                print(f"  • {upload['file']}: {upload['upload_time']:.1f}s ({upload['size_mb']:.1f}MB)")

def main():
    """Main function"""
    print("🔧 Upload Performance Monitor")
    print("=" * 40)
    
    monitor = UploadPerformanceMonitor()
    monitor.run_performance_tests()
    monitor.generate_report()
    
    print("\n🎉 Performance monitoring completed!")

if __name__ == "__main__":
    main()
