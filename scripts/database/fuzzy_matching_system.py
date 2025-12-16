#!/usr/bin/env python3
"""
Create a fuzzy matching system for JSON vs Database product names
"""

import re
import sys
import os

# Add the src directory to path
sys.path.append('src')

def decode_json_abbreviations(json_name: str) -> str:
    """Decode JSON abbreviations to full product names."""
    decoded = json_name.lower().strip()
    
    # Decode product type abbreviations
    type_mappings = {
        'ball': 'chocolate ball',
        'bite': 'chocolate bites', 
        'chew': 'fruit chews',
        'caps': 'capsules',
        'tincs': 'tincture',
        'jar': 'balm',
        'squeeze_tube': 'squeeze tube',
        'roll_ups': 'roll up',
    }
    
    # Decode strain abbreviations
    strain_mappings = {
        'sat': 'sativa',
        'ind': 'indica',
    }
    
    # Decode flavor/type abbreviations
    flavor_mappings = {
        'caramel': 'salted caramel',
        'assorted': 'assorted',
        'dark': 'dark chocolate',
        'milk': 'milk chocolate',
        'cookies&cream': 'cookies cream',
        'dragon': 'dragon',
        'malt': 'malt',
        'cherry': 'cherry',
        'mango': 'mango',
        'watermelon': 'watermelon',
        'sour_apple': 'sour apple',
        'tropical': 'tropical',
        'mixed_berry': 'mixed berry',
        'guava': 'guava',
        'balance': 'balance',
        'chill': 'chill',
        'lifted': 'lifted',
        'relief': 'relief',
        'gold_max': 'max gold',
        'xtra': 'xtra strength',
    }
    
    # Split and decode
    parts = decoded.replace('_', ' ').split()
    decoded_parts = []
    
    for part in parts:
        if part in type_mappings:
            decoded_parts.append(type_mappings[part])
        elif part in strain_mappings:
            decoded_parts.append(strain_mappings[part])
        elif part in flavor_mappings:
            decoded_parts.append(flavor_mappings[part])
        elif part.endswith('pk'):
            continue  # Skip pack indicators
        else:
            decoded_parts.append(part)
    
    return ' '.join(decoded_parts)

def extract_key_words(product_name: str) -> set:
    """Extract key identifying words from a product name."""
    
    # First decode if it's a JSON abbreviation
    if '_' in product_name and any(c.isupper() for c in product_name):
        name = decode_json_abbreviations(product_name)
    else:
        name = product_name.lower()
    
    # Remove brand info
    name = re.sub(r'\bby\s+ceres\b', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\bceres\s*-\s*\d+\b', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\bceres\b', '', name, flags=re.IGNORECASE)
    
    # Remove common filler words
    filler_words = {
        'by', 'the', 'a', 'an', 'and', 'or', 'of', 'in', 'on', 'at', 'to', 
        'for', 'with', 'from', 'up', 'about', 'into', 'through', 'during',
        'before', 'after', 'above', 'below', 'between', 'among', 'through',
        'pack', 'pk', 'single', '10', '20', 'mg', 'thc', 'cbd', 'cbg', 'cbn'
    }
    
    # Split into words and filter
    words = re.findall(r'\b\w+\b', name.lower())
    key_words = set()
    
    for word in words:
        if len(word) >= 3 and word not in filler_words:
            key_words.add(word)
    
    return key_words

def fuzzy_match_products(json_name: str, db_name: str, threshold: float = 0.4) -> tuple:
    """Calculate fuzzy match score between JSON and database product names."""
    
    json_words = extract_key_words(json_name)
    db_words = extract_key_words(db_name)
    
    if not json_words or not db_words:
        return False, 0.0, set(), json_words, db_words
    
    # Find intersection
    common_words = json_words & db_words
    
    # Calculate Jaccard similarity
    union_words = json_words | db_words
    jaccard_score = len(common_words) / len(union_words) if union_words else 0.0
    
    # Calculate overlap percentage for JSON words (how many JSON words are found in DB)
    json_coverage = len(common_words) / len(json_words) if json_words else 0.0
    
    # Use the higher of the two scores
    final_score = max(jaccard_score, json_coverage)
    
    is_match = final_score >= threshold
    
    return is_match, final_score, common_words, json_words, db_words

