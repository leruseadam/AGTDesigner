#!/usr/bin/env python3
"""
Simple test script to verify Excel processing optimization is working
"""

import os
import time
import sys

def test_excel_optimization():
    """Test the optimized Excel processor with your actual file"""
    
    print("=" * 70)
    print("EXCEL PROCESSING OPTIMIZATION TEST")
    print("=" * 70)
    print()
    
    # Find your Excel file
    uploads_dir = "uploads"
    excel_files = []
    
    if os.path.exists(uploads_dir):
        for file in os.listdir(uploads_dir):
            if file.endswith('.xlsx'):
                excel_files.append(os.path.join(uploads_dir, file))
    
    if not excel_files:
        print("❌ No Excel files found in uploads/ directory")
        print("Please upload an Excel file first")
        return False
    
    # Use the most recent Excel file
    test_file = max(excel_files, key=os.path.getmtime)
    file_size = os.path.getsize(test_file)
    
    print(f"📁 Test file: {os.path.basename(test_file)}")
    print(f"📊 File size: {file_size / (1024*1024):.2f} MB")
    print()
    
    # Test the optimization
    try:
        from EXCEL_PROCESSING_OPTIMIZATION import get_optimized_excel_processor
        
        print("🚀 Loading optimized processor...")
        processor = get_optimized_excel_processor()
        
        print("⚙️  Processing file with optimization...")
        start_time = time.time()
        
        result = processor.process_excel_optimized(test_file)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print()
        print("-" * 70)
        
        if result['success']:
            rows = result.get('rows_processed', 0)
            strategy = result.get('strategy_used', 'unknown')
            
            print("✅ OPTIMIZATION WORKING!")
            print()
            print(f"   Rows processed: {rows:,}")
            print(f"   Processing time: {processing_time:.2f} seconds")
            print(f"   Strategy used: {strategy}")
            print(f"   Speed: {rows / processing_time:.0f} rows/second")
            print()
            
            # Performance rating
            rows_per_sec = rows / processing_time
            if rows_per_sec > 1000:
                print("   Performance: 🎉 EXCELLENT (>1000 rows/sec)")
            elif rows_per_sec > 500:
                print("   Performance: 👍 GOOD (>500 rows/sec)")
            elif rows_per_sec > 100:
                print("   Performance: ✓ ACCEPTABLE (>100 rows/sec)")
            else:
                print("   Performance: ⚠️  SLOW (<100 rows/sec)")
            
            print()
            print("   Estimated old processor time: ~{:.1f} seconds".format(rows / 100))
            print("   Improvement: ~{:.0f}x faster".format((rows / 100) / processing_time))
            
            return True
        else:
            error = result.get('error', 'Unknown error')
            print(f"❌ OPTIMIZATION FAILED: {error}")
            return False
            
    except ImportError as e:
        print(f"❌ Cannot import optimization module: {e}")
        print()
        print("Make sure EXCEL_PROCESSING_OPTIMIZATION.py is in the same directory")
        return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        print()
        print("=" * 70)

if __name__ == "__main__":
    success = test_excel_optimization()
    sys.exit(0 if success else 1)

