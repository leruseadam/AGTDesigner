#!/usr/bin/env python3
"""
DATABASE SCHEMA MIGRATION FIX
Fixes missing columns in existing databases
"""

import os
import sqlite3
from src.core.data.product_database import ProductDatabase
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fix_database_schema(db_path: str) -> bool:
    """Fix database schema by adding missing columns"""
    try:
        if not os.path.exists(db_path):
            logging.error(f"Database file not found: {db_path}")
            return False
        
        logging.info(f"🔧 Fixing database schema: {db_path}")

        # Prefer ProductDatabase connection when operating on the app uploads DB
        try:
            if 'product_database' in str(db_path):
                product_db = ProductDatabase(store_name='AGT_Bothell')
                conn = product_db._get_connection()
            else:
                conn = sqlite3.connect(db_path)
        except Exception:
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
        logging.info(f"Current columns: {columns}")
        
        # Add missing columns
        missing_columns = []
        
        if 'normalized_name' not in columns:
            missing_columns.append('normalized_name')
        
        if 'name' not in columns:
            missing_columns.append('name')
        
        if 'ProductName' not in columns:
            missing_columns.append('ProductName')
        
        if 'Source' not in columns:
            missing_columns.append('Source')
        
        if missing_columns:
            logging.info(f"Adding missing columns: {missing_columns}")
            
            for column in missing_columns:
                try:
                    if column == 'normalized_name':
                        cursor.execute(f"ALTER TABLE products ADD COLUMN {column} TEXT")
                        # Populate with normalized product names
                        cursor.execute("UPDATE products SET normalized_name = LOWER(REPLACE(REPLACE(\"Product Name*\", ' ', '_'), '-', '_')) WHERE normalized_name IS NULL")
                    elif column == 'name':
                        cursor.execute(f"ALTER TABLE products ADD COLUMN {column} TEXT")
                        # Populate with product names
                        cursor.execute("UPDATE products SET name = \"Product Name*\" WHERE name IS NULL")
                    elif column == 'ProductName':
                        cursor.execute(f"ALTER TABLE products ADD COLUMN \"{column}\" TEXT")
                        # Populate with product names
                        cursor.execute("UPDATE products SET \"ProductName\" = \"Product Name*\" WHERE \"ProductName\" IS NULL")
                    elif column == 'Source':
                        cursor.execute(f"ALTER TABLE products ADD COLUMN \"{column}\" TEXT")
                        # Set default source
                        cursor.execute("UPDATE products SET \"Source\" = 'Database Import' WHERE \"Source\" IS NULL")
                    
                    logging.info(f"✅ Added column: {column}")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" in str(e):
                        logging.info(f"Column {column} already exists")
                    else:
                        logging.error(f"Error adding column {column}: {e}")
                        return False
        
        # Check strains table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='strains'")
        if cursor.fetchone():
            cursor.execute("PRAGMA table_info(strains)")
            strain_columns = [row[1] for row in cursor.fetchall()]
            
            if 'normalized_name' not in strain_columns:
                try:
                    cursor.execute("ALTER TABLE strains ADD COLUMN normalized_name TEXT")
                    cursor.execute("UPDATE strains SET normalized_name = LOWER(REPLACE(REPLACE(strain_name, ' ', '_'), '-', '_')) WHERE normalized_name IS NULL")
                    logging.info("✅ Added normalized_name to strains table")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" not in str(e):
                        logging.error(f"Error adding normalized_name to strains: {e}")
        
        # Commit changes
        conn.commit()
        
        # Verify the fix
        cursor.execute("PRAGMA table_info(products)")
        updated_columns = [row[1] for row in cursor.fetchall()]
        logging.info(f"Updated columns: {updated_columns}")
        
        # Check if normalized_name column exists and has data
        cursor.execute("SELECT COUNT(*) FROM products WHERE normalized_name IS NOT NULL")
        count = cursor.fetchone()[0]
        logging.info(f"Products with normalized_name: {count}")
        
        conn.close()
        
        logging.info(f"✅ Database schema fixed: {db_path}")
        return True
        
    except Exception as e:
        logging.error(f"❌ Error fixing database schema: {e}")
        return False

def fix_all_databases():
    """Fix all database files in the project"""
    logging.info("🔧 DATABASE SCHEMA MIGRATION FIX")
    logging.info("=" * 50)
    
    # Common database locations
    db_paths = [
        "uploads/product_database.db",
        "uploads/product_database_AGT_Bothell.db",
        "uploads/product_database_AGT_Bothell.db-shm",
        "uploads/product_database_AGT_Bothell.db-wal"
    ]
    
    # Also check for any .db files in uploads
    uploads_dir = Path("uploads")
    if uploads_dir.exists():
        for db_file in uploads_dir.glob("*.db"):
            if db_file.name not in [Path(p).name for p in db_paths]:
                db_paths.append(str(db_file))
    
    fixed_count = 0
    total_count = 0
    
    for db_path in db_paths:
        if os.path.exists(db_path) and db_path.endswith('.db'):
            total_count += 1
            if fix_database_schema(db_path):
                fixed_count += 1
        elif db_path.endswith(('.db-shm', '.db-wal')):
            # These are SQLite temporary files, skip them
            logging.info(f"⏭️ Skipping temporary file: {db_path}")
    
    logging.info(f"\n📊 MIGRATION SUMMARY:")
    logging.info(f"   Total databases found: {total_count}")
    logging.info(f"   Successfully fixed: {fixed_count}")
    logging.info(f"   Failed: {total_count - fixed_count}")
    
    if fixed_count == total_count and total_count > 0:
        logging.info("✅ All databases have been successfully migrated!")
    elif total_count == 0:
        logging.warning("⚠️ No database files found to migrate")
    else:
        logging.warning(f"⚠️ {total_count - fixed_count} databases failed to migrate")

def create_fresh_database_with_schema():
    """Create a fresh database with the correct schema"""
    try:
        logging.info("🆕 Creating fresh database with correct schema...")
        
        from src.core.data.product_database import ProductDatabase
        
        # Create a fresh database instance
        db = ProductDatabase("uploads/product_database_fresh.db")
        
        # Initialize with correct schema
        if db.init_database():
            logging.info("✅ Fresh database created successfully")
            
            # Test the database
            conn = db._get_connection()
            cursor = conn.cursor()
            
            # Check columns
            cursor.execute("PRAGMA table_info(products)")
            columns = [row[1] for row in cursor.fetchall()]
            logging.info(f"Fresh database columns: {columns}")
            
            # Check if required columns exist
            required_columns = ['normalized_name', 'name', 'ProductName', 'Source']
            missing = [col for col in required_columns if col not in columns]
            
            if missing:
                logging.error(f"❌ Fresh database missing columns: {missing}")
                return False
            else:
                logging.info("✅ Fresh database has all required columns")
                return True
        else:
            logging.error("❌ Failed to initialize fresh database")
            return False
            
    except Exception as e:
        logging.error(f"❌ Error creating fresh database: {e}")
        return False

def main():
    """Main function"""
    logging.info("🚀 Starting Database Schema Migration")
    
    # Fix existing databases
    fix_all_databases()
    
    # Create a fresh database as backup
    logging.info("\n🆕 Creating fresh database as backup...")
    if create_fresh_database_with_schema():
        logging.info("✅ Fresh database created successfully")
    else:
        logging.error("❌ Failed to create fresh database")
    
    logging.info("\n✅ Database migration completed!")

if __name__ == "__main__":
    main()
