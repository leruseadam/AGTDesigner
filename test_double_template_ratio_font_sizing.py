#!/usr/bin/env python3
"""
Test script to verify double template ratio font sizing fixes.
This tests that ratio content in double template is no longer pinned to 5pt.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.unified_font_sizing import get_font_size, FONT_SIZING_CONFIG
from docx.shared import Pt

def test_double_template_ratio_font_sizing():
    """Test that double template ratio font sizing is working correctly."""
    
    print("🧪 Testing Double Template Ratio Font Sizing Fixes")
    print("=" * 60)
    
    # Test content samples for ratio
    test_content = [
        # Simple ratios
        ("1:1", "Simple ratio"),
        ("2:1", "Two-part ratio"),
        ("1:1:1", "Three-part ratio"),
        
        # Medium complexity ratios
        ("5:2:1", "Medium ratio"),
        ("10:5:2", "Medium ratio with larger numbers"),
        ("1:1:1:1", "Four-part ratio"),
        
        # Complex ratios
        ("10:5:2:1:1", "Complex ratio with many parts"),
        ("15:10:5:2:1", "Very complex ratio"),
        ("100mg THC 50mg CBD 25mg CBG", "THC/CBD format"),
        
        # Very long content
        ("100mg THC 50mg CBD 25mg CBG 10mg CBN 5mg THCV", "Very long THC/CBD content"),
        ("50mg THC 25mg CBD 15mg CBG 10mg CBN 5mg THCV 2mg CBC", "Extremely long content"),
    ]
    
    print("\n📊 Testing Ratio Font Sizing in Double Template:")
    print("-" * 50)
    
    all_tests_passed = True
    
    for text, description in test_content:
        # Get font size for double template ratio
        font_size = get_font_size(text, 'ratio', 'double', 1.0)
        size_pt = font_size.pt
        
        # Check that font size is reasonable (not too small)
        if size_pt < 7:
            print(f"❌ FAILED: '{text[:30]}...' -> {size_pt}pt (too small!)")
            all_tests_passed = False
        elif size_pt >= 7:
            print(f"✅ PASSED: '{text[:30]}...' -> {size_pt}pt")
        
        # Additional checks for specific content types
        if "mg" in text and size_pt < 7:
            print(f"   ⚠️  Warning: THC/CBD content '{text[:30]}...' got {size_pt}pt (should be >= 7pt)")
            all_tests_passed = False
        
        if text.count(':') >= 3 and size_pt < 8:
            print(f"   ⚠️  Warning: Complex ratio '{text[:30]}...' got {size_pt}pt (should be >= 8pt)")
            all_tests_passed = False
    
    print("\n🔍 Configuration Check:")
    print("-" * 30)
    
    # Check the configuration
    double_config = FONT_SIZING_CONFIG.get('standard', {}).get('double', {}).get('ratio', [])
    print(f"Double template ratio configuration: {double_config}")
    
    if double_config:
        fallback_size = double_config[-1][1] if double_config else 0
        print(f"Fallback size: {fallback_size}pt")
        
        if fallback_size >= 7:
            print("✅ Fallback size is appropriate (>= 7pt)")
        else:
            print("❌ Fallback size is too small (< 7pt)")
            all_tests_passed = False
    
    print("\n📋 Summary:")
    print("-" * 20)
    
    if all_tests_passed:
        print("🎉 All tests PASSED! Double template ratio font sizing is working correctly.")
        print("   - Ratio content is no longer pinned to 5pt")
        print("   - Font sizes are appropriate for readability")
        print("   - Special rules are working correctly")
    else:
        print("❌ Some tests FAILED! Double template ratio font sizing needs attention.")
        print("   - Some ratio content is still getting too small")
        print("   - Check the configuration and special rules")
    
    return all_tests_passed

def test_comparison_with_other_templates():
    """Compare double template ratio font sizing with other templates."""
    
    print("\n🔄 Comparing Ratio Font Sizing Across Templates:")
    print("-" * 55)
    
    test_text = "100mg THC 50mg CBD 25mg CBG 10mg CBN"
    
    templates = ['mini', 'double', 'vertical', 'horizontal']
    
    for template in templates:
        font_size = get_font_size(test_text, 'ratio', template, 1.0)
        size_pt = font_size.pt
        
        status = "✅" if size_pt >= 6 else "❌"
        print(f"{status} {template.capitalize():10} -> {size_pt:2.1f}pt")
    
    print("\n📊 Template Comparison Summary:")
    print("-" * 35)
    print("Double template should have better ratio font sizing than horizontal")
    print("All templates should maintain readability (>= 6pt minimum)")

if __name__ == "__main__":
    print("🚀 Starting Double Template Ratio Font Sizing Tests...\n")
    
    # Run main tests
    main_tests_passed = test_double_template_ratio_font_sizing()
    
    # Run comparison tests
    test_comparison_with_other_templates()
    
    print(f"\n🏁 Test Suite Complete!")
    print(f"Main tests: {'PASSED' if main_tests_passed else 'FAILED'}")
    
    if not main_tests_passed:
        sys.exit(1) 