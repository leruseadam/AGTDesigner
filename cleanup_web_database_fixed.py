#!/usr/bin/env python3
"""
Fixed database cleanup script for PythonAnywhere production
Handles the actual database schema correctly
"""

import os
import sys
import sqlite3
import shutil
from datetime import datetime
import glob

def get_database_schema(db_path):
    """Get the actual database schema to understand the column names"""
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get table info
        cursor.execute("PRAGMA table_info(products);")
        columns = cursor.fetchall()
        
        print("📋 Database schema:")
        for col in columns:
            print(f"   {col[1]} ({col[2]})")
        
        # Get column names
        column_names = [col[1] for col in columns]
        
        conn.close()
        return column_names
        
    except Exception as e:
        print(f"❌ Error getting schema: {e}")
        return []

def cleanup_web_database_fixed():
    """Clean up the production database with correct schema handling"""
    
    print("=======================================")
    print("FIXED DATABASE CLEANUP FOR WEB VERSION")
    print("=======================================")
    
    db_path = "uploads/product_database_AGT_Bothell.db"
    
    # Check if database exists
    if not os.path.exists(db_path):
        print("❌ No database file found!")
        return False
    
    # Get database info
    db_size = os.path.getsize(db_path)
    print(f"📊 Database file size: {db_size:,} bytes ({db_size/1024/1024:.1f} MB)")
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check integrity
        print("\n🔍 Checking database integrity...")
        cursor.execute("PRAGMA integrity_check;")
        integrity_result = cursor.fetchone()[0]
        
        if integrity_result == "ok":
            print("✅ Database integrity check passed")
        else:
            print(f"❌ Database integrity check failed: {integrity_result}")
            return False
        
        # Get the actual schema
        schema = get_database_schema(db_path)
        if not schema:
            print("❌ Could not get database schema")
            return False
        
        # Get product count
        print("\n📦 Getting product count...")
        cursor.execute("SELECT COUNT(*) FROM products;")
        product_count = cursor.fetchone()[0]
        print(f"📦 Database contains {product_count:,} products")
        
        if product_count == 0:
            print("⚠️  Database is empty - this might be expected for a fresh deployment")
            conn.close()
            return True
        
        # Check for blank entries using actual column names
        print("\n🧹 Checking for blank entries...")
        
        # Find the correct column names
        product_name_col = None
        description_col = None
        brand_col = None
        
        # Common variations of column names
        name_variations = ['Product Name*', 'ProductName', 'product_name', 'name', 'Name']
        desc_variations = ['Description', 'description', 'desc', 'product_description']
        brand_variations = ['Product Brand', 'Brand', 'brand', 'product_brand']
        
        for col in schema:
            if col in name_variations:
                product_name_col = col
            elif col in desc_variations:
                description_col = col
            elif col in brand_variations:
                brand_col = col
        
        print(f"   Using columns: name='{product_name_col}', description='{description_col}', brand='{brand_col}'")
        
        # Check for blank entries
        blank_counts = {}
        
        if product_name_col:
            cursor.execute(f"SELECT COUNT(*) FROM products WHERE {product_name_col} IS NULL OR {product_name_col} = '';")
            blank_counts['names'] = cursor.fetchone()[0]
            print(f"   Blank product names: {blank_counts['names']}")
        
        if description_col:
            cursor.execute(f"SELECT COUNT(*) FROM products WHERE {description_col} IS NULL OR {description_col} = '';")
            blank_counts['descriptions'] = cursor.fetchone()[0]
            print(f"   Blank descriptions: {blank_counts['descriptions']}")
        
        if brand_col:
            cursor.execute(f"SELECT COUNT(*) FROM products WHERE {brand_col} IS NULL OR {brand_col} = '';")
            blank_counts['brands'] = cursor.fetchone()[0]
            print(f"   Blank brands: {blank_counts['brands']}")
        
        # Clean up blank entries if found
        total_blank = sum(blank_counts.values())
        if total_blank > 0:
            print(f"\n🧹 Cleaning up {total_blank} blank entries...")
            
            # Create backup before cleanup
            backup_path = f"{db_path}.backup_before_cleanup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(db_path, backup_path)
            print(f"📁 Created backup: {backup_path}")
            
            # Remove entries with blank product names
            if product_name_col and blank_counts.get('names', 0) > 0:
                cursor.execute(f"DELETE FROM products WHERE {product_name_col} IS NULL OR {product_name_col} = '';")
                print(f"   Removed {blank_counts['names']} entries with blank product names")
            
            # Update entries with blank descriptions
            if description_col and brand_col and blank_counts.get('descriptions', 0) > 0:
                cursor.execute(f"UPDATE products SET {description_col} = {product_name_col} WHERE {description_col} IS NULL OR {description_col} = '';")
                print(f"   Updated {blank_counts['descriptions']} entries with blank descriptions")
            
            # Update entries with blank brands
            if brand_col and blank_counts.get('brands', 0) > 0:
                cursor.execute(f"UPDATE products SET {brand_col} = 'Unknown' WHERE {brand_col} IS NULL OR {brand_col} = '';")
                print(f"   Updated {blank_counts['brands']} entries with blank brands")
            
            # Commit changes
            conn.commit()
            print("✅ Blank entries cleaned up")
        
        # Vacuum database to reclaim space
        print("\n🧹 Vacuuming database to reclaim space...")
        cursor.execute("VACUUM;")
        print("✅ Database vacuumed")
        
        # Get final stats
        cursor.execute("SELECT COUNT(*) FROM products;")
        final_count = cursor.fetchone()[0]
        print(f"📦 Final product count: {final_count:,} products")
        
        # Close connection
        conn.close()
        
        # Check final file size
        final_size = os.path.getsize(db_path)
        space_saved = db_size - final_size
        print(f"💾 Final database size: {final_size:,} bytes ({final_size/1024/1024:.1f} MB)")
        if space_saved > 0:
            print(f"💾 Space saved: {space_saved:,} bytes ({space_saved/1024/1024:.1f} MB)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during database cleanup: {e}")
        import traceback
        print(f"Full error: {traceback.format_exc()}")
        return False

