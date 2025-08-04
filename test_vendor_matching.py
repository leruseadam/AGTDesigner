import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.data.excel_processor import ExcelProcessor
from src.core.data.json_matcher import JSONMatcher

# Create ExcelProcessor and load the default file
processor = ExcelProcessor()
from src.core.data.excel_processor import get_default_upload_file
default_file = get_default_upload_file()
print(f"Loading file: {default_file}")
success = processor.load_file(default_file)

if success:
    print(f"DataFrame shape: {processor.df.shape}")
    
    # Check what vendors are in the Excel file
    if 'Vendor' in processor.df.columns:
        vendors = processor.df['Vendor'].dropna().unique()
        print(f"\nUnique vendors in Excel file ({len(vendors)}):")
        for i, vendor in enumerate(sorted(vendors)[:20]):  # Show first 20
            print(f"  {i+1}. '{vendor}'")
        if len(vendors) > 20:
            print(f"  ... and {len(vendors) - 20} more")
    
    # Check what brands are in the Excel file
    if 'Product Brand' in processor.df.columns:
        brands = processor.df['Product Brand'].dropna().unique()
        print(f"\nUnique brands in Excel file ({len(brands)}):")
        for i, brand in enumerate(sorted(brands)[:20]):  # Show first 20
            print(f"  {i+1}. '{brand}'")
        if len(brands) > 20:
            print(f"  ... and {len(brands) - 20} more")
    
    # Look for specific vendors/brands
    print(f"\n=== Looking for specific vendors/brands ===")
    
    # Search for Hustler's Ambition
    if 'ProductName' in processor.df.columns:
        hustler_products = processor.df[processor.df['ProductName'].str.contains('Hustler', case=False, na=False)]
        if not hustler_products.empty:
            print(f"Found {len(hustler_products)} products with 'Hustler' in name:")
            for _, row in hustler_products.head(5).iterrows():
                print(f"  '{row['ProductName']}' -> Vendor: '{row.get('Vendor', 'N/A')}', Brand: '{row.get('Product Brand', 'N/A')}'")
        else:
            print("No products found with 'Hustler' in name")
    
    # Search for Dank Czar
    if 'ProductName' in processor.df.columns:
        dank_products = processor.df[processor.df['ProductName'].str.contains('Dank', case=False, na=False)]
        if not dank_products.empty:
            print(f"\nFound {len(dank_products)} products with 'Dank' in name:")
            for _, row in dank_products.head(5).iterrows():
                print(f"  '{row['ProductName']}' -> Vendor: '{row.get('Vendor', 'N/A')}', Brand: '{row.get('Product Brand', 'N/A')}'")
        else:
            print("No products found with 'Dank' in name")
    
    # Search for products with "by" in the name
    if 'ProductName' in processor.df.columns:
        by_products = processor.df[processor.df['ProductName'].str.contains(' by ', case=False, na=False)]
        if not by_products.empty:
            print(f"\nFound {len(by_products)} products with ' by ' in name (first 5):")
            for _, row in by_products.head(5).iterrows():
                print(f"  '{row['ProductName']}' -> Vendor: '{row.get('Vendor', 'N/A')}', Brand: '{row.get('Product Brand', 'N/A')}'")
        else:
            print("No products found with ' by ' in name")
    
    # Test vendor extraction from product names
    print(f"\n=== Testing vendor extraction ===")
    test_names = [
        "Banana OG Distillate Cartridge by Hustler's Ambition - 1g",
        "Medically Compliant - Dank Czar Rosin All-In-One - GMO - 1g",
        "Medically Compliant - Dank Czar Rosin All-In-One - Grape Gas - 1g",
        "Gelato #41 Distillate Cartridge by Hustler's Ambition - 1g"
    ]
    
    json_matcher = JSONMatcher(processor)
    for name in test_names:
        extracted_vendor = json_matcher._extract_vendor(name)
        print(f"'{name}' -> extracted vendor: '{extracted_vendor}'")
    
    # Test key term extraction
    print(f"\n=== Testing key term extraction ===")
    for name in test_names:
        key_terms = json_matcher._extract_key_terms(name)
        print(f"'{name}' -> key terms: {key_terms}")
    
    # Test with some actual product names from the Excel file
    print(f"\n=== Testing with actual Excel product names ===")
    if 'ProductName' in processor.df.columns:
        sample_products = processor.df['ProductName'].dropna().head(10).tolist()
        for product in sample_products:
            extracted_vendor = json_matcher._extract_vendor(product)
            key_terms = json_matcher._extract_key_terms(product)
            print(f"'{product}' -> vendor: '{extracted_vendor}', terms: {key_terms}")
    
else:
    print("Failed to load file") 