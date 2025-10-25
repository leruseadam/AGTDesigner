#!/usr/bin/env python3
"""
Test the SKU search logic to see what search terms are generated
"""

def extract_keywords_from_sku(sku: str) -> set:
    """
    Extract searchable keywords from SKU for matching against database.
    Example: 'BALL_SAT_CARAMEL_10pk' -> {'ball', 'sativa', 'caramel', '10pk'}
    """
    if not sku or not isinstance(sku, str):
        return set()
    
    keywords = set()
    parts = sku.split('_')
    
    # Mappings for abbreviations
    lineage_map = {'SAT': 'sativa', 'IND': 'indica', 'MIXED': 'mixed'}
    product_map = {'BALL': 'ball', 'BITE': 'bite', 'CHEW': 'chew', 'CAPS': 'capsule', 
                   'TINCS': 'tincture', 'JAR': 'jar', 'SQUEEZE': 'squeeze', 'ROLL': 'roll'}
    
    for part in parts:
        part_lower = part.lower()
        # Add the expanded version if it's an abbreviation
        keywords.add(lineage_map.get(part.upper(), part_lower))
        keywords.add(product_map.get(part.upper(), part_lower))
    
    return keywords

def test_sku_search():
    """Test SKU search logic"""
    
    test_skus = [
        'BALL_SAT_CARAMEL_10pk',
        'BITE_SAT_ASSORTED_10pk',
        'CHEW_SAT_CHERRY_10pk'
    ]
    
    for sku in test_skus:
        keywords = extract_keywords_from_sku(sku)
        print(f"SKU: {sku}")
        print(f"Keywords: {keywords}")
        
        # Test what SQL search would look like
        search_terms = list(keywords)[:3]  # Use top 3 most important terms
        print(f"Search terms: {search_terms}")
        
        # Build WHERE clause
        where_clauses = []
        params = []
        for term in search_terms:
            where_clauses.append(f'("Product Name*" LIKE ? OR "Description" LIKE ?)')
            params.extend([f'%{term}%', f'%{term}%'])
        
        where_sql = ' AND '.join(where_clauses)
        where_sql += ' AND "Product Brand" = ?'
        params.append('Ceres')
        
        sql = f'''
            SELECT "Product Name*", "Description", "Product Brand", "Lineage", 
                   "Product Type*", "Weight*", "Units", "Price", "Vendor/Supplier*",
                   "Product Strain"
            FROM products
            WHERE {where_sql}
            LIMIT 1
        '''
        
        print(f"SQL: {sql}")
        print(f"Params: {params}")
        print("-" * 50)

if __name__ == "__main__":
    test_sku_search()
