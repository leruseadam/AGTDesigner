#!/usr/bin/env python3
"""
Script to copy data from product_database.db to product_database_AGT_Bothell.db
before removing the generic database file.
"""
import sqlite3
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def copy_database_data(source_db, target_db):
    """Copy all data from source to target database using ATTACH DATABASE."""
    logger.info(f"Copying data from {source_db} to {target_db}")
    
    if not os.path.exists(source_db):
        logger.warning(f"Source database {source_db} does not exist")
        return
    
    if not os.path.exists(target_db):
        logger.warning(f"Target database {target_db} does not exist")
        return
    
    # Connect to target database
    target_conn = sqlite3.connect(target_db)
    target_cur = target_conn.cursor()
    
    # Attach source database
    target_cur.execute(f"ATTACH DATABASE ? AS source_db", (source_db,))
    
    # Get all tables from source
    target_cur.execute("SELECT name FROM source_db.sqlite_master WHERE type='table' AND name != 'sqlite_sequence'")
    tables = [row[0] for row in target_cur.fetchall()]
    
    logger.info(f"Found tables: {tables}")
    
    for table in tables:
        # Check if table exists in target
        target_cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
        if not target_cur.fetchone():
            logger.info(f"Table {table} does not exist in target, skipping")
            continue
        
        # Get row count from source
        target_cur.execute(f"SELECT COUNT(*) FROM source_db.[{table}]")
        source_count = target_cur.fetchone()[0]
        logger.info(f"Found {source_count} rows in source.{table}")
        
        # Use INSERT OR IGNORE to avoid duplicates based on primary key
        # For products and strains, use INSERT OR REPLACE to merge data
        if table == 'products':
            # Check existing normalized_name values first
            target_cur.execute("SELECT normalized_name FROM products WHERE normalized_name IS NOT NULL")
            existing_names = set(row[0] for row in target_cur.fetchall())
            logger.info(f"Target has {len(existing_names)} existing products")
            
            # Copy all products from source
            target_cur.execute(f"INSERT OR REPLACE INTO products SELECT * FROM source_db.[{table}]")
            target_conn.commit()
            
            # Verify
            target_cur.execute("SELECT COUNT(*) FROM products")
            final_count = target_cur.fetchone()[0]
            logger.info(f"After copy: {final_count} products in target")
        
        elif table == 'strains':
            # Copy all strains from source
            target_cur.execute(f"INSERT OR REPLACE INTO strains SELECT * FROM source_db.[{table}]")
            target_conn.commit()
            
            # Verify
            target_cur.execute("SELECT COUNT(*) FROM strains")
            final_count = target_cur.fetchone()[0]
            logger.info(f"After copy: {final_count} strains in target")
        
        else:
            # For other tables, use INSERT OR REPLACE
            target_cur.execute(f"INSERT OR REPLACE INTO [{table}] SELECT * FROM source_db.[{table}]")
            target_conn.commit()
            logger.info(f"Copied {table}")
    
    # Detach source database
    target_cur.execute("DETACH DATABASE source_db")
    target_conn.close()
    logger.info("Data copy completed")

if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.abspath(__file__))
    source_db = os.path.join(base_dir, 'uploads', 'product_database.db')
    target_db = os.path.join(base_dir, 'uploads', 'product_database_AGT_Bothell.db')
    
    copy_database_data(source_db, target_db)
    
    # Verify counts
    logger.info("\nVerifying final counts:")
    source_conn = sqlite3.connect(source_db)
    target_conn = sqlite3.connect(target_db)
    
    source_cur = source_conn.cursor()
    target_cur = target_conn.cursor()
    
    source_cur.execute("SELECT COUNT(*) FROM products")
    source_count = source_cur.fetchone()[0]
    
    target_cur.execute("SELECT COUNT(*) FROM products")
    target_count = target_cur.fetchone()[0]
    
    logger.info(f"Source products: {source_count}")
    logger.info(f"Target products: {target_count}")
    
    source_cur.execute("SELECT COUNT(*) FROM strains")
    source_strains = source_cur.fetchone()[0]
    
    target_cur.execute("SELECT COUNT(*) FROM strains")
    target_strains = target_cur.fetchone()[0]
    
    logger.info(f"Source strains: {source_strains}")
    logger.info(f"Target strains: {target_strains}")
    
    source_conn.close()
    target_conn.close()
