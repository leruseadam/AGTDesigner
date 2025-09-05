#!/usr/bin/env python3
"""
Product Database Duplicate Removal Script

This script identifies and removes duplicate products from the product database
to improve performance and prevent startup hangs.
"""

import sqlite3
import logging
from pathlib import Path
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def connect_to_database():
    """Connect to the product database."""
    db_path = Path("uploads/product_database.db")
    
    if not db_path.exists():
        logger.error(f"Database not found at {db_path}")
        return None
    
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        logger.info(f"Connected to database: {db_path}")
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        return None

def analyze_duplicates(conn):
    """Analyze the database for duplicate products."""
    cursor = conn.cursor()
    
    # Check for duplicate product names
    logger.info("Analyzing duplicate product names...")
    cursor.execute("""
        SELECT "Product Name*", COUNT(*) as count
        FROM products 
        WHERE "Product Name*" IS NOT NULL AND "Product Name*" != ''
        GROUP BY "Product Name*" 
        HAVING COUNT(*) > 1
        ORDER BY count DESC
    """)
    
    duplicate_names = cursor.fetchall()
    logger.info(f"Found {len(duplicate_names)} product names with duplicates")
    
    # Check for duplicate combinations (vendor + brand + product_name + weight)
    logger.info("Analyzing duplicate product combinations...")
    cursor.execute("""
        SELECT "Vendor/Supplier*", "Product Brand", "Product Name*", "Weight*", COUNT(*) as count
        FROM products 
        WHERE "Vendor/Supplier*" IS NOT NULL AND "Product Brand" IS NOT NULL AND "Product Name*" IS NOT NULL
        GROUP BY "Vendor/Supplier*", "Product Brand", "Product Name*", "Weight*"
        HAVING COUNT(*) > 1
        ORDER BY count DESC
    """)
    
    duplicate_combinations = cursor.fetchall()
    logger.info(f"Found {len(duplicate_combinations)} product combinations with duplicates")
    
    return duplicate_names, duplicate_combinations

def remove_duplicate_names(conn):
    """Remove duplicate product names, keeping the first occurrence."""
    cursor = conn.cursor()
    
    logger.info("Removing duplicate product names...")
    
    # Get all duplicate product names
    cursor.execute("""
        SELECT "Product Name*", COUNT(*) as count
        FROM products 
        WHERE "Product Name*" IS NOT NULL AND "Product Name*" != ''
        GROUP BY "Product Name*" 
        HAVING COUNT(*) > 1
    """)
    
    duplicates = cursor.fetchall()
    
    total_removed = 0
    for duplicate in duplicates:
        product_name = duplicate['Product Name*']
        count = duplicate['count']
        
        # Keep the first occurrence, remove the rest
        cursor.execute("""
            DELETE FROM products 
            WHERE "Product Name*" = ? 
            AND rowid NOT IN (
                SELECT MIN(rowid) 
                FROM products 
                WHERE "Product Name*" = ?
            )
        """, (product_name, product_name))
        
        removed_count = cursor.rowcount
        total_removed += removed_count
        logger.info(f"Removed {removed_count} duplicates for '{product_name}' (kept 1, removed {removed_count})")
    
    conn.commit()
    logger.info(f"Total duplicate product names removed: {total_removed}")
    return total_removed

def remove_duplicate_combinations(conn):
    """Remove duplicate product combinations, keeping the first occurrence."""
    cursor = conn.cursor()
    
    logger.info("Removing duplicate product combinations...")
    
    # Get all duplicate combinations
    cursor.execute("""
        SELECT "Vendor/Supplier*", "Product Brand", "Product Name*", "Weight*", COUNT(*) as count
        FROM products 
        WHERE "Vendor/Supplier*" IS NOT NULL AND "Product Brand" IS NOT NULL AND "Product Name*" IS NOT NULL
        GROUP BY "Vendor/Supplier*", "Product Brand", "Product Name*", "Weight*"
        HAVING COUNT(*) > 1
    """)
    
    duplicates = cursor.fetchall()
    
    total_removed = 0
    for duplicate in duplicates:
        vendor = duplicate['Vendor/Supplier*']
        brand = duplicate['Product Brand']
        product_name = duplicate['Product Name*']
        weight = duplicate['Weight*']
        count = duplicate['count']
        
        # Keep the first occurrence, remove the rest
        cursor.execute("""
            DELETE FROM products 
            WHERE "Vendor/Supplier*" = ? AND "Product Brand" = ? AND "Product Name*" = ? AND "Weight*" = ?
            AND rowid NOT IN (
                SELECT MIN(rowid) 
                FROM products 
                WHERE "Vendor/Supplier*" = ? AND "Product Brand" = ? AND "Product Name*" = ? AND "Weight*" = ?
            )
        """, (vendor, brand, product_name, weight, vendor, brand, product_name, weight))
        
        removed_count = cursor.rowcount
        total_removed += removed_count
        logger.info(f"Removed {removed_count} duplicates for '{product_name}' ({vendor}/{brand}/{weight})")
    
    conn.commit()
    logger.info(f"Total duplicate combinations removed: {total_removed}")
    return total_removed

