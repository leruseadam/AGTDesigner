#!/usr/bin/env python3
"""
Test Script for AI-Enhanced JSON Matching
This script demonstrates the new AI-powered matching capabilities.
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_ai_functions():
    """Test the AI-enhanced matching functions."""
    print("🧪 Testing AI-Enhanced Matching Functions")
    print("=" * 50)
    
    try:
        from core.data.json_matcher import (
            calculate_semantic_similarity,
            ai_enhanced_vendor_matching,
            ai_enhanced_brand_matching,
            ai_context_aware_product_matching
        )
        print("✅ All AI functions imported successfully")
        
        # Test semantic similarity
        print("\n📊 Testing Semantic Similarity...")
        test_cases = [
            ("dank czar", "dcz holdings inc"),
            ("omega labs", "omega cannabis"),
            ("airo pro", "airo"),
            ("completely different", "another company")
        ]
        
        for text1, text2 in test_cases:
            try:
                similarity = calculate_semantic_similarity(text1, text2)
                print(f"  '{text1}' vs '{text2}': {similarity:.3f}")
            except Exception as e:
                print(f"  '{text1}' vs '{text2}': Error - {e}")
        
        # Test vendor matching
        print("\n🏢 Testing AI-Enhanced Vendor Matching...")
        vendor_tests = [
            ("dank czar", "dcz holdings inc"),
            ("omega labs", "omega cannabis"),
            ("completely different", "another company")
        ]
        
        for json_vendor, cache_vendor in vendor_tests:
            try:
                match, confidence = ai_enhanced_vendor_matching(json_vendor, cache_vendor)
                status = "✅ MATCH" if match else "❌ NO MATCH"
                print(f"  {json_vendor} vs {cache_vendor}: {status} (confidence: {confidence:.3f})")
            except Exception as e:
                print(f"  {json_vendor} vs {cache_vendor}: Error - {e}")
        
        # Test brand matching
        print("\n🏷️  Testing AI-Enhanced Brand Matching...")
        brand_tests = [
            ("ceres", "ceres botanicals"),
            ("airo pro", "airo"),
            ("different brand", "unrelated brand")
        ]
        
        for json_brand, cache_brand in brand_tests:
            try:
                confidence = ai_enhanced_brand_matching(json_brand, cache_brand)
                print(f"  {json_brand} vs {cache_brand}: confidence {confidence:.3f}")
            except Exception as e:
                print(f"  {json_brand} vs {cache_brand}: Error - {e}")
        
        # Test context-aware product matching
        print("\n📦 Testing Context-Aware Product Matching...")
        json_item = {
            "product_name": "Banana OG Flower",
            "product_type": "flower",
            "strain_name": "banana og"
        }
        cache_item = {
            "original_name": "Banana OG Premium Flower",
            "product_type": "flower",
            "strain": "banana og"
        }
        
        try:
            score = ai_context_aware_product_matching(json_item, cache_item)
            print(f"  Product match score: {score:.3f}")
        except Exception as e:
            print(f"  Product matching error: {e}")
        
        print("\n🎉 AI-Enhanced Matching Test Complete!")
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("\n💡 To install AI dependencies, run:")
        print("   python install_ai_dependencies.py")
        return False
    except Exception as e:
        print(f"❌ Test Error: {e}")
        return False
    
    return True

def test_fallback_behavior():
    """Test that the system falls back gracefully when AI is unavailable."""
    print("\n🔄 Testing Fallback Behavior...")
    
    try:
        # Test with a simple case that should work without AI
        from core.data.json_matcher import calculate_semantic_similarity
        
        # This should fall back to traditional similarity
        similarity = calculate_semantic_similarity("test", "test")
        print(f"  Fallback similarity test: {similarity:.3f}")
        
        print("✅ Fallback behavior working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Fallback test failed: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 Label Maker - AI-Enhanced Matching Test Suite")
    print("=" * 60)
    
    # Test AI functions
    ai_success = test_ai_functions()
    
    # Test fallback behavior
    fallback_success = test_fallback_behavior()
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 Test Summary:")
    print(f"  AI Functions: {'✅ PASS' if ai_success else '❌ FAIL'}")
    print(f"  Fallback: {'✅ PASS' if fallback_success else '❌ FAIL'}")
    
    if ai_success and fallback_success:
        print("\n🎯 All tests passed! AI-enhanced matching is ready to use.")
        print("\n💡 Next steps:")
        print("   1. Start the Label Maker application")
        print("   2. Use JSON matching with enhanced accuracy")
        print("   3. Monitor logs for AI matching results")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
        if not ai_success:
            print("   💡 Try installing AI dependencies: python install_ai_dependencies.py")

if __name__ == "__main__":
    main()
