#!/usr/bin/env python3
"""
Test script to verify JSON matching functionality
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.data.enhanced_json_matcher import ProductTypeSpecificMatcher

def test_json_matching():
    """Test the field-based JSON matching"""
    matcher = ProductTypeSpecificMatcher()

    # Sample JSON product (vape cartridge)
    json_product = {
        "product_name": "Pure Prana Pulse AIO Disposable - Rainbow Belts Live Resin - Hybrid",
        "description": "Live resin disposable vape cartridge",
        "lineage": "Rainbow Belts",
        "weight": "1.0",
        "units": "mL",
        "thc_content": "80",
        "cbd_content": "0"
    }

    # Sample database products
    database_products = [
        {
            "ProductName": "Rainbow Belts Live Resin Cartridge",
            "JSON": {
                "product_name": "Rainbow Belts Live Resin Cartridge",
                "description": "Premium live resin vape cartridge",
                "lineage": "Rainbow Belts",
                "weight": "1.0",
                "units": "mL",
                "thc_content": "80",
                "cbd_content": "0"
            }
        },
        {
            "ProductName": "Blue Dream Pre-Roll",
            "JSON": {
                "product_name": "Blue Dream Pre-Roll",
                "description": "Premium pre-rolled joint",
                "lineage": "Blue Dream",
                "weight": "1.0",
                "units": "g",
                "thc_content": "20",
                "cbd_content": "0"
            }
        }
    ]

    # Test the matching
    matches = matcher._find_json_column_matches(json_product, database_products)

    print(f"Found {len(matches)} matches:")
    for i, match in enumerate(matches):
        print(f"Match {i+1}:")
        print(f"  Score: {match.score:.3f}")
        print(f"  Confidence: {match.confidence:.3f}")
        print(f"  Product: {match.match_data.get('ProductName', 'Unknown')}")
        print(f"  Match factors: {match.match_factors}")
        print()

    return len(matches) > 0

if __name__ == "__main__":
    success = test_json_matching()
    print(f"Test {'PASSED' if success else 'FAILED'}")