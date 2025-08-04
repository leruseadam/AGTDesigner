#!/usr/bin/env python3
"""
Test script to demonstrate the UI data validation fix.

This test shows how the application now validates that selected tags
actually exist in the loaded Excel data, preventing the error where
"Medically Compliant" tags were selected but not found in the backend.
"""

import json
import requests
from typing import List, Dict

def test_ui_data_validation():
    """Test the UI data validation fix."""
    
    # Simulate the backend data (Excel file content)
    excel_data = [
        {"Product Name*": "Acapulco Gold Wax - 1g", "Product Brand": "1555 Industrial LLC", "Product Type*": "Concentrate", "Lineage": "SATIVA"},
        {"Product Name*": "Blue Dream Wax - 1g", "Product Brand": "1555 Industrial LLC", "Product Type*": "Concentrate", "Lineage": "HYBRID"},
        {"Product Name*": "Forbidden Fruit Wax - 1g", "Product Brand": "Hustler's Ambition", "Product Type*": "Concentrate", "Lineage": "INDICA"},
        {"Product Name*": "Birthday Cake - 14g", "Product Brand": "Hustler's Ambition", "Product Type*": "Flower", "Lineage": "HYBRID/INDICA"},
    ]
    
    # Simulate frontend selected tags (including invalid ones)
    frontend_selected_tags = [
        "Acapulco Gold Wax - 1g",  # Valid - exists in Excel
        "Blue Dream Wax - 1g",     # Valid - exists in Excel
        "Medically Compliant - Dank Czar Rosin All-In-One - GMO - 1g",  # Invalid - not in Excel
        "Medically Compliant - Dank Czar Rosin All-In-One - Grape Gas - 1g",  # Invalid - not in Excel
        "Forbidden Fruit Wax - 1g",  # Valid - exists in Excel
    ]
    
    print("=== UI Data Validation Test ===\n")
    print("Backend Excel Data:")
    for i, item in enumerate(excel_data, 1):
        print(f"  {i}. {item['Product Name*']}")
    
    print(f"\nFrontend Selected Tags ({len(frontend_selected_tags)} total):")
    for i, tag in enumerate(frontend_selected_tags, 1):
        print(f"  {i}. {tag}")
    
    # Simulate the validation logic
    available_product_names = {item['Product Name*'].lower().strip() for item in excel_data}
    
    valid_selected_tags = []
    invalid_selected_tags = []
    
    for tag in frontend_selected_tags:
        tag_lower = tag.strip().lower()
        if tag_lower in available_product_names:
            valid_selected_tags.append(tag.strip())
        else:
            invalid_selected_tags.append(tag.strip())
    
    print(f"\n=== Validation Results ===")
    print(f"Valid tags ({len(valid_selected_tags)}):")
    for tag in valid_selected_tags:
        print(f"  ✓ {tag}")
    
    print(f"\nInvalid tags ({len(invalid_selected_tags)}):")
    for tag in invalid_selected_tags:
        print(f"  ✗ {tag}")
    
    print(f"\n=== Summary ===")
    print(f"Total selected: {len(frontend_selected_tags)}")
    print(f"Valid: {len(valid_selected_tags)}")
    print(f"Invalid: {len(invalid_selected_tags)}")
    
    if invalid_selected_tags:
        print(f"\n⚠️  Warning: {len(invalid_selected_tags)} tags were removed because they don't exist in the current Excel data.")
        print("   These tags were likely from JSON matching but don't exist in the loaded file.")
    
    if not valid_selected_tags:
        print(f"\n❌ Error: No valid tags selected. All {len(invalid_selected_tags)} tags do not exist in the loaded data.")
        print("   Please ensure you have selected tags that exist in the current Excel file.")
    else:
        print(f"\n✅ Success: {len(valid_selected_tags)} valid tags can be processed for label generation.")
    
    return valid_selected_tags, invalid_selected_tags

def test_backend_validation():
    """Test the backend validation logic."""
    
    print("\n=== Backend Validation Test ===")
    
    # Simulate the backend validation in the generate labels endpoint
    excel_data = [
        {"Product Name*": "Acapulco Gold Wax - 1g"},
        {"Product Name*": "Blue Dream Wax - 1g"},
        {"Product Name*": "Forbidden Fruit Wax - 1g"},
    ]
    
    selected_tags_from_request = [
        "Acapulco Gold Wax - 1g",
        "Medically Compliant - Dank Czar Rosin All-In-One - GMO - 1g",
        "Blue Dream Wax - 1g",
    ]
    
    # Backend validation logic
    available_product_names = set()
    if excel_data and 'Product Name*' in excel_data[0]:
        available_product_names = {item['Product Name*'].lower().strip() for item in excel_data}
    
    valid_selected_tags = []
    invalid_selected_tags = []
    
    for tag in selected_tags_from_request:
        tag_lower = tag.strip().lower()
        if tag_lower in available_product_names:
            valid_selected_tags.append(tag.strip())
        else:
            invalid_selected_tags.append(tag.strip())
    
    print(f"Available product names in Excel: {list(available_product_names)}")
    print(f"Selected tags from request: {selected_tags_from_request}")
    print(f"Valid tags: {valid_selected_tags}")
    print(f"Invalid tags: {invalid_selected_tags}")
    
    if invalid_selected_tags:
        print(f"⚠️  Backend would remove {len(invalid_selected_tags)} invalid tags")
        if not valid_selected_tags:
            print("❌ Backend would return error: No valid tags selected")
        else:
            print(f"✅ Backend would process {len(valid_selected_tags)} valid tags")

def test_frontend_validation():
    """Test the frontend validation logic."""
    
    print("\n=== Frontend Validation Test ===")
    
    # Simulate frontend state
    original_tags = [
        {"Product Name*": "Acapulco Gold Wax - 1g"},
        {"Product Name*": "Blue Dream Wax - 1g"},
        {"Product Name*": "Forbidden Fruit Wax - 1g"},
    ]
    
    persistent_selected_tags = {
        "Acapulco Gold Wax - 1g",
        "Medically Compliant - Dank Czar Rosin All-In-One - GMO - 1g",
        "Blue Dream Wax - 1g",
    }
    
    # Frontend validation logic
    valid_product_names = {tag['Product Name*'] for tag in original_tags}
    invalid_tags = []
    valid_tags = []
    
    for tag_name in persistent_selected_tags:
        if tag_name in valid_product_names:
            valid_tags.append(tag_name)
        else:
            invalid_tags.append(tag_name)
    
    print(f"Original tags (Excel data): {[tag['Product Name*'] for tag in original_tags]}")
    print(f"Persistent selected tags: {list(persistent_selected_tags)}")
    print(f"Valid tags: {valid_tags}")
    print(f"Invalid tags: {invalid_tags}")
    
    if invalid_tags:
        print(f"⚠️  Frontend would remove {len(invalid_tags)} invalid tags from selection")
        print(f"✅ Frontend would keep {len(valid_tags)} valid tags")

if __name__ == "__main__":
    print("Testing UI Data Validation Fix")
    print("=" * 50)
    
    # Run all tests
    test_ui_data_validation()
    test_backend_validation()
    test_frontend_validation()
    
    print("\n" + "=" * 50)
    print("Test completed!")
    print("\nThis demonstrates how the application now properly validates")
    print("that selected tags exist in the loaded Excel data, preventing")
    print("the error where 'Medically Compliant' tags were selected but")
    print("not found in the backend.") 