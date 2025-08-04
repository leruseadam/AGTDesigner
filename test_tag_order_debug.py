#!/usr/bin/env python3
"""
Debug script to test tag order preservation from drag and drop to final output.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.data.excel_processor import ExcelProcessor
import tempfile

def test_tag_order_preservation():
    """Test that tag order is preserved from selection to output."""
    
    print("Testing Tag Order Preservation")
    print("=" * 40)
    
    # Create a test Excel processor
    processor = ExcelProcessor()
    
    # Create test data with known order
    test_data = [
        {'ProductName': 'Tag A', 'Product Brand': 'Brand A', 'Lineage': 'SATIVA', 'Price': '10.00'},
        {'ProductName': 'Tag B', 'Product Brand': 'Brand B', 'Lineage': 'INDICA', 'Price': '15.00'},
        {'ProductName': 'Tag C', 'Product Brand': 'Brand C', 'Lineage': 'HYBRID', 'Price': '12.00'},
        {'ProductName': 'Tag D', 'Product Brand': 'Brand D', 'Lineage': 'CBD', 'Price': '20.00'},
        {'ProductName': 'Tag E', 'Product Brand': 'Brand E', 'Lineage': 'MIXED', 'Price': '8.00'},
    ]
    
    # Create a temporary Excel file
    import pandas as pd
    df = pd.DataFrame(test_data)
    
    # Save to temporary file
    temp_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
    df.to_excel(temp_file.name, index=False)
    temp_file.close()
    
    print(f"Created test file: {temp_file.name}")
    print(f"Test data: {test_data}")
    
    # Load the file
    success = processor.load_file(temp_file.name)
    if not success:
        print("❌ Failed to load test file")
        return
    
    print("✅ File loaded successfully")
    
    # Test 1: Set selected tags in a specific order (simulating drag and drop)
    selected_order = ['Tag C', 'Tag A', 'Tag E', 'Tag B', 'Tag D']
    processor.selected_tags = selected_order
    
    print(f"\n1. Set selected tags in order: {selected_order}")
    
    # Test 2: Get selected records and check order
    records = processor.get_selected_records('vertical')
    
    print(f"\n2. Retrieved {len(records)} records from get_selected_records")
    
    # Extract product names from records
    record_names = [record.get('ProductName', '') for record in records]
    print(f"Record names in output order: {record_names}")
    
    # Check if order matches
    if record_names == selected_order:
        print("✅ Order preserved correctly!")
    else:
        print("❌ Order mismatch!")
        print(f"Expected: {selected_order}")
        print(f"Got: {record_names}")
    
    # Test 3: Check the sorting logic
    print(f"\n3. Debugging sorting logic:")
    
    # Get the lineage order used in sorting
    lineage_order = [
        'SATIVA', 'INDICA', 'HYBRID', 'HYBRID/SATIVA',
        'HYBRID/INDICA', 'CBD', 'MIXED', 'PARAPHERNALIA'
    ]
    
    def get_lineage(rec):
        lineage = str(rec.get('Lineage', '')).upper()
        return lineage if lineage in lineage_order else 'MIXED'
    
    def get_selected_order(rec):
        product_name = rec.get('ProductName', '').strip()
        try:
            return selected_order.index(product_name)
        except ValueError:
            return len(selected_order)
    
    # Show sorting details for each record
    for i, record in enumerate(records):
        product_name = record.get('ProductName', '')
        lineage = get_lineage(record)
        selected_index = get_selected_order(record)
        lineage_index = lineage_order.index(lineage)
        
        print(f"  Record {i+1}: '{product_name}'")
        print(f"    - Selected order index: {selected_index}")
        print(f"    - Lineage: {lineage} (index: {lineage_index})")
        print(f"    - Sort key: ({selected_index}, {lineage_index})")
    
    # Clean up
    os.unlink(temp_file.name)
    
    print(f"\n" + "=" * 40)
    print("Test completed!")

if __name__ == "__main__":
    test_tag_order_preservation() 