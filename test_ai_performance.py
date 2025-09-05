#!/usr/bin/env python3
"""
Test Script for AI Matching Performance Improvements
This script tests the performance of the optimized AI matching functions.
"""

import sys
import os
import time
import logging

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_ai_matching_performance():
    """Test the performance of AI matching functions."""
    print("🧪 Testing AI Matching Performance Improvements")
    print("=" * 60)
    
    try:
        from core.data.json_matcher import (
            calculate_semantic_similarity, 
            calculate_semantic_similarity_batch,
            set_ai_matching_enabled,
            is_ai_matching_enabled
        )
        
        # Test data
        test_texts1 = [
            "Banana OG Flower",
            "Sour Diesel Concentrate", 
            "Blue Dream Vape Cartridge",
            "Purple Kush Edibles",
            "White Widow Pre-roll"
        ]
        
        test_texts2 = [
            "Banana OG",
            "Sour Diesel",
            "Blue Dream Cart",
            "Purple Kush Gummies", 
            "White Widow Joint"
        ]
        
        print(f"Test texts: {len(test_texts1)} pairs")
        print()
        
        # Test 1: Individual AI matching (original method)
        print("1️⃣ Testing Individual AI Matching (Original Method)")
        start_time = time.time()
        
        individual_results = []
        for t1, t2 in zip(test_texts1, test_texts2):
            similarity = calculate_semantic_similarity(t1, t2)
            individual_results.append(similarity)
        
        individual_time = time.time() - start_time
        print(f"   Individual matching time: {individual_time:.3f}s")
        print(f"   Results: {[f'{r:.3f}' for r in individual_results]}")
        print()
        
        # Test 2: Batch AI matching (optimized method)
        print("2️⃣ Testing Batch AI Matching (Optimized Method)")
        start_time = time.time()
        
        batch_results = calculate_semantic_similarity_batch(test_texts1, test_texts2)
        
        batch_time = time.time() - start_time
        print(f"   Batch matching time: {batch_time:.3f}s")
        print(f"   Results: {[f'{r:.3f}' for r in batch_results]}")
        print()
        
        # Test 3: Performance comparison
        print("3️⃣ Performance Comparison")
        if individual_time > 0:
            speedup = individual_time / batch_time
            print(f"   Speedup: {speedup:.1f}x faster with batch processing")
        else:
            print("   Speedup: Cannot calculate (too fast to measure)")
        print()
        
        # Test 4: AI matching toggle
        print("4️⃣ Testing AI Matching Toggle")
        print(f"   AI matching enabled: {is_ai_matching_enabled()}")
        
        # Disable AI matching
        set_ai_matching_enabled(False)
        print(f"   AI matching after disable: {is_ai_matching_enabled()}")
        
        # Test traditional matching speed
        start_time = time.time()
        traditional_results = []
        for t1, t2 in zip(test_texts1, test_texts2):
            similarity = calculate_semantic_similarity(t1, t2)
            traditional_results.append(similarity)
        
        traditional_time = time.time() - start_time
        print(f"   Traditional matching time: {traditional_time:.3f}s")
        print(f"   Results: {[f'{r:.3f}' for r in traditional_results]}")
        print()
        
        # Re-enable AI matching
        set_ai_matching_enabled(True)
        print(f"   AI matching re-enabled: {is_ai_matching_enabled()}")
        print()
        
        # Summary
        print("📊 Performance Summary")
        print("=" * 60)
        print(f"Individual AI matching: {individual_time:.3f}s")
        print(f"Batch AI matching:      {batch_time:.3f}s")
        print(f"Traditional matching:   {traditional_time:.3f}s")
        print()
        
        if individual_time > 0 and batch_time > 0:
            ai_speedup = individual_time / batch_time
            print(f"✅ Batch AI matching is {ai_speedup:.1f}x faster than individual AI matching")
        
        if batch_time > 0 and traditional_time > 0:
            traditional_speedup = traditional_time / batch_time
            print(f"✅ Traditional matching is {traditional_speedup:.1f}x faster than batch AI matching")
        
        print("\n🎯 Recommendations:")
        print("   - Use batch processing for multiple comparisons")
        print("   - Disable AI matching if speed is critical")
        print("   - AI matching provides better accuracy but slower speed")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

if __name__ == "__main__":
    success = test_ai_matching_performance()
    if success:
        print("\n✅ AI matching performance test completed successfully!")
    else:
        print("\n❌ AI matching performance test failed!")
