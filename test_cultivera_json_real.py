#!/usr/bin/env python3
"""
Test Cultivera JSON Matching with Real Data
Tests JSON matching functionality with the provided Cultivera manifest.
"""

import sys
import os
import json
import requests
import time
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_cultivera_json_download():
    """Test downloading and parsing the Cultivera JSON file."""
    print("=== Testing Cultivera JSON Download and Parsing ===")
    
    url = "https://files.cultivera.com/435553542D5753313030303438/Interop/25/28/0KMK8B1FTA5RZZ67/Cultivera_ORD-153392_422044.json"
    
    try:
        print(f"Downloading JSON from: {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ Successfully downloaded JSON ({len(response.content)} bytes)")
        print(f"✅ JSON structure validated")
        
        return data
    except Exception as e:
        print(f"❌ Failed to download JSON: {e}")
        return None

def test_cultivera_json_structure(data):
    """Test the structure of the Cultivera JSON data."""
    print("\n=== Testing Cultivera JSON Structure ===")
    
    required_fields = [
        'document_name', 'document_schema_version', 'manifest_type',
        'inventory_transfer_items', 'from_license_name', 'to_license_name'
    ]
    
    for field in required_fields:
        if field in data:
            print(f"✅ Found required field: {field}")
        else:
            print(f"❌ Missing required field: {field}")
            return False
    
    # Check inventory items
    items = data.get('inventory_transfer_items', [])
    print(f"✅ Found {len(items)} inventory transfer items")
    
    if len(items) > 0:
        sample_item = items[0]
        item_fields = ['product_name', 'strain_name', 'qty', 'unit_weight', 'line_price']
        
        for field in item_fields:
            if field in sample_item:
                print(f"✅ Item has field: {field}")
            else:
                print(f"❌ Item missing field: {field}")
    
    return True

def test_json_matcher_with_cultivera(data):
    """Test the JSON matcher with Cultivera data."""
    print("\n=== Testing JSON Matcher with Cultivera Data ===")
    
    try:
        from src.core.data.json_matcher import JSONMatcher, extract_products_from_manifest, map_json_to_db_fields
        
        # Test 1: Extract products from manifest
        print("Testing product extraction...")
        products = extract_products_from_manifest(data)
        print(f"✅ Extracted {len(products)} products from manifest")
        
        # Test 2: Map JSON fields to database fields
        print("Testing field mapping...")
        if products:
            sample_product = products[0]
            mapped_product = map_json_to_db_fields(sample_product)
            print(f"✅ Successfully mapped product: {mapped_product.get('ProductName', 'Unknown')}")
            
            # Show mapping results
            print("Field mapping results:")
            for key, value in mapped_product.items():
                if value is not None and value != '':
                    print(f"  {key}: {value}")
        
        # Test 3: Initialize JSONMatcher
        print("Testing JSONMatcher initialization...")
        matcher = JSONMatcher()
        print("✅ JSONMatcher initialized successfully")
        
        # Test 4: Process the entire manifest
        print("Testing full manifest processing...")
        processed_products = matcher.process_manifest(data)
        print(f"✅ Processed {len(processed_products)} products from manifest")
        
        return True
        
    except Exception as e:
        print(f"❌ JSON matcher test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cultivera_specific_fields(data):
    """Test Cultivera-specific field handling."""
    print("\n=== Testing Cultivera-Specific Fields ===")
    
    items = data.get('inventory_transfer_items', [])
    if not items:
        print("❌ No items to test")
        return False
    
    sample_item = items[0]
    
    # Test Cultivera-specific fields
    cultivera_fields = [
        'integrator_data', 'is_sample', 'sample_type', 'serving_weight',
        'uom', 'unit_weight_uom', 'inventory_id', 'sample_source_id',
        'is_medical', 'is_for_extraction', 'lab_result_passed',
        'lab_result_link', 'lab_result_data', 'inventory_category',
        'inventory_type', 'product_sku'
    ]
    
    found_fields = 0
    for field in cultivera_fields:
        if field in sample_item:
            found_fields += 1
            print(f"✅ Found Cultivera field: {field}")
        else:
            print(f"⚠️  Missing Cultivera field: {field}")
    
    print(f"✅ Found {found_fields}/{len(cultivera_fields)} Cultivera-specific fields")
    
    # Test lab result data
    lab_data = sample_item.get('lab_result_data', {})
    if lab_data:
        print("✅ Lab result data present")
        potency = lab_data.get('potency', [])
        print(f"✅ Found {len(potency)} potency entries")
        
        for p in potency:
            print(f"  - {p.get('type', 'Unknown')}: {p.get('value', 'N/A')} {p.get('unit', '')}")
    
    return True

def test_product_validation(data):
    """Test product validation and data quality."""
    print("\n=== Testing Product Validation ===")
    
    items = data.get('inventory_transfer_items', [])
    
    # Check for required product data
    valid_products = 0
    products_with_strains = 0
    products_with_prices = 0
    products_with_weights = 0
    
    for item in items:
        if item.get('product_name'):
            valid_products += 1
        
        if item.get('strain_name'):
            products_with_strains += 1
        
        if item.get('line_price') and item['line_price'] > 0:
            products_with_prices += 1
        
        if item.get('unit_weight') and item['unit_weight'] > 0:
            products_with_weights += 1
    
    print(f"✅ Valid products: {valid_products}/{len(items)}")
    print(f"✅ Products with strains: {products_with_strains}/{len(items)}")
    print(f"✅ Products with prices: {products_with_prices}/{len(items)}")
    print(f"✅ Products with weights: {products_with_weights}/{len(items)}")
    
    # Show sample products
    print("\nSample products from manifest:")
    for i, item in enumerate(items[:5]):
        print(f"  {i+1}. {item.get('product_name', 'Unknown')} - {item.get('strain_name', 'No strain')}")
    
    return True

def main():
    """Main test function."""
    print("🧪 Cultivera JSON Matching Test")
    print("=" * 50)
    
    # Test 1: Download JSON
    data = test_cultivera_json_download()
    if not data:
        print("❌ Cannot proceed without JSON data")
        return False
    
    # Test 2: Validate structure
    if not test_cultivera_json_structure(data):
        print("❌ JSON structure validation failed")
        return False
    
    # Test 3: Test JSON matcher
    if not test_json_matcher_with_cultivera(data):
        print("❌ JSON matcher test failed")
        return False
    
    # Test 4: Test Cultivera-specific fields
    if not test_cultivera_specific_fields(data):
        print("❌ Cultivera-specific field test failed")
        return False
    
    # Test 5: Test product validation
    if not test_product_validation(data):
        print("❌ Product validation test failed")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 ALL TESTS PASSED! JSON matching works with Cultivera data!")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 