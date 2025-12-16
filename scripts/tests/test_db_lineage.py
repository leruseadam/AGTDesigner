#!/usr/bin/env python3
"""
Test database lineage retrieval for DOCX generation
"""
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

print("=" * 80)
print("DATABASE LINEAGE TEST FOR DOCX GENERATION")
print("=" * 80)

try:
    # Try to import and use the database directly
    from app import get_product_database, get_current_store_name
    
    print("\n1. Getting store name...")
    store_name = get_current_store_name()
    print(f"   Store: '{store_name}'")
    
    print("\n2. Getting product database...")
    product_db = get_product_database(store_name)
    if not product_db:
        print("   ❌ ERROR: product_db is None!")
        sys.exit(1)
    print(f"   ✅ Database loaded: {type(product_db)}")
    
    print("\n3. Testing lineage query for a sample product...")
    test_products = ["Wedding Cake", "Blue Dream", "Girl Scout Cookies"]
    
    for product_name in test_products:
        lineage = product_db.get_product_lineage(product_name)
        print(f"   Product: '{product_name}' -> Lineage: '{lineage}'")
    
    print("\n4. Testing batch query (like DOCX generation)...")
    conn = product_db._get_connection()
    cur = conn.cursor()
    
    # Get all products with lineage
    query = 'SELECT "Product Name*", "Lineage" FROM products WHERE "Lineage" IS NOT NULL AND "Lineage" != "" LIMIT 10'
    cur.execute(query)
    results = cur.fetchall()
    
    print(f"   Found {len(results)} products with lineage:")
    for pname, lineage in results[:5]:
        print(f"     • '{pname}' -> '{lineage}'")
    
    print("\n" + "=" * 80)
    print("✅ DATABASE TEST COMPLETED SUCCESSFULLY")
    print("=" * 80)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
