#!/usr/bin/env python3
"""
Test script to test the unwrap_marker function directly.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

try:
    print("=== TESTING UNWRAP_MARKER FUNCTION ===")
    
    # Import the function
    from src.core.formatting.markers import unwrap_marker
    print("✅ Import successful")
    
    # Test cases
    test_cases = [
        ("PRODUCTBRAND_CENTER_STARTTEST BRANDPRODUCTBRAND_CENTER_END", "PRODUCTBRAND_CENTER"),
        ("LINEAGE_START PRODUCTBRAND_CENTER_STARTTEST BRANDPRODUCTBRAND_CENTER_ENDLINEAGE_END", "LINEAGE"),
        ("PRODUCTBRAND_CENTER_STARTTEST BRANDPRODUCTBRAND_CENTER_END", "LINEAGE"),
        ("LINEAGE_START PRODUCTBRAND_CENTER_STARTTEST BRANDPRODUCTBRAND_CENTER_ENDLINEAGE_END", "PRODUCTBRAND_CENTER"),
    ]
    
    for test_input, marker in test_cases:
        result = unwrap_marker(test_input, marker)
        print(f"Input: '{test_input}'")
        print(f"Marker: '{marker}'")
        print(f"Result: '{result}'")
        print("---")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
