#!/usr/bin/env python3

import pandas as pd
import numpy as np
import json

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

def test_data_processing():
    """Test the exact same data processing as the main app"""
    try:
        print("Loading Excel file...")
        df = pd.read_excel('test_export.xlsx')
        print(f"Loaded {len(df)} rows")
        
        # Process in chunks like the main app
        chunk_size = 1000
        all_data = []
        
        for chunk_start in range(0, len(df), chunk_size):
            chunk_end = min(chunk_start + chunk_size, len(df))
            
            # Read chunk
            df_chunk = df.iloc[chunk_start:chunk_end]
            
            # Convert to list of dictionaries
            chunk_data = df_chunk.to_dict('records')
            
            # Clean NaN values
            chunk_data = clean_nan_values(chunk_data)
            
            # Add to all_data
            all_data.extend(chunk_data)
            
            print(f"Processed chunk {chunk_start}-{chunk_end}: {len(chunk_data)} items")
        
        print(f"Total processed items: {len(all_data)}")
        
        # Test JSON serialization
        print("Testing JSON serialization...")
        json.dumps(all_data[:5])  # Test first 5
        print("First 5 items JSON serialization successful")
        
        json.dumps(all_data)  # Test all data
        print("Full data JSON serialization successful")
        
        print("Data processing test completed successfully!")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_data_processing()
