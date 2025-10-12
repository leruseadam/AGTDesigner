#!/usr/bin/env python3
"""
Final comprehensive fix for Gravity Gummies outliers.
Standardizes all Gravity Gummies products to consistent format.
"""

import sqlite3
import logging
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_gravity_gummies_final(db_path: str = 'uploads/product_database_AGT_Bothell.db'):
    """
    Final comprehensive fix for all Gravity Gummies inconsistencies.
    
    Standardizes all products to:
    - Price: $35
    - Weight: 1.12oz
    - Naming: 1:1:1 prefix
    """
    
    if not Path(db_path).exists():
        logger.error(f"Database not found: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        logger.info("="*80)
        logger.info("FINAL GRAVITY GUMMIES STANDARDIZATION")
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
        
        logger.info(f"Standardizing {len(gravity_products)} Gravity Gummies products")
        logger.info("Target: $35, 1.12oz, 1:1:1 naming")
        logger.info("")
        
        fixes_applied = {
            'price_fixes': 0,
            'weight_fixes': 0,
            'naming_fixes': 0
        }
        
        # Process each product
        for rowid, name, weight, unit, price, brand in gravity_products:
            logger.info(f"Processing: {name}")
            
            # Fix price - standardize to $35
            if price != '$35':
                logger.info(f"  Price: '{price}' → '$35'")
                cursor.execute('''
                    UPDATE products 
                    SET "Price" = '$35', updated_at = ?
                    WHERE rowid = ?
                ''', (datetime.now().isoformat(), rowid))
                fixes_applied['price_fixes'] += 1
            
            # Fix weight and unit - standardize to 1.12oz
            if weight != '1.12' or unit != 'oz':
                logger.info(f"  Weight: {weight}{unit} → 1.12oz")
                cursor.execute('''
                    UPDATE products 
                    SET "Weight*" = '1.12', "Units" = 'oz', updated_at = ?
                    WHERE rowid = ?
                ''', (datetime.now().isoformat(), rowid))
                fixes_applied['weight_fixes'] += 1
            
            # Fix naming - ensure 1:1:1 prefix
            if not name.startswith('1:1:1'):
                # Add 1:1:1 prefix
                new_name = f"1:1:1 {name}"
                logger.info(f"  Naming: '{name}' → '{new_name}'")
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
        logger.info("FINAL STANDARDIZATION SUMMARY")
        logger.info("="*80)
        logger.info(f"Price fixes applied: {fixes_applied['price_fixes']}")
        logger.info(f"Weight fixes applied: {fixes_applied['weight_fixes']}")
        logger.info(f"Naming fixes applied: {fixes_applied['naming_fixes']}")
        logger.info("="*80)
        
        return True
        
    except Exception as e:
        logger.error(f"Error in final standardization: {e}")
        if 'conn' in locals():
            conn.rollback()
        return False
    
    finally:
        if 'conn' in locals():
            conn.close()

def verify_gravity_gummies_consistency(db_path: str = 'uploads/product_database_AGT_Bothell.db'):
    """Verify all Gravity Gummies products are now consistent."""
    
    if not Path(db_path).exists():
        logger.error(f"Database not found: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        logger.info("="*80)
        logger.info("GRAVITY GUMMIES CONSISTENCY VERIFICATION")
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
        
        logger.info(f"Verifying {len(products)} Gravity Gummies products")
        logger.info("")
        
        consistent_count = 0
        inconsistent_products = []
        
        for name, weight, unit, price, brand, updated in products:
            is_consistent = True
            issues = []
            
            # Check price
            if price != '$35':
                is_consistent = False
                issues.append(f"Price: {price} (expected $35)")
            
            # Check weight
            if weight != '1.12' or unit != 'oz':
                is_consistent = False
                issues.append(f"Weight: {weight}{unit} (expected 1.12oz)")
            
            # Check naming
            if not name.startswith('1:1:1'):
                is_consistent = False
                issues.append(f"Naming: missing 1:1:1 prefix")
            
            if is_consistent:
                consistent_count += 1
                logger.info(f"✅ {name}")
            else:
                inconsistent_products.append((name, issues))
                logger.warning(f"❌ {name}")
                for issue in issues:
                    logger.warning(f"   ⚠️  {issue}")
        
        logger.info("")
        logger.info("="*80)
        logger.info("VERIFICATION RESULTS")
        logger.info("="*80)
        
        consistency_rate = (consistent_count / len(products)) * 100
        logger.info(f"Consistent products: {consistent_count}/{len(products)} ({consistency_rate:.1f}%)")
        
        if consistent_count == len(products):
            logger.info("")
            logger.info("🎉 ALL GRAVITY GUMMIES PRODUCTS ARE NOW CONSISTENT!")
            logger.info("✅ All products have:")
            logger.info("   • Price: $35")
            logger.info("   • Weight: 1.12oz")
            logger.info("   • Naming: 1:1:1 prefix")
        else:
            logger.info("")
            logger.warning(f"⚠️  {len(inconsistent_products)} products still need attention:")
            for name, issues in inconsistent_products:
                logger.warning(f"   • {name}: {', '.join(issues)}")
        
    except Exception as e:
        logger.error(f"Error in verification: {e}")
    
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'verify':
        verify_gravity_gummies_consistency()
    else:
        success = fix_gravity_gummies_final()
        if success:
            print("\n🎉 Final Gravity Gummies standardization completed!")
            print("Run 'python3 fix_gravity_gummies_final.py verify' to verify consistency.")
        else:
            print("\n❌ Failed to apply final Gravity Gummies standardization.")
