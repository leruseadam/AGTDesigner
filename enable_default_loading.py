#!/usr/bin/env python3
"""
Script to enable default file loading and test JSON matching
"""

import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def enable_default_loading():
    """Enable default file loading and test JSON matching."""
    print("=== Enabling Default File Loading ===")
    
    # Clear the environment variable that's disabling startup file loading
    if 'DISABLE_STARTUP_FILE_LOADING' in os.environ:
        del os.environ['DISABLE_STARTUP_FILE_LOADING']
        print("✅ Cleared DISABLE_STARTUP_FILE_LOADING environment variable")
    
    try:
        from src.core.data.excel_processor import ExcelProcessor
        
        # Initialize Excel processor (should now load default files)
        ep = ExcelProcessor()
        print("✅ Excel processor initialized")
        
        # Check if DataFrame is loaded
        print(f"DataFrame loaded: {ep.df is not None}")
        
        if ep.df is not None:
            print(f"Columns: {list(ep.df.columns)}")
            print(f"Row count: {len(ep.df)}")
            
            if len(ep.df) > 0:
                print("\n✅ SUCCESS: Default file loaded with products!")
                print("Sample products:")
                
                # Try to get key columns
                key_columns = []
                for col in ['Product Name*', 'Product Name', 'product_name', 'ProductName']:
                    if col in ep.df.columns:
                        key_columns.append(col)
                        break
                
                brand_columns = []
                for col in ['Product Brand', 'Brand', 'brand', 'ProductBrand']:
                    if col in ep.df.columns:
                        brand_columns.append(col)
                        break
                
                strain_columns = []
                for col in ['Product Strain', 'Strain', 'strain', 'ProductStrain']:
                    if col in ep.df.columns:
                        strain_columns.append(col)
                        break
                
                if key_columns and brand_columns and strain_columns:
                    sample_data = ep.df[[key_columns[0], brand_columns[0], strain_columns[0]]].head(5)
                    print(sample_data.to_string())
                    
                    print(f"\n🎯 Now you can test JSON matching with the Bamboo manifest!")
                    print(f"Products available for matching: {len(ep.df)}")
                else:
                    print("Key columns not found for display")
            else:
                print("DataFrame is empty - no products available for matching")
        else:
            print("❌ No DataFrame loaded - default file loading still not working")
            
    except Exception as e:
        print(f"❌ Error testing Excel data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    enable_default_loading()
