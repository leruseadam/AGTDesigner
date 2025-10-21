#!/usr/bin/env python3
"""
QUICK PERFORMANCE TEST
Test the Excel processing performance improvements
"""

import os
import time
import logging
import pandas as pd
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_test_excel_file(filename: str, rows: int = 1000, columns: int = 10):
    """Create a test Excel file for performance testing"""
    try:
        # Create test data
        data = {}
        for i in range(columns):
            data[f'Column_{i+1}'] = [f'Test_Data_{j}_{i}' for j in range(rows)]
        
        # Add some specific columns that the app expects
        data['Description'] = [f'Test Product {i}' for i in range(rows)]
        data['Product Brand'] = [f'Brand {i % 5}' for i in range(rows)]
        data['Price'] = [f'${i * 1.5:.2f}' for i in range(rows)]
        data['Lineage'] = [f'Lineage {i % 3}' for i in range(rows)]
        
        df = pd.DataFrame(data)
        
        # Save to Excel
        df.to_excel(filename, index=False, engine='openpyxl')
        
        file_size = os.path.getsize(filename)
        logging.info(f"✅ Created test file: {filename}")
        logging.info(f"   Rows: {rows:,}, Columns: {len(df.columns)}, Size: {file_size:,} bytes")
        
        return filename, file_size
        
    except Exception as e:
        logging.error(f"❌ Failed to create test file: {e}")
        return None, 0

def test_optimized_processor(file_path: str):
    """Test the optimized Excel processor"""
    try:
        logging.info("🚀 Testing optimized processor...")
        
        from EXCEL_PROCESSING_OPTIMIZATION import get_optimized_excel_processor
        
        processor = get_optimized_excel_processor()
        start_time = time.time()
        
        result = processor.process_excel_optimized(file_path)
        
        processing_time = time.time() - start_time
        
        if result['success']:
            logging.info(f"✅ Optimized processor SUCCESS:")
            logging.info(f"   Rows processed: {result['rows_processed']:,}")
            logging.info(f"   Processing time: {processing_time:.3f}s")
            logging.info(f"   Method used: {result.get('method', 'unknown')}")
            logging.info(f"   Strategy: {result.get('strategy_used', 'unknown')}")
            
            # Calculate speed metrics
            rows_per_second = result['rows_processed'] / processing_time
            logging.info(f"   Speed: {rows_per_second:.0f} rows/sec")
            
            return True, processing_time, result['rows_processed']
        else:
            logging.error(f"❌ Optimized processor FAILED: {result.get('error')}")
            return False, 0, 0
            
    except ImportError:
        logging.warning("⚠️ Optimized processor not available")
        return False, 0, 0
    except Exception as e:
        logging.error(f"❌ Optimized processor error: {e}")
        return False, 0, 0

def test_fast_processor(file_path: str):
    """Test the fast Excel processor"""
    try:
        logging.info("🏃 Testing fast processor...")
        
        from FAST_EXCEL_UPLOAD import FastExcelProcessor
        
        processor = FastExcelProcessor()
        start_time = time.time()
        
        result = processor.process_excel_fast(file_path)
        
        processing_time = time.time() - start_time
        
        if result['success']:
            logging.info(f"✅ Fast processor SUCCESS:")
            logging.info(f"   Rows processed: {result['rows_processed']:,}")
            logging.info(f"   Processing time: {processing_time:.3f}s")
            logging.info(f"   Method used: {result.get('method', 'unknown')}")
            
            # Calculate speed metrics
            rows_per_second = result['rows_processed'] / processing_time
            logging.info(f"   Speed: {rows_per_second:.0f} rows/sec")
            
            return True, processing_time, result['rows_processed']
        else:
            logging.error(f"❌ Fast processor FAILED: {result.get('error')}")
            return False, 0, 0
            
    except ImportError:
        logging.warning("⚠️ Fast processor not available")
        return False, 0, 0
    except Exception as e:
        logging.error(f"❌ Fast processor error: {e}")
        return False, 0, 0

def test_performance_monitor():
    """Test the performance monitoring system"""
    try:
        logging.info("📊 Testing performance monitor...")
        
        from PERFORMANCE_MONITOR import performance_monitor, print_performance_report
        
        # Simulate some performance data
        performance_monitor.log_processing("test1.xlsx", 2.5, 1000, 3.2, "optimized")
        performance_monitor.log_processing("test2.xlsx", 5.1, 2500, 8.7, "fast")
        performance_monitor.log_processing("test3.xlsx", 12.3, 5000, 25.4, "chunked")
        
        # Print performance report
        print_performance_report()
        
        logging.info("✅ Performance monitor test completed")
        return True
        
    except ImportError:
        logging.warning("⚠️ Performance monitor not available")
        return False
    except Exception as e:
        logging.error(f"❌ Performance monitor error: {e}")
        return False

def main():
    """Main test function"""
    logging.info("🧪 EXCEL PROCESSING PERFORMANCE TEST")
    logging.info("=" * 50)
    
    # Create test files
    test_files = []
    
    # Small file test
    small_file, small_size = create_test_excel_file("test_small.xlsx", 500, 8)
    if small_file:
        test_files.append((small_file, small_size, "small"))
    
    # Medium file test
    medium_file, medium_size = create_test_excel_file("test_medium.xlsx", 2000, 10)
    if medium_file:
        test_files.append((medium_file, medium_size, "medium"))
    
    # Large file test
    large_file, large_size = create_test_excel_file("test_large.xlsx", 5000, 12)
    if large_file:
        test_files.append((large_file, large_size, "large"))
    
    if not test_files:
        logging.error("❌ No test files created, aborting test")
        return
    
    # Test each file with both processors
    results = []
    
    for file_path, file_size, size_type in test_files:
        logging.info(f"\n📁 Testing {size_type} file: {file_path}")
        logging.info(f"   File size: {file_size:,} bytes")
        
        # Test optimized processor
        opt_success, opt_time, opt_rows = test_optimized_processor(file_path)
        
        # Test fast processor
        fast_success, fast_time, fast_rows = test_fast_processor(file_path)
        
        # Store results
        results.append({
            'file': file_path,
            'size_type': size_type,
            'file_size': file_size,
            'optimized_success': opt_success,
            'optimized_time': opt_time,
            'optimized_rows': opt_rows,
            'fast_success': fast_success,
            'fast_time': fast_time,
            'fast_rows': fast_rows
        })
    
    # Test performance monitor
    test_performance_monitor()
    
    # Print summary
    logging.info("\n📊 TEST SUMMARY")
    logging.info("=" * 50)
    
    for result in results:
        logging.info(f"\nFile: {result['file']} ({result['size_type']})")
        logging.info(f"Size: {result['file_size']:,} bytes")
        
        if result['optimized_success']:
            logging.info(f"✅ Optimized: {result['optimized_rows']:,} rows in {result['optimized_time']:.3f}s")
        else:
            logging.info("❌ Optimized: FAILED")
        
        if result['fast_success']:
            logging.info(f"✅ Fast: {result['fast_rows']:,} rows in {result['fast_time']:.3f}s")
        else:
            logging.info("❌ Fast: FAILED")
    
    # Cleanup test files
    logging.info("\n🧹 Cleaning up test files...")
    for file_path, _, _ in test_files:
        try:
            os.remove(file_path)
            logging.info(f"✅ Removed: {file_path}")
        except Exception as e:
            logging.warning(f"⚠️ Could not remove {file_path}: {e}")
    
    logging.info("\n✅ Performance test completed!")

if __name__ == "__main__":
    main()
