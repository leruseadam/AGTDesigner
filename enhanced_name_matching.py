#!/usr/bin/env python3
"""
Enhanced name matching to improve JSON-to-database product matching
"""

import re

def enhanced_normalize_product_name(product_name: str) -> str:
    """Enhanced normalization to better match JSON names with database names."""
    if not isinstance(product_name, str):
        return ""
    
    # Start with basic normalization
    name = product_name.lower().strip()
    
    # Remove common prefixes/suffixes that differ between JSON and DB
    # Common patterns in CERES products
    brand_removals = [
        r'\bby\s+ceres\b',
        r'\bceres\s*-\s*\d+\b',  # Remove "CERES - 435011" style
        r'\bceres\b',
        r'\bby\s+\w+\b',  # "by [brand]"
    ]
    
    for pattern in brand_removals:
        name = re.sub(pattern, '', name, flags=re.IGNORECASE)
    
    # Normalize common variations
    name = re.sub(r'\bthc\b', 'thc', name)
    name = re.sub(r'\bcbd\b', 'cbd', name)
    name = re.sub(r'\bcbg\b', 'cbg', name)
    name = re.sub(r'\bcbn\b', 'cbn', name)
    
    # Normalize dosage formats
    name = re.sub(r'(\d+)\s*mg\s*thc', r'\1mg thc', name)
    name = re.sub(r'(\d+)\s*mg\s*cbd', r'\1mg cbd', name)
    name = re.sub(r'(\d+)\s*mg', r'\1mg', name)
    
    # Normalize product type variations
    type_normalizations = {
        'choco bites': 'chocolate bites',
        'soft chews': 'chews', 
        'fruit chews': 'chews',
        'chocolate bites': 'bites',
        'assorted': 'mixed',
    }
    
    for old, new in type_normalizations.items():
        name = re.sub(r'\b' + re.escape(old) + r'\b', new, name)
    
    # Remove extra words that might differ
    removal_words = [
        r'\bsingle\b',
        r'\b10pk\b', r'\b10pack\b', r'\b10\s*pack\b',
        r'\bpackage\b', r'\bpkg\b',
        r'\b\d+\s*piece\b', r'\b\d+\s*pc\b',
        r'\bcount\b', r'\bct\b',
    ]
    
    for pattern in removal_words:
        name = re.sub(pattern, '', name, flags=re.IGNORECASE)
    
    # Clean up formatting
    name = re.sub(r'\u2011', '-', name)  # non-breaking hyphen
    name = re.sub(r'[-\s]+', ' ', name)  # collapse spaces and hyphens
    name = re.sub(r'[^\w\s]', '', name)  # remove punctuation except space
    name = re.sub(r'\s+', ' ', name)  # collapse multiple spaces
    
    return name.strip()

def create_fuzzy_variations(product_name: str) -> list:
    """Create variations of a product name for fuzzy matching."""
    variations = [enhanced_normalize_product_name(product_name)]
    
    base_name = enhanced_normalize_product_name(product_name)
    
    # Add variation without dosage
    no_dosage = re.sub(r'\d+mg.*', '', base_name).strip()
    if no_dosage and no_dosage != base_name:
        variations.append(no_dosage)
    
    # Add variation without strain type
    no_strain = re.sub(r'\b(indica|sativa|hybrid)\b', '', base_name).strip()
    if no_strain and no_strain != base_name:
        variations.append(no_strain)
    
    # Add variation with common words removed
    minimal = re.sub(r'\b(chocolate|choco|fruit|soft|mixed|assorted)\b', '', base_name).strip()
    if minimal and minimal not in variations:
        variations.append(minimal)
    
    return list(set(variations))

def test_enhanced_matching():
    """Test the enhanced matching with sample CERES products."""
    
    # Sample JSON names vs Database names from your output
    test_pairs = [
        ("Indica PM Tincture 100mg THC", "Indica PM Tincture by Ceres - 100mg THC"),
        ("Milk Chocolate Sativa Bites 100mg", "Milk Chocolate Sativa Bites by Ceres - 100mg"),
        ("1:1 Balance Capsules 200mg", "1:1 Balance Capsules by Ceres - 100mg THC / 100mg CBD"),
        ("Assorted Indica Chocolate Bites", "Assorted Indica Chocolate Bites by Ceres - 100mg"),
        ("Watermelon Fruit Chews Single", "Watermelon Indica Fruit Chew Single by Ceres - 10mg THC"),
    ]
    
    print("=" * 80)
    print("TESTING ENHANCED PRODUCT NAME MATCHING")
    print("=" * 80)
    
    for json_name, db_name in test_pairs:
        json_normalized = enhanced_normalize_product_name(json_name)
        db_normalized = enhanced_normalize_product_name(db_name)
        
        json_variations = create_fuzzy_variations(json_name)
        db_variations = create_fuzzy_variations(db_name)
        
        # Check for any overlap in variations
        matches = set(json_variations) & set(db_variations)
        
        print(f"\n🧪 TEST CASE:")
        print(f"   JSON: '{json_name}'")
        print(f"   DB:   '{db_name}'")
        print(f"   JSON normalized: '{json_normalized}'")
        print(f"   DB normalized:   '{db_normalized}'")
        print(f"   Direct match: {'✅ YES' if json_normalized == db_normalized else '❌ NO'}")
        print(f"   Fuzzy matches: {len(matches)} overlaps")
        if matches:
            print(f"   Overlap: {list(matches)}")

if __name__ == "__main__":
    test_enhanced_matching()