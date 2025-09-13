#!/usr/bin/env python3

import pandas as pd
import numpy as np

def check_excel_types():
    """Check data types in the Excel file"""
    try:
        print("Loading Excel file...")
        df = pd.read_excel('test_export.xlsx')
        print(f"Loaded {len(df)} rows, {len(df.columns)} columns")
        print(f"Columns: {list(df.columns)}")
        print(f"Data types: {df.dtypes.to_dict()}")
        
        # Check each column for mixed types
        for col in df.columns:
            print(f"\nColumn: {col}")
            print(f"Data type: {df[col].dtype}")
            
            # Get unique values and their types
            unique_values = df[col].dropna().unique()
            print(f"Unique values count: {len(unique_values)}")
            
            # Check for mixed types
            types = set(type(x).__name__ for x in unique_values)
            print(f"Types found: {types}")
            
            if len(types) > 1:
                print(f"⚠️  Mixed types found in column '{col}'")
                # Show examples of each type
                for t in types:
                    examples = [x for x in unique_values if type(x).__name__ == t][:3]
                    print(f"  {t}: {examples}")
            
            # Check for problematic values
            for i, value in enumerate(unique_values[:10]):  # Check first 10 values
                if isinstance(value, (int, float)) and isinstance(value, str):
                    print(f"⚠️  Mixed type value at index {i}: {value} (type: {type(value)})")
                elif pd.isna(value):
                    print(f"⚠️  NaN value at index {i}")
        
        # Test the exact conversion that's failing
        print("\nTesting to_dict('records') conversion...")
        try:
            data = df.to_dict('records')
            print(f"✅ Successfully converted to {len(data)} records")
            
            # Check first record
            if data:
                first_record = data[0]
                print(f"First record: {first_record}")
                print(f"First record types: {[(k, type(v).__name__) for k, v in first_record.items()]}")
                
        except Exception as e:
            print(f"❌ Error in to_dict conversion: {e}")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_excel_types()
