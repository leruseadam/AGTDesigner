#!/usr/bin/env python3
"""
Simple Database Copy
Copies the working database to the uploads directory
"""

import sqlite3
import os
import shutil

def copy_database():
    """Copy the working database to uploads directory."""
    print("Copying working database to uploads directory...")
    
    try:
        # Source and destination paths
        source_db = 'product_database.db'
        dest_db = 'uploads/product_database.db'
        
        # Check if source exists
        if not os.path.exists(source_db):
            print(f"❌ Source database not found: {source_db}")
            return False
        
        # Remove destination if it exists
        if os.path.exists(dest_db):
            os.remove(dest_db)
        
        # Copy the file
        shutil.copy2(source_db, dest_db)
        
        # Verify the copy
        conn = sqlite3.connect(dest_db)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM products')
        count = cursor.fetchone()[0]
        conn.close()
        
        print(f"✅ Database copied successfully: {count} products")
        return True
        
    except Exception as e:
        print(f"❌ Error copying database: {e}")
        return False

def main():
    """Main function."""
    print("Simple Database Copy")
    print("=" * 20)
    
    if copy_database():
        print("\n🎉 Database copied successfully!")
        print("The application should now have all products.")
    else:
        print("\n❌ Database copy failed!")

if __name__ == "__main__":
    main()
