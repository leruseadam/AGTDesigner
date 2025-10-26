#!/usr/bin/env python3
"""
Advanced name matching that can decode JSON abbreviations to match database names
"""

import re

def decode_json_abbreviations(json_name: str) -> str:
    """Decode JSON abbreviations to full product names."""
    
    # Start with the original name
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
        'mix': 'mixed',
        'hybrid': 'hybrid',
    }
    
    # Decode flavor/type abbreviations
    flavor_mappings = {
        'caramel': 'salted caramel',
        'assorted': 'assorted',
        'dark': 'dark chocolate',
        'milk': 'milk chocolate',
        'cookies&cream': 'cookies and cream',
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
    
    # Decode pack size
    pack_mappings = {
        '10pk': '10 pack',
        '20pk': '20 pack',
        'single': 'single',
    }
    
    # Split the JSON name into parts
    parts = decoded.replace('_', ' ').split()
    decoded_parts = []
    
    for part in parts:
        # Check each mapping
        if part in type_mappings:
            decoded_parts.append(type_mappings[part])
        elif part in strain_mappings:
            decoded_parts.append(strain_mappings[part])
        elif part in flavor_mappings:
            decoded_parts.append(flavor_mappings[part])
        elif part in pack_mappings:
            decoded_parts.append(pack_mappings[part])
        else:
            decoded_parts.append(part)
    
    return ' '.join(decoded_parts)

def enhanced_normalize_product_name(product_name: str) -> str:
    """Enhanced normalization for better matching."""
    if not isinstance(product_name, str):
        return ""
    
    # First decode if it looks like a JSON abbreviation
    if '_' in product_name and any(c.isupper() for c in product_name):
        name = decode_json_abbreviations(product_name)
    else:
        name = product_name.lower().strip()
    
    # Remove brand information
    brand_removals = [
        r'\bby\s+ceres\b',
        r'\bceres\s*-\s*\d+\b',
        r'\bceres\b',
        r'\bby\s+\w+\b',
    ]
    
    for pattern in brand_removals:
        name = re.sub(pattern, '', name, flags=re.IGNORECASE)
    
    # Normalize dosage formats
    name = re.sub(r'(\d+)\s*mg\s*thc', r'\1mg thc', name)
    name = re.sub(r'(\d+)\s*mg\s*cbd', r'\1mg cbd', name)
    name = re.sub(r'(\d+)\s*mg', r'\1mg', name)
    
    # Remove common variations that differ
    name = re.sub(r'\b(pack|pk|single)\b', '', name)
    name = re.sub(r'\b\d+\s*(pack|pk)\b', '', name)
    
    # Clean up
    name = re.sub(r'[-\s]+', ' ', name)
    name = re.sub(r'[^\w\s]', '', name)
    name = re.sub(r'\s+', ' ', name)
    
    return name.strip()

def create_search_variations(product_name: str) -> list:
    """Create multiple search variations for fuzzy matching."""
    base_name = enhanced_normalize_product_name(product_name)
    variations = [base_name]
    
    # Add variation without dosage
    no_dosage = re.sub(r'\d+mg.*', '', base_name).strip()
    if no_dosage and no_dosage != base_name:
        variations.append(no_dosage)
    
    # Add variation with just key words
    key_words = []
    for word in base_name.split():
        if len(word) > 3 and word not in ['chocolate', 'fruit', 'single']:
            key_words.append(word)
    
    if len(key_words) >= 2:
        variations.append(' '.join(key_words))
    
    return list(set(variations))

# Test with actual data
test_cases = [
    ('BALL_SAT_CARAMEL_10pk', 'Sativa Salted Caramel Chocolate Ball Single by Ceres - 10mg THC'),
    ('BITE_SAT_ASSORTED_10pk', 'Sativa Assorted Chocolate by Ceres - 100mg THC'),
    ('BITE_SAT_DARK_10pk', 'Dark Chocolate Sativa Bites by Ceres - 100mg THC'),
    ('BITE_SAT_MILK_10pk', 'Milk Chocolate Sativa Bites by Ceres - 100mg'),
    ('CHEW_SAT_CHERRY_10pk', 'Sativa Cherry Fruit Chews by Ceres - 100mg THC'),
    ('CAPS_BALANCE_1000_10pk', 'Balance 1000 Capsules by Ceres - 1000mg CBD / 50mg CBG / 50mg CBN / 3mg THC'),
]

print('TESTING ADVANCED DECODING AND MATCHING:')
print('=' * 70)

for json_name, db_name in test_cases:
    print(f'JSON: {json_name}')
    
    # Show decoding process
    decoded = decode_json_abbreviations(json_name)
    print(f'  Decoded: {decoded}')
    
    json_norm = enhanced_normalize_product_name(json_name)
    db_norm = enhanced_normalize_product_name(db_name)
    
    print(f'  JSON normalized: {json_norm}')
    print(f'  DB normalized:   {db_norm}')
    
    # Create variations
    json_variations = create_search_variations(json_name)
    db_variations = create_search_variations(db_name)
    
    # Check for any matches
    matches = set(json_variations) & set(db_variations)
    
    print(f'  JSON variations: {json_variations}')
    print(f'  DB variations:   {db_variations}')
    print(f'  Matches: {list(matches) if matches else "None"}')
    print(f'  Result: {"✅ MATCH" if matches else "❌ NO MATCH"}')
    print()