def create_fresh_database_if_needed():
    """Create a fresh database if the current one is empty or corrupted"""
    
    print("\n🔄 Checking if fresh database creation is needed...")
    
    db_path = "uploads/product_database_AGT_Bothell.db"
    
    if not os.path.exists(db_path):
        print("📝 No database file found, creating fresh database...")
        try:
            # Run the fresh database creation script
            import subprocess
            result = subprocess.run(['python3', 'create_fresh_database.py'], 
                                  capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print("✅ Fresh database created successfully")
                return True
            else:
                print(f"❌ Failed to create fresh database: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error creating fresh database: {e}")
            return False
    
    # Check if database is too small (likely empty or corrupted)
    db_size = os.path.getsize(db_path)
    if db_size < 100000:  # Less than 100KB is suspicious
        print(f"⚠️  Database is very small ({db_size} bytes), might be corrupted")
        
        # Try to get product count
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM products;")
            count = cursor.fetchone()[0]
            conn.close()
            
            if count == 0:
                print("📝 Database is empty, creating fresh database...")
                return create_fresh_database_if_needed()
            
        except Exception as e:
            print(f"❌ Database appears corrupted: {e}")
            print("📝 Creating fresh database...")
            return create_fresh_database_if_needed()
    
    return True

def cleanup_files():
    """Clean up old files and temporary data"""
    
    print("\n🧹 Cleaning up old files...")
    
    # Clean up old backup files (keep only last 5)
    backup_files = sorted(glob.glob("uploads/*.db.backup*"), key=os.path.getmtime, reverse=True)
    if len(backup_files) > 5:
        for old_backup in backup_files[5:]:
            os.remove(old_backup)
            print(f"   Removed old backup: {old_backup}")
    
    # Clean up lock files
    lock_files = glob.glob("uploads/*.db-shm") + glob.glob("uploads/*.db-wal")
    for lock_file in lock_files:
        try:
            os.remove(lock_file)
            print(f"   Removed lock file: {lock_file}")
        except:
            pass
    
    # Clean up old sessions
    if os.path.exists("sessions"):
        import time
        current_time = time.time()
        for session_file in os.listdir("sessions"):
            session_path = os.path.join("sessions", session_file)
            if os.path.isfile(session_path):
                # Remove sessions older than 1 day
                if current_time - os.path.getmtime(session_path) > 86400:
                    os.remove(session_path)
                    print(f"   Removed old session: {session_file}")
    
    print("✅ File cleanup completed")

def main():
    """Main cleanup function"""
    
    print("🚀 Starting fixed database cleanup...")
    
    # Change to the correct directory
    if not os.path.exists("uploads"):
        print("❌ Not in the correct directory. Please run from the AGTDesigner directory.")
        return False
    
    # First, ensure we have a proper database
    if not create_fresh_database_if_needed():
        print("❌ Could not create or verify database")
        return False
    
    # Run database cleanup
    db_success = cleanup_web_database_fixed()
    
    # Run file cleanup
    cleanup_files()
    
    if db_success:
        print("\n✅ FIXED DATABASE CLEANUP COMPLETE!")
        print("Next steps:")
        print("1. Go to PythonAnywhere Web tab")
        print("2. Click 'Reload www.agtpricetags.com'")
        print("3. Test the application")
    else:
        print("\n❌ Database cleanup failed. Check the error messages above.")
    
    return db_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
