#!/usr/bin/env python3
"""
Debug script to check JointRatio column processing
"""

import sys
import os
import pandas as pd
import requests
import json

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def debug_joint_ratio_columns():
    """Debug JointRatio column processing"""
    print("🔍 Debugging JointRatio Column Processing")
    print("=" * 60)
    
    # Check Flask app status
    try:
        response = requests.get('http://127.0.0.1:9090/api/status')
        if response.status_code == 200:
            status = response.json()
            print(f"📊 Flask app data: {status['data_shape'][0]} rows, {status['data_shape'][1]} columns")
            print(f"📁 File: {status['last_loaded_file']}")
        else:
            print("❌ Flask app not responding")
            return
    except Exception as e:
        print(f"❌ Error connecting to Flask app: {e}")
        return
    
    print()
    
    # Get sample data from Flask app
    try:
        response = requests.get('http://127.0.0.1:9090/api/sample-data')
        if response.status_code == 200:
            sample_data = response.json()
            print("✅ Retrieved sample data from Flask app")
        else:
            print("❌ Could not get sample data from Flask app")
            return
    except Exception as e:
        print(f"❌ Error getting sample data: {e}")
        return
    
    # Check all columns for JointRatio-related names
    print("\n1. Checking for JointRatio-related columns:")
    print("-" * 40)
    joint_ratio_columns = []
    for col in sample_data.get('columns', []):
        if 'joint' in col.lower() or 'ratio' in col.lower():
            joint_ratio_columns.append(col)
            print(f"   Found: '{col}'")
    
    if not joint_ratio_columns:
        print("   ❌ No JointRatio-related columns found!")
    print()
    
    # Check for pre-roll products in sample data
    print("2. Checking pre-roll products in sample data:")
    print("-" * 40)
    sample_records = sample_data.get('records', [])
    preroll_records = []
    
    for record in sample_records:
        product_type = record.get('Product Type*', '')
        if 'pre-roll' in str(product_type).lower():
            preroll_records.append(record)
    
    print(f"   Found {len(preroll_records)} pre-roll products in sample")
    
    if preroll_records:
        print("   Sample pre-roll products:")
        for record in preroll_records[:5]:
            product_name = record.get('ProductName', 'Unknown')
            product_type = record.get('Product Type*', 'Unknown')
            print(f"     {product_name} - {product_type}")
            
            # Check for JointRatio-related values
            for col in joint_ratio_columns:
                value = record.get(col, '')
                if value and str(value).strip() != '':
                    print(f"       {col}: '{value}'")
    print()
    
    # Check if JointRatio column exists
    print("3. Checking for JointRatio column:")
    print("-" * 40)
    if "JointRatio" in sample_data.get('columns', []):
        print("   ✅ JointRatio column exists")
        joint_ratio_values = []
        for record in sample_records:
            value = record.get('JointRatio', '')
            if value and str(value).strip() != '':
                joint_ratio_values.append(value)
        
        print(f"   Non-empty values: {len(joint_ratio_values)}")
        
        if joint_ratio_values:
            print("   Sample JointRatio values:")
            for value in joint_ratio_values[:10]:
                print(f"     '{value}'")
    else:
        print("   ❌ JointRatio column does not exist")
    print()
    
    # Check for "Joint Ratio" column (with space)
    print("4. Checking for 'Joint Ratio' column (with space):")
    print("-" * 40)
    if "Joint Ratio" in sample_data.get('columns', []):
        print("   ✅ 'Joint Ratio' column exists")
        joint_ratio_values = []
        for record in sample_records:
            value = record.get('Joint Ratio', '')
            if value and str(value).strip() != '':
                joint_ratio_values.append(value)
        
        print(f"   Non-empty values: {len(joint_ratio_values)}")
        
        if joint_ratio_values:
            print("   Sample 'Joint Ratio' values:")
            for value in joint_ratio_values[:10]:
                print(f"     '{value}'")
    else:
        print("   ❌ 'Joint Ratio' column does not exist")
    print()
    
    # Check all columns for debugging
    print("5. All columns in the dataset:")
    print("-" * 40)
    columns = sample_data.get('columns', [])
    for i, col in enumerate(columns):
        print(f"   {i+1:2d}. '{col}'")
    print()
    
    # Check for any columns that might contain joint ratio data
    print("6. Checking for potential joint ratio data in other columns:")
    print("-" * 40)
    potential_columns = []
    for col in columns:
        if any(keyword in col.lower() for keyword in ['pack', 'count', 'quantity', 'joint']):
            potential_columns.append(col)
    
    if potential_columns:
        print("   Potential columns containing joint ratio data:")
        for col in potential_columns:
            values = []
            for record in sample_records:
                value = record.get(col, '')
                if value and str(value).strip() != '':
                    values.append(value)
            
            print(f"     '{col}': {len(values)} non-empty values")
            if values:
                for value in values[:3]:
                    print(f"       '{value}'")
    else:
        print("   No obvious columns containing joint ratio data found")

if __name__ == "__main__":
    debug_joint_ratio_columns() 