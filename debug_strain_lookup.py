#!/usr/bin/env python3
"""
Debug script to check strain database lookup.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.data.product_database import get_product_database

def debug_strain_lookup():
    """Debug strain lookup in database."""
    print("Debugging Strain Database Lookup")
    
    product_db = get_product_database()
    
    # Test strain names
    test_strains = [
        "Acapulco Gold",
        "acapulco gold", 
        "ACAPULCO GOLD",
        "AcapulcoGold",
        "Acapulco_Gold"
    ]
    
    print("1. Checking strain database:")
    for strain_name in test_strains:
        print(f"\n   Testing strain name: '{strain_name}'")
        try:
            strain_info = product_db.get_strain_info(strain_name)
            if strain_info:
                print(f"   ✓ Found strain: {strain_info}")
                print(f"   - ID: {strain_info.get('id')}")
                print(f"   - Name: {strain_info.get('strain_name')}")
                print(f"   - Normalized: {strain_info.get('normalized_name')}")
                print(f"   - Canonical Lineage: {strain_info.get('canonical_lineage')}")
                print(f"   - Sovereign Lineage: {strain_info.get('sovereign_lineage')}")
            else:
                print(f"   ✗ Strain not found")
        except Exception as e:
            print(f"   ✗ Error looking up strain: {e}")
    
    print("\n2. Checking all strains in database:")
    try:
        all_strains = product_db.get_all_strains()
        print(f"   Total strains in database: {len(all_strains)}")
        
        # Look for strains containing "acapulco"
        acapulco_strains = [s for s in all_strains if 'acapulco' in s.lower()]
        print(f"   Strains containing 'acapulco': {acapulco_strains}")
        
        # Look for strains containing "gold"
        gold_strains = [s for s in all_strains if 'gold' in s.lower()]
        print(f"   Strains containing 'gold': {gold_strains[:10]}...")  # Show first 10
        
    except Exception as e:
        print(f"   ✗ Error getting all strains: {e}")
    
    print("\n3. Checking strain lineage map:")
    try:
        lineage_map = product_db.get_strain_lineage_map()
        print(f"   Total strains in lineage map: {len(lineage_map)}")
        
        # Look for acapulco strains in lineage map
        acapulco_lineages = {k: v for k, v in lineage_map.items() if 'acapulco' in k.lower()}
        print(f"   Strains with 'acapulco' in lineage map: {acapulco_lineages}")
        
    except Exception as e:
        print(f"   ✗ Error getting lineage map: {e}")

if __name__ == "__main__":
    debug_strain_lookup() 