#!/usr/bin/env python3
"""
Analyze database for weight patterns and inconsistencies.
Used to expand the weight normalization system.
"""

import sqlite3
import re
from collections import defaultdict, Counter
from pathlib import Path
import pandas as pd

# Database path
DB_PATH = Path(__file__).parent / 'uploads' / 'product_database_AGT_Bothell.db'

def analyze_weight_patterns():
    """Analyze all weight patterns in the database."""
    
    if not DB_PATH.exists():
        print(f"❌ Database not found: {DB_PATH}")
        return False
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("="*80)
    print("DATABASE WEIGHT PATTERN ANALYSIS")
    print("="*80)
    print()
    
    # Get all products with weight data
    cursor.execute('''
        SELECT 
            "Product Name*", 
            "Product Brand", 
            "Weight*", 
            "Units", 
            "Product Type*",
            rowid
        FROM products
        WHERE "Weight*" IS NOT NULL
        AND "Weight*" != ''
        AND "Weight*" != 'nan'
    ''')
    
    all_products = cursor.fetchall()
    print(f"Analyzing {len(all_products)} products with weight data...")
    print()
    
    # Analysis 1: Weight distribution by product type
    print("1. WEIGHT DISTRIBUTION BY PRODUCT TYPE")
    print("-" * 80)
    
    type_weight_analysis = defaultdict(lambda: defaultdict(int))
    
    for name, brand, weight, units, ptype, rowid in all_products:
        try:
            weight_val = float(weight)
            unit_key = f"{units.lower()}"
            weight_unit_key = f"{weight_val}{units.lower()}"
            
            type_weight_analysis[ptype][unit_key] += 1
            
        except ValueError:
            pass
    
    for ptype, unit_counts in sorted(type_weight_analysis.items()):
        if ptype:  # Skip empty types
            print(f"  {ptype}:")
            for unit, count in sorted(unit_counts.items(), key=lambda x: x[1], reverse=True):
                print(f"    {unit}: {count} products")
            print()
    
    # Analysis 2: Common weight values
    print("2. MOST COMMON WEIGHT VALUES")
    print("-" * 80)
    
    weight_counter = Counter()
    
    for name, brand, weight, units, ptype, rowid in all_products:
        try:
            weight_val = float(weight)
            weight_unit = f"{weight_val}{units.lower()}"
            weight_counter[weight_unit] += 1
        except ValueError:
            pass
    
    print("  Top 20 weight values:")
    for weight_unit, count in weight_counter.most_common(20):
        print(f"    {weight_unit}: {count} products")
    print()
    
    # Analysis 3: Weight inconsistencies by brand
    print("3. WEIGHT INCONSISTENCIES BY BRAND")
    print("-" * 80)
    
    brand_weights = defaultdict(lambda: defaultdict(list))
    
    for name, brand, weight, units, ptype, rowid in all_products:
        if brand and brand.strip():
            try:
                weight_val = float(weight)
                brand_weights[brand][ptype].append((name, weight_val, units.lower()))
            except ValueError:
                pass
    
    inconsistencies = []
    
    for brand, types in brand_weights.items():
        for ptype, products in types.items():
            if len(products) > 1:  # Multiple products of same type
                # Check for weight variations
                weights = [p[1] for p in products]
                units = [p[2] for p in products]
                
                if len(set(units)) > 1:  # Mixed units
                    inconsistencies.append({
                        'brand': brand,
                        'type': ptype,
                        'count': len(products),
                        'issue': 'mixed_units',
                        'units': list(set(units))
                    })
                elif len(set(weights)) > 1:  # Mixed weights
                    inconsistencies.append({
                        'brand': brand,
                        'type': ptype,
                        'count': len(products),
                        'issue': 'mixed_weights',
                        'weights': sorted(set(weights))
                    })
    
    # Show top inconsistencies
    print("  Top inconsistencies:")
    for inc in sorted(inconsistencies, key=lambda x: x['count'], reverse=True)[:15]:
        if inc['issue'] == 'mixed_units':
            print(f"    {inc['brand']} - {inc['type']}: {inc['count']} products with units {inc['units']}")
        else:
            print(f"    {inc['brand']} - {inc['type']}: {inc['count']} products with weights {inc['weights']}")
    print()
    
    # Analysis 4: Specific product patterns
    print("4. SPECIFIC PRODUCT PATTERNS")
    print("-" * 80)
    
    # Look for patterns in product names
    name_patterns = defaultdict(list)
    
    for name, brand, weight, units, ptype, rowid in all_products:
        if name and name.strip():
            name_lower = name.lower()
            
            # Extract common patterns
            if 'moonshot' in name_lower:
                name_patterns['moonshot'].append((name, weight, units, brand))
            elif 'pre-roll' in name_lower or 'preroll' in name_lower:
                name_patterns['pre_roll'].append((name, weight, units, brand))
            elif 'gummy' in name_lower or 'gummies' in name_lower:
                name_patterns['gummies'].append((name, weight, units, brand))
            elif 'chocolate' in name_lower:
                name_patterns['chocolate'].append((name, weight, units, brand))
            elif 'beverage' in name_lower or 'drink' in name_lower:
                name_patterns['beverage'].append((name, weight, units, brand))
            elif 'topical' in name_lower or 'cream' in name_lower or 'salve' in name_lower:
                name_patterns['topical'].append((name, weight, units, brand))
            elif 'concentrate' in name_lower or 'wax' in name_lower or 'shatter' in name_lower:
                name_patterns['concentrate'].append((name, weight, units, brand))
    
    for pattern, products in name_patterns.items():
        if len(products) > 5:  # Only show patterns with multiple products
            print(f"  {pattern.upper()} ({len(products)} products):")
            
            # Group by weight/unit
            weight_groups = defaultdict(list)
            for name, weight, units, brand in products:
                key = f"{weight}{units}"
                weight_groups[key].append((name, brand))
            
            for weight_unit, product_list in sorted(weight_groups.items(), key=lambda x: len(x[1]), reverse=True):
                print(f"    {weight_unit}: {len(product_list)} products")
                # Show a few examples
                for name, brand in product_list[:3]:
                    print(f"      • {name} by {brand}")
                if len(product_list) > 3:
                    print(f"      ... and {len(product_list) - 3} more")
            print()
    
    # Analysis 5: Potential normalization candidates
    print("5. POTENTIAL NORMALIZATION CANDIDATES")
    print("-" * 80)
    
    candidates = []
    
    for name, brand, weight, units, ptype, rowid in all_products:
        try:
            weight_val = float(weight)
            
            # Look for potential issues
            issues = []
            
            # High gram weights (might need oz conversion)
            if units.lower() in ['g', 'gram', 'grams'] and weight_val > 100:
                if 'concentrate' not in ptype.lower():
                    issues.append(f"High gram weight: {weight}g (might need oz)")
            
            # Small oz weights (might need gram conversion)
            if units.lower() in ['oz', 'ounce', 'ounces'] and weight_val < 0.1:
                issues.append(f"Small oz weight: {weight}oz (might need g)")
            
            # Specific problematic weights
            if weight in ['190', '190.0', '190g', '190.0g'] and 'concentrate' not in ptype.lower():
                issues.append(f"190g weight (should probably be 6.7oz)")
            
            if weight in ['2.5', '2.5oz'] and 'moonshot' in name.lower() and 'constellation' in brand.lower():
                issues.append(f"Moonshot 2.5oz (should be 1.7oz)")
            
            # Mixed units for same product type
            if brand and ptype:
                # This would require more complex analysis
                pass
            
            if issues:
                candidates.append({
                    'name': name,
                    'brand': brand,
                    'type': ptype,
                    'weight': weight,
                    'units': units,
                    'issues': issues
                })
        
        except ValueError:
            pass
    
    # Show top candidates
    print(f"  Found {len(candidates)} potential normalization candidates:")
    for i, candidate in enumerate(candidates[:20], 1):
        print(f"    {i}. {candidate['name']} by {candidate['brand']}")
        print(f"       {candidate['weight']}{candidate['units']} ({candidate['type']})")
        for issue in candidate['issues']:
            print(f"       ⚠️  {issue}")
        print()
    
    if len(candidates) > 20:
        print(f"  ... and {len(candidates) - 20} more candidates")
    
    # Analysis 6: Unit consistency by product type
    print("6. UNIT CONSISTENCY BY PRODUCT TYPE")
    print("-" * 80)
    
    type_unit_analysis = defaultdict(lambda: defaultdict(int))
    
    for name, brand, weight, units, ptype, rowid in all_products:
        if ptype and units:
            type_unit_analysis[ptype][units.lower()] += 1
    
    for ptype, unit_counts in sorted(type_unit_analysis.items()):
        if len(unit_counts) > 1:  # Only show types with mixed units
            total = sum(unit_counts.values())
            print(f"  {ptype} ({total} products):")
            for unit, count in sorted(unit_counts.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total) * 100
                print(f"    {unit}: {count} ({percentage:.1f}%)")
            print()
    
    conn.close()
    
    print("="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
    print()
    print("Use this analysis to expand the weight normalization system!")
    
    return True

if __name__ == "__main__":
    analyze_weight_patterns()
