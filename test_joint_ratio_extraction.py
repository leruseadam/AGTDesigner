#!/usr/bin/env python3
"""
Test script to verify joint ratio extraction from product names
"""

import sys
import os
import pandas as pd
import re

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_joint_ratio_extraction():
    """Test the joint ratio extraction from product names"""
    print("🧪 Testing Joint Ratio Extraction from Product Names")
    print("=" * 60)
    
    # Test data based on the actual Excel file
    test_data = {
        'Product Name*': [
            'Gelato Live Resin Infused Pre-Roll by Dabstract - 0.5g x 2 Pack',
            'Ice Cream Sandwiches Live Resin Infused Pre-Roll by Dabstract - 0.5g x 2 Pack',
            'Blueberry Banana Pie Flavour Stix Infused Pre-Roll by Dank Czar - .75g x 5 Pack',
            'Peach Rings Flavour Stix Infused Pre-Roll by Dank Czar - .75g',
            'Forbidden Fruit Core Flower Pre-Roll by Phat Panda - 1g',
            'Hybrid Infused Pre-Roll by Cloud 9 Farms - 1g',
            'Maui Sunrise Juicy Stickz Infused Pre-Roll by Hellavated - .75g',
            'Sour Diesel Live Resin Infused Pre-Roll by Dabstract - 0.5g x 2 Pack',
            'Test Product - 1g x 28 Pack',
            'Another Test - 3.5g x 10'
        ],
        'Product Type*': [
            'infused pre-roll',
            'infused pre-roll',
            'infused pre-roll',
            'infused pre-roll',
            'pre-roll',
            'infused pre-roll',
            'infused pre-roll',
            'infused pre-roll',
            'pre-roll',
            'pre-roll'
        ]
    }
    
    df = pd.DataFrame(test_data)
    
    print("📊 Test data created with sample pre-roll products")
    print()
    
    # Define the extraction function (same as in the Excel processor)
    def extract_joint_ratio_from_name(product_name):
        if pd.isna(product_name) or str(product_name).strip() == '':
            return ''
        
        product_name_str = str(product_name)
        
        # Look for patterns like "0.5g x 2 Pack", "1g x 28 Pack", etc.
        
        # Pattern 1: "weight x count Pack" (e.g., "0.5g x 2 Pack", ".75g x 5 Pack")
        pattern1 = r'(\d*\.?\d+g)\s*x\s*(\d+)\s*Pack'
        match1 = re.search(pattern1, product_name_str, re.IGNORECASE)
        if match1:
            weight = match1.group(1)
            count = match1.group(2)
            return f"{weight} x {count} Pack"
        
        # Pattern 2: "weight x count" (e.g., "0.5g x 2", ".75g x 5")
        pattern2 = r'(\d*\.?\d+g)\s*x\s*(\d+)'
        match2 = re.search(pattern2, product_name_str, re.IGNORECASE)
        if match2:
            weight = match2.group(1)
            count = match2.group(2)
            return f"{weight} x {count}"
        
        # Pattern 3: Just weight (e.g., "1g", "0.5g", ".75g")
        pattern3 = r'(\d*\.?\d+g)'
        match3 = re.search(pattern3, product_name_str, re.IGNORECASE)
        if match3:
            weight = match3.group(1)
            return weight
        
        return ''
    
    # Test the extraction
    print("1. Testing joint ratio extraction:")
    print("-" * 40)
    
    results = []
    for idx, row in df.iterrows():
        product_name = row['Product Name*']
        product_type = row['Product Type*']
        joint_ratio = extract_joint_ratio_from_name(product_name)
        
        results.append({
            'product_name': product_name,
            'product_type': product_type,
            'extracted_joint_ratio': joint_ratio
        })
        
        print(f"   Product: {product_name}")
        print(f"   Type: {product_type}")
        print(f"   Extracted: '{joint_ratio}'")
        print()
    
    # Test specific cases
    print("2. Testing specific cases:")
    print("-" * 40)
    
    test_cases = [
        ("Gelato Live Resin Infused Pre-Roll by Dabstract - 0.5g x 2 Pack", "0.5g x 2 Pack"),
        ("Blueberry Banana Pie Flavour Stix Infused Pre-Roll by Dank Czar - .75g x 5 Pack", ".75g x 5 Pack"),
        ("Peach Rings Flavour Stix Infused Pre-Roll by Dank Czar - .75g", ".75g"),
        ("Forbidden Fruit Core Flower Pre-Roll by Phat Panda - 1g", "1g"),
        ("Test Product - 1g x 28 Pack", "1g x 28 Pack"),
        ("Another Test - 3.5g x 10", "3.5g x 10")
    ]
    
    all_passed = True
    for product_name, expected in test_cases:
        extracted = extract_joint_ratio_from_name(product_name)
        if extracted == expected:
            print(f"✅ PASSED: '{product_name}' → '{extracted}'")
        else:
            print(f"❌ FAILED: '{product_name}' → '{extracted}' (expected: '{expected}')")
            all_passed = False
    
    print()
    
    if all_passed:
        print("🎉 All test cases passed!")
    else:
        print("⚠️  Some test cases failed!")
    
    # Test with the actual Excel file data
    print("\n3. Testing with actual Excel file data:")
    print("-" * 40)
    
    excel_file = "/Users/adamcordova/Downloads/A Greener Today - Bothell_inventory_07-30-2025  5_00 AM.xlsx"
    
    if os.path.exists(excel_file):
        try:
            actual_df = pd.read_excel(excel_file)
            print(f"✅ Successfully read Excel file: {len(actual_df)} rows")
            
            # Find pre-roll products
            if "Product Type*" in actual_df.columns:
                preroll_mask = actual_df["Product Type*"].str.strip().str.lower().isin(["pre-roll", "infused pre-roll"])
                preroll_count = preroll_mask.sum()
                print(f"   Found {preroll_count} pre-roll products")
                
                # Test extraction on first 10 pre-roll products
                sample_prerolls = actual_df[preroll_mask].head(10)
                print("   Sample extractions:")
                
                for idx, row in sample_prerolls.iterrows():
                    product_name = row.get('Product Name*', '')
                    joint_ratio = extract_joint_ratio_from_name(product_name)
                    print(f"     '{product_name}' → '{joint_ratio}'")
                
        except Exception as e:
            print(f"❌ Error reading Excel file: {e}")
    else:
        print(f"❌ Excel file not found: {excel_file}")

if __name__ == "__main__":
    test_joint_ratio_extraction() 