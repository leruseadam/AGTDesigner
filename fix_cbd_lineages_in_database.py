#!/usr/bin/env python3
"""
Fix CBD lineages in the database.
This script finds all products with CBD indicators and ensures they have CBD lineage.
"""

import sys
import logging
from src.core.data.product_database import get_product_database

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def fix_cbd_lineages():
    """Fix CBD lineages for all products in the database."""
    try:
        logger.info("🌿 Starting CBD lineage fix...")
        
        # Get database
        product_db = get_product_database()
        if not product_db:
            logger.error("Failed to get product database")
            return False
        
        product_db.init_database()
        
        # Get connection
        conn = product_db._get_connection()
        cursor = conn.cursor()
        
        # Find all products with CBD indicators
        cbd_indicators_query = '''
            SELECT id, "Product Name*", "Product Type*", "Product Strain", Lineage
            FROM products
            WHERE 
                ("Product Name*" LIKE '%CBD%' COLLATE NOCASE OR
                 "Product Type*" LIKE '%CBD%' COLLATE NOCASE OR
                 "Product Strain" LIKE '%CBD%' COLLATE NOCASE)
                AND (Lineage != 'CBD' OR Lineage IS NULL)
        '''
        
        cursor.execute(cbd_indicators_query)
        cbd_products = cursor.fetchall()
        
        logger.info(f"🔍 Found {len(cbd_products)} products with CBD indicators that don't have CBD lineage")
        
        if not cbd_products:
            logger.info("✅ No products need CBD lineage fix")
            return True
        
        # Update each product
        fixed_count = 0
        for row in cbd_products:
            product_id, product_name, product_type, product_strain, old_lineage = row
            
            try:
                cursor.execute('''
                    UPDATE products
                    SET Lineage = 'CBD'
                    WHERE id = ?
                ''', (product_id,))
                
                logger.info(f"   ✅ Fixed: '{product_name}' (was: '{old_lineage}' → now: 'CBD')")
                fixed_count += 1
                
            except Exception as e:
                logger.error(f"   ❌ Failed to fix '{product_name}': {e}")
        
        # Commit changes
        conn.commit()
        
        # Also update strain lineages for CBD strains
        logger.info("🌿 Fixing strain lineages...")
        
        cbd_strain_query = '''
            UPDATE strains
            SET canonical_lineage = 'CBD'
            WHERE 
                (strain_name LIKE '%CBD%' COLLATE NOCASE OR
                 strain_name LIKE '%CBD Blend%' COLLATE NOCASE)
                AND (canonical_lineage != 'CBD' OR canonical_lineage IS NULL)
        '''
        
        cursor.execute(cbd_strain_query)
        strain_count = cursor.rowcount
        conn.commit()
        
        logger.info(f"✅ Fixed {fixed_count} product lineages and {strain_count} strain lineages")
        logger.info("🎉 CBD lineage fix completed successfully!")
        
        # Verify the fix
        cursor.execute('''
            SELECT COUNT(*) FROM products
            WHERE ("Product Name*" LIKE '%CBD%' COLLATE NOCASE OR
                   "Product Type*" LIKE '%CBD%' COLLATE NOCASE OR
                   "Product Strain" LIKE '%CBD%' COLLATE NOCASE)
                  AND Lineage = 'CBD'
        ''')
        cbd_with_correct_lineage = cursor.fetchone()[0]
        logger.info(f"📊 Verification: {cbd_with_correct_lineage} CBD products now have CBD lineage")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error fixing CBD lineages: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = fix_cbd_lineages()
    sys.exit(0 if success else 1)

