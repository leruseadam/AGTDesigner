import pandas as pd

# Load the Excel file
df = pd.read_excel('uploads/A Greener Today - Bothell_inventory_08-26-2025  4_05 PM.xlsx')

# Define columns
vendor_col = 'Vendor/Supplier*'
brand_col = 'Product Brand'
product_type_col = 'Product Type*'
lineage_col = 'Lineage'

# Test parameters
vendor_filter = 'LIFTED CANNABIS'
search_term = 'meta'

print(f"Total rows in Excel: {len(df)}")
print(f"Available columns: {list(df.columns)}")
print(f"Vendor filter: {vendor_filter}")
print(f"Search term: {search_term}")

# Step 1: Filter by vendor
vendor_mask = df[vendor_col].str.contains(vendor_filter, case=False, na=False)
vendor_filtered_df = df[vendor_mask].copy()
print(f"\nStep 1 - Vendor filtered rows: {len(vendor_filtered_df)}")

# Step 2: Apply search term filter
search_mask = vendor_filtered_df[brand_col].str.contains(search_term, case=False, na=False)

# Add product type search if available
if product_type_col:
    search_mask = search_mask | vendor_filtered_df[product_type_col].str.contains(search_term, case=False, na=False)

# Also search in Product Strain
if 'Product Strain' in vendor_filtered_df.columns:
    search_mask = search_mask | vendor_filtered_df['Product Strain'].str.contains(search_term, case=False, na=False)

# Apply search filter
filtered_df = vendor_filtered_df[search_mask].copy()
print(f"Step 2 - After search filtering: {len(filtered_df)} rows")

# Show results
if len(filtered_df) > 0:
    print("\nFinal results:")
    print(filtered_df[['Product Name*', 'Product Strain', 'Product Brand', 'Vendor/Supplier*']].to_string())
else:
    print("\nNo results found!")
    
    # Debug: Show some vendor-filtered rows
    print(f"\nDebug: First 5 vendor-filtered rows:")
    print(vendor_filtered_df[['Product Name*', 'Product Strain', 'Product Brand', 'Vendor/Supplier*']].head().to_string())
    
    # Debug: Check if Product Strain column has data
    print(f"\nDebug: Product Strain column info:")
    print(f"Column exists: {'Product Strain' in vendor_filtered_df.columns}")
    if 'Product Strain' in vendor_filtered_df.columns:
        print(f"Non-null values: {vendor_filtered_df['Product Strain'].notna().sum()}")
        print(f"Sample values: {vendor_filtered_df['Product Strain'].dropna().head().tolist()}")