def test_fuzzy_matching():
    """Test fuzzy matching with real product pairs."""
    
    test_cases = [
        ('BALL_SAT_CARAMEL_10pk', 'Sativa Salted Caramel Chocolate Ball Single by Ceres - 10mg THC'),
        ('BITE_SAT_ASSORTED_10pk', 'Sativa Assorted Chocolate by Ceres - 100mg THC'),
        ('BITE_SAT_DARK_10pk', 'Dark Chocolate Sativa Bites by Ceres - 100mg THC'),
        ('BITE_SAT_MILK_10pk', 'Milk Chocolate Sativa Bites by Ceres - 100mg'),
        ('CHEW_SAT_CHERRY_10pk', 'Sativa Cherry Fruit Chews by Ceres - 100mg THC'),
        ('CAPS_BALANCE_1000_10pk', 'Balance 1000 Capsules by Ceres - 1000mg CBD / 50mg CBG / 50mg CBN / 3mg THC'),
    ]
    
    print('FUZZY MATCHING TEST RESULTS:')
    print('=' * 80)
    
    for json_name, db_name in test_cases:
        is_match, score, common, json_words, db_words = fuzzy_match_products(json_name, db_name)
        
        print(f'JSON: {json_name}')
        print(f'DB:   {db_name}')
        print(f'Decoded JSON: {decode_json_abbreviations(json_name)}')
        print(f'JSON words: {sorted(json_words)}')
        print(f'DB words:   {sorted(db_words)}')
        print(f'Common:     {sorted(common)}')
        print(f'Score:      {score:.3f}')
        print(f'Result:     {"✅ MATCH" if is_match else "❌ NO MATCH"}')
        print()

def create_fuzzy_matcher_patch():
    """Create a patch for the product database to use fuzzy matching."""
    
    patch_code = '''
def enhanced_get_products_by_names_with_fuzzy(self, product_names: List[str]) -> List[Dict[str, Any]]:
    """Enhanced product lookup with fuzzy matching for JSON abbreviations."""
    
    # First try exact matching
    exact_results = self.get_products_by_names(product_names)
    
    # Count how many exact matches we got
    exact_matches = [r for r in exact_results if r.get('id') is not None]
    
    if len(exact_matches) >= len(product_names) * 0.8:  # If we got 80%+ exact matches
        return exact_results
    
    # Otherwise, try fuzzy matching for missing items
    print(f"🔍 FUZZY MATCHING: Only {len(exact_matches)}/{len(product_names)} exact matches found")
    
    # Get all CERES products for fuzzy matching
    conn = self._get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, "Product Name*", normalized_name, "Vendor/Supplier*"
        FROM products 
        WHERE "Vendor/Supplier*" LIKE '%CERES%'
        LIMIT 500
    """)
    
    ceres_products = cursor.fetchall()
    print(f"🔍 FUZZY MATCHING: Checking against {len(ceres_products)} CERES products")
    
    # Create fuzzy matching results
    fuzzy_results = []
    
    for product_name in product_names:
        best_match = None
        best_score = 0.0
        
        # Check if we already have an exact match
        exact_match = None
        for result in exact_results:
            if result.get('Product Name*') == product_name or result.get('normalized_name') == self._normalize_product_name(product_name):
                exact_match = result
                break
        
        if exact_match and exact_match.get('id'):
            fuzzy_results.append(exact_match)
            continue
        
        # Try fuzzy matching
        for db_product in ceres_products:
            db_name = db_product[1]  # Product Name*
            
            is_match, score, common, json_words, db_words = fuzzy_match_products(product_name, db_name)
            
            if score > best_score and score >= 0.4:  # 40% threshold
                best_score = score
                best_match = db_product
        
        if best_match:
            print(f"🔍 FUZZY MATCH: '{product_name}' -> '{best_match[1]}' (score: {best_score:.3f})")
            
            # Get full product info
            full_products = self.get_products_by_names([best_match[1]])
            if full_products and full_products[0].get('id'):
                fuzzy_results.append(full_products[0])
            else:
                # Create placeholder
                fuzzy_results.append({
                    'ProductName': product_name,
                    'Product Name*': product_name,
                    'Description': product_name,
                    'Vendor': '',
                    'Vendor/Supplier*': '',
                })
        else:
            print(f"🔍 FUZZY NO MATCH: '{product_name}' - no suitable match found")
            # Create placeholder
            fuzzy_results.append({
                'ProductName': product_name,
                'Product Name*': product_name,
                'Description': product_name,
                'Vendor': '',
                'Vendor/Supplier*': '',
            })
    
    return fuzzy_results
'''
    
    print("FUZZY MATCHER PATCH:")
    print("=" * 50)
    print("This code can be added to ProductDatabase class")
    print("to enable fuzzy matching for JSON abbreviations")
    print()
    print(patch_code)

if __name__ == "__main__":
    test_fuzzy_matching()
    print("\n" + "=" * 80)
    create_fuzzy_matcher_patch()