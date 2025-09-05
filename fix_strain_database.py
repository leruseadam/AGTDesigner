#!/usr/bin/env python3
"""
Strain Database Fix Script

This script fixes various issues in the strain database:
1. Standardizes lineage values to proper format
2. Fixes mixed case issues
3. Converts invalid lineage formats to standard ones
4. Reports on the fixes made
"""

import sqlite3
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_strain_database(db_path):
    """Fix the strain database issues."""
    
    # Lineage mapping for fixes
    lineage_fixes = {
        'hybrid': 'HYBRID',
        'indica': 'INDICA', 
        'sativa': 'SATIVA',
        'cbd': 'CBD',
        'indica_hybrid': 'HYBRID/INDICA',
        'sativa_hybrid': 'HYBRID/SATIVA',
        'hybrid_indica': 'HYBRID/INDICA',
        'hybrid_sativa': 'HYBRID/SATIVA'
    }
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Get current stats
            logger.info("Getting current database stats...")
            cursor.execute("SELECT COUNT(*) FROM strains")
            total_strains = cursor.fetchone()[0]
            
            cursor.execute("SELECT canonical_lineage, COUNT(*) FROM strains WHERE canonical_lineage IS NOT NULL AND canonical_lineage != '' GROUP BY canonical_lineage")
            current_lineages = dict(cursor.fetchall())
            
            logger.info(f"Total strains: {total_strains}")
            logger.info("Current lineage distribution:")
            for lineage, count in sorted(current_lineages.items()):
                logger.info(f"  {lineage}: {count}")
            
            # Apply fixes
            logger.info("\nApplying lineage fixes...")
            total_fixed = 0
            
            for old_lineage, new_lineage in lineage_fixes.items():
                cursor.execute("""
                    UPDATE strains 
                    SET canonical_lineage = ?, updated_at = ?
                    WHERE canonical_lineage = ?
                """, (new_lineage, datetime.now().isoformat(), old_lineage))
                
                rows_affected = cursor.fetchone()[0] if cursor.fetchone() else 0
                if rows_affected > 0:
                    logger.info(f"  Fixed {rows_affected} strains: '{old_lineage}' -> '{new_lineage}'")
                    total_fixed += rows_affected
            
            # Fix any remaining mixed case issues
            cursor.execute("""
                UPDATE strains 
                SET canonical_lineage = UPPER(canonical_lineage), updated_at = ?
                WHERE canonical_lineage IS NOT NULL 
                AND canonical_lineage != '' 
                AND canonical_lineage != UPPER(canonical_lineage)
                AND canonical_lineage NOT IN ('HYBRID/INDICA', 'HYBRID/SATIVA')
            """, (datetime.now().isoformat(),))
            
            mixed_case_fixed = cursor.fetchone()[0] if cursor.fetchone() else 0
            if mixed_case_fixed > 0:
                logger.info(f"  Fixed {mixed_case_fixed} mixed case lineages")
                total_fixed += mixed_case_fixed
            
            # Commit changes
            conn.commit()
            
            # Get updated stats
            logger.info("\nGetting updated database stats...")
            cursor.execute("SELECT canonical_lineage, COUNT(*) FROM strains WHERE canonical_lineage IS NOT NULL AND canonical_lineage != '' GROUP BY canonical_lineage ORDER BY canonical_lineage")
            updated_lineages = dict(cursor.fetchall())
            
            logger.info("Updated lineage distribution:")
            for lineage, count in sorted(updated_lineages.items()):
                logger.info(f"  {lineage}: {count}")
            
            logger.info(f"\nTotal strains fixed: {total_fixed}")
            
            # Check for any remaining issues
            cursor.execute("""
                SELECT canonical_lineage, COUNT(*) 
                FROM strains 
                WHERE canonical_lineage IS NOT NULL 
                AND canonical_lineage != '' 
                AND canonical_lineage NOT IN ('HYBRID', 'INDICA', 'SATIVA', 'CBD', 'HYBRID/INDICA', 'HYBRID/SATIVA', 'PARAPHERNALIA')
                GROUP BY canonical_lineage
            """)
            
            remaining_issues = cursor.fetchall()
            if remaining_issues:
                logger.warning("\nRemaining non-standard lineages:")
                for lineage, count in remaining_issues:
                    logger.warning(f"  {lineage}: {count}")
            else:
                logger.info("\n✅ All lineages are now standardized!")
            
            return True
            
    except Exception as e:
        logger.error(f"Error fixing strain database: {e}")
        return False

def main():
    """Main function."""
    db_path = "uploads/product_database.db"
    
    logger.info("Starting strain database fix...")
    logger.info(f"Database path: {db_path}")
    
    success = fix_strain_database(db_path)
    
    if success:
        logger.info("✅ Strain database fix completed successfully!")
    else:
        logger.error("❌ Strain database fix failed!")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
