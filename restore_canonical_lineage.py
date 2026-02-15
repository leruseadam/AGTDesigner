#!/usr/bin/env python3
"""
Restore canonical lineage from strains table to products table.

This script fixes products that have the wrong lineage by restoring
the canonical_lineage from the strains table (which should be the
authoritative source of truth for lineage data).

Usage:
    python3 restore_canonical_lineage.py [--store STORE_NAME] [--dry-run]
"""

import sqlite3
import sys
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def restore_canonical_lineage(store_name='AGT_Bothell', dry_run=False):
    """Restore canonical lineage from strains table to products."""
    
    # Determine database path - it's in uploads/ directory
    uploads_dir = project_root / 'uploads'
    db_path = uploads_dir / f'product_database_{store_name}.db'
    
    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        print(f"   Looking in: {uploads_dir}")
        # List available databases
        if uploads_dir.exists():
            db_files = list(uploads_dir.glob('product_database_*.db'))
            if db_files:
                print(f"   Available databases:")
                for f in db_files:
                    print(f"      - {f.name}")
        return False
    
    print(f"{'[DRY RUN] ' if dry_run else ''}Restoring canonical lineage for store: {store_name}")
    print(f"Database: {db_path}")
    print("-" * 80)
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Get all products that have a strain_id
        cursor.execute('''
            SELECT 
                p.id,
                p."Product Name*",
                p.strain_id,
                p."Lineage" as product_lineage,
                s.canonical_lineage as strain_canonical,
                s.strain_name
            FROM products p
            LEFT JOIN strains s ON p.strain_id = s.id
            WHERE p.strain_id IS NOT NULL
              AND s.canonical_lineage IS NOT NULL
              AND TRIM(s.canonical_lineage) != ''
              AND s.canonical_lineage NOT IN ('nan', 'None', 'null')
        ''')
        
        products = cursor.fetchall()
        print(f"Found {len(products)} products with strain canonical lineage available")
        print()
        
        if not products:
            print("✅ No products need updating")
            return True
        
        updated_count = 0
        mismatch_count = 0
        
        for product_id, product_name, strain_id, product_lineage, strain_canonical, strain_name in products:
            product_lineage_clean = (product_lineage or '').strip().upper()
            strain_canonical_clean = (strain_canonical or '').strip().upper()
            
            # Only update if they differ
            if product_lineage_clean != strain_canonical_clean:
                mismatch_count += 1
                print(f"🔧 Product: {product_name}")
                print(f"   Strain: {strain_name}")
                print(f"   Current product lineage: {product_lineage_clean or '(empty)'}")
                print(f"   Strain canonical lineage: {strain_canonical_clean}")
                
                if not dry_run:
                    # Update the product's Lineage to match strain canonical_lineage
                    cursor.execute('''
                        UPDATE products 
                        SET "Lineage" = ?,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    ''', (strain_canonical_clean, product_id))
                    updated_count += 1
                    print(f"   ✅ Updated to: {strain_canonical_clean}")
                else:
                    print(f"   [DRY RUN] Would update to: {strain_canonical_clean}")
                print()
        
        if not dry_run:
            conn.commit()
            print("=" * 80)
            print(f"✅ SUCCESS: Updated {updated_count} products with canonical lineage from strains table")
            print(f"   Total products checked: {len(products)}")
            print(f"   Products with mismatches: {mismatch_count}")
            print(f"   Products updated: {updated_count}")
        else:
            print("=" * 80)
            print(f"[DRY RUN] Would update {mismatch_count} products")
            print(f"   Run without --dry-run to apply changes")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Restore canonical lineage from strains to products')
    parser.add_argument('--store', default='AGT_Bothell', help='Store name (default: AGT_Bothell)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be updated without making changes')
    
    args = parser.parse_args()
    
    success = restore_canonical_lineage(store_name=args.store, dry_run=args.dry_run)
    sys.exit(0 if success else 1)
