#!/usr/bin/env python3
"""
Comprehensive fix for Gravity Gummies outliers and inconsistencies.
Addresses all issues found in the database audit.
"""

import sqlite3
import logging
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_gravity_gummies_comprehensive(db_path: str = 'uploads/product_database_AGT_Bothell.db'):
    """
    Comprehensive fix for Gravity Gummies outliers and inconsistencies.
    
    Issues to fix:
    1. Price placeholders ($Price*)
    2. Weight unit inconsistencies (g vs oz)
    3. Missing 1:1:1 prefixes
    4. Weight value inconsistencies
    """
    
    if not Path(db_path).exists():
        logger.error(f"Database not found: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        logger.info("="*80)
        logger.info("COMPREHENSIVE GRAVITY GUMMIES FIX")
        logger.info("="*80)
        logger.info("")
        
        # Get all Gravity Gummies products
        cursor.execute('''
            SELECT rowid, "Product Name*", "Weight*", "Units", "Price", "Product Brand"
            FROM products 
            WHERE "Product Brand" LIKE '%Gravity%'
            ORDER BY "Product Name*"
        ''')
        
        gravity_products = cursor.fetchall()
        
        if not gravity_products:
            logger.warning("No Gravity Gummies products found.")
            return False
        
        logger.info(f"Found {len(gravity_products)} Gravity Gummies products to fix")
        logger.info("")
        
        fixes_applied = {
            'price_fixes': 0,
            'weight_fixes': 0,
            'naming_fixes': 0,
            'unit_fixes': 0
        }
        
        # Process each product
        for rowid, name, weight, unit, price, brand in gravity_products:
            logger.info(f"Processing: {name}")
            
            # Fix price if it's a placeholder
            if price == '$Price*' or price == 'Price*' or not price or str(price).strip() == '':
                logger.info(f"  Fixing price: '{price}' → '$35'")
                cursor.execute('''
                    UPDATE products 
                    SET "Price" = '$35', updated_at = ?
                    WHERE rowid = ?
                ''', (datetime.now().isoformat(), rowid))
                fixes_applied['price_fixes'] += 1
            
            # Fix weight and unit
            if weight and unit:
                # Convert grams to ounces for consistency
                if unit.lower() in ['g', 'gram', 'grams']:
                    try:
                        weight_float = float(weight)
                        # Convert to ounces (1g = 0.035274 oz)
                        weight_oz = round(weight_float * 0.035274, 2)
                        
                        # For Gravity Gummies, standardize to 1.12oz
                        if abs(weight_oz - 1.12) < 0.1:  # Close to 1.12oz
                            logger.info(f"  Fixing weight: {weight}{unit} → 1.12oz")
                            cursor.execute('''
                                UPDATE products 
                                SET "Weight*" = '1.12', "Units" = 'oz', updated_at = ?
                                WHERE rowid = ?
                            ''', (datetime.now().isoformat(), rowid))
                            fixes_applied['weight_fixes'] += 1
                            fixes_applied['unit_fixes'] += 1
                    except ValueError:
                        logger.warning(f"  Invalid weight value: {weight}")
                
                # Fix ounces that are close to 1.12oz
                elif unit.lower() in ['oz', 'ounce', 'ounces']:
                    try:
                        weight_float = float(weight)
                        if abs(weight_float - 1.12) < 0.1:  # Close to 1.12oz
                            logger.info(f"  Standardizing weight: {weight}{unit} → 1.12oz")
                            cursor.execute('''
                                UPDATE products 
                                SET "Weight*" = '1.12', "Units" = 'oz', updated_at = ?
                                WHERE rowid = ?
                            ''', (datetime.now().isoformat(), rowid))
                            fixes_applied['weight_fixes'] += 1
                    except ValueError:
                        logger.warning(f"  Invalid weight value: {weight}")
            
            # Fix naming - add 1:1:1 prefix if missing
            if not name.startswith('1:1:1') and not name.startswith('1:1'):
                # Determine the new name based on the product
                new_name = None
                
                if 'Pink Lemonade' in name:
                    parts = name.split('Pink Lemonade Hash Gummies')
                    new_name = '1:1:1 Pink Lemonade Hash Gummies' + (parts[1] if len(parts) > 1 else '')
                elif 'Blueberry' in name and 'Hash Gummies' in name:
                    parts = name.split('Blueberry Hash Gummies')
                    new_name = '1:1:1 Blueberry Hash Gummies' + (parts[1] if len(parts) > 1 else '')
                elif 'Mixed Berry' in name and 'Hash Gummies' in name:
                    parts = name.split('Mixed Berry Hash Gummies')
                    new_name = '1:1:1 Mixed Berry Hash Gummies' + (parts[1] if len(parts) > 1 else '')
                elif 'Pineapple' in name and 'Hash Gummies' in name and not name.startswith('Sour'):
                    parts = name.split('Pineapple Hash Gummies')
                    new_name = '1:1:1 Pineapple Hash Gummies' + (parts[1] if len(parts) > 1 else '')
                elif 'Watermelon' in name and 'Hash Gummies' in name and not name.startswith('Sour'):
                    parts = name.split('Watermelon Hash Gummies')
                    new_name = '1:1:1 Watermelon Hash Gummies' + (parts[1] if len(parts) > 1 else '')
                elif 'Sour Pineapple' in name and 'Hash Gummies' in name:
                    parts = name.split('Sour Pineapple Hash Gummies')
                    new_name = '1:1:1 Sour Pineapple Hash Gummies' + (parts[1] if len(parts) > 1 else '')
                elif 'Sour Watermelon' in name and 'Hash Gummies' in name:
                    parts = name.split('Sour Watermelon Hash Gummies')
                    new_name = '1:1:1 Sour Watermelon Hash Gummies' + (parts[1] if len(parts) > 1 else '')
                
                if new_name:
                    logger.info(f"  Fixing naming: '{name}' → '{new_name}'")
                    cursor.execute('''
                        UPDATE products 
                        SET "Product Name*" = ?, updated_at = ?
                        WHERE rowid = ?
                    ''', (new_name, datetime.now().isoformat(), rowid))
                    fixes_applied['naming_fixes'] += 1
            
            logger.info("")
        
        # Commit all changes
        conn.commit()
        
        # Summary
        logger.info("="*80)
        logger.info("COMPREHENSIVE FIX SUMMARY")
        logger.info("="*80)
        logger.info(f"Price fixes applied: {fixes_applied['price_fixes']}")
        logger.info(f"Weight fixes applied: {fixes_applied['weight_fixes']}")
        logger.info(f"Unit fixes applied: {fixes_applied['unit_fixes']}")
        logger.info(f"Naming fixes applied: {fixes_applied['naming_fixes']}")
        logger.info("="*80)
        
        return True
        
    except Exception as e:
        logger.error(f"Error in comprehensive fix: {e}")
        if 'conn' in locals():
            conn.rollback()
        return False
    
    finally:
        if 'conn' in locals():
            conn.close()

def audit_gravity_gummies_final(db_path: str = 'uploads/product_database_AGT_Bothell.db'):
    """Final audit of Gravity Gummies products after comprehensive fix."""
    
    if not Path(db_path).exists():
        logger.error(f"Database not found: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        logger.info("="*80)
        logger.info("FINAL GRAVITY GUMMIES AUDIT")
        logger.info("="*80)
        
        cursor.execute('''
            SELECT "Product Name*", "Weight*", "Units", "Price", "Product Brand", updated_at
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
        
        consistent_products = 0
        total_products = len(products)
        
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
            
            # Check if product meets consistency criteria
            is_consistent = True
            
            # Check naming (should have 1:1:1 prefix)
            if not name.startswith('1:1:1'):
                is_consistent = False
                naming_patterns.add('no prefix')
            else:
                naming_patterns.add('1:1:1 prefix')
            
            # Check price (should be 35)
            if price != '35':
                is_consistent = False
            
            # Check weight (should be 1.12oz)
            if weight != '1.12' or unit != 'oz':
                is_consistent = False
            
            if is_consistent:
                consistent_products += 1
        
        # Consistency report
        logger.info("="*80)
        logger.info("FINAL CONSISTENCY REPORT")
        logger.info("="*80)
        
        consistency_rate = (consistent_products / total_products) * 100
        logger.info(f"Consistency Rate: {consistent_products}/{total_products} ({consistency_rate:.1f}%)")
        logger.info("")
        
        if len(prices) == 1 and '35' in prices:
            logger.info(f"✅ Pricing: Consistent at ${list(prices)[0]}")
        else:
            logger.warning(f"⚠️  Pricing: Inconsistent - {prices}")
        
        if len(weights) == 1 and len(units) == 1 and '1.12' in weights and 'oz' in units:
            logger.info(f"✅ Weight: Consistent at {list(weights)[0]}{list(units)[0]}")
        else:
            logger.warning(f"⚠️  Weight: Inconsistent - {weights} {units}")
        
        if len(naming_patterns) == 1 and '1:1:1 prefix' in naming_patterns:
            logger.info(f"✅ Naming: Consistent - {list(naming_patterns)[0]}")
        else:
            logger.warning(f"⚠️  Naming: Inconsistent - {naming_patterns}")
        
        if consistency_rate == 100:
            logger.info("")
            logger.info("🎉 ALL GRAVITY GUMMIES PRODUCTS ARE NOW CONSISTENT!")
        else:
            logger.info("")
            logger.warning(f"⚠️  {total_products - consistent_products} products still need attention.")
        
    except Exception as e:
        logger.error(f"Error in final audit: {e}")
    
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'audit':
        audit_gravity_gummies_final()
    else:
        success = fix_gravity_gummies_comprehensive()
        if success:
            print("\n🎉 Comprehensive Gravity Gummies fix completed!")
            print("Run 'python3 fix_gravity_gummies_comprehensive.py audit' to verify consistency.")
        else:
            print("\n❌ Failed to apply comprehensive Gravity Gummies fix.")
