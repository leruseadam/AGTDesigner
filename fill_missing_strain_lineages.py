#!/usr/bin/env python3
"""
Fill Missing Strain Lineages Script

This script fills in missing strain lineages by looking at the lineage information
from products in the database.
"""

import sqlite3
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fill_missing_strain_lineages(db_path):
    """Fill in missing strain lineages from product data."""
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Get strains with missing lineage
            cursor.execute("""
                SELECT id, strain_name 
                FROM strains 
                WHERE canonical_lineage IS NULL 
                OR canonical_lineage = '' 
                OR canonical_lineage = 'nan'
            """)
            
            strains_without_lineage = cursor.fetchall()
            logger.info(f"Found {len(strains_without_lineage)} strains without lineage information")
            
            if not strains_without_lineage:
                logger.info("No strains need lineage information filled in!")
                return True
            
            # Process each strain
            filled_count = 0
            for strain_id, strain_name in strains_without_lineage:
                # Look for products with this strain that have lineage info
                cursor.execute("""
                    SELECT "Lineage", COUNT(*) as count
                    FROM products 
                    WHERE "Product Strain" = ? 
                    AND "Lineage" IS NOT NULL 
                    AND "Lineage" != '' 
                    AND "Lineage" != 'nan'
                    GROUP BY "Lineage"
                    ORDER BY count DESC
                """, (strain_name,))
                
                lineage_counts = cursor.fetchall()
                
                if lineage_counts:
                    # Use the most common lineage for this strain
                    most_common_lineage = lineage_counts[0][0]
                    count = lineage_counts[0][1]
                    
                    logger.info(f"  Strain '{strain_name}': Found lineage '{most_common_lineage}' from {count} products")
                    
                    # Update the strain with the found lineage
                    cursor.execute("""
                        UPDATE strains 
                        SET canonical_lineage = ?, updated_at = ?
                        WHERE id = ?
                    """, (most_common_lineage, datetime.now().isoformat(), strain_id))
                    
                    filled_count += 1
                else:
                    logger.warning(f"  Strain '{strain_name}': No lineage information found in products")
            
            # Commit changes
            conn.commit()
            
            logger.info(f"\nFilled in lineage information for {filled_count} strains")
            
            # Get updated stats
            cursor.execute("""
                SELECT canonical_lineage, COUNT(*) 
                FROM strains 
                WHERE canonical_lineage IS NOT NULL 
                AND canonical_lineage != '' 
                AND canonical_lineage != 'nan'
                GROUP BY canonical_lineage 
                ORDER BY canonical_lineage
            """)
            
            updated_lineages = dict(cursor.fetchall())
            
            logger.info("Updated lineage distribution:")
            for lineage, count in sorted(updated_lineages.items()):
                logger.info(f"  {lineage}: {count}")
            
            # Check remaining strains without lineage
            cursor.execute("""
                SELECT COUNT(*) 
                FROM strains 
                WHERE canonical_lineage IS NULL 
                OR canonical_lineage = '' 
                OR canonical_lineage = 'nan'
            """)
            
            remaining = cursor.fetchone()[0]
            logger.info(f"\nRemaining strains without lineage: {remaining}")
            
            if remaining == 0:
                logger.info("✅ All strains now have lineage information!")
            else:
                logger.warning(f"⚠️  {remaining} strains still need lineage information")
            
            return True
            
    except Exception as e:
        logger.error(f"Error filling missing strain lineages: {e}")
        return False

def main():
    """Main function."""
    db_path = "uploads/product_database.db"
    
    logger.info("Starting to fill missing strain lineages...")
    logger.info(f"Database path: {db_path}")
    
    success = fill_missing_strain_lineages(db_path)
    
    if success:
        logger.info("✅ Strain lineage filling completed successfully!")
    else:
        logger.error("❌ Strain lineage filling failed!")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
