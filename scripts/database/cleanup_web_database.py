#!/usr/bin/env python3
"""
Advanced database cleanup script for PythonAnywhere production
Run this script ON PYTHONANYWHERE to clean up the database
"""

import os
import sys
import sqlite3
import shutil
from datetime import datetime
import glob
from src.core.data.product_database import ProductDatabase

def cleanup_web_database():
    """Clean up the production database on PythonAnywhere"""
    
    print("=======================================")
    print("ADVANCED DATABASE CLEANUP FOR WEB VERSION")
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
        # Connect to database (prefer ProductDatabase connection)
        try:
            product_db = ProductDatabase(store_name='AGT_Bothell')
            conn = product_db._get_connection()
        except Exception:
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
        
        # Get product count
        cursor.execute("SELECT COUNT(*) FROM products;")
        product_count = cursor.fetchone()[0]
        print(f"📦 Database contains {product_count:,} products")
        
        # Check for blank entries
        print("\n🧹 Checking for blank entries...")
        cursor.execute("SELECT COUNT(*) FROM products WHERE Product_Name IS NULL OR Product_Name = '';")
        blank_names = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM products WHERE Description IS NULL OR Description = '';")
        blank_descriptions = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM products WHERE Product_Brand IS NULL OR Product_Brand = '';")
        blank_brands = cursor.fetchone()[0]
        
        print(f"   Blank product names: {blank_names}")
        print(f"   Blank descriptions: {blank_descriptions}")
        print(f"   Blank brands: {blank_brands}")
        
        # Clean up blank entries if found
        if blank_names > 0 or blank_descriptions > 0 or blank_brands > 0:
            print("\n🧹 Cleaning up blank entries...")
            
            # Create backup before cleanup
            backup_path = f"{db_path}.backup_before_cleanup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(db_path, backup_path)
            print(f"📁 Created backup: {backup_path}")
            
            # Remove entries with blank product names
            if blank_names > 0:
                cursor.execute("DELETE FROM products WHERE Product_Name IS NULL OR Product_Name = '';")
                print(f"   Removed {blank_names} entries with blank product names")
            
            # Update entries with blank descriptions
            if blank_descriptions > 0:
                cursor.execute("UPDATE products SET Description = Product_Name WHERE Description IS NULL OR Description = '';")
                print(f"   Updated {blank_descriptions} entries with blank descriptions")
            
            # Update entries with blank brands
            if blank_brands > 0:
                cursor.execute("UPDATE products SET Product_Brand = 'Unknown' WHERE Product_Brand IS NULL OR Product_Brand = '';")
                print(f"   Updated {blank_brands} entries with blank brands")
            
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
        
        # Close connection only if we opened sqlite3 directly
        try:
            if 'product_db' not in locals():
                conn.close()
        except Exception:
            pass
        
        # Check final file size
        final_size = os.path.getsize(db_path)
        space_saved = db_size - final_size
        print(f"💾 Final database size: {final_size:,} bytes ({final_size/1024/1024:.1f} MB)")
        if space_saved > 0:
            print(f"💾 Space saved: {space_saved:,} bytes ({space_saved/1024/1024:.1f} MB)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during database cleanup: {e}")
        return False

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
        os.remove(lock_file)
        print(f"   Removed lock file: {lock_file}")
    
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

    print("🚀 Starting comprehensive database cleanup...")

    # Change to the correct directory
    if not os.path.exists("uploads"):
        print("❌ Not in the correct directory. Please run from the AGTDesigner directory.")
        return False

    # Run database cleanup
    db_success = cleanup_web_database()

    # Run file cleanup
    cleanup_files()

    if db_success:
        print("\n✅ DATABASE CLEANUP COMPLETE!")
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
