#!/usr/bin/env python3
"""
Check for weight mismatches in the database.
Looks for inconsistencies between product names and their weight values.
"""

import sqlite3
import re
from pathlib import Path
from collections import defaultdict

# Database path
DB_PATH = Path(__file__).parent / 'uploads' / 'product_database_AGT_Bothell.db'

def extract_weight_from_name(name):
    """Extract weight from product name (e.g., '3.5g', '1g', '14g', '1oz')."""
    if not name:
        return None
    
    # Common patterns: "3.5g", "1g", "14g", "1oz", "0.5g", etc.
    patterns = [
        r'(\d+\.?\d*)\s*g\b',  # Match "3.5g", "1g", "14g", etc.
        r'(\d+\.?\d*)\s*oz\b',  # Match "1oz", "0.5oz", etc.
        r'-\s*(\d+\.?\d*)\s*g\b',  # Match "- 1g", "- 3.5g", etc.
        r'\b(\d+\.?\d*)\s*gram',  # Match "1 gram", etc.
    ]
    
    for pattern in patterns:
        match = re.search(pattern, name, re.IGNORECASE)
        if match:
            weight = float(match.group(1))
            unit = 'oz' if 'oz' in pattern else 'g'
            return (weight, unit)
    
    return None

def check_weight_mismatches():
    """Check for weight mismatches in the database."""
    
    if not DB_PATH.exists():
        print(f"❌ Database not found: {DB_PATH}")
        return False
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("="*80)
    print("WEIGHT MISMATCH ANALYSIS")
    print("="*80)
    print()
    
    # Get all products
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
    ''')
    
    all_products = cursor.fetchall()
    
    mismatches = []
    unit_issues = defaultdict(list)
    high_weights = []
    
    print(f"Analyzing {len(all_products)} products...")
    print()
    
    for name, brand, db_weight, db_unit, ptype, rowid in all_products:
        try:
            db_weight_val = float(db_weight)
        except (ValueError, TypeError):
            continue
        
        # Check 1: Extract weight from product name
        name_weight = extract_weight_from_name(name)
        if name_weight:
            name_val, name_unit = name_weight
            
            # Check if units match
            if db_unit and name_unit.lower() != db_unit.lower():
                # Convert for comparison
                if name_unit.lower() == 'g' and db_unit.lower() == 'oz':
                    name_val_oz = round(name_val / 28.3495, 2)
                    if abs(name_val_oz - db_weight_val) > 0.1:
                        mismatches.append({
                            'name': name,
                            'brand': brand,
                            'type': ptype,
                            'name_weight': f"{name_val}g ({name_val_oz}oz)",
                            'db_weight': f"{db_weight}{db_unit}",
                            'rowid': rowid
                        })
                elif name_unit.lower() == 'oz' and db_unit.lower() == 'g':
                    name_val_g = round(name_val * 28.3495, 2)
                    if abs(name_val_g - db_weight_val) > 0.5:
                        mismatches.append({
                            'name': name,
                            'brand': brand,
                            'type': ptype,
                            'name_weight': f"{name_val}oz ({name_val_g}g)",
                            'db_weight': f"{db_weight}{db_unit}",
                            'rowid': rowid
                        })
            else:
                # Same units, check if values match
                if abs(name_val - db_weight_val) > 0.1:
                    mismatches.append({
                        'name': name,
                        'brand': brand,
                        'type': ptype,
                        'name_weight': f"{name_val}{name_unit}",
                        'db_weight': f"{db_weight}{db_unit}",
                        'rowid': rowid
                    })
        
        # Check 2: Unit consistency by product type
        if ptype:
            # Flower should be in grams
            if 'Flower' in ptype and db_unit and db_unit.lower() == 'oz':
                unit_issues['flower_in_oz'].append({
                    'name': name,
                    'brand': brand,
                    'weight': f"{db_weight}{db_unit}",
                    'rowid': rowid
                })
            
            # Concentrates should be in grams
            if 'Concentrate' in ptype and db_unit and db_unit.lower() == 'oz':
                unit_issues['concentrate_in_oz'].append({
                    'name': name,
                    'brand': brand,
                    'weight': f"{db_weight}{db_unit}",
                    'rowid': rowid
                })
            
            # Topicals should be in oz
            if 'Topical' in ptype and db_unit and db_unit.lower() == 'g' and db_weight_val > 10:
                unit_issues['topical_in_g'].append({
                    'name': name,
                    'brand': brand,
                    'weight': f"{db_weight}{db_unit}",
                    'rowid': rowid
                })
            
            # Edible Solids should be in oz
            if 'Edible (Solid)' in ptype and db_unit and db_unit.lower() == 'g' and db_weight_val > 20:
                unit_issues['edible_solid_in_g'].append({
                    'name': name,
                    'brand': brand,
                    'weight': f"{db_weight}{db_unit}",
                    'rowid': rowid
                })
        
        # Check 3: High weights that might need conversion
        if db_unit and db_unit.lower() == 'g' and db_weight_val > 100:
            # Exclude concentrates (they're supposed to be small)
            if ptype and 'Concentrate' not in ptype:
                high_weights.append({
                    'name': name,
                    'brand': brand,
                    'type': ptype,
                    'weight': f"{db_weight}g",
                    'oz_equivalent': f"{round(db_weight_val / 28.3495, 2)}oz",
                    'rowid': rowid
                })
    
    # Print results
    print("="*80)
    print("RESULTS")
    print("="*80)
    print()
    
    if mismatches:
        print(f"❌ Found {len(mismatches)} products where name weight doesn't match database:")
        print("-" * 80)
        for m in mismatches[:20]:  # Show first 20
            print(f"  • {m['name']} by {m['brand']}")
            print(f"    Name says: {m['name_weight']} | DB says: {m['db_weight']}")
            print(f"    Type: {m['type']}")
            print()
        if len(mismatches) > 20:
            print(f"  ... and {len(mismatches) - 20} more")
        print()
    else:
        print("✅ No weight mismatches between product names and database")
        print()
    
    if unit_issues['flower_in_oz']:
        print(f"⚠️  Found {len(unit_issues['flower_in_oz'])} flower products in oz (should be g):")
        for item in unit_issues['flower_in_oz'][:5]:
            print(f"  • {item['name']}: {item['weight']}")
        print()
    
    if unit_issues['concentrate_in_oz']:
        print(f"⚠️  Found {len(unit_issues['concentrate_in_oz'])} concentrates in oz (should be g):")
        for item in unit_issues['concentrate_in_oz'][:5]:
            print(f"  • {item['name']}: {item['weight']}")
        print()
    
    if unit_issues['topical_in_g']:
        print(f"⚠️  Found {len(unit_issues['topical_in_g'])} topicals in g (should be oz):")
        for item in unit_issues['topical_in_g'][:5]:
            print(f"  • {item['name']}: {item['weight']}")
        print()
    
    if unit_issues['edible_solid_in_g']:
        print(f"⚠️  Found {len(unit_issues['edible_solid_in_g'])} edible solids in g (should be oz):")
        for item in unit_issues['edible_solid_in_g'][:5]:
            print(f"  • {item['name']}: {item['weight']}")
        print()
    
    if high_weights:
        print(f"⚠️  Found {len(high_weights)} products with high gram weights (>100g):")
        print("-" * 80)
        for hw in high_weights[:10]:
            print(f"  • {hw['name']} by {hw['brand']}")
            print(f"    {hw['weight']} (= {hw['oz_equivalent']})")
            print(f"    Type: {hw['type']}")
            print()
        if len(high_weights) > 10:
            print(f"  ... and {len(high_weights) - 10} more")
        print()
    
    if not mismatches and not any(unit_issues.values()) and not high_weights:
        print("🎉 Everything looks good!")
        print()
    
    conn.close()
    return True

if __name__ == "__main__":
    print()
    check_weight_mismatches()

