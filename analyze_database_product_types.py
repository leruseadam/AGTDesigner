#!/usr/bin/env python3
"""
Analyze database to understand product types and weight patterns.
"""

import sqlite3
import pandas as pd
from collections import defaultdict, Counter
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent / 'uploads' / 'product_database_AGT_Bothell.db'

def analyze_product_types():
    """Analyze all product types in the database."""
    
    if not DB_PATH.exists():
        print(f"❌ Database not found: {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    
    print("="*80)
    print("DATABASE PRODUCT TYPE ANALYSIS")
    print("="*80)
    print()
    
    # Get all unique product types
    cursor = conn.cursor()
    cursor.execute('''
        SELECT "Product Type*", COUNT(*) as count
        FROM products
        WHERE "Product Type*" IS NOT NULL AND "Product Type*" != ''
        GROUP BY "Product Type*"
        ORDER BY count DESC
    ''')
    
    product_types = cursor.fetchall()
    
    print("PRODUCT TYPE DISTRIBUTION:")
    print("-" * 80)
    for ptype, count in product_types:
        print(f"  {count:4d} | {ptype}")
    print()
    
    # Analyze weight patterns by product type
    print("WEIGHT PATTERNS BY PRODUCT TYPE:")
    print("-" * 80)
    
    for ptype, _ in product_types[:15]:  # Top 15 types
        print(f"\n📦 {ptype}:")
        
        # Get weight/unit combinations
        cursor.execute('''
            SELECT "Weight*", "Units", COUNT(*) as count
            FROM products
            WHERE "Product Type*" = ? 
            AND "Weight*" IS NOT NULL 
            AND "Weight*" != ''
            GROUP BY "Weight*", "Units"
            ORDER BY count DESC
            LIMIT 10
        ''', (ptype,))
        
        weight_patterns = cursor.fetchall()
        
        for weight, unit, count in weight_patterns:
            print(f"    {count:3d}x | {weight}{unit}")
    
    conn.close()

def analyze_classic_vs_nonclassic():
    """Analyze classic vs non-classic product types."""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("\n" + "="*80)
    print("CLASSIC VS NON-CLASSIC ANALYSIS")
    print("="*80)
    
    # Define classic types (from constants)
    classic_types = [
        'Flower', 'Pre-Roll', 'Infused Pre-Roll', 'Concentrate', 
        'Solventless Concentrate', 'Edible (Solid)', 'Edible (Liquid)'
    ]
    
    # Get all product types with counts
    cursor.execute('''
        SELECT "Product Type*", COUNT(*) as count
        FROM products
        WHERE "Product Type*" IS NOT NULL AND "Product Type*" != ''
        GROUP BY "Product Type*"
        ORDER BY count DESC
    ''')
    
    all_types = cursor.fetchall()
    
    classic_count = 0
    nonclassic_count = 0
    classic_types_found = []
    nonclassic_types_found = []
    
    print("\nCLASSIC TYPES:")
    print("-" * 40)
    for ptype, count in all_types:
        is_classic = any(ct in ptype for ct in classic_types)
        if is_classic:
            classic_count += count
            classic_types_found.append((ptype, count))
            print(f"  ✓ {count:4d} | {ptype}")
    
    print("\nNON-CLASSIC TYPES:")
    print("-" * 40)
    for ptype, count in all_types:
        is_classic = any(ct in ptype for ct in classic_types)
        if not is_classic:
            nonclassic_count += count
            nonclassic_types_found.append((ptype, count))
            print(f"  • {count:4d} | {ptype}")
    
    print(f"\nSUMMARY:")
    print(f"  Classic types: {classic_count:,} products")
    print(f"  Non-classic types: {nonclassic_count:,} products")
    print(f"  Total: {classic_count + nonclassic_count:,} products")
    
    conn.close()
    
    return classic_types_found, nonclassic_types_found

def analyze_weight_unit_patterns():
    """Analyze weight and unit patterns across product types."""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("\n" + "="*80)
    print("WEIGHT/UNIT PATTERN ANALYSIS")
    print("="*80)
    
    # Get weight/unit combinations by product type
    cursor.execute('''
        SELECT 
            "Product Type*",
            "Units",
            COUNT(*) as count,
            MIN(CAST("Weight*" AS REAL)) as min_weight,
            MAX(CAST("Weight*" AS REAL)) as max_weight,
            AVG(CAST("Weight*" AS REAL)) as avg_weight
        FROM products
        WHERE "Product Type*" IS NOT NULL 
        AND "Weight*" IS NOT NULL 
        AND "Units" IS NOT NULL
        AND "Weight*" != ''
        AND "Units" != ''
        GROUP BY "Product Type*", "Units"
        HAVING COUNT(*) >= 5
        ORDER BY "Product Type*", count DESC
    ''')
    
    patterns = cursor.fetchall()
    
    current_type = None
    for ptype, unit, count, min_w, max_w, avg_w in patterns:
        if ptype != current_type:
            print(f"\n📦 {ptype}:")
            current_type = ptype
        
        print(f"    {count:3d}x | {unit:3s} | Range: {min_w:6.2f}-{max_w:6.2f} | Avg: {avg_w:6.2f}")
    
    conn.close()

def find_weight_inconsistencies():
    """Find weight inconsistencies that need normalization."""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("\n" + "="*80)
    print("WEIGHT INCONSISTENCIES TO FIX")
    print("="*80)
    
    # Find products that should probably be in different units
    inconsistencies = []
    
    # 1. Large gram weights that should be oz
    cursor.execute('''
        SELECT "Product Type*", "Product Name*", "Weight*", "Units", COUNT(*) as count
        FROM products
        WHERE CAST("Weight*" AS REAL) > 100
        AND LOWER("Units") = 'g'
        AND "Product Type*" NOT LIKE '%Concentrate%'
        AND "Product Type*" NOT LIKE '%Flower%'
        AND "Product Type*" NOT LIKE '%Pre-Roll%'
        GROUP BY "Product Type*", "Product Name*", "Weight*", "Units"
        ORDER BY count DESC
        LIMIT 20
    ''')
    
    large_grams = cursor.fetchall()
    if large_grams:
        print("\n🔍 Large gram weights (>100g) that might need oz conversion:")
        for ptype, name, weight, unit, count in large_grams:
            print(f"    {count:2d}x | {weight}{unit} | {ptype} | {name[:50]}")
    
    # 2. Small oz weights that might need grams
    cursor.execute('''
        SELECT "Product Type*", "Product Name*", "Weight*", "Units", COUNT(*) as count
        FROM products
        WHERE CAST("Weight*" AS REAL) < 0.1
        AND LOWER("Units") = 'oz'
        AND "Product Type*" NOT LIKE '%Edible%'
        GROUP BY "Product Type*", "Product Name*", "Weight*", "Units"
        ORDER BY count DESC
        LIMIT 20
    ''')
    
    small_oz = cursor.fetchall()
    if small_oz:
        print("\n🔍 Small oz weights (<0.1oz) that might need gram conversion:")
        for ptype, name, weight, unit, count in small_oz:
            print(f"    {count:2d}x | {weight}{unit} | {ptype} | {name[:50]}")
    
    # 3. Mixed units within same product type
    cursor.execute('''
        SELECT 
            "Product Type*",
            COUNT(DISTINCT "Units") as unit_variety,
            GROUP_CONCAT(DISTINCT "Units") as units
        FROM products
        WHERE "Product Type*" IS NOT NULL 
        AND "Units" IS NOT NULL
        AND "Units" != ''
        GROUP BY "Product Type*"
        HAVING COUNT(DISTINCT "Units") > 1
        ORDER BY unit_variety DESC
        LIMIT 15
    ''')
    
    mixed_units = cursor.fetchall()
    if mixed_units:
        print("\n🔍 Product types with mixed units:")
        for ptype, variety, units in mixed_units:
            print(f"    {ptype} | Units: {units}")
    
    conn.close()

if __name__ == "__main__":
    analyze_product_types()
    classic_types, nonclassic_types = analyze_classic_vs_nonclassic()
    analyze_weight_unit_patterns()
    find_weight_inconsistencies()
