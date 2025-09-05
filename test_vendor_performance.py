#!/usr/bin/env python3
"""
Test Script for Vendor Filtering Performance
This script tests the optimized vendor filtering approach.
"""

import sys
import os
import time
import logging

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_vendor_filtering_performance():
    """Test the performance of vendor filtering."""
    print("🧪 Testing Vendor Filtering Performance Improvements")
    print("=" * 60)
    
    try:
        from core.data.json_matcher import JSONMatcher
        
        # Create a mock Excel processor for testing
        class MockExcelProcessor:
            def __init__(self):
                self.sheet_cache = []
                # Create mock data with different vendors
                vendors = ['dcz holdings inc', 'omega labs', 'airo pro', 'hustler\'s ambition']
                for i, vendor in enumerate(vendors):
                    for j in range(50):  # 50 items per vendor
                        self.sheet_cache.append({
                            'idx': i * 50 + j,
                            'original_name': f'Product {j} from {vendor}',
                            'vendor': vendor,
                            'product_type': 'flower',
                            'strain': f'Strain {j}'
                        })
        
        mock_processor = MockExcelProcessor()
        
        # Create JSON matcher
        matcher = JSONMatcher(mock_processor)
        
        # Mock the DataFrame that the matcher expects
        import pandas as pd
        mock_data = []
        for item in mock_processor.sheet_cache:
            mock_data.append({
                'Product Name*': item['original_name'],
                'Product Brand': 'Test Brand',
                'Vendor': item['vendor'],
                'Product Type*': item['product_type'],
                'Lineage': 'HYBRID',
                'Product Strain': item['strain']
            })
        
        mock_processor.df = pd.DataFrame(mock_data)
        
        # Build the indexed cache
        matcher._build_sheet_cache()
        
        # Test data
        test_items = [
            {'product_name': 'Banana OG Flower', 'vendor': 'dcz holdings inc'},
            {'product_name': 'Sour Diesel', 'vendor': 'omega labs'},
            {'product_name': 'Blue Dream', 'vendor': 'airo pro'},
            {'product_name': 'Purple Kush', 'vendor': 'hustler\'s ambition'},
        ]
        
        print(f"Test items: {len(test_items)}")
        print(f"Mock database: {len(mock_processor.sheet_cache)} items")
        print()
        
        # Test candidate finding performance
        total_time = 0
        total_candidates = 0
        
        for i, item in enumerate(test_items):
            print(f"Testing item {i+1}: {item['product_name']} (vendor: {item['vendor']})")
            
            start_time = time.time()
            candidates = matcher._find_candidates_optimized(item)
            item_time = time.time() - start_time
            
            total_time += item_time
            total_candidates += len(candidates)
            
            print(f"  Found {len(candidates)} candidates in {item_time:.3f}s")
            
            # Show vendor distribution
            vendor_counts = {}
            for candidate in candidates:
                vendor = candidate.get('vendor', 'unknown')
                vendor_counts[vendor] = vendor_counts.get(vendor, 0) + 1
            
            print(f"  Vendor distribution: {vendor_counts}")
            print()
        
        print("📊 Performance Summary")
        print("=" * 60)
        print(f"Total time: {total_time:.3f}s")
        print(f"Average time per item: {total_time/len(test_items):.3f}s")
        print(f"Total candidates found: {total_candidates}")
        print(f"Average candidates per item: {total_candidates/len(test_items):.1f}")
        print()
        
        if total_time < 1.0:
            print("✅ Performance is excellent (< 1 second total)")
        elif total_time < 5.0:
            print("✅ Performance is good (< 5 seconds total)")
        else:
            print("⚠️  Performance could be improved")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

if __name__ == "__main__":
    success = test_vendor_filtering_performance()
    if success:
        print("\n✅ Vendor filtering performance test completed successfully!")
    else:
        print("\n❌ Vendor filtering performance test failed!")
