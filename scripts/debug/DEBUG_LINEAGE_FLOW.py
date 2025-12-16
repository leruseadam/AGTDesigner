#!/usr/bin/env python3
"""
Debug script to test the lineage flow from frontend to backend to generation.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_lineage_normalization():
    """Test the lineage normalization functions."""
    print("=== TESTING LINEAGE NORMALIZATION ===")
    
    # Test the normalize_lineage function
    from src.core.data.excel_processor import normalize_lineage
    
    test_cases = [
        "indica/hybrid",
        "hybrid/indica", 
        "sativa/hybrid",
        "hybrid/sativa",
        "indica_hybrid",
        "sativa_hybrid",
        "hybrid",
        "indica",
        "sativa"
    ]
    
    for test_case in test_cases:
        result = normalize_lineage(test_case)
        print(f"Input: '{test_case}' -> Output: '{result}'")

def test_excel_processor_lineage():
    """Test Excel processor lineage handling."""
    print("\n=== TESTING EXCEL PROCESSOR LINEAGE ===")
    
    try:
        from src.core.data.excel_processor import ExcelProcessor
        
        # Create a test processor
        processor = ExcelProcessor()
        
        # Test lineage mapping
        print("Testing lineage mapping in ExcelProcessor...")
        
        # Simulate some test data
        import pandas as pd
        test_data = {
            'Product Name*': ['Test Product 1', 'Test Product 2'],
            'Lineage': ['indica/hybrid', 'sativa/hybrid']
        }
        df = pd.DataFrame(test_data)
        
        # Apply lineage normalization
        if 'Lineage' in df.columns:
            df['Lineage'] = df['Lineage'].apply(normalize_lineage)
            print(f"Normalized lineages: {df['Lineage'].tolist()}")
        
    except Exception as e:
        print(f"Error testing ExcelProcessor: {e}")

def test_backend_lineage_processing():
    """Test backend lineage processing logic."""
    print("\n=== TESTING BACKEND LINEAGE PROCESSING ===")
    
    # Simulate the backend logic for processing full tag objects
    selected_tags_from_request = [
        {
            'Product Name*': 'Test Product 1',
            'lineage': 'HYBRID/INDICA',
            'Lineage': 'HYBRID/INDICA'
        },
        {
            'Product Name*': 'Test Product 2', 
            'lineage': 'HYBRID/SATIVA',
            'Lineage': 'HYBRID/SATIVA'
        }
    ]
    
    print("Simulating backend processing of full tag objects...")
    
    if selected_tags_from_request and isinstance(selected_tags_from_request[0], dict):
        print("✅ Detected full tag objects format")
        tag_names = []
        lineage_updates = {}
        
        for tag_obj in selected_tags_from_request:
            tag_name = tag_obj.get('Product Name*') or tag_obj.get('ProductName', '')
            if tag_name:
                tag_names.append(tag_name)
                
                updated_lineage = tag_obj.get('lineage') or tag_obj.get('Lineage', '')
                if updated_lineage:
                    lineage_updates[tag_name] = updated_lineage
                    print(f"✅ Tag '{tag_name}' has updated lineage: '{updated_lineage}'")
        
        print(f"Tag names: {tag_names}")
        print(f"Lineage updates: {lineage_updates}")
    else:
        print("❌ Expected full tag objects format")

if __name__ == "__main__":
    test_lineage_normalization()
    test_excel_processor_lineage()
    test_backend_lineage_processing()
    print("\n=== DEBUG COMPLETE ===")
