#!/usr/bin/env python3
"""
Test script to debug CBD classic type styling issues.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_cbd_styling_issue():
    """Test what might be causing CBD classic types to get non-classic styling."""
    print("=== DEBUGGING CBD CLASSIC TYPE STYLING ===")
    
    # Import required modules
    from src.core.constants import CLASSIC_TYPES
    
    # Test scenarios that might be causing the issue
    test_cases = [
        {
            'product_name': 'CBD Flower - Charlotte\'s Web',
            'product_type': 'Flower',
            'lineage': 'CBD',
            'product_strain': 'Charlotte\'s Web',
            'description': 'CBD Flower - Charlotte\'s Web 3.5g'
        },
        {
            'product_name': 'CBD Pre-Roll',
            'product_type': 'Pre-roll', 
            'lineage': 'CBD',
            'product_strain': 'CBD Blend',
            'description': 'CBD Pre-Roll 1g'
        },
        {
            'product_name': 'THC Flower - Blue Dream',
            'product_type': 'Flower',
            'lineage': 'HYBRID',
            'product_strain': 'Blue Dream',
            'description': 'THC Flower - Blue Dream 3.5g'
        }
    ]
    
    print("Testing potential styling issues:")
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n  Test Case {i}: {case['product_name']}")
        
        # Check if product type is classic
        is_classic_type = case['product_type'].lower() in [ct.lower() for ct in CLASSIC_TYPES]
        print(f"    Product Type: {case['product_type']} -> {'Classic' if is_classic_type else 'Non-Classic'}")
        
        # Check lineage
        print(f"    Lineage: {case['lineage']}")
        
        # Check product strain
        print(f"    Product Strain: {case['product_strain']}")
        
        # Simulate the styling decision logic
        if is_classic_type:
            # Classic types should show lineage
            expected_styling = "classic (shows lineage)"
            expected_content = case['lineage']
            expected_color = get_expected_color(case['lineage'])
        else:
            # Non-classic types should show brand
            expected_styling = "non-classic (shows brand)"
            expected_content = case['product_strain'] or "BRAND"
            expected_color = "blue (MIXED)"
        
        print(f"    Expected Styling: {expected_styling}")
        print(f"    Expected Content: {expected_content}")
        print(f"    Expected Color: {expected_color}")
        
        # Check for potential issues
        issues = []
        
        # Issue 1: Product strain contains "CBD Blend" which might trigger non-classic logic
        if 'CBD Blend' in case.get('product_strain', ''):
            issues.append("Product strain contains 'CBD Blend' - might trigger non-classic logic")
        
        # Issue 2: Lineage is CBD but product might be processed as edible-like
        if case['lineage'] == 'CBD' and any(word in case['product_name'].lower() for word in ['cbd', 'hemp']):
            issues.append("CBD product - might be misclassified as edible-like")
        
        # Issue 3: Description contains CBD which might affect processing
        if 'CBD' in case.get('description', ''):
            issues.append("Description contains CBD - might affect lineage processing")
        
        if issues:
            print(f"    ⚠️  Potential Issues:")
            for issue in issues:
                print(f"      - {issue}")
        else:
            print(f"    ✅ No obvious issues detected")

def get_expected_color(lineage):
    """Get the expected color for a lineage."""
    color_map = {
        'SATIVA': 'red',
        'INDICA': 'purple', 
        'HYBRID': 'green',
        'HYBRID/SATIVA': 'red',
        'HYBRID/INDICA': 'purple',
        'CBD': 'yellow',
        'MIXED': 'blue',
        'PARAPHERNALIA': 'pink'
    }
    return color_map.get(lineage, 'unknown')

def test_color_application_logic():
    """Test the color application logic for CBD."""
    print("\n=== TESTING COLOR APPLICATION LOGIC ===")
    
    # Simulate the color application logic from docx_formatting.py
    def simulate_color_application(cell_text):
        """Simulate how colors are applied to cell text."""
        text = cell_text.upper()
        
        # Remove markers (simulate the actual logic)
        for marker in ["LINEAGE_START", "LINEAGE_END", "PRODUCTSTRAIN_START", "PRODUCTSTRAIN_END", "PRODUCTBRAND_CENTER_START", "PRODUCTBRAND_CENTER_END"]:
            text = text.replace(marker, "")
        text = text.strip()
        
        # Apply coloring logic (from docx_formatting.py)
        if "PARAPHERNALIA" in text:
            return "pink"
        elif "HYBRID/INDICA" in text or "HYBRID INDICA" in text:
            return "purple"
        elif "HYBRID/SATIVA" in text or "HYBRID SATIVA" in text:
            return "red"
        elif "SATIVA" in text:
            return "red"
        elif "INDICA" in text:
            return "purple"
        elif "HYBRID" in text:
            return "green"
        elif "CBD" in text or "CBD_BLEND" in text:
            return "yellow"
        elif "CBD BLEND" in text:
            return "yellow"
        elif "MIXED" in text:
            return "blue"
        else:
            return "no color"
    
    test_texts = [
        "LINEAGE_STARTCBDLINEAGE_END",
        "CBD",
        "CBD BLEND",
        "HYBRID",
        "SATIVA",
        "PRODUCTBRAND_CENTER_STARTCBD BLENDPRODUCTBRAND_CENTER_END",
        "Charlotte's Web CBD",
        "MIXED"
    ]
    
    print("Color application simulation:")
    for text in test_texts:
        color = simulate_color_application(text)
        print(f"  '{text}' -> {color}")

if __name__ == "__main__":
    test_cbd_styling_issue()
    test_color_application_logic()
    print("\n=== CBD STYLING DEBUG COMPLETE ===")
