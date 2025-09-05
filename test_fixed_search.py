import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.getcwd())

try:
    from app import get_excel_processor
    
    print("Testing fixed Excel processor...")
    
    # Get Excel processor
    excel_processor = get_excel_processor()
    print(f"Excel processor: {excel_processor}")
    
    if excel_processor:
        print(f"DataFrame loaded: {excel_processor.df is not None}")
        if excel_processor.df is not None:
            print(f"DataFrame shape: {excel_processor.df.shape}")
            print(f"DataFrame columns: {list(excel_processor.df.columns)}")
            
            # Check if LIFTED CANNABIS data exists
            if 'Vendor/Supplier*' in excel_processor.df.columns:
                lifted_df = excel_processor.df[excel_processor.df['Vendor/Supplier*'] == 'LIFTED CANNABIS']
                print(f"LIFTED CANNABIS rows: {len(lifted_df)}")
                
                if len(lifted_df) > 0:
                    # Check for meta strains
                    meta_strains = lifted_df[lifted_df['Product Strain'].str.contains('meta', case=False, na=False)]
                    print(f"Meta strains found: {len(meta_strains)}")
                    if len(meta_strains) > 0:
                        print("Meta strains:")
                        print(meta_strains[['Product Name*', 'Product Strain', 'Product Brand']].to_string())
                    
                    # Show some sample strains
                    print(f"\nSample strains from LIFTED CANNABIS:")
                    sample_strains = lifted_df['Product Strain'].dropna().head(10).tolist()
                    for i, strain in enumerate(sample_strains, 1):
                        print(f"{i}. {strain}")
                else:
                    print("No LIFTED CANNABIS products found!")
            else:
                print("No Vendor/Supplier* column found!")
                
            # Check what file was loaded
            if hasattr(excel_processor, '_last_loaded_file'):
                print(f"\nLast loaded file: {excel_processor._last_loaded_file}")
        else:
            print("DataFrame is None!")
    else:
        print("Excel processor is None!")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
