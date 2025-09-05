#!/usr/bin/env python3
"""
Debug script to check vendor columns in Excel data
"""

import pandas as pd
import os
from pathlib import Path

def debug_vendor_columns():
    """Debug vendor columns in Excel data"""
    
    # Check for uploaded Excel files
    session_file_path = None
    
    # Look for Excel files in common locations
    possible_paths = [
        "uploads",
        "data", 
        ".",
        "backups"
    ]
    
    excel_files = []
    for path in possible_paths:
        if os.path.exists(path):
            for file in os.listdir(path):
                if file.endswith(('.xlsx', '.xls')):
                    excel_files.append(os.path.join(path, file))
    
    print(f"Found {len(excel_files)} Excel files:")
    for file in excel_files:
        print(f"  - {file}")
    
    if not excel_files:
        print("No Excel files found. Please upload an Excel file first.")
        return
    
    # Use the first Excel file found
    excel_file = excel_files[0]
    print(f"\nAnalyzing: {excel_file}")
    
    try:
        # Load the Excel file
        df = pd.read_excel(excel_file)
        
        print(f"\nExcel file loaded successfully!")
        print(f"Shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        
        # Check for vendor-related columns
        vendor_columns = []
        for col in df.columns:
            col_lower = str(col).lower()
            if 'vendor' in col_lower or 'supplier' in col_lower:
                vendor_columns.append(col)
        
        print(f"\nVendor-related columns found:")
        if vendor_columns:
            for col in vendor_columns:
                print(f"  - {col}")
                
                # Check unique values in this column
                unique_values = df[col].dropna().unique()
                print(f"    Unique values ({len(unique_values)}): {list(unique_values[:10])}")
                if len(unique_values) > 10:
                    print(f"    ... and {len(unique_values) - 10} more")
        else:
            print("  No vendor-related columns found!")
        
        # Check first few rows for vendor data
        print(f"\nFirst 5 rows vendor data:")
        for i, row in df.head().iterrows():
            vendor_data = {}
            for col in df.columns:
                col_lower = str(col).lower()
                if 'vendor' in col_lower or 'supplier' in col_lower:
                    vendor_data[col] = row[col]
            
            if vendor_data:
                print(f"  Row {i}: {vendor_data}")
            else:
                print(f"  Row {i}: No vendor data")
        
        # Check for empty vendor columns
        print(f"\nChecking for empty vendor columns:")
        for col in vendor_columns:
            non_empty = df[col].notna().sum()
            total = len(df)
            print(f"  {col}: {non_empty}/{total} non-empty values ({non_empty/total*100:.1f}%)")
        
    except Exception as e:
        print(f"Error loading Excel file: {e}")

if __name__ == "__main__":
    debug_vendor_columns()
