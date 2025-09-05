import pandas as pd

# Check the Downloads file
downloads_file = '/Users/adamcordova/Downloads/A Greener Today - Bothell_inventory_08-28-2025 12_19 PM.xlsx'

try:
    df = pd.read_excel(downloads_file)
    print(f"Downloads file loaded: {len(df)} rows")
    
    # Check if LIFTED CANNABIS exists
    if 'Vendor/Supplier*' in df.columns:
        lifted_df = df[df['Vendor/Supplier*'] == 'LIFTED CANNABIS']
        print(f"LIFTED CANNABIS products in Downloads file: {len(lifted_df)}")
        
        if len(lifted_df) > 0:
            print("Product Strains:")
            print(lifted_df['Product Strain'].dropna().unique()[:10])
            
            # Check for meta strains
            meta_strains = lifted_df[lifted_df['Product Strain'].str.contains('meta', case=False, na=False)]
            print(f"\nMeta strains found: {len(meta_strains)}")
            if len(meta_strains) > 0:
                print("Meta strains:")
                print(meta_strains[['Product Name*', 'Product Strain', 'Product Brand']].to_string())
        else:
            print("No LIFTED CANNABIS products found in Downloads file")
    else:
        print("No Vendor/Supplier* column found")
        
except Exception as e:
    print(f"Error: {e}")
