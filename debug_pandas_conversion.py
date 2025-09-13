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

def debug_pandas_conversion():
    """Debug the pandas conversion step by step"""
    try:
        print("Loading Excel file...")
        df = pd.read_excel('test_export.xlsx')
        print(f"Loaded {len(df)} rows, {len(df.columns)} columns")
        print(f"Columns: {list(df.columns)}")
        print(f"Data types: {df.dtypes.to_dict()}")
        
        # Check for mixed types in columns
        for col in df.columns:
            unique_types = set(type(x).__name__ for x in df[col].dropna().unique())
            if len(unique_types) > 1:
                print(f"Column '{col}' has mixed types: {unique_types}")
                print(f"Sample values: {df[col].dropna().head().tolist()}")
        
        print("\nTesting chunked processing...")
        chunk_size = 1000
        all_data = []
        
        for chunk_start in range(0, len(df), chunk_size):
            chunk_end = min(chunk_start + chunk_size, len(df))
            print(f"\nProcessing chunk {chunk_start}-{chunk_end}")
            
            # Read chunk
            df_chunk = df.iloc[chunk_start:chunk_end]
            print(f"Chunk shape: {df_chunk.shape}")
            
            # Convert to list of dictionaries
            print("Converting to dict...")
            chunk_data = df_chunk.to_dict('records')
            print(f"Converted to {len(chunk_data)} records")
            
            # Check first record
            if chunk_data:
                first_record = chunk_data[0]
                print(f"First record keys: {list(first_record.keys())}")
                print(f"First record types: {[(k, type(v).__name__) for k, v in first_record.items()]}")
                
                # Check for problematic values
                for k, v in first_record.items():
                    if isinstance(v, (int, float)) and isinstance(v, str):
                        print(f"Mixed type in {k}: {v} (type: {type(v)})")
            
            # Clean NaN values
            print("Cleaning NaN values...")
            chunk_data = clean_nan_values(chunk_data)
            print(f"Cleaned data: {len(chunk_data)} records")
            
            # Test JSON serialization of this chunk
            try:
                json.dumps(chunk_data[:5])  # Test first 5
                print("Chunk JSON serialization successful for first 5")
            except Exception as e:
                print(f"Chunk JSON serialization failed: {e}")
                # Find the problematic record
                for i, record in enumerate(chunk_data):
                    try:
                        json.dumps(record)
                    except Exception as record_error:
                        print(f"Problematic record {i} in chunk: {record}")
                        print(f"Record error: {record_error}")
                        break
                break
            
            # Add to all_data
            all_data.extend(chunk_data)
            print(f"Total data so far: {len(all_data)} records")
        
        print(f"\nTotal processed items: {len(all_data)}")
        
        # Test full JSON serialization
        print("Testing full JSON serialization...")
        try:
            json.dumps(all_data)
            print("Full data JSON serialization successful")
        except Exception as e:
            print(f"Full data JSON serialization failed: {e}")
            # Find the problematic item
            for i, item in enumerate(all_data):
                try:
                    json.dumps(item)
                except Exception as item_error:
                    print(f"Problematic item {i}: {item}")
                    print(f"Item error: {item_error}")
                    break
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_pandas_conversion()
