#!/usr/bin/env python3
"""
Test script to debug the matching logic
"""

import pandas as pd

def extract_vendor(name):
    # If "Medically Compliant -" prefix, use the next part and take the first two words as brand
    if name.lower().startswith("medically compliant -"):
        after_prefix = name.split("-", 1)[1].strip()
        brand_words = after_prefix.split()
        if brand_words:
            return " ".join(brand_words[:2]).lower()
        return after_prefix.lower()
    # Otherwise, use the first two words before the next dash
    parts = name.split("-", 1)
    brand_words = parts[0].strip().split()
    return " ".join(brand_words[:2]).lower() if brand_words else ""

def extract_key_words(name):
    """Extract meaningful product words, excluding common prefixes/suffixes."""
    name_lower = name.lower()
    words = set(name_lower.replace('-', ' ').replace('_', ' ').split())
    common_words = {
        'medically', 'compliant', 'all', 'in', 'one', '1g', '2g', '3.5g', '7g', '14g', '28g', 'oz', 'gram', 'grams',
        'pk', 'pack', 'packs', 'piece', 'pieces', 'roll', 'rolls', 'stix', 'stick', 'sticks', 'brand', 'vendor', 'product'
    }
    return words - common_words

def test_matching():
    # Load Excel data
    df = pd.read_excel('uploads/A Greener Today - Bothell_inventory_07-07-2025 10_19 AM.xlsx')
    
    # Filter for cannabis-related products
    cannabis_keywords = ['rosin', 'thc', 'cbd', 'cannabis', 'marijuana', 'weed', 'dank', 'medically', 'compliant', 'czar']
    cannabis_products = df[df['Product Name*'].str.lower().str.contains('|'.join(cannabis_keywords), na=False)]
    available_tags = cannabis_products.to_dict('records')
    
    # Sample JSON names (from your Cultivera data)
    json_names = [
        "Medically Compliant - Dank Czar Rosin All-In-One - GMO - 1g",
        "Medically Compliant - Dank Czar Rosin All-In-One - Grape Gas - 1g",
        "Medically Compliant - Melt Stix - F: Elephant Garlic H: Cookies & Cream - 2pk"
    ]
    
    print("=== TESTING MATCHING LOGIC ===\n")
    print(f"Found {len(cannabis_products)} cannabis-related products in Excel\n")
    
    # Test vendor extraction
    print("Vendor extraction test:")
    for name in json_names:
        vendor = extract_vendor(name)
        key_words = extract_key_words(name)
        print(f"'{name}' -> vendor: '{vendor}', key_words: {key_words}")
    
    print("\nCannabis product names (first 10):")
    for i, tag in enumerate(available_tags[:10]):
        tag_name = tag.get('Product Name*', '')
        vendor = extract_vendor(tag_name)
        key_words = extract_key_words(tag_name)
        print(f"{i+1}. '{tag_name}' -> vendor: '{vendor}', key_words: {key_words}")
    
    # Test matching logic
    print("\n=== MATCHING TEST ===")
    for json_name in json_names:
        print(f"\nTesting: '{json_name}'")
        json_lower = json_name.lower()
        json_vendor = extract_vendor(json_name)
        json_key_words = extract_key_words(json_name)
        
        found = None
        
        # Strategy 1: Exact match
        for tag in available_tags[:20]:  # Test first 20 tags
            tag_name = str(tag.get('Product Name*', '')).strip().lower()
            if json_lower == tag_name:
                found = tag
                print(f"  ✓ EXACT MATCH: '{tag.get('Product Name*', '')}'")
                break
        
        # Strategy 2: Contains matching
        if not found:
            for tag in available_tags[:20]:
                tag_name = str(tag.get('Product Name*', '')).strip().lower()
                tag_vendor = extract_vendor(tag_name)
                
                vendor_ok = True
                if json_vendor and tag_vendor:
                    vendor_ok = json_vendor == tag_vendor
                
                if tag_name and vendor_ok:
                    if json_lower in tag_name or tag_name in json_lower:
                        found = tag
                        print(f"  ✓ CONTAINS MATCH: '{tag.get('Product Name*', '')}'")
                        break
        
        # Strategy 3: Word-based matching
        if not found and json_key_words:
            for tag in available_tags[:20]:
                tag_name = str(tag.get('Product Name*', '')).strip().lower()
                tag_vendor = extract_vendor(tag_name)
                tag_key_words = extract_key_words(tag_name)
                
                vendor_ok = True
                if json_vendor and tag_vendor:
                    vendor_ok = json_vendor == tag_vendor
                
                if tag_name and vendor_ok and tag_key_words:
                    overlap = json_key_words.intersection(tag_key_words)
                    overlap_ratio = len(overlap) / min(len(json_key_words), len(tag_key_words)) if min(len(json_key_words), len(tag_key_words)) > 0 else 0
                    if overlap_ratio >= 0.4:  # Lowered to 40%
                        found = tag
                        print(f"  ✓ WORD MATCH: '{tag.get('Product Name*', '')}' (overlap: {overlap_ratio:.2f})")
                        break
        
        if not found:
            print(f"  ✗ NO MATCH FOUND")
            print(f"    JSON vendor: '{json_vendor}', key_words: {json_key_words}")
            
            # Show potential matches with lower thresholds
            print(f"    Potential matches (lower threshold):")
            for tag in available_tags[:10]:
                tag_name = str(tag.get('Product Name*', '')).strip().lower()
                tag_vendor = extract_vendor(tag_name)
                tag_key_words = extract_key_words(tag_name)
                
                if tag_key_words:
                    overlap = json_key_words.intersection(tag_key_words)
                    overlap_ratio = len(overlap) / min(len(json_key_words), len(tag_key_words)) if min(len(json_key_words), len(tag_key_words)) > 0 else 0
                    if overlap_ratio > 0.2:  # Show any overlap > 20%
                        print(f"      '{tag.get('Product Name*', '')}' (overlap: {overlap_ratio:.2f})")

if __name__ == "__main__":
    test_matching() 