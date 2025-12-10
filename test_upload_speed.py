#!/usr/bin/env python3
"""Test script to verify Excel upload optimization"""

import time
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_excel_load_speed():
    """Test how fast we can load an Excel file and get tags"""

    # Find a test Excel file
    test_file = "/Users/adamcordova/Desktop/labelMaker_ QR copy final/uploads/1765162770_A Greener Today - Bothell_inventory_12-07-2025  8_33 AM.xlsx"

    if not os.path.exists(test_file):
        print(f"❌ Test file not found: {test_file}")
        return

    print(f"🔍 Testing with file: {os.path.basename(test_file)}")
    print(f"📦 File size: {os.path.getsize(test_file) / (1024*1024):.2f} MB")
    print()

    # Test 1: Load Excel file
    print("=" * 60)
    print("TEST 1: Load Excel file with ExcelProcessor")
    print("=" * 60)

    start = time.time()
    try:
        from src.core.data.excel_processor import ExcelProcessor
        processor = ExcelProcessor()
        success = processor.load_file(test_file)
        load_time = time.time() - start

        if success:
            row_count = len(processor.df) if hasattr(processor, 'df') and processor.df is not None else 0
            print(f"✅ File loaded successfully: {row_count} rows")
            print(f"⏱️  Load time: {load_time:.3f}s")
        else:
            print(f"❌ File load failed")
            return
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        import traceback
        traceback.print_exc()
        return

    print()

    # Test 2: Get available tags
    print("=" * 60)
    print("TEST 2: Get available tags from loaded file")
    print("=" * 60)

    start = time.time()
    try:
        tags = processor.get_available_tags(filters=None)
        tags_time = time.time() - start

        print(f"✅ Got {len(tags)} tags")
        print(f"⏱️  Tags generation time: {tags_time:.3f}s")

        if len(tags) > 0:
            print(f"📝 Sample tag: {tags[0].get('Product Name*', 'N/A')}")
    except Exception as e:
        print(f"❌ Error getting tags: {e}")
        import traceback
        traceback.print_exc()
        return

    print()

    # Test 3: Total time
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)

    total_time = load_time + tags_time
    print(f"📊 Total time: {total_time:.3f}s")
    print(f"   - Load file: {load_time:.3f}s ({load_time/total_time*100:.1f}%)")
    print(f"   - Get tags: {tags_time:.3f}s ({tags_time/total_time*100:.1f}%)")
    print()

    if total_time < 1.0:
        print("✅ EXCELLENT: Upload should be instant (< 1 second)")
    elif total_time < 3.0:
        print("✅ GOOD: Upload should be fast (< 3 seconds)")
    elif total_time < 5.0:
        print("⚠️  OK: Upload will take a few seconds (< 5 seconds)")
    else:
        print("❌ SLOW: Upload will be slow (> 5 seconds)")
        print("💡 Optimization needed!")

if __name__ == '__main__':
    test_excel_load_speed()
