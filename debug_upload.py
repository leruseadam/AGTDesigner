#!/usr/bin/env python3

import pandas as pd
import json
import numpy as np

def clean_nan_values(obj):
    """Clean NaN values for JSON serialization"""
    if isinstance(obj, dict):
        return {k: clean_nan_values(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_nan_values(item) for item in obj]
    elif isinstance(obj, float) and np.isnan(obj):
        return None  # Convert NaN to None for JSON
    else:
        return obj

def test_excel_processing():
    """Test Excel processing to find the error"""
    try:
        print("Loading Excel file...")
        df = pd.read_excel('test_export.xlsx')
        print(f"Loaded {len(df)} rows")
        
        print("Converting to dict...")
        data = df.to_dict('records')
        print(f"Converted to {len(data)} records")
        
        print("Cleaning NaN values...")
        cleaned_data = clean_nan_values(data)
        print(f"Cleaned data: {len(cleaned_data)} records")
        
        print("Testing JSON serialization...")
        json_str = json.dumps(cleaned_data[:5])  # Test with first 5 records
        print("JSON serialization successful for first 5 records")
        
        print("Testing full JSON serialization...")
        json_str = json.dumps(cleaned_data)
        print("Full JSON serialization successful")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_excel_processing()
