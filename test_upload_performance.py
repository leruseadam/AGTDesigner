#!/usr/bin/env python3
"""
Performance testing script for Excel upload optimization.
Tests the speed improvements of the optimized upload process.
"""

import os
import time
import logging
import tempfile
import pandas as pd
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_test_excel_file(rows=1000, filename="test_upload_performance.xlsx"):
    """Create a test Excel file with sample data for performance testing."""
    logger.info(f"Creating test Excel file with {rows} rows...")
    
    # Sample data for testing - ensure all arrays have the same length
    product_types = ['flower'] * (rows // 4) + ['concentrate'] * (rows // 4) + ['edible (solid)'] * (rows // 4) + ['tincture'] * (rows - 3 * (rows // 4))
    lineages = ['HYBRID'] * (rows // 3) + ['SATIVA'] * (rows // 3) + ['INDICA'] * (rows - 2 * (rows // 3))
    
    data = {
        'Product Name*': [f'Test Product {i}' for i in range(rows)],
        'Product Type*': product_types,
        'Lineage': lineages,
        'Product Brand': [f'Brand {i % 10}' for i in range(rows)],
        'Vendor/Supplier*': [f'Vendor {i % 5}' for i in range(rows)],
        'Weight*': [1.0 + (i % 10) * 0.1 for i in range(rows)],
        'Weight Unit* (grams/gm or ounces/oz)': ['g'] * rows,
        'Price* (Tier Name for Bulk)': [10.0 + (i % 50) for i in range(rows)],
        'DOH Compliant (Yes/No)': ['Yes'] * rows,
        'Product Strain': [f'Strain {i % 20}' for i in range(rows)],
        'Description': [f'Description for product {i}' for i in range(rows)],
        'Ratio': ['THC: 20% | CBD: 2%'] * rows,
    }
    
    df = pd.DataFrame(data)
    
    # Save to temporary file
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, filename)
    df.to_excel(file_path, index=False, engine='openpyxl')
    
    logger.info(f"Test file created: {file_path} ({os.path.getsize(file_path)} bytes)")
    return file_path

def test_original_load_performance(file_path):
    """Test the original load_file method performance."""
    logger.info("Testing original load_file method...")
    
    try:
        from src.core.data.excel_processor import ExcelProcessor
        
        # Temporarily disable fast loading to test original method
        import src.core.data.excel_processor as ep
        original_fast_loading = ep.ENABLE_FAST_LOADING
        ep.ENABLE_FAST_LOADING = False
        
        processor = ExcelProcessor()
        
        start_time = time.time()
        success = processor.load_file(file_path)
        load_time = time.time() - start_time
        
        # Restore original setting
        ep.ENABLE_FAST_LOADING = original_fast_loading
        
        if success:
            logger.info(f"Original load_file: SUCCESS in {load_time:.2f}s")
            return load_time, True
        else:
            logger.error("Original load_file: FAILED")
            return load_time, False
            
    except Exception as e:
        logger.error(f"Original load_file error: {e}")
        return 0, False

def test_optimized_load_performance(file_path):
    """Test the optimized fast_load_file method performance."""
    logger.info("Testing optimized fast_load_file method...")
    
    try:
        from src.core.data.excel_processor import ExcelProcessor
        
        processor = ExcelProcessor()
        
        start_time = time.time()
        success = processor.fast_load_file(file_path)
        load_time = time.time() - start_time
        
        if success:
            logger.info(f"Optimized fast_load_file: SUCCESS in {load_time:.2f}s")
            return load_time, True
        else:
            logger.error("Optimized fast_load_file: FAILED")
            return load_time, False
            
    except Exception as e:
        logger.error(f"Optimized fast_load_file error: {e}")
        return 0, False

def test_minimal_processing_performance(file_path):
    """Test the minimal processing mode performance."""
    logger.info("Testing minimal processing mode...")
    
    try:
        from src.core.data.excel_processor import ExcelProcessor
        
        # Enable minimal processing
        import src.core.data.excel_processor as ep
        original_minimal = ep.ENABLE_MINIMAL_PROCESSING
        ep.ENABLE_MINIMAL_PROCESSING = True
        
        processor = ExcelProcessor()
        
        start_time = time.time()
        success = processor.fast_load_file(file_path)
        load_time = time.time() - start_time
        
        # Restore original setting
        ep.ENABLE_MINIMAL_PROCESSING = original_minimal
        
        if success:
            logger.info(f"Minimal processing: SUCCESS in {load_time:.2f}s")
            return load_time, True
        else:
            logger.error("Minimal processing: FAILED")
            return load_time, False
            
    except Exception as e:
        logger.error(f"Minimal processing error: {e}")
        return 0, False

def run_performance_tests():
    """Run comprehensive performance tests."""
    logger.info("=== EXCEL UPLOAD PERFORMANCE TESTING ===")
    
    # Test different file sizes
    test_sizes = [100, 500, 1000, 2000, 5000]
    
    results = {}
    
    for size in test_sizes:
        logger.info(f"\n--- Testing with {size} rows ---")
        
        # Create test file
        file_path = create_test_excel_file(size)
        
        try:
            # Test original method
            original_time, original_success = test_original_load_performance(file_path)
            
            # Test optimized method
            optimized_time, optimized_success = test_optimized_load_performance(file_path)
            
            # Test minimal processing
            minimal_time, minimal_success = test_minimal_processing_performance(file_path)
            
            # Calculate improvements
            if original_success and optimized_success:
                improvement = ((original_time - optimized_time) / original_time) * 100
                minimal_improvement = ((original_time - minimal_time) / original_time) * 100
                
                results[size] = {
                    'original_time': original_time,
                    'optimized_time': optimized_time,
                    'minimal_time': minimal_time,
                    'improvement_percent': improvement,
                    'minimal_improvement_percent': minimal_improvement
                }
                
                logger.info(f"Results for {size} rows:")
                logger.info(f"  Original: {original_time:.2f}s")
                logger.info(f"  Optimized: {optimized_time:.2f}s")
                logger.info(f"  Minimal: {minimal_time:.2f}s")
                logger.info(f"  Improvement: {improvement:.1f}%")
                logger.info(f"  Minimal Improvement: {minimal_improvement:.1f}%")
            
        finally:
            # Clean up test file
            try:
                os.remove(file_path)
                logger.debug(f"Cleaned up test file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to clean up test file: {e}")
    
    # Print summary
    logger.info("\n=== PERFORMANCE TEST SUMMARY ===")
    for size, result in results.items():
        logger.info(f"{size} rows: {result['improvement_percent']:.1f}% faster (original: {result['original_time']:.2f}s, optimized: {result['optimized_time']:.2f}s)")
    
    # Calculate average improvement
    if results:
        avg_improvement = sum(r['improvement_percent'] for r in results.values()) / len(results)
        avg_minimal_improvement = sum(r['minimal_improvement_percent'] for r in results.values()) / len(results)
        logger.info(f"\nAverage improvement: {avg_improvement:.1f}%")
        logger.info(f"Average minimal processing improvement: {avg_minimal_improvement:.1f}%")

if __name__ == "__main__":
    run_performance_tests() 