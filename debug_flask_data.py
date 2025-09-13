#!/usr/bin/env python3

import sys
sys.path.append('.')
from app import processed_data, clean_nan_values
import json

print("=== Debug Flask Data ===")
print(f"Processed data keys: {list(processed_data.keys())}")

for filename, data in processed_data.items():
    print(f"\nFile: {filename}")
    print(f"Status: {data.get('status', 'unknown')}")
    
    if 'data' in data and len(data['data']) > 0:
        print(f"Data length: {len(data['data'])}")
        print(f"Sample data type: {type(data['data'][0])}")
        print(f"Sample data keys: {list(data['data'][0].keys())[:5]}")
        
        # Try to clean just one item first
        try:
            sample_item = data['data'][0]
            print(f"Original sample item type: {type(sample_item)}")
            cleaned_item = clean_nan_values(sample_item)
            print(f"Cleaned sample item type: {type(cleaned_item)}")
            print(f"Cleaned sample item keys: {list(cleaned_item.keys())[:5]}")
            
            # Try to serialize just one item
            json.dumps(cleaned_item)
            print("✓ Single item JSON serialization works")
            
        except Exception as e:
            print(f"✗ Single item cleaning/serialization failed: {e}")
            import traceback
            traceback.print_exc()
        
        # Try to clean a small batch
        try:
            small_batch = data['data'][:10]
            cleaned_batch = clean_nan_values(small_batch)
            print(f"Cleaned batch type: {type(cleaned_batch)}")
            print(f"Cleaned batch length: {len(cleaned_batch)}")
            
            # Try to serialize the batch
            json.dumps(cleaned_batch)
            print("✓ Small batch JSON serialization works")
            
        except Exception as e:
            print(f"✗ Small batch cleaning/serialization failed: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("No data found")
