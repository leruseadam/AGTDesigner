#!/usr/bin/env python3
"""Debug script to identify where the 26pt vertical price value is coming from."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def debug_vertical_price_issue():
    """Debug the vertical price font sizing issue."""
    
    print("🔍 Debugging Vertical Price Font Sizing Issue")
    print("=" * 60)
    
    # Test 1: Check unified font sizing
    print("\n📊 Test 1: Unified Font Sizing")
    print("-" * 30)
    try:
        from src.core.generation.unified_font_sizing import get_font_size
        unified_result = get_font_size("$29.99", "price", "vertical", 1.0)
        print(f"✅ Unified system result: {unified_result}pt")
    except Exception as e:
        print(f"❌ Unified system error: {e}")
    
    # Test 2: Check old font sizing
    print("\n📊 Test 2: Old Font Sizing")
    print("-" * 30)
    try:
        from src.core.generation.font_sizing import get_thresholded_font_size_price
        old_result = get_thresholded_font_size_price("$29.99", "vertical", 1.0)
        print(f"✅ Old system result: {old_result}pt")
    except Exception as e:
        print(f"❌ Old system error: {e}")
    
    # Test 3: Check app's font sizing function
    print("\n📊 Test 3: App's Font Sizing Function")
    print("-" * 30)
    try:
        from app import _get_template_specific_font_size
        app_result = _get_template_specific_font_size("$29.99", "price", "vertical", 1.0)
        print(f"✅ App function result: {app_result}pt")
    except Exception as e:
        print(f"❌ App function error: {e}")
    
    # Test 4: Check if there are any other font sizing functions
    print("\n📊 Test 4: Check for other font sizing functions")
    print("-" * 30)
    try:
        import src.core.generation.font_sizing as old_font_sizing
        import src.core.generation.unified_font_sizing as new_font_sizing
        
        print("Old font sizing functions:")
        for attr in dir(old_font_sizing):
            if 'font' in attr.lower() and 'size' in attr.lower():
                print(f"  - {attr}")
        
        print("\nNew font sizing functions:")
        for attr in dir(new_font_sizing):
            if 'font' in attr.lower() and 'size' in attr.lower():
                print(f"  - {attr}")
                
    except Exception as e:
        print(f"❌ Error checking functions: {e}")
    
    # Test 5: Check configuration
    print("\n📊 Test 5: Check Font Sizing Configuration")
    print("-" * 30)
    try:
        from src.core.generation.unified_font_sizing import FONT_SIZING_CONFIG
        vertical_price_config = FONT_SIZING_CONFIG.get('vertical', {}).get('price', [])
        print(f"✅ Vertical price config: {vertical_price_config}")
    except Exception as e:
        print(f"❌ Config error: {e}")
    
    # Test 6: Check if there are any cached imports
    print("\n📊 Test 6: Check for cached imports")
    print("-" * 30)
    try:
        import sys
        print("Python path:")
        for path in sys.path[:5]:  # Show first 5 paths
            print(f"  - {path}")
        
        print("\nLoaded modules containing 'font':")
        for module_name in sys.modules:
            if 'font' in module_name.lower():
                print(f"  - {module_name}")
                
    except Exception as e:
        print(f"❌ Error checking imports: {e}")

if __name__ == "__main__":
    debug_vertical_price_issue() 