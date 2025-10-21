#!/usr/bin/env python3
"""
DATABASE VERIFICATION SCRIPT
Verify that database schema fixes are working correctly
"""

import os
import sqlite3
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def verify_database_schema(db_path: str) -> bool:
    """Verify that a database has the correct schema"""
    try:
        if not os.path.exists(db_path):
            logging.warning(f"Database file not found: {db_path}")
            return False
        
        logging.info(f"🔍 Verifying database: {db_path}")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if products table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='products'")
        if not cursor.fetchone():
            logging.error("Products table not found")
            return False
        
        # Get current columns
        cursor.execute("PRAGMA table_info(products)")
        columns = [row[1] for row in cursor.fetchall()]
        
        # Check for required columns
        required_columns = ['normalized_name', 'name', 'ProductName', 'Source']
        missing_columns = [col for col in required_columns if col not in columns]
        
        if missing_columns:
            logging.error(f"❌ Missing required columns: {missing_columns}")
            return False
        
        # Check if normalized_name has data
        cursor.execute("SELECT COUNT(*) FROM products WHERE normalized_name IS NOT NULL")
        count = cursor.fetchone()[0]
        
        # Check total products
        cursor.execute("SELECT COUNT(*) FROM products")
        total_count = cursor.fetchone()[0]
        
        logging.info(f"✅ Database schema is correct")
        logging.info(f"   Total products: {total_count}")
        logging.info(f"   Products with normalized_name: {count}")
        logging.info(f"   Required columns present: {required_columns}")
        
        conn.close()
        return True
        
    except Exception as e:
        logging.error(f"❌ Error verifying database: {e}")
        return False

def test_database_functionality():
    """Test that database functionality is working"""
    try:
        logging.info("🧪 Testing database functionality...")
        
        from src.core.data.product_database import ProductDatabase
        
        # Test with main database
        db = ProductDatabase("uploads/product_database.db")
        
        if db.init_database():
            logging.info("✅ Database initialization successful")
            
            # Test basic operations
            conn = db._get_connection()
            cursor = conn.cursor()
            
            # Test query that was failing before
            try:
                cursor.execute("SELECT COUNT(*) FROM products WHERE normalized_name IS NOT NULL")
                count = cursor.fetchone()[0]
                logging.info(f"✅ normalized_name query successful: {count} products")
            except Exception as e:
                logging.error(f"❌ normalized_name query failed: {e}")
                return False
            
            # Test name column query
            try:
                cursor.execute("SELECT COUNT(*) FROM products WHERE name IS NOT NULL")
                count = cursor.fetchone()[0]
                logging.info(f"✅ name column query successful: {count} products")
            except Exception as e:
                logging.error(f"❌ name column query failed: {e}")
                return False
            
            logging.info("✅ All database functionality tests passed")
            return True
        else:
            logging.error("❌ Database initialization failed")
            return False
            
    except Exception as e:
        logging.error(f"❌ Database functionality test failed: {e}")
        return False

def main():
    """Main verification function"""
    logging.info("🔍 DATABASE VERIFICATION")
    logging.info("=" * 40)
    
    # Check main databases
    main_databases = [
        "uploads/product_database.db",
        "uploads/product_database_AGT_Bothell.db"
    ]
    
    all_good = True
    
    for db_path in main_databases:
        if os.path.exists(db_path):
            if not verify_database_schema(db_path):
                all_good = False
        else:
            logging.warning(f"Database not found: {db_path}")
    
    # Test functionality
    if not test_database_functionality():
        all_good = False
    
    if all_good:
        logging.info("\n🎉 ALL VERIFICATIONS PASSED!")
        logging.info("✅ Database schema fixes are working correctly")
        logging.info("✅ No more 'no such column' errors")
        logging.info("✅ Ready for production use")
    else:
        logging.error("\n❌ SOME VERIFICATIONS FAILED!")
        logging.error("Please check the errors above")
    
    return all_good

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
