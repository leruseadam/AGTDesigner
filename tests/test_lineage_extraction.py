#!/usr/bin/env python3
"""
Quick test to verify lineage extraction from database is working correctly.
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.data.product_database import get_product_database
from src.core.data.excel_processor import ExcelProcessor

print("=" * 80)
print("LINEAGE EXTRACTION TEST")
print("=" * 80)

try:
    # Get product database - try to get store name from app or use default
    print("\n1. Getting product database...")
    try:
        from app import get_current_store_name
        store_name = get_current_store_name()
        print(f"   Store name: '{store_name}'")
    except:
        # Default to Bothell if we can't get it from app
        store_name = "AGT_Bothell"
        print(f"   Using default store: '{store_name}'")
    
    product_db = get_product_database(store_name=store_name)
    if not product_db:
        print("   ❌ ERROR: product_db is None!")
        sys.exit(1)
    print(f"   ✅ Database loaded")
    
    # Test 1: Check what field name the database returns
    print("\n2. Testing database query field names...")
    test_products = ["Wedding Cake", "Blue Dream", "Girl Scout Cookies"]
    
    for product_name in test_products:
        products = product_db.get_products_by_names([product_name])
        if products:
            db_record = products[0]
            print(f"\n   Product: '{product_name}'")
            print(f"   Available fields: {list(db_record.keys())}")
            
            # Check all possible lineage fields
            lineage_fields = {
                'Lineage': db_record.get('Lineage'),
                'lineage': db_record.get('lineage'),
                'canonical_lineage': db_record.get('canonical_lineage'),
                'sovereign_lineage': db_record.get('sovereign_lineage'),
            }
            
            print(f"   Lineage values found:")
            for field, value in lineage_fields.items():
                if value:
                    print(f"     • {field}: '{value}'")
                else:
                    print(f"     • {field}: None")
    
    # Test 2: Simulate tag enrichment
    print("\n3. Testing tag enrichment logic...")
    test_tag = {
        'Product Name*': test_products[0] if test_products else 'Test Product',
        'Lineage': '',  # Empty initially
    }
    
    products = product_db.get_products_by_names([test_tag['Product Name*']])
    if products:
        db_record = products[0]
        
        # Simulate the enrichment logic
        db_lineage_value = db_record.get('Lineage') or db_record.get('lineage') or db_record.get('canonical_lineage') or db_record.get('sovereign_lineage')
        
        if db_lineage_value:
            db_lineage = str(db_lineage_value).strip().upper()
            test_tag['Lineage'] = db_lineage
            test_tag['lineage'] = db_lineage
            test_tag['canonical_lineage'] = db_lineage
            test_tag['currentLineage'] = db_lineage
            
            print(f"   ✅ Tag enriched successfully!")
            print(f"   Original tag lineage: '' (empty)")
            print(f"   Database lineage found: '{db_lineage_value}'")
            print(f"   Enriched tag fields:")
            print(f"     • Lineage: '{test_tag.get('Lineage')}'")
            print(f"     • lineage: '{test_tag.get('lineage')}'")
            print(f"     • canonical_lineage: '{test_tag.get('canonical_lineage')}'")
            print(f"     • currentLineage: '{test_tag.get('currentLineage')}'")
        else:
            print(f"   ⚠️  No lineage found in database for '{test_tag['Product Name*']}'")
    else:
        print(f"   ⚠️  Product '{test_tag['Product Name*']}' not found in database")
    
    # Test 3: Check cache version
    print("\n4. Checking cache version...")
    from src.core.data.excel_processor import TAGS_CACHE_VERSION
    print(f"   ✅ Current cache version: {TAGS_CACHE_VERSION}")
    print(f"   This means old cached tags (v2.0) will be invalidated")
    
    print("\n" + "=" * 80)
    print("✅ LINEAGE EXTRACTION TEST COMPLETED")
    print("=" * 80)
    print("\n💡 Next steps:")
    print("   1. Refresh your browser to clear the old cache")
    print("   2. Check the lineage dropdown in the UI")
    print("   3. Verify lineage values match the database")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
