#!/usr/bin/env python3
"""Test to directly call the app function and see what it returns."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from docx.shared import Pt

def test_app_function_direct():
    """Test the app function directly."""
    
    print("🔍 Direct App Function Test")
    print("=" * 40)
    
    # Test 1: Import and call the app function directly
    print("\n📊 Test 1: Direct app function call")
    print("-" * 30)
    try:
        from app import _get_template_specific_font_size
        
        result = _get_template_specific_font_size("$29.99", "PRICE", "vertical", 1.0)
        print(f"✅ App function result: {result}")
        print(f"✅ Result type: {type(result)}")
        print(f"✅ Result value: {result.pt if hasattr(result, 'pt') else result}")
        print(f"✅ Is Pt object: {isinstance(result, Pt)}")
    except Exception as e:
        print(f"❌ App function error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Compare with unified function
    print("\n📊 Test 2: Compare with unified function")
    print("-" * 30)
    try:
        from src.core.generation.unified_font_sizing import get_font_size
        
        unified_result = get_font_size("$29.99", "price", "vertical", 1.0)
        print(f"✅ Unified function result: {unified_result}")
        print(f"✅ Unified result type: {type(unified_result)}")
        print(f"✅ Unified result value: {unified_result.pt if hasattr(unified_result, 'pt') else unified_result}")
        print(f"✅ Unified is Pt object: {isinstance(unified_result, Pt)}")
    except Exception as e:
        print(f"❌ Unified function error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_app_function_direct() 