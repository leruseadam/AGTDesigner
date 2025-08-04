#!/usr/bin/env python3
"""
Test script to verify tincture lineage determination and color application.
"""

def test_tincture_lineage_logic():
    """Test lineage determination logic for tinctures."""
    
    # Test cases based on the logs
    test_cases = [
        {
            'name': 'High CBD Tincture',
            'product_name': 'High CBD Anytime Tincture by Green Revolution - 2000mg CBD / 80mg THC / 800mg CBG',
            'product_type': 'tincture',
            'product_strain': 'CBD Blend',
            'original_lineage': 'GREEN REVOLUTION',
            'expected_lineage': 'CBD'
        },
        {
            'name': 'Indica Tincture',
            'product_name': 'Indica PM Tincture by Ceres - 100mg THC',
            'product_type': 'tincture',
            'product_strain': 'Mixed',
            'original_lineage': 'CERES',
            'expected_lineage': 'MIXED'
        },
        {
            'name': 'Regular Tincture',
            'product_name': 'Sativa Lifestyle Tincture by Fairwinds - 100mg THC',
            'product_type': 'tincture',
            'product_strain': 'Mixed',
            'original_lineage': 'FAIRWINDS MANUFACTURING',
            'expected_lineage': 'MIXED'
        },
        {
            'name': 'CBD Tincture by Name',
            'product_name': 'CBD Wellness Tincture by Brand - 500mg CBD',
            'product_type': 'tincture',
            'product_strain': 'Mixed',
            'original_lineage': 'BRAND',
            'expected_lineage': 'CBD'
        }
    ]
    
    print("Testing tincture lineage determination logic...")
    print("=" * 60)
    
    for test_case in test_cases:
        print(f"\nTest: {test_case['name']}")
        print(f"Product: {test_case['product_name']}")
        print(f"Product Type: {test_case['product_type']}")
        print(f"Product Strain: {test_case['product_strain']}")
        print(f"Original Lineage: {test_case['original_lineage']}")
        
        # Apply the lineage determination logic
        product_type = test_case['product_type']
        product_strain = test_case['product_strain']
        product_name = test_case['product_name']
        
        # Define classic types
        classic_types = [
            "flower", "pre-roll", "infused pre-roll", "concentrate", 
            "solventless concentrate", "vape cartridge"
        ]
        
        if product_type in classic_types:
            final_lineage = test_case['original_lineage']
        else:
            # For non-Classic Types: Determine lineage based on product strain and other indicators
            if product_type == "paraphernalia":
                final_lineage = "PARAPHERNALIA"
            elif product_strain.lower() == "cbd blend":
                final_lineage = "CBD"
            elif product_strain.lower() == "mixed":
                final_lineage = "MIXED"
            elif "CBD" in product_name.upper() or "CBG" in product_name.upper() or "CBN" in product_name.upper() or "CBC" in product_name.upper():
                final_lineage = "CBD"
            else:
                # Default to MIXED for tinctures and other non-classic types
                final_lineage = "MIXED"
        
        print(f"Final Lineage: {final_lineage}")
        print(f"Expected Lineage: {test_case['expected_lineage']}")
        
        if final_lineage == test_case['expected_lineage']:
            print("✅ PASS - Lineage determined correctly")
        else:
            print("❌ FAIL - Lineage mismatch")
    
    print("\n" + "=" * 60)
    print("Test completed!")

def test_color_application():
    """Test that the lineage values will result in proper colors."""
    
    # Define the color mapping from docx_formatting.py
    COLORS = {
        'SATIVA': 'ED4123',
        'INDICA': '9900FF',
        'HYBRID': '009900',
        'HYBRID_INDICA': '9900FF',
        'HYBRID_SATIVA': 'ED4123',
        'CBD': 'F1C232',
        'MIXED': '0021F5',
        'PARA': 'FFC0CB'
    }
    
    print("\nTesting color application for lineage values...")
    print("=" * 60)
    
    test_lineages = ['CBD', 'MIXED', 'SATIVA', 'INDICA', 'HYBRID']
    
    for lineage in test_lineages:
        # Check if the lineage will be recognized by the color system
        text = f"LINEAGE_START{lineage}LINEAGE_END"
        color_hex = None
        
        if "PARAPHERNALIA" in text.upper():
            color_hex = COLORS['PARA']
        elif "HYBRID/INDICA" in text.upper() or "HYBRID INDICA" in text.upper():
            color_hex = COLORS['HYBRID_INDICA']
        elif "HYBRID/SATIVA" in text.upper() or "HYBRID SATIVA" in text.upper():
            color_hex = COLORS['HYBRID_SATIVA']
        elif "SATIVA" in text.upper():
            color_hex = COLORS['SATIVA']
        elif "INDICA" in text.upper():
            color_hex = COLORS['INDICA']
        elif "HYBRID" in text.upper():
            color_hex = COLORS['HYBRID']
        elif "CBD" in text.upper():
            color_hex = COLORS['CBD']
        elif "MIXED" in text.upper():
            color_hex = COLORS['MIXED']
        
        if color_hex:
            print(f"✅ {lineage} -> Color: #{color_hex}")
        else:
            print(f"❌ {lineage} -> No color found")
    
    print("=" * 60)

if __name__ == "__main__":
    test_tincture_lineage_logic()
    test_color_application() 