def vacuum_database(conn):
    """Vacuum the database to reclaim space after removing duplicates."""
    logger.info("Vacuuming database to reclaim space...")
    
    try:
        conn.execute("VACUUM")
        logger.info("Database vacuumed successfully")
    except Exception as e:
        logger.error(f"Failed to vacuum database: {e}")

def get_database_stats(conn):
    """Get current database statistics."""
    cursor = conn.cursor()
    
    # Get total product count
    cursor.execute("SELECT COUNT(*) as total FROM products")
    total_products = cursor.fetchone()['total']
    
    # Get unique product names count
    cursor.execute("""
        SELECT COUNT(DISTINCT "Product Name*") as unique_names 
        FROM products 
        WHERE "Product Name*" IS NOT NULL AND "Product Name*" != ''
    """)
    unique_names = cursor.fetchone()['unique_names']
    
    # Get unique combinations count
    cursor.execute("""
        SELECT COUNT(DISTINCT "Vendor/Supplier*" || '|' || "Product Brand" || '|' || "Product Name*" || '|' || "Weight*") as unique_combinations
        FROM products 
        WHERE "Vendor/Supplier*" IS NOT NULL AND "Product Brand" IS NOT NULL AND "Product Name*" IS NOT NULL
    """)
    unique_combinations = cursor.fetchone()['unique_combinations']
    
    logger.info(f"Database Statistics:")
    logger.info(f"  Total products: {total_products}")
    logger.info(f"  Unique product names: {unique_names}")
    logger.info(f"  Unique combinations: {unique_combinations}")
    
    return total_products, unique_names, unique_combinations

def main():
    """Main function to remove duplicates from the product database."""
    logger.info("Starting Product Database Duplicate Removal...")
    
    # Connect to database
    conn = connect_to_database()
    if not conn:
        sys.exit(1)
    
    try:
        # Get initial statistics
        logger.info("Getting initial database statistics...")
        initial_total, initial_unique_names, initial_unique_combinations = get_database_stats(conn)
        
        # Analyze duplicates
        duplicate_names, duplicate_combinations = analyze_duplicates(conn)
        
        if not duplicate_names and not duplicate_combinations:
            logger.info("No duplicates found in the database!")
            return
        
        # Remove duplicates
        removed_names = remove_duplicate_names(conn)
        removed_combinations = remove_duplicate_combinations(conn)
        
        # Vacuum database
        vacuum_database(conn)
        
        # Get final statistics
        logger.info("Getting final database statistics...")
        final_total, final_unique_names, final_unique_combinations = get_database_stats(conn)
        
        # Summary
        logger.info("=" * 50)
        logger.info("DUPLICATE REMOVAL SUMMARY")
        logger.info("=" * 50)
        logger.info(f"Initial total products: {initial_total}")
        logger.info(f"Final total products: {final_total}")
        logger.info(f"Products removed: {initial_total - final_total}")
        logger.info(f"Duplicate names removed: {removed_names}")
        logger.info(f"Duplicate combinations removed: {removed_combinations}")
        logger.info(f"Space saved: {initial_total - final_total} records")
        logger.info("=" * 50)
        
        if initial_total - final_total > 0:
            logger.info("✅ Duplicate removal completed successfully!")
            logger.info("This should improve database performance and reduce startup hangs.")
        else:
            logger.info("ℹ️ No duplicates were removed.")
            
    except Exception as e:
        logger.error(f"Error during duplicate removal: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()
        logger.info("Database connection closed")

if __name__ == "__main__":
    main()
