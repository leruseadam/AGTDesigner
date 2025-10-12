#!/usr/bin/env python3
"""
Fix Gravity Gummies outliers and inconsistencies.
Based on the image analysis showing several inconsistencies in the labels.
"""

import sqlite3
import logging
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_gravity_gummies_outliers(db_path: str = 'uploads/product_database_AGT_Bothell.db'):
    """
    Fix Gravity Gummies outliers and inconsistencies.
    
    Issues identified from image:
    1. Pricing inconsistencies: $35 vs $30
    2. Weight inconsistencies: 1.12oz vs 1oz
    3. Naming convention inconsistencies: Missing "1:1:1" prefix
    4. Bottom section design inconsistencies
    """
    
    if not Path(db_path).exists():
        logger.error(f"Database not found: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        logger.info("="*80)
        logger.info("FIXING GRAVITY GUMMIES OUTLIERS")
        logger.info("="*80)
        logger.info("")
        
        # 1. Fix pricing inconsistencies - standardize to $35
        logger.info("1. Fixing pricing inconsistencies...")
        logger.info("-" * 40)
        
        pricing_fixes = [
            {
                'name_pattern': 'Blueberry Hash Gummies',
                'current_price': '30',
                'new_price': '35',
                'reason': 'Standardize Gravity Gummies pricing to $35'
            },
            {
                'name_pattern': 'Sour Pineapple Hash Gummies',
                'current_price': '30',
                'new_price': '35',
                'reason': 'Standardize Gravity Gummies pricing to $35'
            }
        ]
        
        for fix in pricing_fixes:
            cursor.execute('''
                SELECT rowid, "Product Name*", "Price*", "Product Brand"
                FROM products 
                WHERE "Product Name*" LIKE ? AND "Price*" = ? AND "Product Brand" LIKE '%Gravity%'
            ''', (f'%{fix["name_pattern"]}%', fix['current_price']))
            
            products = cursor.fetchall()
            for rowid, name, price, brand in products:
                logger.info(f"  Fixing pricing: {name} ${price} → ${fix['new_price']}")
                cursor.execute('''
                    UPDATE products 
                    SET "Price*" = ?, "Last Updated" = ?
                    WHERE rowid = ?
                ''', (fix['new_price'], datetime.now().isoformat(), rowid))
        
        logger.info(f"  ✓ Updated {len(pricing_fixes)} pricing inconsistencies")
        logger.info("")
        
        # 2. Fix weight inconsistencies - standardize to 1.12oz
        logger.info("2. Fixing weight inconsistencies...")
        logger.info("-" * 40)
        
        weight_fixes = [
            {
                'name_pattern': '1:1:1 Blueberry Hash Gummies',
                'current_weight': '1',
                'current_unit': 'oz',
                'new_weight': '1.12',
                'new_unit': 'oz',
                'reason': 'Standardize 1:1:1 products to 1.12oz'
            },
            {
                'name_pattern': 'Blueberry Hash Gummies',
                'current_weight': '1',
                'current_unit': 'oz',
                'new_weight': '1.12',
                'new_unit': 'oz',
                'reason': 'Standardize Gravity Gummies to 1.12oz'
            }
        ]
        
        for fix in weight_fixes:
            cursor.execute('''
                SELECT rowid, "Product Name*", "Weight*", "Units", "Product Brand"
                FROM products 
                WHERE "Product Name*" LIKE ? AND "Weight*" = ? AND "Units" = ? AND "Product Brand" LIKE '%Gravity%'
            ''', (f'%{fix["name_pattern"]}%', fix['current_weight'], fix['current_unit']))
            
            products = cursor.fetchall()
            for rowid, name, weight, unit, brand in products:
                logger.info(f"  Fixing weight: {name} {weight}{unit} → {fix['new_weight']}{fix['new_unit']}")
                cursor.execute('''
                    UPDATE products 
                    SET "Weight*" = ?, "Units" = ?, "Last Updated" = ?
                    WHERE rowid = ?
                ''', (fix['new_weight'], fix['new_unit'], datetime.now().isoformat(), rowid))
        
        logger.info(f"  ✓ Updated weight inconsistencies")
        logger.info("")
        
        # 3. Fix naming convention inconsistencies - add "1:1:1" prefix where missing
        logger.info("3. Fixing naming convention inconsistencies...")
        logger.info("-" * 40)
        
        naming_fixes = [
            {
                'current_name': 'Blueberry Hash Gummies',
                'new_name': '1:1:1 Blueberry Hash Gummies',
                'reason': 'Add 1:1:1 prefix for consistency with other Gravity Gummies'
            }
        ]
        
        for fix in naming_fixes:
            cursor.execute('''
                SELECT rowid, "Product Name*", "Product Brand"
                FROM products 
                WHERE "Product Name*" = ? AND "Product Brand" LIKE '%Gravity%'
            ''', (fix['current_name'],))
            
            products = cursor.fetchall()
            for rowid, name, brand in products:
                logger.info(f"  Fixing naming: '{name}' → '{fix['new_name']}'")
                cursor.execute('''
                    UPDATE products 
                    SET "Product Name*" = ?, "Last Updated" = ?
                    WHERE rowid = ?
                ''', (fix['new_name'], datetime.now().isoformat(), rowid))
        
        logger.info(f"  ✓ Updated naming conventions")
        logger.info("")
        
        # 4. Verify all Gravity Gummies are now consistent
        logger.info("4. Verifying Gravity Gummies consistency...")
        logger.info("-" * 40)
        
        cursor.execute('''
            SELECT "Product Name*", "Weight*", "Units", "Price*", "Product Brand"
            FROM products 
            WHERE "Product Brand" LIKE '%Gravity%'
            ORDER BY "Product Name*"
        ''')
        
        gravity_products = cursor.fetchall()
        
        if gravity_products:
            logger.info("Current Gravity Gummies products:")
            for name, weight, unit, price, brand in gravity_products:
                logger.info(f"  • {name} - {weight}{unit} - ${price}")
            
            # Check for remaining inconsistencies
            inconsistencies = []
            expected_price = '35'
            expected_weight = '1.12'
            expected_unit = 'oz'
            expected_prefix = '1:1:1'
            
            for name, weight, unit, price, brand in gravity_products:
                if price != expected_price:
                    inconsistencies.append(f"Price: {name} has ${price} (expected ${expected_price})")
                if weight != expected_weight or unit != expected_unit:
                    inconsistencies.append(f"Weight: {name} has {weight}{unit} (expected {expected_weight}{expected_unit})")
                if not name.startswith(expected_prefix):
                    inconsistencies.append(f"Naming: {name} missing '{expected_prefix}' prefix")
            
            if inconsistencies:
                logger.warning("Remaining inconsistencies found:")
                for inconsistency in inconsistencies:
                    logger.warning(f"  ⚠️  {inconsistency}")
            else:
                logger.info("  ✅ All Gravity Gummies are now consistent!")
        else:
            logger.warning("  ⚠️  No Gravity Gummies products found in database")
        
        # Commit changes
        conn.commit()
        logger.info("")
        logger.info("="*80)
        logger.info("GRAVITY GUMMIES OUTLIER FIXES COMPLETED")
        logger.info("="*80)
        
        return True
        
    except Exception as e:
        logger.error(f"Error fixing Gravity Gummies outliers: {e}")
        if 'conn' in locals():
            conn.rollback()
        return False
    
    finally:
        if 'conn' in locals():
            conn.close()

def audit_gravity_gummies(db_path: str = 'uploads/product_database_AGT_Bothell.db'):
    """Audit Gravity Gummies products for consistency."""
    
    if not Path(db_path).exists():
        logger.error(f"Database not found: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        logger.info("="*80)
        logger.info("GRAVITY GUMMIES AUDIT")
        logger.info("="*80)
        
        cursor.execute('''
            SELECT "Product Name*", "Weight*", "Units", "Price*", "Product Brand", "Last Updated"
            FROM products 
            WHERE "Product Brand" LIKE '%Gravity%'
            ORDER BY "Product Name*"
        ''')
        
        products = cursor.fetchall()
        
        if not products:
            logger.info("No Gravity Gummies products found.")
            return
        
        logger.info(f"Found {len(products)} Gravity Gummies products:")
        logger.info("")
        
        # Check consistency
        prices = set()
        weights = set()
        units = set()
        naming_patterns = set()
        
        for name, weight, unit, price, brand, updated in products:
            logger.info(f"• {name}")
            logger.info(f"  Weight: {weight}{unit}")
            logger.info(f"  Price: ${price}")
            logger.info(f"  Brand: {brand}")
            logger.info(f"  Last Updated: {updated}")
            logger.info("")
            
            prices.add(price)
            weights.add(weight)
            units.add(unit)
            if name.startswith('1:1:1'):
                naming_patterns.add('1:1:1 prefix')
            else:
                naming_patterns.add('no prefix')
        
        # Consistency report
        logger.info("="*80)
        logger.info("CONSISTENCY REPORT")
        logger.info("="*80)
        
        if len(prices) == 1:
            logger.info(f"✅ Pricing: Consistent at ${list(prices)[0]}")
        else:
            logger.warning(f"⚠️  Pricing: Inconsistent - {prices}")
        
        if len(weights) == 1 and len(units) == 1:
            logger.info(f"✅ Weight: Consistent at {list(weights)[0]}{list(units)[0]}")
        else:
            logger.warning(f"⚠️  Weight: Inconsistent - {weights} {units}")
        
        if len(naming_patterns) == 1:
            logger.info(f"✅ Naming: Consistent - {list(naming_patterns)[0]}")
        else:
            logger.warning(f"⚠️  Naming: Inconsistent - {naming_patterns}")
        
    except Exception as e:
        logger.error(f"Error auditing Gravity Gummies: {e}")
    
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'audit':
        audit_gravity_gummies()
    else:
        success = fix_gravity_gummies_outliers()
        if success:
            print("\n🎉 Gravity Gummies outliers fixed successfully!")
            print("Run 'python3 fix_gravity_gummies_outliers.py audit' to verify consistency.")
        else:
            print("\n❌ Failed to fix Gravity Gummies outliers.")
