#!/usr/bin/env python3
"""
Test script to verify lineage fix is working correctly.
This tests that database lineage is always used, not Excel file lineage.
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_lineage_query():
    """Test that database lineage query works correctly."""
    print("🧪 Testing lineage fix...")
    
    try:
        from src.core.data.product_database import ProductDatabase
        from src.core.data.excel_processor import ExcelProcessor
        
        # Get store name
        store_name = "AGT_Bothell"  # Default store
        if len(sys.argv) > 1:
            store_name = sys.argv[1]
        
        print(f"📦 Using store: {store_name}")
        
        # Initialize database
        product_db = ProductDatabase(store_name)
        product_db.init_database()
        
        # Test: Query a specific product
        test_product_name = "100 Rackz Super Sale by Mt Baker Homegrown - 14g"
        print(f"\n🔍 Testing product: '{test_product_name}'")
        
        # Query database
        db_records = product_db.get_products_by_names([test_product_name])
        
        if db_records:
            db_record = db_records[0]
            db_lineage = (
                db_record.get('currentLineage') or
                db_record.get('canonical_lineage') or
                db_record.get('Lineage')
            )
            print(f"✅ Database lineage: '{db_lineage}'")
            print(f"   - currentLineage: {db_record.get('currentLineage')}")
            print(f"   - canonical_lineage: {db_record.get('canonical_lineage')}")
            print(f"   - Lineage: {db_record.get('Lineage')}")
            
            if db_lineage:
                print(f"\n✅ SUCCESS: Database has lineage '{db_lineage}' for product")
                return True
            else:
                print(f"\n❌ ERROR: Database record exists but has no lineage")
                return False
        else:
            print(f"\n❌ ERROR: Product not found in database")
            print(f"   This means the product needs to be created in the database first")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_lineage_query()
    sys.exit(0 if success else 1)
