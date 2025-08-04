#!/usr/bin/env python3
"""Simple test to isolate the font sizing issue."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.unified_font_sizing import get_font_size, FONT_SIZING_CONFIG
from docx.shared import Pt

def test_simple_font_sizing():
    """Test simple font sizing to isolate the issue."""
    
    print("🔍 Simple Font Sizing Test")
    print("=" * 40)
    
    # Test 1: Direct call to get_font_size
    print("\n📊 Test 1: Direct get_font_size call")
    print("-" * 30)
    try:
        result = get_font_size("$29.99", "price", "vertical", 1.0)
        print(f"✅ Direct result: {result}")
        print(f"✅ Result type: {type(result)}")
        print(f"✅ Result value: {result.pt if hasattr(result, 'pt') else result}")
        print(f"✅ Is Pt object: {isinstance(result, Pt)}")
    except Exception as e:
        print(f"❌ Direct call error: {e}")
    
    # Test 2: Check configuration
    print("\n📊 Test 2: Check Configuration")
    print("-" * 30)
    try:
        config = FONT_SIZING_CONFIG.get('standard', {}).get('vertical', {}).get('price', [])
        print(f"✅ Vertical price config: {config}")
    except Exception as e:
        print(f"❌ Config error: {e}")
    
    # Test 3: Test with different scale factors
    print("\n📊 Test 3: Test with different scale factors")
    print("-" * 30)
    try:
        for scale in [0.5, 1.0, 1.5, 2.0]:
            result = get_font_size("$29.99", "price", "vertical", scale)
            print(f"✅ Scale {scale}: {result} (type: {type(result)})")
            if hasattr(result, 'pt'):
                print(f"   Value: {result.pt}pt")
    except Exception as e:
        print(f"❌ Scale test error: {e}")
    
    # Test 4: Test with different prices
    print("\n📊 Test 4: Test with different prices")
    print("-" * 30)
    try:
        for price in ["$9.99", "$19.99", "$29.99", "$129.99", "$1,299.99"]:
            result = get_font_size(price, "price", "vertical", 1.0)
            print(f"✅ Price '{price}': {result} (type: {type(result)})")
            if hasattr(result, 'pt'):
                print(f"   Value: {result.pt}pt")
    except Exception as e:
        print(f"❌ Price test error: {e}")

if __name__ == "__main__":
    test_simple_font_sizing() 