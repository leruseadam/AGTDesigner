#!/usr/bin/env python3
"""
Debug script to understand why only 2 out of 86 matches are being processed.
Simulates the actual application flow.
"""

import sys
import os
import logging
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

def debug_86_matches_issue():
    """Debug the 86 matches issue by simulating the application flow."""
    print("Debugging 86 Matches Issue")
    print("=" * 50)
    
    # Simulate the application flow
    try:
        # Get Excel processor (same as main app)
        from app import get_excel_processor
        excel_processor = get_excel_processor()
        excel_processor.enable_product_db_integration(False)
        
        print("✓ Excel processor initialized")
        
        # Check if data is loaded
        if excel_processor.df is None or excel_processor.df.empty:
            print("❌ No data loaded in Excel processor")
            print("This suggests the Excel file hasn't been loaded yet")
            return
        
        print(f"✓ Data loaded: {len(excel_processor.df)} total records")
        
        # Check available columns
        print(f"\nAvailable columns: {list(excel_processor.df.columns)}")
        
        # Check for product name column
        product_name_col = 'ProductName'
        if product_name_col not in excel_processor.df.columns:
            print(f"❌ ProductName column not found")
            return
        
        print(f"✓ Using product name column: {product_name_col}")
        
        # Check selected tags
        selected_tags = excel_processor.get_selected_tags()
        print(f"\nSelected tags: {selected_tags}")
        print(f"Number of selected tags: {len(selected_tags)}")
        
        if not selected_tags:
            print("❌ No tags selected - this is the root cause!")
            print("The system found 86 matches but no tags were selected for processing")
            return
        
        # Analyze what happens in get_selected_records
        print(f"\nAnalyzing get_selected_records processing...")
        
        # Simulate the exact logic from get_selected_records
        try:
            # Build canonical mapping
            from src.core.data.excel_processor import normalize_name
            canonical_map = {normalize_name(name): name for name in excel_processor.df[product_name_col]}
            print(f"✓ Canonical map created with {len(canonical_map)} entries")
            
            # Map selected tags to canonical names
            canonical_selected = [canonical_map.get(normalize_name(tag)) for tag in selected_tags if canonical_map.get(normalize_name(tag))]
            print(f"✓ Canonical selected tags: {canonical_selected}")
            print(f"  Number of canonical matches: {len(canonical_selected)}")
            
            if not canonical_selected:
                print("❌ No canonical matches found - this explains the filtering!")
                print("The selected tags don't match the actual data in the Excel file")
                return
            
            # Filter DataFrame to only include selected records
            filtered_df = excel_processor.df[excel_processor.df[product_name_col].isin(canonical_selected)]
            print(f"✓ Filtered DataFrame: {len(filtered_df)} records")
            
            # Convert to list of dictionaries
            records = filtered_df.to_dict('records')
            print(f"✓ Converted to {len(records)} records")
            
            # Now check what happens in the record processing
            print(f"\nAnalyzing record processing...")
            
            processed_records = []
            for record in records:
                try:
                    # Simulate the processing logic
                    product_name = record.get(product_name_col, '').strip()
                    product_type = str(record.get('Product Type*', '')).strip().lower()
                    
                    # Check if this record would be filtered out
                    if (
                        'trade sample' in product_type or
                        'sample' in product_name.lower() or
                        'trade sample' in product_name.lower()
                    ):
                        print(f"⚠️  Record '{product_name}' would be filtered out due to sample/trade sample")
                        continue
                    
                    # Check for required fields
                    required_fields = ['Product Name*', 'Price', 'Lineage']
                    missing_fields = [field for field in required_fields if not record.get(field) or str(record.get(field)).strip() == '']
                    
                    if missing_fields:
                        print(f"⚠️  Record '{product_name}' missing required fields: {missing_fields}")
                        continue
                    
                    processed_records.append(record)
                    print(f"✓ Record '{product_name}' processed successfully")
                    
                except Exception as e:
                    print(f"❌ Error processing record: {e}")
                    continue
            
            print(f"\nFinal Results:")
            print(f"  Total records in Excel: {len(excel_processor.df)}")
            print(f"  Selected tags: {len(selected_tags)}")
            print(f"  Canonical matches: {len(canonical_selected)}")
            print(f"  Filtered records: {len(filtered_df)}")
            print(f"  Successfully processed: {len(processed_records)}")
            
            if len(processed_records) == 2:
                print(f"\n✅ This explains why only 2 tags are generated!")
                print(f"The other {len(records) - len(processed_records)} records were filtered out during processing")
            else:
                print(f"\n❓ Unexpected result - should have 2 processed records")
            
        except Exception as e:
            print(f"❌ Error in get_selected_records simulation: {e}")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        print(f"❌ Error in main flow simulation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_86_matches_issue()
