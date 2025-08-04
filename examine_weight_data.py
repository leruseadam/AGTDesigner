import pandas as pd
import os
from src.core.data.excel_processor import get_default_upload_file

# Get the default file
default_file = get_default_upload_file()
print(f"Default file: {default_file}")

if default_file and os.path.exists(default_file):
    # Read the Excel file
    df = pd.read_excel(default_file)
    print(f"\nDataFrame shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")
    # Look for weight-related columns
    weight_cols = [col for col in df.columns if 'weight' in col.lower() or 'Weight' in col]
    print(f"\nWeight-related columns: {weight_cols}")
    
    # Check specific weight columns
    for col in weight_cols:
        print(f"\n{col}:")
        print(f"  Non-null count: {df[col].notna().sum()}")
        print(f"  Unique values: {df[col].dropna().unique()[:10]}")
    
    # Check Product Name column for weight patterns
    if 'Product Name*' in df.columns:
        print(f"\nProduct Name* column:")
        print(f"  Sample values:")
        for i, name in enumerate(df['Product Name*'].head(10)):
            print(f"    {i+1}: {name}")
    
    # Check if there are any weight values in the data
    all_weight_values = set()
    for col in weight_cols:
        if col in df.columns:
            values = df[col].dropna().unique()
            all_weight_values.update(values)
    
    print(f"\nAll weight values found: {sorted(all_weight_values)}")
    # Test the weight extraction logic
    import re
    weight_values = set()
    if 'Product Name*' in df.columns:
        for product_name in df['Product Name*'].dropna():
            if isinstance(product_name, str):
                weight_patterns = [
                    r'\d+(?:\.\d+)?\s*(?:g|gram|grams|gm)\b',
                    r'\d+(?:\.\d+)?\s*(?:oz|ounce|ounces)\b'
                ]
                for pattern in weight_patterns:
                    matches = re.findall(pattern, product_name, re.IGNORECASE)
                    weight_values.update(matches)
    
    print(f"\nWeight values extracted from product names: {sorted(weight_values)}")
else:
    print("Default file not found or doesn't exist") 