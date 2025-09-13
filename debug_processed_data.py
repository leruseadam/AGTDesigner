#!/usr/bin/env python3

import sys
import os
sys.path.append('.')

# Import the app to get access to the global variables
from app import processed_data, clean_nan_values
import json

def debug_processed_data():
    """Debug the processed_data structure"""
    try:
        print(f"Processed data keys: {list(processed_data.keys())}")
        
        for filename, data in processed_data.items():
            print(f"\nFile: {filename}")
            print(f"Status: {data['status']}")
            print(f"Data type: {type(data['data'])}")
            print(f"Data length: {len(data['data'])}")
            
            if data['status'] == 'completed':
                print("Testing data cleaning...")
                cleaned_data = clean_nan_values(data['data'])
                print(f"Cleaned data length: {len(cleaned_data)}")
                
                print("Testing JSON serialization...")
                json_str = json.dumps(cleaned_data[:5])  # Test with first 5
                print("JSON serialization successful for first 5 records")
                
                # Test full serialization
                try:
                    json_str = json.dumps(cleaned_data)
                    print("Full JSON serialization successful")
                except Exception as e:
                    print(f"Full JSON serialization failed: {e}")
                    # Find the problematic record
                    for i, record in enumerate(cleaned_data):
                        try:
                            json.dumps(record)
                        except Exception as record_error:
                            print(f"Problematic record {i}: {record}")
                            print(f"Record error: {record_error}")
                            break
                    break
                
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_processed_data()
