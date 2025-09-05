#!/usr/bin/env python3
"""
Test script to check if the strain database is causing issues during label generation.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.data.product_database import get_product_database
from src.core.data.excel_processor import get_excel_processor

def test_strain_database():
    """Test the strain database functionality."""
    
    print("Testing strain database...")
    
    try:
        # Test product database
        print("1. Testing product database...")
        product_db = get_product_database()
        if product_db:
            print("   ✅ Product database available")
            
            # Test getting strain info
            test_strain = "Blue Dream"
            strain_info = product_db.get_strain_info(test_strain)
            if strain_info:
                print(f"   ✅ Strain info for '{test_strain}': {strain_info.get('canonical_lineage', 'N/A')}")
            else:
                print(f"   ⚠️  No strain info for '{test_strain}'")
        else:
            print("   ❌ Product database not available")
        
        # Test Excel processor
        print("\n2. Testing Excel processor...")
        excel_processor = get_excel_processor()
        if excel_processor:
            print("   ✅ Excel processor available")
            
            if excel_processor.df is not None:
                print(f"   ✅ Data loaded: {excel_processor.df.shape}")
                
                # Test getting selected records
                print("\n3. Testing selected records processing...")
                try:
                    # Test with a simple template type
                    records = excel_processor.get_selected_records('horizontal')
                    print(f"   ✅ Selected records processing: {len(records) if records else 0} records")
                except Exception as e:
                    print(f"   ❌ Error processing selected records: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print("   ❌ No data loaded in Excel processor")
        else:
            print("   ❌ Excel processor not available")
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_strain_database()
