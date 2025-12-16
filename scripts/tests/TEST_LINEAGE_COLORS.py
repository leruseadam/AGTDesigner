#!/usr/bin/env python3
"""
Test script to verify lineage color mapping is working correctly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_lineage_color_mapping():
    """Test the lineage color mapping."""
    print("=== TESTING LINEAGE COLOR MAPPING ===")
    
    try:
        from src.core.generation.docx_formatting import COLORS
        
        print("COLORS mapping:")
        for lineage, color in COLORS.items():
            print(f"  {lineage}: #{color}")
        
        # Test specific mappings
        test_cases = [
            ('HYBRID/INDICA', '9900FF', 'Purple (like INDICA)'),
            ('HYBRID/SATIVA', 'ED4123', 'Red (like SATIVA)'),
            ('HYBRID', '009900', 'Green'),
            ('INDICA', '9900FF', 'Purple'),
            ('SATIVA', 'ED4123', 'Red')
        ]
        
        print("\nTesting color mappings:")
        for lineage, expected_color, description in test_cases:
            actual_color = COLORS.get(lineage, 'NOT_FOUND')
            if actual_color == expected_color:
                print(f"✅ {lineage}: #{actual_color} - {description}")
            else:
                print(f"❌ {lineage}: Expected #{expected_color}, got #{actual_color}")
                
    except Exception as e:
        print(f"Error testing color mapping: {e}")

def test_color_logic():
    """Test the color matching logic."""
    print("\n=== TESTING COLOR MATCHING LOGIC ===")
    
    try:
        from src.core.generation.docx_formatting import COLORS
        
        def get_color_for_text(text):
            """Simulate the color matching logic."""
            text = text.upper().strip()
            
            # Remove markers
            for marker in ["LINEAGE_START", "LINEAGE_END", "PRODUCTSTRAIN_START", "PRODUCTSTRAIN_END", "PRODUCTBRAND_CENTER_START", "PRODUCTBRAND_CENTER_END"]:
                text = text.replace(marker, "")
            text = text.strip()
            
            # Apply lineage coloring logic
            if "PARAPHERNALIA" in text:
                return COLORS['PARA']
            elif "HYBRID/INDICA" in text or "HYBRID INDICA" in text:
                return COLORS['HYBRID/INDICA']
            elif "HYBRID/SATIVA" in text or "HYBRID SATIVA" in text:
                return COLORS['HYBRID/SATIVA']
            elif "SATIVA" in text:
                return COLORS['SATIVA']
            elif "INDICA" in text:
                return COLORS['INDICA']
            elif "HYBRID" in text:
                return COLORS['HYBRID']
            elif "CBD" in text or "CBD_BLEND" in text:
                return COLORS['CBD']
            elif "MIXED" in text:
                return COLORS['MIXED']
            else:
                return None
        
        # Test cases
        test_texts = [
            ("HYBRID/INDICA", "9900FF", "Purple"),
            ("HYBRID/SATIVA", "ED4123", "Red"),
            ("HYBRID", "009900", "Green"),
            ("INDICA", "9900FF", "Purple"),
            ("SATIVA", "ED4123", "Red"),
            ("LINEAGE_STARTHYBRID/INDICALINEAGE_END", "9900FF", "Purple (with markers)"),
            ("HYBRID INDICA", "9900FF", "Purple (with space)"),
            ("HYBRID SATIVA", "ED4123", "Red (with space)")
        ]
        
        print("Testing color matching logic:")
        for text, expected_color, description in test_texts:
            actual_color = get_color_for_text(text)
            if actual_color == expected_color:
                print(f"✅ '{text}' -> #{actual_color} - {description}")
            else:
                print(f"❌ '{text}' -> Expected #{expected_color}, got #{actual_color}")
                
    except Exception as e:
        print(f"Error testing color logic: {e}")

if __name__ == "__main__":
    test_lineage_color_mapping()
    test_color_logic()
    print("\n=== COLOR TEST COMPLETE ===")
