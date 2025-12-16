#!/usr/bin/env python3
"""
Complete lineage debugging script to trace the entire flow.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_lineage_color_map():
    """Test the LINEAGE_COLOR_MAP ordering."""
    print("=== TESTING LINEAGE_COLOR_MAP ===")
    
    try:
        from src.core.constants import LINEAGE_COLOR_MAP
        print("LINEAGE_COLOR_MAP keys:", list(LINEAGE_COLOR_MAP.keys()))
        
        # Test if HYBRID/INDICA is in the map
        if "HYBRID/INDICA" in LINEAGE_COLOR_MAP:
            print("✅ HYBRID/INDICA is in LINEAGE_COLOR_MAP")
        else:
            print("❌ HYBRID/INDICA is NOT in LINEAGE_COLOR_MAP")
            
        # Test the ordering issue
        test_lineage = "HYBRID/INDICA"
        lineage_order = list(LINEAGE_COLOR_MAP.keys())
        print(f"Testing '{test_lineage}' against lineage_order...")
        
        if test_lineage in lineage_order:
            print(f"✅ '{test_lineage}' found in lineage_order at index {lineage_order.index(test_lineage)}")
        else:
            print(f"❌ '{test_lineage}' NOT found in lineage_order")
            print(f"Available lineages: {lineage_order}")
            
    except Exception as e:
        print(f"Error testing LINEAGE_COLOR_MAP: {e}")

def test_lineage_normalization():
    """Test lineage normalization functions."""
    print("\n=== TESTING LINEAGE NORMALIZATION ===")
    
    try:
        from src.core.data.excel_processor import normalize_lineage
        
        test_cases = [
            "indica/hybrid",
            "hybrid/indica", 
            "sativa/hybrid",
            "hybrid/sativa",
            "HYBRID/INDICA",
            "HYBRID/SATIVA"
        ]
        
        for test_case in test_cases:
            result = normalize_lineage(test_case)
            print(f"normalize_lineage('{test_case}') -> '{result}'")
            
    except Exception as e:
        print(f"Error testing lineage normalization: {e}")

def test_template_processor_lineage():
    """Test template processor lineage handling."""
    print("\n=== TESTING TEMPLATE PROCESSOR LINEAGE ===")
    
    try:
        # Simulate the template processor logic
        classic_lineages = ["HYBRID/SATIVA", "HYBRID/INDICA", "SATIVA", "INDICA", "HYBRID", "CBD", "MIXED"]
        print(f"classic_lineages: {classic_lineages}")
        
        test_values = [
            "HYBRID/INDICA",
            "HYBRID/SATIVA", 
            "HYBRID",
            "INDICA",
            "SATIVA"
        ]
        
        for test_val in test_values:
            cleaned_lineage_val = test_val.strip()
            result = None
            
            for classic_lineage in classic_lineages:
                if cleaned_lineage_val.upper().startswith(classic_lineage.upper()):
                    result = cleaned_lineage_val[:len(classic_lineage)]
                    print(f"'{test_val}' -> matched '{classic_lineage}' -> result: '{result}'")
                    break
                    
            if result is None:
                print(f"'{test_val}' -> no match found")
                
    except Exception as e:
        print(f"Error testing template processor lineage: {e}")

def test_tag_generator_lineage():
    """Test tag generator lineage handling."""
    print("\n=== TESTING TAG GENERATOR LINEAGE ===")
    
    try:
        from src.core.constants import LINEAGE_COLOR_MAP
        
        def get_lineage(rec):
            possible_fields = ['Lineage', 'lineage', 'Product Lineage', 'ProductLineage', 'Strain Type', 'StrainType']
            lin = ''
            for field in possible_fields:
                if field in rec and rec[field]:
                    lin = str(rec[field]).strip()
                    break
            
            # Normalize the lineage value
            lin = lin.upper().replace('PARA', 'PARAPHERNALIA')
            
            lineage_order = list(LINEAGE_COLOR_MAP.keys())
            return lin if lin in lineage_order else 'MIXED'
        
        # Test records
        test_records = [
            {'Lineage': 'HYBRID/INDICA', 'ProductName': 'Test Product 1'},
            {'lineage': 'HYBRID/SATIVA', 'ProductName': 'Test Product 2'},
            {'Lineage': 'HYBRID', 'ProductName': 'Test Product 3'},
        ]
        
        for record in test_records:
            result = get_lineage(record)
            print(f"Record {record['ProductName']}: Lineage '{record.get('Lineage', record.get('lineage', 'N/A'))}' -> '{result}'")
            
    except Exception as e:
        print(f"Error testing tag generator lineage: {e}")

def test_excel_processor_lineage():
    """Test Excel processor lineage handling."""
    print("\n=== TESTING EXCEL PROCESSOR LINEAGE ===")
    
    try:
        import pandas as pd
        from src.core.data.excel_processor import normalize_lineage
        
        # Simulate Excel processor lineage standardization
        test_data = {
            'Lineage': ['indica/hybrid', 'hybrid/indica', 'sativa/hybrid', 'HYBRID/INDICA']
        }
        df = pd.DataFrame(test_data)
        
        print("Original lineages:", df['Lineage'].tolist())
        
        # Apply the same logic as in excel_processor.py
        df['Lineage'] = (
            df['Lineage']
            .str.lower()
            .replace({
                "indica_hybrid": "HYBRID/INDICA",
                "indica/hybrid": "HYBRID/INDICA",  # FIX: Add forward slash format
                "hybrid/indica": "HYBRID/INDICA",  # FIX: Add reverse format
                "sativa_hybrid": "HYBRID/SATIVA",
                "sativa/hybrid": "HYBRID/SATIVA",  # FIX: Add forward slash format
                "hybrid/sativa": "HYBRID/SATIVA",  # FIX: Add reverse format
                "sativa": "SATIVA",
                "hybrid": "HYBRID",
                "indica": "INDICA",
                "cbd": "CBD"
            })
            .str.upper()
        )
        
        print("Processed lineages:", df['Lineage'].tolist())
        
    except Exception as e:
        print(f"Error testing Excel processor lineage: {e}")

if __name__ == "__main__":
    test_lineage_color_map()
    test_lineage_normalization()
    test_template_processor_lineage()
    test_tag_generator_lineage()
    test_excel_processor_lineage()
    print("\n=== DEBUG COMPLETE ===")
