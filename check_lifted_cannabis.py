import pandas as pd

# Load the file
df = pd.read_excel('/Users/adamcordova/Downloads/A Greener Today - Bothell_inventory_08-28-2025 12_19 PM.xlsx')

# Check for LIFTED CANNABIS products
lifted_df = df[df['Vendor/Supplier*'] == 'LIFTED CANNABIS']
print(f'LIFTED CANNABIS products: {len(lifted_df)}')

if len(lifted_df) > 0:
    print('\nProduct Strains:')
    print(lifted_df['Product Strain'].dropna().unique()[:10])
    
    # Check for meta strains
    meta_strains = lifted_df[lifted_df['Product Strain'].str.contains('meta', case=False, na=False)]
    print(f'\nMeta strains found: {len(meta_strains)}')
    
    if len(meta_strains) > 0:
        print('\nMeta strains details:')
        print(meta_strains[['Product Name*', 'Product Strain', 'Product Brand']].to_string())
else:
    print('No LIFTED CANNABIS products found!')
    
    # Check what vendors exist
    print('\nAvailable vendors:')
    vendors = df['Vendor/Supplier*'].unique()
    print(vendors[:20])  # Show first 20 vendors
