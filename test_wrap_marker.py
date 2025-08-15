#!/usr/bin/env python3
"""
Test script to test the wrap_with_marker function directly.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

try:
    print("=== TESTING WRAP_WITH_MARKER FUNCTION ===")
    
    # Import the function
    from src.core.formatting.markers import wrap_with_marker
    print("✅ Import successful")
    
    # Test cases
    test_cases = [
        ("TEST BRAND", "LINEAGE"),
        ("CONSTELLATION CANNABIS", "LINEAGE"),
    ]
    
    for test_input, marker in test_cases:
        result = wrap_with_marker(test_input, marker)
        print(f"Input: '{test_input}'")
        print(f"Marker: '{marker}'")
        print(f"Result: '{result}'")
        print("---")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
