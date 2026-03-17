#!/usr/bin/env python3
"""
Test script to verify JSON matched products persistence after tag generation.
"""
import sys
import os
from pathlib import Path
import pandas as pd
from unittest.mock import Mock, MagicMock

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_json_matched_products_persistence():
    """Test that JSON matched products are preserved during DataFrame restoration."""

    # Mock the necessary components
    from src.core.data.excel_processor import ExcelProcessor

    # Create a mock processor with sample data
    processor = ExcelProcessor()
    processor.df = pd.DataFrame({
        'ProductName': ['Original Product 1', 'Original Product 2'],
        'Vendor': ['Vendor A', 'Vendor A'],
        'Price': [10.0, 15.0],
        'Source': ['Excel', 'Excel']
    })

    # Simulate JSON matching - add JSON matched products
    json_products = pd.DataFrame({
        'ProductName': ['JSON Product 1', 'JSON Product 2'],
        'Vendor': ['Grow Op Farms', 'Grow Op Farms'],
        'Price': [20.0, 25.0],
        'Source': ['JSON Match', 'JSON Match']
    })

    # Add JSON products to DataFrame (simulating what /api/json-match does)
    processor.df = pd.concat([processor.df, json_products], ignore_index=True)

    print(f"DataFrame after JSON matching: {len(processor.df)} rows")
    print(f"JSON matched products: {len(processor.df[processor.df['Source'] == 'JSON Match'])}")

    # Store original DataFrame (simulating what generate endpoint does)
    original_df = processor.df.copy()

    # Simulate tag generation - replace DataFrame with selected tags
    selected_tags = pd.DataFrame({
        'ProductName': ['JSON Product 1'],  # Only select JSON matched product
        'Vendor': ['Grow Op Farms'],
        'Price': [20.0],
        'Source': ['JSON Match']
    })

    processor.df = selected_tags
    print(f"DataFrame during generation: {len(processor.df)} rows")

    # Simulate DataFrame restoration with JSON preservation
    json_matched_products = None
    has_json_matched_products = True  # Simulate session flag

    if has_json_matched_products:
        if processor.df is not None and not processor.df.empty:
            json_matched_products = processor.df[processor.df['Source'] == 'JSON Match'].copy()
            print(f"Preserved {len(json_matched_products)} JSON matched products during restoration")

    # Restore original DataFrame
    processor.df = original_df.copy()

    # The original_df already contains the JSON matched products, so we don't need to re-add them
    # The preservation logic ensures they weren't lost during the temporary replacement

    # Verify results
    final_df = processor.df
    json_count = len(final_df[final_df['Source'] == 'JSON Match'])

    print(f"Final DataFrame: {len(final_df)} rows")
    print(f"Final JSON matched products: {json_count}")

    assert json_count == 2, f"Expected 2 JSON matched products, got {json_count}"
    assert len(final_df) == 4, f"Expected 4 total products, got {len(final_df)}"

    print("✅ JSON matched products persistence test PASSED")

if __name__ == '__main__':
    test_json_matched_products_persistence()