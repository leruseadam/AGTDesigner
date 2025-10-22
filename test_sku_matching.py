#!/usr/bin/env python3
"""
Test SKU matching against database to verify the logic works.
"""

import sqlite3

def test_sku_matching():
    """Test SKU-based database matching."""
    
    db_path = 'uploads/product_database.db'
    
    # Test SKUs
    test_cases = [
        ('BALL_SAT_CARAMEL_10pk', ['ball', 'balls'], 'sativa', 'caramel'),
        ('BITE_IND_DARK_10pk', ['bite', 'bites'], 'indica', 'dark'),
        ('CHEW_SAT_CHERRY_10pk', ['chew', 'chews'], 'sativa', 'cherry'),
    ]
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("SKU Matching Test")
    print("=" * 100)
    
    for sku, product_terms, lineage, flavor in test_cases:
        print(f"\nSKU: {sku}")
        print(f"Search terms: {product_terms}, {lineage}, {flavor}")
        
        # Try each product term
        found = False
        for product_term in product_terms:
            sql = '''
                SELECT "Product Name*", "Description", "Price", "Weight*", "Units"
                FROM products
                WHERE ("Product Name*" LIKE ? OR "Description" LIKE ?)
                  AND ("Product Name*" LIKE ? OR "Description" LIKE ?)
                  AND ("Product Name*" LIKE ? OR "Description" LIKE ?)
                  AND "Product Brand" = 'Ceres'
                LIMIT 1
            '''
            
            params = [
                f'%{product_term}%', f'%{product_term}%',
                f'%{lineage}%', f'%{lineage}%',
                f'%{flavor}%', f'%{flavor}%'
            ]
            
            cursor.execute(sql, params)
            result = cursor.fetchone()
            
            if result:
                print(f"  ✅ MATCH FOUND (using '{product_term}'):")
                print(f"     Product Name*: {result[0]}")
                print(f"     Description:   {result[1]}")
                print(f"     Price:         {result[2]}")
                print(f"     Weight:        {result[3]} {result[4]}")
                found = True
                break
        
        if not found:
            print(f"  ❌ NO MATCH FOUND")
            # Try without brand filter
            sql = '''
                SELECT "Product Name*", "Description", "Price", "Weight*", "Units"
                FROM products
                WHERE ("Product Name*" LIKE ? OR "Description" LIKE ?)
                  AND ("Product Name*" LIKE ? OR "Description" LIKE ?)
                LIMIT 3
            '''
            
            params = [
                f'%{product_terms[0]}%', f'%{product_terms[0]}%',
                f'%{lineage}%', f'%{lineage}%'
            ]
            
            cursor.execute(sql, params)
            results = cursor.fetchall()
            
            if results:
                print(f"  📝 Similar products found (without brand filter):")
                for r in results:
                    print(f"     - {r[1]}")
    
    conn.close()
    print("\n" + "=" * 100)

if __name__ == "__main__":
    test_sku_matching()

