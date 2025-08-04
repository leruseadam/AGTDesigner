#!/usr/bin/env python3
"""
Simple debug script to check JointRatio in the actual Excel file
"""

import sys
import os
import pandas as pd

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def debug_joint_ratio_simple():
    """Debug JointRatio by reading the actual Excel file"""
    print("🔍 Debugging JointRatio in Actual Excel File")
    print("=" * 60)
    
    # Path to the Excel file
    excel_file = "/Users/adamcordova/Downloads/A Greener Today - Bothell_inventory_07-30-2025  5_00 AM.xlsx"
    
    if not os.path.exists(excel_file):
        print(f"❌ Excel file not found: {excel_file}")
        return
    
    print(f"📁 Reading Excel file: {excel_file}")
    
    try:
        # Read the Excel file
        df = pd.read_excel(excel_file)
        print(f"✅ Successfully read Excel file: {len(df)} rows, {len(df.columns)} columns")
        print()
        
        # Check all columns for JointRatio-related names
        print("1. Checking for JointRatio-related columns:")
        print("-" * 40)
        joint_ratio_columns = []
        for col in df.columns:
            if 'joint' in col.lower() or 'ratio' in col.lower():
                joint_ratio_columns.append(col)
                print(f"   Found: '{col}'")
        
        if not joint_ratio_columns:
            print("   ❌ No JointRatio-related columns found!")
        print()
        
        # Check for pre-roll products
        print("2. Checking pre-roll products:")
        print("-" * 40)
        if "Product Type*" in df.columns:
            preroll_mask = df["Product Type*"].str.strip().str.lower().isin(["pre-roll", "infused pre-roll"])
            preroll_count = preroll_mask.sum()
            print(f"   Found {preroll_count} pre-roll products")
            
            if preroll_count > 0:
                print("   Sample pre-roll products:")
                sample_prerolls = df[preroll_mask].head(10)
                for idx, row in sample_prerolls.iterrows():
                    product_name = row.get('Product Name*', 'Unknown')
                    product_type = row.get('Product Type*', 'Unknown')
                    print(f"     {product_name} - {product_type}")
                    
                    # Check for JointRatio-related values
                    for col in joint_ratio_columns:
                        value = row.get(col, '')
                        if pd.notna(value) and str(value).strip() != '':
                            print(f"       {col}: '{value}'")
        else:
            print("   ❌ 'Product Type*' column not found")
        print()
        
        # Check for "Joint Ratio" column (with space)
        print("3. Checking for 'Joint Ratio' column (with space):")
        print("-" * 40)
        if "Joint Ratio" in df.columns:
            print("   ✅ 'Joint Ratio' column exists")
            joint_ratio_values = df["Joint Ratio"].dropna()
            print(f"   Non-empty values: {len(joint_ratio_values)}")
            
            if len(joint_ratio_values) > 0:
                print("   Sample 'Joint Ratio' values:")
                for value in joint_ratio_values.head(10):
                    print(f"     '{value}'")
        else:
            print("   ❌ 'Joint Ratio' column does not exist")
        print()
        
        # Check for "JointRatio" column (no space)
        print("4. Checking for 'JointRatio' column (no space):")
        print("-" * 40)
        if "JointRatio" in df.columns:
            print("   ✅ 'JointRatio' column exists")
            joint_ratio_values = df["JointRatio"].dropna()
            print(f"   Non-empty values: {len(joint_ratio_values)}")
            
            if len(joint_ratio_values) > 0:
                print("   Sample 'JointRatio' values:")
                for value in joint_ratio_values.head(10):
                    print(f"     '{value}'")
        else:
            print("   ❌ 'JointRatio' column does not exist")
        print()
        
        # Check all columns for debugging
        print("5. All columns in the Excel file:")
        print("-" * 40)
        for i, col in enumerate(df.columns):
            print(f"   {i+1:2d}. '{col}'")
        print()
        
        # Check for any columns that might contain joint ratio data
        print("6. Checking for potential joint ratio data in other columns:")
        print("-" * 40)
        potential_columns = []
        for col in df.columns:
            if any(keyword in col.lower() for keyword in ['pack', 'count', 'quantity', 'joint']):
                potential_columns.append(col)
        
        if potential_columns:
            print("   Potential columns containing joint ratio data:")
            for col in potential_columns:
                non_empty = df[col].dropna()
                print(f"     '{col}': {len(non_empty)} non-empty values")
                if len(non_empty) > 0:
                    sample_values = non_empty.head(3)
                    for value in sample_values:
                        print(f"       '{value}'")
        else:
            print("   No obvious columns containing joint ratio data found")
        
        # Check for "Ratio" column
        print("\n7. Checking 'Ratio' column:")
        print("-" * 40)
        if "Ratio" in df.columns:
            print("   ✅ 'Ratio' column exists")
            ratio_values = df["Ratio"].dropna()
            print(f"   Non-empty values: {len(ratio_values)}")
            
            if len(ratio_values) > 0:
                print("   Sample 'Ratio' values:")
                for value in ratio_values.head(10):
                    print(f"     '{value}'")
        else:
            print("   ❌ 'Ratio' column does not exist")
        
    except Exception as e:
        print(f"❌ Error reading Excel file: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_joint_ratio_simple() 